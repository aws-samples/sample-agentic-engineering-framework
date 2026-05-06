from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200

def test_users():
    response = client.get("/users")
    assert response.status_code == 200
    assert len(response.json()["users"]) == 2
