# 🍎 SundayApp — Groceries Tracker with Persistent Storage

> A self-healing, data-persistent REST API for tracking items employees depend on (coffee, yogurt, apples, etc.)

## ⚡ Key Features

✅ **Never Lose Data** — Uses PersistentVolume for data storage  
✅ **Self-Healing** — Managed by EtherealPod controller  
✅ **Auto-Recovery** — Pods automatically recreated after crashes  
✅ **REST API** — FastAPI with OpenAPI documentation  
✅ **Simple Deployment** — Docker + Kubernetes ready  

---

## 🎯 Assignment Compliance

This project fulfills **Part B: Sunday App** requirements:

| Requirement | Implementation | Status |
|-------------|----------------|--------|
| Must always be up | EtherealPod controller monitors and recreates pods | ✅ |
| Recover from failures | Automatic pod recreation on crash/deletion | ✅ |
| Never lose data | SQLite + PersistentVolumeClaim | ✅ |
| Data model: USER:ELEMENT:NUMBER | Implemented via `/list_all` endpoint | ✅ |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  EtherealPod Controller (Part A)                            │
│  Monitors: sunday-app-ep                                    │
└───────────────────────┬─────────────────────────────────────┘
                        │ watches & recreates
                        ↓
┌─────────────────────────────────────────────────────────────┐
│  Sunday App Pod                                             │
│  ┌──────────────────────────────────────────────┐           │
│  │  FastAPI Application (sunday_app.py)         │           │
│  │  - Handles HTTP requests                     │           │
│  │  - Manages grocery data                      │           │
│  └────────────────┬─────────────────────────────┘           │
│                   │ reads/writes                            │
│                   ↓                                          │
│  ┌──────────────────────────────────────────────┐           │
│  │  /data/sunday.db (SQLite database)           │           │
│  │  Mounted from PersistentVolumeClaim          │           │
│  └──────────────────────────────────────────────┘           │
└───────────────────────┬─────────────────────────────────────┘
                        │ persisted to
                        ↓
┌─────────────────────────────────────────────────────────────┐
│  PersistentVolumeClaim: sunday-data-pvc                     │
│  - Stores database file persistently                        │
│  - Survives pod restarts/crashes                            │
│  - 1GB storage capacity                                     │
└─────────────────────────────────────────────────────────────┘
```

**Data Flow:**
1. User makes API request → Sunday App Pod
2. App writes to → `/data/sunday.db`
3. File stored on → PersistentVolume (disk)
4. Pod crashes → EtherealPod recreates it
5. New pod mounts → Same PersistentVolume
6. Data intact! ✅

---

## 📋 Prerequisites

- ✅ Kubernetes cluster (v1.20+)
- ✅ `kubectl` configured
- ✅ Docker installed
- ✅ EtherealPod CRD and controller deployed (from Part A)

---

## 🚀 Complete Testing Workflow

### ⚠️ Important: Deploy Part A First!

This Sunday App (Part B) **requires** the EtherealPod controller from Part A to be running first.

### Phase 1: Deploy EtherealPod Controller (Part A)

**Navigate to the EtherealPod folder and deploy the controller:**

```bash
cd /path/to/EtherealPod/

# Option A: Use the quick deploy script (RECOMMENDED)
chmod +x quick-deploy.sh
./quick-deploy.sh
```

**OR manually:**

```bash
# Option B: Manual deployment
kubectl apply -f etherealpod-crd.yaml
kubectl apply -f rbac.yaml
docker build -t etherealpod-controller:latest .
kubectl apply -f controller-deployment.yaml
```

**Verify the controller is running:**

```bash
kubectl get pods -l app=etherealpod-controller
or
kubectl get pods -n etherealpod-system
```

Expected output:
```
NAME                                     READY   STATUS    RESTARTS   AGE
etherealpod-controller-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
```

✅ **Controller is ready!** Now proceed to Part B.

---

### Phase 2: Deploy Sunday App (Part B)

**Navigate to the Sunday App folder:**

```bash
cd /path/to/Sunday\ App/
```

**Step 1: Build the Docker Image**

```bash
docker build -t sundayapp:latest .
```

**Step 2: Deploy Storage and App**

```bash
# Create the PersistentVolumeClaim
kubectl apply -f sunday-pvc.yaml

# Verify PVC is bound
kubectl get pvc sunday-data-pvc
# Should show STATUS: Bound

# Deploy SundayApp with EtherealPod
kubectl apply -f sunday-etherealpod.yaml

# Wait for pod to be ready
kubectl wait --for=condition=ready pod -l app=sunday-app --timeout=90s
```

**Verify deployment:**

```bash
kubectl get pods | grep sunday
```

Expected output:
```
sunday-app-ep-pod   1/1     Running   0          20s
```

✅ **Sunday App is running!**

---

### Phase 3: Test the API

**Terminal 1: Start Port Forwarding**

```bash
# Forward port 8000 to your local machine
kubectl port-forward sunday-app-ep-pod 8000:8000
or
kubectl port-forward pod/sunday-app-ep-pod 8000:8000

```

Keep this terminal open!

**Terminal 2: Test API Endpoints**

Open a new terminal and run:

```bash
# Health check
curl http://localhost:8000/health

# Add some data
curl -X POST "http://localhost:8000/write?user_id=1&product_name=coffee&amount=5"
curl -X POST "http://localhost:8000/write?user_id=2&product_name=beer&amount=3"

# Verify data
curl http://localhost:8000/list_all
```

Expected output:
```json
[
  {"user":"loki","element":"coffee","number":5},
  {"user":"thor","element":"beer","number":3}
]
```

✅ **API is working!**

Visit **http://localhost:8000/docs** for interactive API documentation.

---

### Phase 4: Test Data Persistence (Critical Test!)

This test proves data survives pod crashes.

**Terminal 1: Stop port forward** (press Ctrl+C)

**Terminal 2: Simulate pod crash**

```bash
# Delete the pod
kubectl delete pod sunday-app-ep-pod

# Watch EtherealPod automatically recreate it
kubectl get pods -w
```

You'll see the pod terminating and a new one being created. Press Ctrl+C when the new pod is Running.

**Wait for the new pod to be ready:**

```bash
kubectl wait --for=condition=ready pod -l app=sunday-app --timeout=90s
```

**Terminal 1: Port forward to the NEW pod**

```bash
kubectl port-forward sunday-app-ep-pod 8000:8000
```

**Terminal 2: Check if data survived**

```bash
curl http://localhost:8000/list_all
```

**Expected output (SAME data as before):**
```json
[
  {"user":"loki","element":"coffee","number":5},
  {"user":"thor","element":"beer","number":3}
]
```

🎉 **SUCCESS! Data survived the pod restart!** This proves:
- ✅ EtherealPod recreated the pod automatically
- ✅ Data was stored on PersistentVolume
- ✅ New pod mounted the same storage
- ✅ **No data was lost!**

---

## 📬 API Endpoints

### POST `/write`
Add or increase product amount for a user.

```bash
curl -X POST "http://localhost:8000/write?user_id=1&product_name=apple&amount=2"
```

**Response:**
```json
{"message": "ok", "user": "loki", "element": "apple", "number": 2}
```

### GET `/get_product_amount`
Get total amount of a product across all users.

```bash
curl "http://localhost:8000/get_product_amount?product_name=coffee"
```

**Response:**
```json
{"product_name": "coffee", "amount": 12}
```

### DELETE `/delete_product`
Remove a product for all users.

```bash
curl -X DELETE "http://localhost:8000/delete_product?product_name=apple"
```

**Response:**
```json
{"message": "ok", "product_name": "apple", "deleted_rows": 3}
```

### GET `/list_all`
Return complete data model: **USER : ELEMENT : NUMBER**

```bash
curl "http://localhost:8000/list_all"
```

**Response:**
```json
[
  {"user": "loki", "element": "coffee", "number": 5},
  {"user": "thor", "element": "beer", "number": 3}
]
```

### GET `/health`
Health check for Kubernetes liveness/readiness probes.

```bash
curl "http://localhost:8000/health"
```

**Response:**
```json
{"status": "healthy", "database": "/data/sunday.db"}
```

---

## 🧠 Data Model

### Logical Model (API Response Format)

```
USER : ELEMENT : NUMBER
```

Example:
```json
{"user": "loki", "element": "coffee", "number": 5}
```

### Internal Schema

**Table: users** (Static mock data)
| user_id | user_name |
|---------|-----------|
| 1 | loki |
| 2 | thor |
| 3 | hulk |
| ... | ... |

**Table: groceries** (Persistent data)
| user_id | product_name | amount |
|---------|--------------|--------|
| 1 | coffee | 5 |
| 2 | beer | 3 |

---

## 🎨 Design Decisions

###  ✅ PersistentVolumeClaim Benefits

- **Survives pod deletion/crashes**
- **Survives node failures** (with proper storage class)
- **Easy backup/restore** (can copy database file)
- **Production-ready pattern**

### 3. ✅ EtherealPod Integration

- Automatic pod recreation on crash
- Tracks restart count
- Ensures single active pod
- Guarantees uptime

### 4. ✅ Health Checks

- Kubernetes liveness probes detect hung processes
- Readiness probes ensure pod is ready before traffic
- Auto-restart on failure

---

## 📁 Files Included


## 🔍 Monitoring

### Check Pod Status
```bash
kubectl get pods | grep sunday
```

### View Pod Logs
```bash
kubectl logs sunday-app-ep-pod
```

### Check EtherealPod Status
```bash
kubectl get etherealpods sunday-app-ep
```

### Check PVC Status
```bash
kubectl get pvc sunday-data-pvc
```

### Inspect Database File
```bash
kubectl exec -it sunday-app-ep-pod -- ls -lh /data/
```

---

## 🧹 Cleanup

```bash
# Delete EtherealPod (also deletes managed pod)
kubectl delete ep sunday-app-ep

# Delete PVC (⚠️ WARNING: Deletes all data!)
kubectl delete pvc sunday-data-pvc
```

---

## 🚨 Troubleshooting

### Issue: "EtherealPod CRD not found" or "error: the server doesn't have a resource type 'etherealpods'"

**Cause:** Part A (EtherealPod controller) is not deployed.

**Solution:** Deploy the EtherealPod controller first:
```bash
cd /path/to/EtherealPod/
./quick-deploy.sh
```

**Verify:**
```bash
kubectl get crd etherealpods.example.com
kubectl get pods -l app=etherealpod-controller
```

### Issue: PVC stuck in "Pending"

**Check:**
```bash
kubectl describe pvc sunday-data-pvc
```

**Solution:** Ensure your cluster has a storage provisioner or default StorageClass.

**For minikube:**
```bash
minikube addons enable default-storageclass
minikube addons enable storage-provisioner
```

**For kind:**
```bash
# Kind has default local storage, should work automatically
kubectl get storageclass
```

### Issue: Pod won't start

**Check:**
```bash
kubectl describe pod sunday-app-ep-pod
kubectl logs sunday-app-ep-pod
```

**Common causes:**
- Image not found (rebuild with `docker build -t sundayapp:latest .`)
- PVC not bound (check `kubectl get pvc`)
- EtherealPod controller not running
- Insufficient cluster resources

### Issue: Can't connect to localhost:8000

**Check port-forward is running:**
```bash
ps aux | grep port-forward
```

**Solution:** Restart port-forward:
```bash
kubectl port-forward sunday-app-ep-pod 8000:8000
```

**Check pod is actually running:**
```bash
kubectl get pods | grep sunday
# Should show: sunday-app-ep-pod   1/1     Running
```

### Issue: Data not persisting after pod restart

**Check if volume is mounted:**
```bash
kubectl describe pod sunday-app-ep-pod | grep -A 5 Volumes
```

**Check database file exists:**
```bash
kubectl exec -it sunday-app-ep-pod -- ls -la /data/
# Should show: sunday.db
```

**Check app is using correct path:**
```bash
kubectl exec -it sunday-app-ep-pod -- env | grep DB_PATH
# Should show: DB_PATH=/data/sunday.db
```

### Issue: Database errors

**Check permissions:**
```bash
kubectl exec -it sunday-app-ep-pod -- ls -la /data/
```

**Reset database:**
```bash
kubectl exec -it sunday-app-ep-pod -- rm /data/sunday.db
kubectl delete pod sunday-app-ep-pod  # Will recreate with fresh DB
```

---


## ✅ Assignment Requirements Checklist

- [x] Always up (EtherealPod ensures uptime)
- [x] Recover from failures automatically (Self-healing)
- [x] Never lose data (PersistentVolume)
- [x] REST API with required endpoints
- [x] Correct data model (USER : ELEMENT : NUMBER)
- [x] Docker deployment
- [x] Kubernetes integration
- [x] Documentation

---

## 📄 License

Created for assignment purposes. Free to use and modify.
