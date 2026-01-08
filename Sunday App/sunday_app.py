from fastapi import FastAPI, HTTPException
import sqlite3
from typing import List, Dict
import os

from users_data import STATIC_USERS  # <- mock users come from a separate file

app = FastAPI(title="SundayApp - Grocery Tracker (USER : ELEMENT : NUMBER)")


# The /data directory will be mounted as a PersistentVolume
DB_PATH = os.getenv("DB_PATH", "/data/sunday.db")

# Ensure the directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Connect to file-based database (will be created if it doesn't exist)
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.row_factory = sqlite3.Row


# ------------------------------
# DB schema + seeding
# ------------------------------
def init_db():
    # users table: holds user_id -> user_name
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id   INTEGER PRIMARY KEY,
            user_name TEXT NOT NULL
        );
        """
    )

    # groceries table: core data model
    # USER : ELEMENT : NUMBER  ==  user_id : product_name : amount
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS groceries (
            user_id      INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            amount       INTEGER NOT NULL CHECK (amount >= 0),
            PRIMARY KEY (user_id, product_name),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
        """
    )

    # Seed static users from users_data.py
    for uid, uname in STATIC_USERS.items():
        conn.execute(
            "INSERT OR IGNORE INTO users (user_id, user_name) VALUES (?, ?)",
            (uid, uname),
        )

    conn.commit()


init_db()


# ------------------------------
# Helper functions
# ------------------------------

def validate_lowercase_letters(value: str, field_name: str) -> str:
    """
    Requirement: assume names and products contain lowercase letters only.
    Enforce that for user_name and product_name.
    """
    if not value.isalpha() or not value.islower():
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} must contain lowercase letters only (a-z).",
        )
    return value


def get_user_name_or_error(user_id: int) -> str:
    row = conn.execute(
        "SELECT user_name FROM users WHERE user_id = ?", (user_id,)
    ).fetchone()
    if not row:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown user_id {user_id}. Expected one of: {sorted(STATIC_USERS.keys())}",
        )
    user_name = row["user_name"]
    validate_lowercase_letters(user_name, "user_name")
    return user_name


# ------------------------------
# API Endpoints (per assignment)
# ------------------------------

@app.post("/write")
def write_item(user_id: int, product_name: str, amount: int):
    """
    POST /write
    Params: user_id, product_name, amount

    Uses user_id only (no user_name parameter).
    user_name is looked up from the static users table.

    Logical data model:
      USER  : ELEMENT       : NUMBER
      name  : product_name  : amount
    """
    if amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be > 0")

    # Make sure user exists & get user_name
    user_name = get_user_name_or_error(user_id)

    # Validate product_name according to requirement
    product_name = validate_lowercase_letters(product_name, "product_name")

    # Upsert into groceries:
    # if (user_id, product_name) exists, increment the amount
    conn.execute(
        """
        INSERT INTO groceries (user_id, product_name, amount)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, product_name)
        DO UPDATE SET amount = groceries.amount + excluded.amount
        """,
        (user_id, product_name, amount),
    )
    conn.commit()

    # Read back the current total for this user/product
    row = conn.execute(
        """
        SELECT amount FROM groceries
        WHERE user_id = ? AND product_name = ?
        """,
        (user_id, product_name),
    ).fetchone()

    current_amount = row["amount"] if row else amount

    # Logically this is: USER : ELEMENT : NUMBER
    return {
        "message": "ok",
        "user": user_name,        # USER (name)
        "element": product_name,  # ELEMENT (product)
        "number": current_amount  # NUMBER (amount)
    }


@app.get("/get_product_amount")
def get_product_amount(product_name: str):
    """
    GET /get_product_amount?product_name=...

    Returns total NUMBER of that ELEMENT across all USERs.
    """
    product_name = validate_lowercase_letters(product_name, "product_name")

    row = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) AS total FROM groceries WHERE product_name = ?",
        (product_name,),
    ).fetchone()

    total = row["total"] if row and row["total"] is not None else 0
    return {"product_name": product_name, "amount": total}


@app.delete("/delete_product")
def delete_product(product_name: str):
    """
    DELETE /delete_product?product_name=...

    Remove this ELEMENT (product_name) for all USERs.
    """
    product_name = validate_lowercase_letters(product_name, "product_name")

    cur = conn.execute(
        "DELETE FROM groceries WHERE product_name = ?",
        (product_name,),
    )
    conn.commit()

    return {
        "message": "ok",
        "product_name": product_name,
        "deleted_rows": cur.rowcount,
    }


# ------------------------------
# Helper endpoint to expose USER : ELEMENT : NUMBER
# ------------------------------

@app.get("/list_all")
def list_all() -> List[Dict]:
    """
    Returns the logical data model rows:

      USER : ELEMENT : NUMBER

    Example:
    [
      { "user": "loki", "element": "apple", "number": 1 },
      { "user": "thor", "element": "beer",  "number": 3 }
    ]
    """
    rows = conn.execute(
        """
        SELECT u.user_name, g.product_name, g.amount
        FROM groceries g
        JOIN users u ON u.user_id = g.user_id
        ORDER BY u.user_name ASC, g.product_name ASC
        """
    ).fetchall()

    return [
        {"user": r["user_name"], "element": r["product_name"], "number": r["amount"]}
        for r in rows
    ]


# NEW: Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint for Kubernetes"""
    return {"status": "healthy", "database": DB_PATH}
