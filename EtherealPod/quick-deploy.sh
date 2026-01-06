#!/bin/bash
# quick-deploy.sh - One command to deploy everything!

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════╗"
echo "║                                                ║"
echo "║     EtherealPod Quick Deploy Script            ║"
echo "║     One command to deploy everything!          ║"
echo "║                                                ║"
echo "╚════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${BLUE}→${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check prerequisites
print_info "Checking prerequisites..."

if ! command -v kubectl &> /dev/null; then
    print_error "kubectl not found. Please install kubectl first."
    echo "  Visit: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    print_error "Docker not found. Please install Docker first."
    echo "  Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! kubectl cluster-info &> /dev/null; then
    print_error "Cannot connect to Kubernetes cluster."
    echo "  Please ensure your cluster is running and kubectl is configured."
    exit 1
fi

print_status "All prerequisites met"
echo ""

# Step 1: Install CRD
print_info "Step 1/5: Installing Custom Resource Definition (CRD)..."
kubectl apply -f etherealpod-crd.yaml > /dev/null 2>&1
print_status "CRD installed"

# Wait for CRD to be ready
print_info "Waiting for CRD to be established..."
kubectl wait --for condition=established --timeout=60s crd/etherealpods.example.com > /dev/null 2>&1
print_status "CRD is ready"
echo ""

# Step 2: Install RBAC
print_info "Step 2/5: Installing RBAC (permissions)..."
kubectl apply -f rbac.yaml > /dev/null 2>&1
print_status "RBAC configured"
echo ""

# Step 3: Build Docker image
print_info "Step 3/5: Building controller Docker image..."
echo "  This may take a minute..."

# Check if we're using Minikube
if kubectl config current-context | grep -q minikube; then
    print_info "Detected Minikube - using Minikube's Docker daemon"
    eval $(minikube docker-env)
fi

# Check if we're using Kind
if kubectl config current-context | grep -q kind; then
    USING_KIND=true
    print_info "Detected Kind (Kubernetes in Docker)"
fi

docker build -t etherealpod-controller:latest . > /dev/null 2>&1
print_status "Docker image built"

# Load image into Kind if needed
if [ "$USING_KIND" = true ]; then
    print_info "Loading image into Kind cluster..."
    kind load docker-image etherealpod-controller:latest > /dev/null 2>&1
    print_status "Image loaded into Kind"
fi

echo ""

# Step 4: Deploy controller
print_info "Step 4/5: Deploying controller to Kubernetes..."
kubectl apply -f submission.yaml > /dev/null 2>&1
print_status "Controller deployed"
echo ""

# Step 5: Wait for controller to be ready
print_info "Step 5/5: Waiting for controller to be ready..."
kubectl wait --for=condition=available --timeout=120s deployment/etherealpod-controller -n etherealpod-system > /dev/null 2>&1
print_status "Controller is running!"
echo ""

# Verify deployment
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}     ✓ Deployment Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo ""

print_info "Verifying installation..."
echo ""

# Show controller status
echo "Controller status:"
kubectl get pods -n etherealpod-system
echo ""

# Show CRD
echo "Custom Resource Definition:"
kubectl get crd etherealpods.example.com
echo ""

echo -e "${BLUE}════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  What's Next?${NC}"
echo -e "${BLUE}════════════════════════════════════════════════${NC}"
echo ""
echo "1. Create your first EtherealPod:"
echo -e "   ${YELLOW}kubectl apply -f example-etherealpod.yaml${NC}"
echo ""
echo "2. View EtherealPods:"
echo -e "   ${YELLOW}kubectl get eps${NC}"
echo ""
echo "3. Test self-healing:"
echo -e "   ${YELLOW}kubectl delete pod example-ep-pod${NC}"
echo -e "   ${YELLOW}kubectl get pods -w${NC}  ${GREEN}# Watch it recreate!${NC}"
echo ""
echo "4. Run automated tests:"
echo -e "   ${YELLOW}./test-selfhealing.sh${NC}"
echo ""
echo "5. View controller logs:"
echo -e "   ${YELLOW}kubectl logs -n etherealpod-system -l app=etherealpod-controller${NC}"
echo ""
echo -e "${GREEN}Happy healing! 🚀${NC}"
echo ""