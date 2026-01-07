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

<br>

---

## 📌 Features

| Feature | Description |
|---------|-------------|
| ✅ **Add Items** | Add grocery items for users |
| ✅ **Get Totals** | Get total amount of a product across all users |
| ✅ **Delete Products** | Remove a product for all users |
| ✅ **List All** | Return full logical model (USER : ELEMENT : NUMBER) |
| ✅ **Zero Setup** | Uses in-memory SQLite (no configuration needed) |
| ✅ **Complete Toolkit** | Includes Dockerfile + Docker Compose + Postman Collection + Tests |
| ✅ **Clean Schema** | Normalized schema with FK constraints |
| ✅ **Mock Users** | Static user table of 10 predefined users |

<br>

---

## 🧠 Data Model

### Logical Model (Required Format)

The assignment defines the logical data model as:

```
USER : ELEMENT : NUMBER
```

This API outputs exactly this format via:

```bash
GET /list_all
```

**Example Response:**

```json
[
  {"user": "loki", "element": "apple", "number": 1},
  {"user": "thor", "element": "beer", "number": 3}
]
```

<br>

---

## 🗂 Internal Architecture

To support correctness and realistic behavior, the app internally uses two tables:

### ✔️ Table: `users` (Static Mock Data)

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

### ✔️ Table: `groceries`

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | INT | Foreign key to users table |
| `product_name` | TEXT | Name of the product |
| `amount` | INT | Quantity of the product |

**Primary Key:** `(user_id, product_name)`

### Data Model Mapping

```
USER    = user_name
ELEMENT = product_name
NUMBER  = amount
```

<br>

---

## 🚀 Running the Application

### Option 1: Docker Compose 🐳 (Recommended)

The easiest way to run the application!

#### 1. Start the Application

```bash
docker-compose up
```

Or run in detached mode:

```bash
docker-compose up -d
```

#### 2. Access the Application

Application now reachable at: **http://127.0.0.1:8000**

#### 3. Stop the Application

```bash
docker-compose down
```

<br>

### Option 2: Local Python

#### 1. Install Dependencies

```bash
pip install fastapi uvicorn
or
pip3 install fastapi uvicorn
```

#### 2. Run the API

```bash
uvicorn sunday_app:app --reload
```

#### 3. Access the Server

Server starts at: **http://127.0.0.1:8000**

<br>

### Option 3: Docker

#### 1. Build the Container

```bash
docker build -t sunday_app .
```

#### 2. Run the Container

```bash
docker run -p 8000:8000 sunday_app
```

#### 3. Access the Application

Application now reachable at: **http://127.0.0.1:8000**

<br>

---

## 📬 API Endpoints

### 🔹 POST `/write`

Add or increase product amount for a user.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `user_id` | int | Identifies the user (1-10) |
| `product_name` | str | Product name (lowercase only) |
| `amount` | int | Quantity (must be > 0) |

**Example:**

```bash
curl -X POST "http://127.0.0.1:8000/write?user_id=1&product_name=apple&amount=1"
```

**Response:**

```json
{"message": "Updated apple for user loki"}
```

<br>

### 🔹 GET `/get_product_amount`

Get total amount of a product across all users.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `product_name` | str | Product name to query |

**Example:**

```bash
curl "http://127.0.0.1:8000/get_product_amount?product_name=apple"
```

**Response:**

```json
{"product_name": "apple", "total_amount": 5}
```

<br>

### 🔹 DELETE `/delete_product`

Remove a product for all users.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `product_name` | str | Product name to delete |

**Example:**

```bash
curl -X DELETE "http://127.0.0.1:8000/delete_product?product_name=apple"
```

**Response:**

```json
{"message": "Deleted apple for all users"}
```

<br>

### 🔹 GET `/list_all`

Return the logical model: **USER : ELEMENT : NUMBER**

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

<br>

---

## 🧪 Testing

### Unit Tests

Tests are located in: **`test_sunday_app.py`**

#### Run Tests

```bash
# Install pytest
pip install pytest

# Run tests
pytest -q
```

### Test Coverage

Tests cover:

- ✅ Adding items
- ✅ Summing product amounts
- ✅ Deleting products
- ✅ Listing all rows
- ✅ Handling invalid/unknown user_id

<br>

---

## 🧪 Quick Manual Testing Guide

### Step-by-Step Testing

#### 1. Add Items

```bash
# Add apple for loki
curl -X POST "http://127.0.0.1:8000/write?user_id=1&product_name=apple&amount=1"

# Add beer for thor
curl -X POST "http://127.0.0.1:8000/write?user_id=2&product_name=beer&amount=3"

# Add more apples for hulk
curl -X POST "http://127.0.0.1:8000/write?user_id=3&product_name=apple&amount=2"
```

#### 2. Get Product Totals

```bash
# Get total beer across all users
curl "http://127.0.0.1:8000/get_product_amount?product_name=beer"

# Get total apples
curl "http://127.0.0.1:8000/get_product_amount?product_name=apple"
```

#### 3. List All Entries

```bash
curl "http://127.0.0.1:8000/list_all"
```

#### 4. Delete a Product

```bash
# Delete apple for all users
curl -X DELETE "http://127.0.0.1:8000/delete_product?product_name=apple"

# Verify deletion
curl "http://127.0.0.1:8000/list_all"
```

<br>

---

## 📬 Postman Collection

A complete Postman collection is included: **`SundayApp.postman_collection.json`**

### How to Use

1. Open Postman
2. Click **Import**
3. Select `SundayApp.postman_collection.json`
4. All endpoints ready to test!

<br>

---

## 🧩 Design Decisions

### ✔️ 1. Normalized Schema

The logical model is flat (`USER : ELEMENT : NUMBER`), but using a normalized schema provides:

- **Unique user identity** via `user_id`
- **Support for duplicate names** (e.g., two employees named "loki")
- **Efficient joins** and data relationships
- **Scalability** for future enhancements

### ✔️ 2. Static User Table

The assignment doesn't require user management, so user data is loaded from a static mapping file: **`users_data.py`**

**Benefits:**
- Keeps the API simple and focused
- Deterministic and predictable behavior
- Easy to understand and maintain

### ✔️ 3. In-memory SQLite

**Why SQLite in-memory?**

- ✅ Zero setup required
- ✅ Supports SQL constraints & joins
- ✅ Perfect for self-contained demos/tests
- ✅ Production-like database behavior
- ✅ Easy to reset and test

### ✔️ 4. FastAPI Framework

FastAPI provides:

- ✅ Clean request validation
- ✅ Automatic interactive docs (`/docs`)
- ✅ Strong developer experience
- ✅ Modern Python async support
- ✅ Type hints and Pydantic models

### ✔️ 5. Helper Endpoint `/list_all`

The assignment requires output in the exact format:

```
USER : ELEMENT : NUMBER
```

The `/list_all` endpoint reconstructs this logical model by joining the `users` and `groceries` tables, ensuring the API contract matches the specification perfectly.

<br>

---

## 🔍 API Documentation

FastAPI provides **automatic interactive documentation**:

### Swagger UI (Recommended)

Visit: **http://127.0.0.1:8000/docs**

- Interactive API testing
- Request/response examples
- Schema validation

### ReDoc (Alternative)

Visit: **http://127.0.0.1:8000/redoc**

- Clean documentation layout
- Detailed API specifications

<br>

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

### Scenario 2: Beer for Team Event

```bash
# Thor wants beer
curl -X POST "http://127.0.0.1:8000/write?user_id=2&product_name=beer&amount=6"

# List everything
curl "http://127.0.0.1:8000/list_all"
```

### Scenario 3: Remove Out-of-Stock Item

```bash
# Apples are gone, remove from list
curl -X DELETE "http://127.0.0.1:8000/delete_product?product_name=apple"
```

<br>

---

## 🛠️ Development Tips

### Hot Reload

Use `--reload` flag for development:

```bash
uvicorn sunday_app:app --reload
```

### Custom Port

Run on a different port:

```bash
uvicorn sunday_app:app --port 8080
```

### Docker Compose Development

Build and run with logs:

```bash
docker-compose up --build
```

View logs:

```bash
docker-compose logs -f
```

Rebuild after changes:

```bash
docker-compose down
docker-compose up --build
```

### Docker Development (without Compose)

Build and run with logs:

```bash
docker build -t sunday_app . && docker run -p 8000:8000 sunday_app
```

<br>

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

<br>

---

## 🚨 Error Handling

The API handles common errors gracefully:

| Error | Status Code | Example |
|-------|-------------|---------|
| Invalid user_id | 400 | `user_id=99` (not in 1-10) |
| Invalid amount | 400 | `amount=0` or negative |
| Product not found | 404 | Querying non-existent product |
| Missing parameters | 422 | Omitting required query params |

<br>

---

## 📄 License

This project is created for assignment purposes.

---

<div align="center">

**Made with ☕ for tracking office groceries**

[View Docs](http://127.0.0.1:8000/docs) · [Report Bug](#) · [Request Feature](#)

</div>
