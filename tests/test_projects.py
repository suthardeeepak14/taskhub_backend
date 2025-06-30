
from fastapi.testclient import TestClient
from taskApi.app.main import app

client = TestClient(app)

def test_create_project():
    response = client.post("/projects", json={
        "name": "Test Project",
        "description": "Testing",
        "status": "pending",
        "due_date": "2025-07-01"
    })
    assert response.status_code == 200
    assert response.json()["name"] == "Test Project"