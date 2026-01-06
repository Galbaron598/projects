#!/usr/bin/env bash
set -euo pipefail

# reset.sh — cleans up EtherealPod demo resources (and optionally resets kind cluster)
#
# Usage:
#   ./reset.sh                    # safe reset: delete EtherealPod resources + controller/RBAC + default namespace workloads
#   ./reset.sh --all-namespaces    # also wipe workloads from all namespaces (NOT recommended)
#   ./reset.sh --delete-crd        # also delete the CRD
#   ./reset.sh --kind              # FULL RESET: delete and recreate kind cluster (most clean)
#   ./reset.sh --help

DEFAULT_NS="default"
APP_LABEL="app=etherealpod-controller"
CRD_NAME="etherealpods.example.com"
CR_API="etherealpods.example.com"
SA_NAME="etherealpod-controller"
ROLE_NAME="etherealpod-controller"
RB_NAME="etherealpod-controller"

ALL_NAMESPACES=0
DELETE_CRD=0
RESET_KIND=0

log() { printf "\n\033[1;33m[i]\033[0m %s\n" "$*"; }
ok()  { printf "\033[0;32m[✓]\033[0m %s\n" "$*"; }
err() { printf "\033[0;31m[✗]\033[0m %s\n" "$*"; }

usage() {
  cat <<EOF
reset.sh - reset EtherealPod demo resources

Options:
  --all-namespaces   Also delete workloads from ALL namespaces (dangerous)
  --delete-crd       Delete CRD (${CRD_NAME}) as well
  --kind             FULL RESET: kind delete cluster + kind create cluster
  --help             Show this help

Default (no flags):
  - Delete all EtherealPod CRs (all namespaces)
  - Delete controller deployment + pods (default namespace)
  - Delete RBAC (SA/ClusterRole/ClusterRoleBinding)
  - Clean common workloads in default namespace
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --all-namespaces) ALL_NAMESPACES=1; shift ;;
    --delete-crd)     DELETE_CRD=1; shift ;;
    --kind)           RESET_KIND=1; shift ;;
    --help|-h)        usage; exit 0 ;;
    *) err "Unknown option: $1"; usage; exit 1 ;;
  esac
done

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || { err "Missing command: $1"; exit 1; }
}

need_cmd kubectl

if [[ $RESET_KIND -eq 1 ]]; then
  need_cmd kind
  log "FULL RESET (kind): deleting cluster..."
  kind delete cluster || true
  ok "kind cluster deleted (or did not exist)"
  log "Creating fresh kind cluster..."
  kind create cluster
  ok "kind cluster created"
  log "Done. You now need to re-apply CRD/RBAC/controller and reload image."
  exit 0
fi

log "Checking cluster access..."
kubectl cluster-info >/dev/null 2>&1 || { err "kubectl cannot reach a cluster (check context)"; exit 1; }
ok "kubectl connected"

# 1) Delete EtherealPod CRs everywhere (safe, just deletes your custom objects)
log "Deleting EtherealPod custom resources in all namespaces..."
kubectl delete "${CR_API}" --all -A --ignore-not-found=true >/dev/null 2>&1 || true
ok "Deleted EtherealPod CRs (or none existed)"

# 2) Delete controller deployment/pods in default namespace
log "Deleting controller deployment/pods in namespace '${DEFAULT_NS}'..."
kubectl delete deployment etherealpod-controller -n "${DEFAULT_NS}" --ignore-not-found=true >/dev/null 2>&1 || true
kubectl delete pod -l "${APP_LABEL}" -n "${DEFAULT_NS}" --ignore-not-found=true >/dev/null 2>&1 || true
ok "Controller removed (or already gone)"

# 3) Delete RBAC
log "Deleting RBAC (ServiceAccount/ClusterRole/ClusterRoleBinding)..."
kubectl delete serviceaccount "${SA_NAME}" -n "${DEFAULT_NS}" --ignore-not-found=true >/dev/null 2>&1 || true
kubectl delete clusterrole "${ROLE_NAME}" --ignore-not-found=true >/dev/null 2>&1 || true
kubectl delete clusterrolebinding "${RB_NAME}" --ignore-not-found=true >/dev/null 2>&1 || true
ok "RBAC removed (or already gone)"

# 4) Clean namespace workloads
if [[ $ALL_NAMESPACES -eq 1 ]]; then
  log "DANGEROUS: deleting workloads in ALL namespaces..."
  # This avoids kube-system by filtering out common system namespaces
  for ns in $(kubectl get ns -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' | grep -Ev '^(kube-system|kube-public|kube-node-lease|local-path-storage)$'); do
    log "Cleaning namespace: ${ns}"
    kubectl delete all --all -n "${ns}" --ignore-not-found=true >/dev/null 2>&1 || true
    kubectl delete configmap --all -n "${ns}" --ignore-not-found=true >/dev/null 2>&1 || true
    kubectl delete secret --all -n "${ns}" --ignore-not-found=true >/dev/null 2>&1 || true
  done
  ok "All non-system namespaces cleaned"
else
  log "Cleaning common workloads in namespace '${DEFAULT_NS}'..."
  kubectl delete all --all -n "${DEFAULT_NS}" --ignore-not-found=true >/dev/null 2>&1 || true
  kubectl delete configmap --all -n "${DEFAULT_NS}" --ignore-not-found=true >/dev/null 2>&1 || true
  kubectl delete secret --all -n "${DEFAULT_NS}" --ignore-not-found=true >/dev/null 2>&1 || true
  ok "Default namespace cleaned"
fi

# 5) Optionally delete CRD
if [[ $DELETE_CRD -eq 1 ]]; then
  log "Deleting CRD ${CRD_NAME}..."
  kubectl delete crd "${CRD_NAME}" --ignore-not-found=true >/dev/null 2>&1 || true
  ok "CRD deleted (or already gone)"
fi

log "Reset complete ✅"
echo ""
echo "Quick verify:"
echo "  kubectl get eps -A"
echo "  kubectl get pods -A | grep ethereal || true"
echo "  kubectl get crd | grep ethereal || true"
