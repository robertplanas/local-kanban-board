import pytest
import os
import json
from web import app
import db


@pytest.fixture
def client(tmp_path):
    """
    Creates a Flask test client with a temporary database.
    """
    # 1. Setup: Create a temp DB file
    db_path = tmp_path / "test_api.db"

    # 2. Configure Flask to use this DB
    # We need to monkeypatch the DB_PATH in web.py so it uses our temp file
    import web

    web.DB_PATH = str(db_path)

    # Initialize the DB schema
    db.init_db(str(db_path))

    # 3. Create the test client
    with app.test_client() as client:
        yield client


def test_get_tasks_empty(client):
    """Start with 0 tasks"""
    rv = client.get("/api/tasks")
    assert rv.status_code == 200
    assert rv.json == []


def test_create_and_move_task(client):
    """Test the full flow: Create -> Verify -> Move -> Verify"""

    # 1. Create Task
    payload = {
        "title": "Integration Test Task",
        "description": "Testing API",
        "priority": "High",
        "project": "QA",
        "column": "Backlog",
        "deadline": "2025-01-01",
        "subtasks": [{"text": "subtask 1", "completed": False}],
    }
    rv = client.post("/api/task", json=payload)
    assert rv.status_code == 200
    task_id = rv.json.get("id")
    assert task_id is not None

    # 2. Verify it exists in Backlog
    rv = client.get("/api/tasks")
    tasks = rv.json
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Integration Test Task"
    assert tasks[0]["column"] == "Backlog"

    # 3. Move Task via API
    move_payload = {"to": "In Progress"}
    rv = client.post(f"/api/task/{task_id}/move", json=move_payload)
    assert rv.status_code == 200
    assert rv.json["moved"] is True

    # 4. Verify Move
    rv = client.get("/api/tasks")
    assert rv.json[0]["column"] == "In Progress"

    # 5. Delete Task
    rv = client.delete(f"/api/task/{task_id}")
    assert rv.status_code == 200
