# ✨ EtherealPod - Self-Healing Kubernetes Workload

**EtherealPod** is a custom Kubernetes resource that ensures a Pod never stops existing. It automatically recreates pods that crash, get deleted, or terminate—guaranteeing your workload stays alive.

<br>

## 🎯 Key Features

| Feature | Description |
|---------|-------------|
| **Self-Healing** | Automatically recreates pods if they crash, are deleted, or terminate |
| **Restart Tracking** | Exposes the number of restarts of the managed pod |
| **Singleton Pattern** | Only one EtherealPod allowed per cluster |
| **Simple API** | Easy-to-use custom resource with familiar Pod template syntax |
| **Owner References** | Managed pods are automatically cleaned up when EtherealPod is deleted |

<br>

---

## ⚠️ Important: Singleton Constraint

**Only ONE EtherealPod can exist in the cluster at a time.**

### What This Means

- ✅ You can create **one** EtherealPod managing **one** pod
- ❌ Creating a second EtherealPod will be **rejected** by the controller
- ✅ Delete the first to create a different one

### Example

```bash
# ✅ This works
kubectl apply -f example-etherealpod.yaml

# ❌ This will be rejected (first one still exists)
kubectl apply -f example-second-etherealpod.yaml  # Status: Rejected

# ✅ Delete first, then create second
kubectl delete ep example-ep
kubectl apply -f example-second-etherealpod.yaml  # Now works!
```

<br>

---

## 🏗️ Architecture

The solution consists of three main components:

1. **Custom Resource Definition (CRD)** - Defines the EtherealPod resource type
2. **Controller** - Watches EtherealPod resources and manages their lifecycle
3. **RBAC** - Service account and permissions for the controller

### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│  1. EtherealPod created → Controller validates singleton    │
│  2. Validation passes → Controller creates managed Pod      │
│  3. Controller monitors Pod health continuously             │
│  4. Pod deleted/crashes → Controller recreates it           │
│  5. Container restarts → Tracked in EtherealPod status      │
│  6. EtherealPod deleted → Managed Pod cleaned up            │
│  7. Second EtherealPod attempted → Rejected                 │
└─────────────────────────────────────────────────────────────┘
```

<br>

---

## 📋 Prerequisites

Before you begin, ensure you have:

- ✅ Kubernetes cluster (v1.20+)
- ✅ `kubectl` configured to access your cluster
- ✅ Docker (for building the controller image)

<br>

---

## 🚀 Quick Start - One Command Deploy

### **Recommended Method**

Run this single script to deploy everything:

```bash
chmod +x quick-deploy.sh
./quick-deploy.sh
```

or

```bash
bash quick-deploy.sh
```

### What It Does

The script automatically:

1. ✅ Checks prerequisites (kubectl, docker, cluster access)
2. ✅ Installs the CRD
3. ✅ Sets up RBAC
4. ✅ Builds the Docker image
5. ✅ Deploys the controller
6. ✅ Waits for everything to be ready

**⏱️ Total Time: ~2 minutes**

After deployment completes, jump to the [Usage](#-usage) section!

<br>

---

## 🔧 Manual Installation

If you prefer to understand each step or customize the deployment:

<details>
<summary><b>Click to expand manual installation steps</b></summary>

### Step 1: Apply the CRD

```bash
kubectl apply -f etherealpod-crd.yaml
```

### Step 2: Set up RBAC

```bash
kubectl apply -f rbac.yaml
```

### Step 3: Build and Deploy the Controller

**Build the controller image:**

```bash
docker build -t etherealpod-controller:latest .
```

**If using a remote registry:**

```bash
docker tag etherealpod-controller:latest <your-registry>/etherealpod-controller:latest
docker push <your-registry>/etherealpod-controller:latest
```

**Deploy the controller:**

```bash
# Update the image in controller-deployment.yaml if needed
kubectl apply -f controller-deployment.yaml
```

### Step 4: Verify Installation

**Check that the controller is running:**

```bash
kubectl get pods -l app=etherealpod-controller
```

**Check the CRD is installed:**

```bash
kubectl get crd etherealpods.example.com
```

</details>

<br>

---

## 📖 Usage

### Create an EtherealPod

Create a file `my-etherealpod.yaml`:

```yaml
apiVersion: example.com/v1
kind: EtherealPod
metadata:
  name: example-ep
  namespace: default
spec:
  template:
    spec:
      containers:
        - name: nginx
          image: nginx:latest
          ports:
            - containerPort: 80
      restartPolicy: Always
```

**Apply it:**

```bash
kubectl apply -f my-etherealpod.yaml
```

### View EtherealPods

**List all EtherealPods:**

```bash
kubectl get eps
```

**Output:**

```
NAME           AGE     RESTARTS
example-ep     12m     3
```

**Get detailed information:**

```bash
kubectl describe ep example-ep
```

### Test Self-Healing

**Delete the managed pod:**

```bash
kubectl delete pod example-ep-pod
```

**Watch it automatically recreate:**

```bash
kubectl get pods -w
```

**Check the restart count:**

```bash
kubectl get eps
```

### Understanding Singleton Constraints

Only one EtherealPod can exist at a time:

```bash
# ✅ First EtherealPod succeeds
kubectl apply -f example-etherealpod.yaml
# Output: etherealpod.example.com/example-ep created

# ✅ Second EtherealPod created but rejected by controller
kubectl apply -f another-etherealpod.yaml
# Output: etherealpod.example.com/another-ep created

# 📊 Check status
kubectl get eps
# NAME          AGE   RESTARTS   STATUS
# example-ep    1m    0          Running
# another-ep    10s   0          Rejected  ← Blocked by controller

kubectl describe ep another-ep
# Status:
#   Phase:    Rejected
#   Message:  Only one EtherealPod allowed. example-ep already exists
```

**To create a new EtherealPod, delete the existing one first:**

```bash
kubectl delete ep example-ep
kubectl apply -f another-etherealpod.yaml  # ✅ Now succeeds
```

### Simulate Pod Crashes

Create an EtherealPod with a crashing container:

```yaml
apiVersion: example.com/v1
kind: EtherealPod
metadata:
  name: crasher-ep
spec:
  template:
    spec:
      containers:
        - name: crasher
          image: busybox
          command: ["sh", "-c", "echo 'Starting...'; sleep 5; exit 1"]
      restartPolicy: Always
```

**Watch the restarts accumulate:**

```bash
kubectl get eps crasher-ep -w
```

<br>

---

<br>

---

## 🧹 Cleanup

### Automated Cleanup - Reset Script

For development convenience, a reset script is provided.

#### Default Reset

```bash
chmod +x reset.sh
./reset.sh
```

or

```bash
bash ./reset.sh
```

**Deletes:**

- All EtherealPod custom resources
- Controller deployment & pods
- RBAC resources
- Workloads in the default namespace

#### Advanced Options

**Delete CRD:**

```bash
./reset.sh --delete-crd
```

**Full kind cluster reset:**

```bash
./reset.sh --kind
```

**Clean all namespaces (⚠️ dangerous):**

```bash
./reset.sh --all-namespaces
```

### Manual Cleanup

**Delete an EtherealPod (also deletes the managed pod):**

```bash
kubectl delete ep example-ep
```

**Uninstall the controller:**

```bash
kubectl delete -f controller-deployment.yaml
kubectl delete -f rbac.yaml
kubectl delete -f etherealpod-crd.yaml
```

<br>

---

## 👨‍💻 Development

### Building Locally

```bash
go mod download
go build -o controller main.go
```

### Running Locally (for development)

You can run the controller locally:

```bash
go run main.go
```

**Note:** This requires proper kubeconfig setup and will use your current kubectl context.

<br>

---

## 🔍 Troubleshooting

### Controller Not Starting

**Check logs:**

```bash
kubectl logs -l app=etherealpod-controller
```

### Pod Not Being Created

1. **Check EtherealPod status:**
   ```bash
   kubectl describe ep <name>
   ```

2. **Check controller logs for errors**

3. **Verify RBAC permissions are correct**

### Restarts Not Updating

The controller checks pod health every 10 seconds. Wait a moment and check again:

```bash
kubectl get eps -w
```

<br>

---

## 🎨 Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Controller Pattern** | Uses a Kubernetes controller with informers for efficient resource watching |
| **Owner References** | Managed pods use owner references for automatic cleanup |
| **Health Checking** | Periodic reconciliation ensures eventual consistency |
| **Restart Counting** | Tracks container restart counts from pod status |
| **Terminal State Handling** | Automatically recreates pods that reach Failed or Succeeded states |
| **Singleton Pattern** | Simplifies controller logic and prevents resource conflicts |

<br>

---

## 📄 License

**MIT License** - Feel free to use and modify as needed.
</div>