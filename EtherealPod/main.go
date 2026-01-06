package main

import (
	"context"
	"fmt"
	"time"

	corev1 "k8s.io/api/core/v1"
	apierrors "k8s.io/apimachinery/pkg/api/errors"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/apis/meta/v1/unstructured"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/runtime/schema"
	"k8s.io/apimachinery/pkg/watch"
	"k8s.io/client-go/dynamic"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
	"k8s.io/client-go/tools/cache"
	"k8s.io/klog/v2"
)

var (
	etherealPodGVR = schema.GroupVersionResource{
		Group:    "example.com",
		Version:  "v1",
		Resource: "etherealpods",
	}
	etherealPodGVK = schema.GroupVersionKind{
		Group:   "example.com",
		Version: "v1",
		Kind:    "EtherealPod",
	}
)

type Controller struct {
	clientset     *kubernetes.Clientset
	dynamicClient dynamic.Interface
	informer      cache.SharedIndexInformer
}

func NewController(clientset *kubernetes.Clientset, dynamicClient dynamic.Interface) *Controller {
	// Watch all namespaces for this Namespaced CRD (cluster-wide watch)
	informer := cache.NewSharedIndexInformer(
		&cache.ListWatch{
			ListFunc: func(options metav1.ListOptions) (runtime.Object, error) {
				return dynamicClient.Resource(etherealPodGVR).Namespace(metav1.NamespaceAll).List(context.TODO(), options)
			},
			WatchFunc: func(options metav1.ListOptions) (watch.Interface, error) {
				return dynamicClient.Resource(etherealPodGVR).Namespace(metav1.NamespaceAll).Watch(context.TODO(), options)
			},
		},
		&unstructured.Unstructured{},
		0,
		cache.Indexers{},
	)

	c := &Controller{
		clientset:     clientset,
		dynamicClient: dynamicClient,
		informer:      informer,
	}

	informer.AddEventHandler(cache.ResourceEventHandlerFuncs{
		AddFunc:    c.handleAdd,
		UpdateFunc: c.handleUpdate,
		DeleteFunc: c.handleDelete,
	})

	return c
}

func (c *Controller) Run(stopCh <-chan struct{}) {
	defer klog.Info("Shutting down controller")
	klog.Info("Starting EtherealPod controller (SINGLETON MODE - oldest wins per namespace)")

	go c.informer.Run(stopCh)

	if !cache.WaitForCacheSync(stopCh, c.informer.HasSynced) {
		klog.Fatal("Failed to sync cache")
	}
	klog.Info("Controller synced and ready")

	go c.healthCheckLoop(stopCh)

	<-stopCh
}

func (c *Controller) healthCheckLoop(stopCh <-chan struct{}) {
	ticker := time.NewTicker(10 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			c.reconcileAll()
		case <-stopCh:
			return
		}
	}
}

func (c *Controller) reconcileAll() {
	items := c.informer.GetStore().List()
	for _, item := range items {
		ep, ok := item.(*unstructured.Unstructured)
		if !ok {
			continue
		}
		c.reconcile(ep)
	}
}

func (c *Controller) handleAdd(obj interface{}) {
	ep := obj.(*unstructured.Unstructured)
	klog.Infof("EtherealPod added: %s/%s", ep.GetNamespace(), ep.GetName())
	c.reconcile(ep)
}

func (c *Controller) handleUpdate(_, newObj interface{}) {
	ep := newObj.(*unstructured.Unstructured)
	klog.Infof("EtherealPod updated: %s/%s", ep.GetNamespace(), ep.GetName())
	c.reconcile(ep)
}

func (c *Controller) handleDelete(obj interface{}) {
	// Delete events can be tombstones
	var ep *unstructured.Unstructured
	switch t := obj.(type) {
	case *unstructured.Unstructured:
		ep = t
	case cache.DeletedFinalStateUnknown:
		u, ok := t.Obj.(*unstructured.Unstructured)
		if !ok {
			klog.Warning("Delete tombstone contained object that is not Unstructured")
			return
		}
		ep = u
	default:
		klog.Warning("Unknown delete object type")
		return
	}

	klog.Infof("EtherealPod deleted: %s/%s", ep.GetNamespace(), ep.GetName())
	c.deleteManagedPod(ep)
}

// Leader selection: for a Namespaced CRD, enforce singleton PER NAMESPACE.
// Rule: the "oldest" EtherealPod in that namespace is the leader.
func (c *Controller) leaderForNamespace(namespace string) *unstructured.Unstructured {
	items := c.informer.GetStore().List()
	var leader *unstructured.Unstructured

	for _, item := range items {
		ep, ok := item.(*unstructured.Unstructured)
		if !ok {
			continue
		}
		if ep.GetNamespace() != namespace {
			continue
		}
		if leader == nil || ep.GetCreationTimestamp().Time.Before(leader.GetCreationTimestamp().Time) {
			leader = ep
		}
	}
	return leader
}

func (c *Controller) reconcile(ep *unstructured.Unstructured) {
	namespace := ep.GetNamespace()
	name := ep.GetName()

	leader := c.leaderForNamespace(namespace)
	if leader != nil && leader.GetUID() != ep.GetUID() {
		msg := fmt.Sprintf(
			"Only one EtherealPod allowed per namespace. Leader is %s/%s",
			leader.GetNamespace(),
			leader.GetName(),
		)
		klog.Warningf("SINGLETON VIOLATION: rejecting %s/%s. %s", namespace, name, msg)

		// Mark rejected + ensure no pod is running for this rejected CR
		c.updateStatusRejected(ep, msg)
		c.deleteManagedPod(ep)
		return
	}

	// Leader path: ensure pod exists / heal it.
	podSpec, found, err := unstructured.NestedMap(ep.Object, "spec", "template", "spec")
	if err != nil || !found {
		klog.Errorf("Failed to get pod template spec from EtherealPod %s/%s: %v", namespace, name, err)
		return
	}

	podName := fmt.Sprintf("%s-pod", name)

	pod, err := c.clientset.CoreV1().Pods(namespace).Get(context.TODO(), podName, metav1.GetOptions{})
	if apierrors.IsNotFound(err) {
		klog.Infof("Pod %s/%s not found, creating...", namespace, podName)
		if err := c.createPod(ep, podName, podSpec); err != nil {
			klog.Errorf("Failed to create pod: %v", err)
			return
		}
		// Make sure status is written even when restarts==0
		c.updateStatus(ep, podName, 0, "Running")
		return
	}
	if err != nil {
		klog.Errorf("Error checking pod: %v", err)
		return
	}

	restarts := c.countRestarts(pod)

	phase := "Running"
	if pod.Status.Phase == corev1.PodPending {
		phase = "Pending"
	}
	c.updateStatus(ep, podName, restarts, phase)

	// If pod is in terminal state, recreate it.
	if pod.Status.Phase == corev1.PodFailed || pod.Status.Phase == corev1.PodSucceeded {
		klog.Infof("Pod %s/%s is in terminal state %s, recreating...", namespace, podName, pod.Status.Phase)
		if err := c.clientset.CoreV1().Pods(namespace).Delete(context.TODO(), podName, metav1.DeleteOptions{}); err != nil && !apierrors.IsNotFound(err) {
			klog.Errorf("Failed to delete terminated pod: %v", err)
			return
		}
		time.Sleep(2 * time.Second)
		if err := c.createPod(ep, podName, podSpec); err != nil {
			klog.Errorf("Failed to recreate pod: %v", err)
			return
		}
		c.updateStatus(ep, podName, 0, "Running")
	}
}

func (c *Controller) createPod(ep *unstructured.Unstructured, podName string, podSpec map[string]interface{}) error {
	namespace := ep.GetNamespace()

	pod := &corev1.Pod{
		ObjectMeta: metav1.ObjectMeta{
			Name:      podName,
			Namespace: namespace,
			Labels: map[string]string{
				"etherealpod": ep.GetName(),
			},
			OwnerReferences: []metav1.OwnerReference{
				*metav1.NewControllerRef(ep, etherealPodGVK),
			},
		},
	}

	if err := runtime.DefaultUnstructuredConverter.FromUnstructured(podSpec, &pod.Spec); err != nil {
		return fmt.Errorf("failed to unmarshal pod spec: %v", err)
	}

	_, err := c.clientset.CoreV1().Pods(namespace).Create(context.TODO(), pod, metav1.CreateOptions{})
	if err != nil && !apierrors.IsAlreadyExists(err) {
		return err
	}

	klog.Infof("Created pod %s/%s", namespace, podName)
	return nil
}

func (c *Controller) deleteManagedPod(ep *unstructured.Unstructured) {
	namespace := ep.GetNamespace()
	name := ep.GetName()
	podName := fmt.Sprintf("%s-pod", name)

	err := c.clientset.CoreV1().Pods(namespace).Delete(context.TODO(), podName, metav1.DeleteOptions{})
	if err != nil && !apierrors.IsNotFound(err) {
		klog.Errorf("Failed to delete pod %s/%s: %v", namespace, podName, err)
		return
	}
	klog.Infof("Deleted pod %s/%s (or already gone)", namespace, podName)
}

func (c *Controller) countRestarts(pod *corev1.Pod) int32 {
	var total int32
	for _, cs := range pod.Status.ContainerStatuses {
		total += cs.RestartCount
	}
	return total
}

// Always update status if any relevant field differs/missing.
func (c *Controller) updateStatus(ep *unstructured.Unstructured, podName string, restarts int32, phase string) {
	namespace := ep.GetNamespace()
	name := ep.GetName()

	curPhase, _, _ := unstructured.NestedString(ep.Object, "status", "phase")
	curPod, _, _ := unstructured.NestedString(ep.Object, "status", "podName")
	curRest, foundRest, _ := unstructured.NestedInt64(ep.Object, "status", "restarts")

	needs := !foundRest || curPhase != phase || curPod != podName || curRest != int64(restarts)
	if !needs {
		return
	}

	unstructured.SetNestedField(ep.Object, int64(restarts), "status", "restarts")
	unstructured.SetNestedField(ep.Object, podName, "status", "podName")
	unstructured.SetNestedField(ep.Object, phase, "status", "phase")

	_, err := c.dynamicClient.Resource(etherealPodGVR).Namespace(namespace).UpdateStatus(
		context.TODO(),
		ep,
		metav1.UpdateOptions{},
	)
	if err != nil {
		klog.Errorf("Failed to update status for %s/%s: %v", namespace, name, err)
		return
	}
	klog.Infof("Updated status for %s/%s: phase=%s restarts=%d", namespace, name, phase, restarts)
}

func (c *Controller) updateStatusRejected(ep *unstructured.Unstructured, reason string) {
	namespace := ep.GetNamespace()
	name := ep.GetName()

	unstructured.SetNestedField(ep.Object, "Rejected", "status", "phase")
	unstructured.SetNestedField(ep.Object, reason, "status", "message")

	_, err := c.dynamicClient.Resource(etherealPodGVR).Namespace(namespace).UpdateStatus(
		context.TODO(),
		ep,
		metav1.UpdateOptions{},
	)
	if err != nil {
		klog.Errorf("Failed to update rejected status for %s/%s: %v", namespace, name, err)
	}
}

func main() {
	klog.InitFlags(nil)

	config, err := rest.InClusterConfig()
	if err != nil {
		klog.Fatalf("Failed to get in-cluster config: %v", err)
	}

	clientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		klog.Fatalf("Failed to create clientset: %v", err)
	}

	dynamicClient, err := dynamic.NewForConfig(config)
	if err != nil {
		klog.Fatalf("Failed to create dynamic client: %v", err)
	}

	controller := NewController(clientset, dynamicClient)

	stopCh := make(chan struct{})
	defer close(stopCh)

	controller.Run(stopCh)
}
