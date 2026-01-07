import pytest
from fastapi.testclient import TestClient

from sunday_app import app

client = TestClient(app)


def test_write_and_list_all_basic():
    # Clean start: no products yet
    resp = client.get("/list_all")
    assert resp.status_code == 200
    assert resp.json() == []

    # user_id=1 -> loki, add apple:1
    resp = client.post("/write", params={"user_id": 1, "product_name": "apple", "amount": 1})
    assert resp.status_code == 200
    data = resp.json()
    assert data["user"] == "loki"
    assert data["element"] == "apple"
    assert data["number"] == 1

    # user_id=2 -> thor, add beer:3
    resp = client.post("/write", params={"user_id": 2, "product_name": "beer", "amount": 3})
    assert resp.status_code == 200
    data = resp.json()
    assert data["user"] == "thor"
    assert data["element"] == "beer"
    assert data["number"] == 3

    # Check list_all returns 2 logical rows
    resp = client.get("/list_all")
    assert resp.status_code == 200
    rows = resp.json()
    # Order is by user_name ASC then product_name ASC
    assert rows == [
        {"user": "loki", "element": "apple", "number": 1},
        {"user": "thor", "element": "beer", "number": 3},
    ]


def test_increment_amount_for_same_user_and_product():
    # user_id=1 adds apple:2
    resp = client.post("/write", params={"user_id": 1, "product_name": "apple", "amount": 2})
    assert resp.status_code == 200
    data = resp.json()
    assert data["user"] == "loki"
    assert data["element"] == "apple"
    # This test assumes previous tests might have run, but we only assert >= 2
    assert data["number"] >= 2

    # Get total for apple across users
    resp = client.get("/get_product_amount", params={"product_name": "apple"})
    assert resp.status_code == 200
    total_data = resp.json()
    assert total_data["product_name"] == "apple"
    assert total_data["amount"] >= 2  # at least what we just added


def test_get_product_amount_zero_when_missing():
    resp = client.get("/get_product_amount", params={"product_name": "nonexistent"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["product_name"] == "nonexistent"
    assert data["amount"] == 0


def test_delete_product():
    # Add some oranges
    client.post("/write", params={"user_id": 1, "product_name": "orange", "amount": 2})
    client.post("/write", params={"user_id": 2, "product_name": "orange", "amount": 5})

    # Check total
    resp = client.get("/get_product_amount", params={"product_name": "orange"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["amount"] >= 7

    # Delete the product everywhere
    resp = client.delete("/delete_product", params={"product_name": "orange"})
    assert resp.status_code == 200
    del_data = resp.json()
    assert del_data["product_name"] == "orange"
    assert del_data["deleted_rows"] >= 2

    # Now total should be 0
    resp = client.get("/get_product_amount", params={"product_name": "orange"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["amount"] == 0


def test_unknown_user_id():
    resp = client.post("/write", params={"user_id": 999, "product_name": "apple", "amount": 1})
    assert resp.status_code == 400
    data = resp.json()
    assert "Unknown user_id" in data["detail"]
