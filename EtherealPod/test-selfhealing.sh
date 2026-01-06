#!/bin/bash
set -euo pipefail

echo "=== EtherealPod Self-Healing Test ==="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[✓]${NC} $1"; }
print_info()   { echo -e "${YELLOW}[i]${NC} $1"; }
print_error()  { echo -e "${RED}[✗]${NC} $1"; }

EP="etherealpods.example.com"

# Use an isolated namespace so singleton-per-namespace doesn't conflict with existing CRs
NS="ep-test-$(date +%s)"

print_info "Checking prerequisites..."
command -v kubectl >/dev/null 2>&1 || { print_error "kubectl is required but not installed. Aborting."; exit 1; }
print_status "kubectl found"

print_info "Creating isolated namespace: ${NS}"
kubectl create namespace "${NS}" >/dev/null
print_status "Namespace created"

cleanup() {
  print_info "Cleaning up namespace ${NS}..."
  kubectl delete namespace "${NS}" --ignore-not-found >/dev/null 2>&1 || true
  print_status "Cleanup complete"
}
trap cleanup EXIT

# Create test EtherealPod
print_info "Creating test EtherealPod..."
cat <<EOF | kubectl apply -n "${NS}" -f -
apiVersion: example.com/v1
kind: EtherealPod
metadata:
  name: test-ep
spec:
  template:
    spec:
      containers:
        - name: nginx
          image: nginx:latest
          ports:
            - containerPort: 80
      restartPolicy: Always
EOF
print_status "EtherealPod created"

# Wait for pod to be created (poll instead of fixed sleep)
print_info "Waiting for managed pod to be created..."
for i in {1..30}; do
  if kubectl get pod test-ep-pod -n "${NS}" >/dev/null 2>&1; then
    print_status "Managed pod 'test-ep-pod' is running"
    break
  fi
  sleep 1
done

if ! kubectl get pod test-ep-pod -n "${NS}" >/dev/null 2>&1; then
  print_error "Managed pod was not created"
  print_info "Debug: controller logs (last 50 lines):"
  kubectl logs deployment/etherealpod-controller --tail=50 || true
  print_info "Debug: EtherealPod resource:"
  kubectl get "${EP}" test-ep -n "${NS}" -o yaml || true
  exit 1
fi

print_info "Initial state:"
kubectl get "${EP}" test-ep -n "${NS}"
echo ""

# Test 1: Delete the pod and ensure it is recreated
print_info "Test 1: Testing pod deletion recovery..."
kubectl delete pod test-ep-pod -n "${NS}"
print_status "Pod deleted"

print_info "Waiting for pod to be recreated..."
for i in {1..30}; do
  if kubectl get pod test-ep-pod -n "${NS}" >/dev/null 2>&1; then
    print_status "Pod successfully recreated!"
    break
  fi
  sleep 1
done

if ! kubectl get pod test-ep-pod -n "${NS}" >/dev/null 2>&1; then
  print_error "Pod was not recreated"
  exit 1
fi

echo ""
print_info "State after deletion test:"
kubectl get "${EP}" test-ep -n "${NS}"
echo ""

# Test 2: Verify singleton constraint (controller-based: second CR should be Rejected)
print_info "Test 2: Testing singleton constraint..."
echo ""
print_info "Attempting to create a second EtherealPod (should be rejected)..."
cat <<EOF | kubectl apply -n "${NS}" -f -
apiVersion: example.com/v1
kind: EtherealPod
metadata:
  name: second-ep
spec:
  template:
    spec:
      containers:
        - name: nginx
          image: nginx:latest
      restartPolicy: Always
EOF

# Wait for status.phase to become Rejected
print_info "Waiting for second-ep to be marked Rejected..."
STATUS=""
for i in {1..30}; do
  STATUS=$(kubectl get "${EP}" second-ep -n "${NS}" -o jsonpath='{.status.phase}' 2>/dev/null || echo "")
  if [ "$STATUS" = "Rejected" ]; then
    print_status "Second EtherealPod correctly rejected (singleton constraint enforced)"
    break
  fi
  sleep 1
done

if [ "$STATUS" != "Rejected" ]; then
  print_error "Second EtherealPod was not rejected (phase='${STATUS}'). Singleton constraint not working."
  kubectl get "${EP}" second-ep -n "${NS}" -o yaml || true
  exit 1
fi

echo ""
print_info "Verifying only one EtherealPod-managed pod exists:"
POD_COUNT=$(kubectl get pods -n "${NS}" -l etherealpod --no-headers 2>/dev/null | wc -l | tr -d ' ')
if [ "$POD_COUNT" -eq 1 ]; then
  print_status "Confirmed: Exactly 1 pod running"
else
  print_error "Expected 1 pod, found $POD_COUNT"
  kubectl get pods -n "${NS}" -l etherealpod || true
  exit 1
fi

echo ""
print_info "Current state:"
kubectl get "${EP}" -n "${NS}"
kubectl get pods -n "${NS}" -l etherealpod
echo ""

echo "=== All tests passed! ==="
