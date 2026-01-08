# 🍎 SundayApp — Groceries Tracker API

> A simple REST API for tracking items employees depend on (coffee, yogurt, apples, etc.)

This project implements **Part B — Sunday App** of the assignment. It follows the required data model:

```
USER : ELEMENT : NUMBER
```

**Examples:**
```
loki : apple : 1
thor : beer  : 3
```

Under the hood, the API uses SQLite (in-memory) and a static mock user table to resolve `user_id → user_name` while exposing the logical data model exactly as required.

---

## 📌 Features

- ✅ **Add Items** — Add grocery items for users
- ✅ **Get Totals** — Get total amount of a product across all users
- ✅ **Delete Products** — Remove a product for all users
- ✅ **List All** — Return full logical model (USER : ELEMENT : NUMBER)
- ✅ **Zero Setup** — Uses in-memory SQLite (no configuration needed)
- ✅ **Docker Ready** — Includes Dockerfile + Docker Compose for easy deployment
- ✅ **Mock Users** — Static user table of 10 predefined users

---

## 🚀 Quick Start

The fastest way to run the application is with Docker Compose:

```bash
docker-compose up
```

Access the API at: **http://127.0.0.1:8000**

View interactive docs at: **http://127.0.0.1:8000/docs**

---

## 🧠 Data Model

### Logical Model (Required Format)

The assignment defines the logical data model as:

```
USER : ELEMENT : NUMBER
```

This API outputs exactly this format via the `/list_all` endpoint.

**Example Response:**

```json
[
  {"user": "loki", "element": "apple", "number": 1},
  {"user": "thor", "element": "beer", "number": 3}
]
```

### Internal Architecture

To support correctness and realistic behavior, the app internally uses two tables:

#### Table: `users` (Static Mock Data)

| user_id | user_name |
|---------|-----------|
| 1 | loki |
| 2 | thor |
| 3 | hulk |
| 4 | natasha |
| 5 | steve |
| 6 | tony |
| 7 | bruce |
| 8 | clint |
| 9 | wanda |
| 10 | sam |

> 📝 **Note:** These mappings are located in `users_data.py`


#### Table: `groceries`

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | INT | Foreign key to users table |
| `product_name` | TEXT | Name of the product |
| `amount` | INT | Quantity of the product |

**Primary Key:** `(user_id, product_name)`

**Data Model Mapping:**
- `USER` = user_name
- `ELEMENT` = product_name
- `NUMBER` = amount

---

## 🐳 Running with Docker

### Option 1: Docker Compose (Recommended)

The easiest way to run the application!

**Start the application:**

```bash
docker-compose up
```

**Run in detached mode:**

```bash
docker-compose up -d
```

**Stop the application:**

```bash
docker-compose down
```

**Rebuild after changes:**

```bash
docker-compose up --build
```

**View logs:**

```bash
docker-compose logs -f
```

The API will be available at: **http://127.0.0.1:8000**

### Option 2: Docker (without Compose)

**Build the container:**

```bash
docker build -t sunday_app .
```

**Run the container:**

```bash
docker run -p 8000:8000 sunday_app
```

The API will be available at: **http://127.0.0.1:8000**

---

## 💻 Running Locally (without Docker)

### Prerequisites

- Python 3.8+
- pip

### Installation

**Install dependencies:**

```bash
pip install fastapi uvicorn
```

Or using pip3:

```bash
pip3 install fastapi uvicorn
```

### Run the API

**Start the server:**

```bash
uvicorn sunday_app:app --reload
```

The server will start at: **http://127.0.0.1:8000**

**Custom port:**

```bash
uvicorn sunday_app:app --port 8080
```

---

## 📬 API Endpoints

### POST `/write`

Add or increase product amount for a user.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | int | Yes | User identifier (1-10) |
| `product_name` | str | Yes | Product name (lowercase) |
| `amount` | int | Yes | Quantity (must be > 0) |

**Example:**

```bash
curl -X POST "http://127.0.0.1:8000/write?user_id=1&product_name=apple&amount=1"
```

**Response:**

```json
{"message": "Updated apple for user loki"}
```

---

### GET `/get_product_amount`

Get total amount of a product across all users.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `product_name` | str | Yes | Product name to query |

**Example:**

```bash
curl "http://127.0.0.1:8000/get_product_amount?product_name=apple"
```

**Response:**

```json
{"product_name": "apple", "total_amount": 5}
```

---

### DELETE `/delete_product`

Remove a product for all users.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `product_name` | str | Yes | Product name to delete |

**Example:**

```bash
curl -X DELETE "http://127.0.0.1:8000/delete_product?product_name=apple"
```

**Response:**

```json
{"message": "Deleted apple for all users"}
```

---

### GET `/list_all`

Return the complete logical model: **USER : ELEMENT : NUMBER**

**Example:**

```bash
curl "http://127.0.0.1:8000/list_all"
```

**Response:**

```json
[
  {"user": "loki", "element": "apple", "number": 1},
  {"user": "thor", "element": "beer", "number": 3},
  {"user": "hulk", "element": "coffee", "number": 2}
]
```

---

## 🧪 Manual Testing Guide

### Complete Testing Workflow

**1. Add items for multiple users:**

```bash
# Add apple for loki
curl -X POST "http://127.0.0.1:8000/write?user_id=1&product_name=apple&amount=1"

# Add beer for thor
curl -X POST "http://127.0.0.1:8000/write?user_id=2&product_name=beer&amount=3"

# Add more apples for hulk
curl -X POST "http://127.0.0.1:8000/write?user_id=3&product_name=apple&amount=2"

# Add coffee for steve
curl -X POST "http://127.0.0.1:8000/write?user_id=5&product_name=coffee&amount=1"
```

**2. Query product totals:**

```bash
# Get total beer across all users
curl "http://127.0.0.1:8000/get_product_amount?product_name=beer"

# Get total apples
curl "http://127.0.0.1:8000/get_product_amount?product_name=apple"
```

**3. List all entries:**

```bash
curl "http://127.0.0.1:8000/list_all"
```

**4. Delete a product:**

```bash
# Delete apple for all users
curl -X DELETE "http://127.0.0.1:8000/delete_product?product_name=apple"

# Verify deletion
curl "http://127.0.0.1:8000/list_all"
```

---

## 🎯 Example Use Cases

### Scenario 1: Office Coffee Tracking

```bash
# Everyone wants coffee!
curl -X POST "http://127.0.0.1:8000/write?user_id=1&product_name=coffee&amount=2"
curl -X POST "http://127.0.0.1:8000/write?user_id=5&product_name=coffee&amount=1"
curl -X POST "http://127.0.0.1:8000/write?user_id=6&product_name=coffee&amount=3"

# Check total coffee needed
curl "http://127.0.0.1:8000/get_product_amount?product_name=coffee"
# Output: {"product_name": "coffee", "total_amount": 6}
```

### Scenario 2: Team Event Planning

```bash
# Thor wants beer for the team event
curl -X POST "http://127.0.0.1:8000/write?user_id=2&product_name=beer&amount=6"

# Tony also wants beer
curl -X POST "http://127.0.0.1:8000/write?user_id=6&product_name=beer&amount=4"

# Check total beer needed
curl "http://127.0.0.1:8000/get_product_amount?product_name=beer"
# Output: {"product_name": "beer", "total_amount": 10}
```

### Scenario 3: Remove Out-of-Stock Item

```bash
# Apples are no longer available, remove from list
curl -X DELETE "http://127.0.0.1:8000/delete_product?product_name=apple"

# Verify removal
curl "http://127.0.0.1:8000/list_all"
```

---

## 🧩 Design Decisions

### 1. Normalized Schema

The logical model is flat (`USER : ELEMENT : NUMBER`), but using a normalized schema provides:

- **Unique user identity** via `user_id`
- **Support for duplicate names** (e.g., two employees named "loki")
- **Efficient joins** and data relationships
- **Scalability** for future enhancements
- **Data integrity** through foreign key constraints

### 2. Static User Table

The assignment doesn't require user management, so user data is loaded from a static mapping file: **`users_data.py`**

**Benefits:**
- Keeps the API simple and focused
- Deterministic and predictable behavior
- Easy to understand and maintain
- No complex user authentication needed

### 3. In-memory SQLite

**Why SQLite in-memory?**

- ✅ Zero setup required
- ✅ Supports SQL constraints & joins
- ✅ Perfect for self-contained demos/tests
- ✅ Production-like database behavior
- ✅ Easy to reset and test
- ✅ Lightweight and fast

**Trade-off:** Data is lost when the server restarts. This is acceptable for a demo/assignment but not for production use.

### 4. FastAPI Framework

FastAPI was chosen for its:

- ✅ Clean request validation with Pydantic
- ✅ Automatic interactive documentation
- ✅ Excellent developer experience
- ✅ Modern Python async support
- ✅ Type hints and automatic validation
- ✅ High performance

### 5. Docker Support

Docker deployment provides:

- ✅ **Consistency** — Same environment everywhere
- ✅ **Portability** — Run anywhere Docker is installed
- ✅ **Isolation** — No dependency conflicts
- ✅ **Easy deployment** — Single command to start
- ✅ **Production-ready** — Can be deployed to any container platform

---

## 🚨 Error Handling

The API handles common errors gracefully:

| Error | Status Code | Example | Response |
|-------|-------------|---------|----------|
| Invalid user_id | 400 | `user_id=99` | `{"detail": "Invalid user_id..."}` |
| Invalid amount | 400 | `amount=0` | `{"detail": "Amount must be > 0"}` |
| Product not found | 404 | Non-existent product | `{"product_name": "...", "total_amount": 0}` |
| Missing parameters | 422 | Omitted required params | Validation error details |

---

## 📊 Sample Data Scenarios

<details>
<summary><b>Click to view sample test data</b></summary>

```bash
# Populate sample data
curl -X POST "http://127.0.0.1:8000/write?user_id=1&product_name=apple&amount=1"
curl -X POST "http://127.0.0.1:8000/write?user_id=2&product_name=beer&amount=3"
curl -X POST "http://127.0.0.1:8000/write?user_id=3&product_name=coffee&amount=2"
curl -X POST "http://127.0.0.1:8000/write?user_id=4&product_name=yogurt&amount=5"
curl -X POST "http://127.0.0.1:8000/write?user_id=5&product_name=apple&amount=2"
curl -X POST "http://127.0.0.1:8000/write?user_id=6&product_name=beer&amount=1"

# View all data
curl "http://127.0.0.1:8000/list_all"
```

**Expected Output:**

```json
[
  {"user": "loki", "element": "apple", "number": 1},
  {"user": "thor", "element": "beer", "number": 3},
  {"user": "hulk", "element": "coffee", "number": 2},
  {"user": "natasha", "element": "yogurt", "number": 5},
  {"user": "steve", "element": "apple", "number": 2},
  {"user": "tony", "element": "beer", "number": 1}
]
```

</details>

---
## 🛠️ Development Tips

### Hot Reload

Use the `--reload` flag during development for automatic reloading:

```bash
uvicorn sunday_app:app --reload
```

### Custom Port

Run on a different port:

```bash
uvicorn sunday_app:app --port 8080
```

### Docker Development

Build and run with logs:

```bash
docker-compose up --build
```

Rebuild after code changes:

```bash
docker-compose down
docker-compose up --build
```

View real-time logs:

```bash
docker-compose logs -f
```

---

## 🚀 Deployment

### Docker Hub

Build and push to Docker Hub:

```bash
docker build -t yourusername/sunday_app .
docker push yourusername/sunday_app
```
---

## 📄 License

This project is created for assignment purposes.
