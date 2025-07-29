import uuid
import pytest
from datetime import datetime, timezone, timedelta

from fastapi.testclient import TestClient

from src.main import app
from src.core.schemas.task import TaskOut
from src.core.exceptions import NotFoundError

client = TestClient(app)


@pytest.fixture
def now() -> datetime:
    return datetime.now(timezone.utc)


# we use a fixed UUID so our assertions are deterministic
DUMMY_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")


def make_payload(now: datetime) -> dict:
    return {
        "title": "Important Task",
        "description": "Task Description",
        "priority": 2,
        "due_date": (now + timedelta(days=1)).isoformat(),
    }


def make_taskout(now: datetime) -> TaskOut:
    return TaskOut(
        id=DUMMY_ID,                                 
        title="Important Task",
        description="Task Description",
        priority=2,
        due_date=now + timedelta(days=1),
        completed=False,
    )


def test_create_task_endpoint(monkeypatch, now):
    dummy = make_taskout(now)
    monkeypatch.setattr(
        "src.api.endpoints.tasks.svc_create",
        lambda db, payload: dummy,
    )

    resp = client.post("/tasks/", json=make_payload(now))
    assert resp.status_code == 201

    data = resp.json()
    # id should be the stringified UUID
    assert data["id"] == str(DUMMY_ID)
    assert data["title"] == "Important Task"
    assert data["description"] == "Task Description"
    assert data["priority"] == 2
    assert data["completed"] is False

    # compare parsed due_date
    expected_due = now + timedelta(days=1)
    # pydantic serializes as RFC3339 (with Z), so normalize before parse
    iso = data["due_date"].replace("Z", "+00:00")
    parsed = datetime.fromisoformat(iso)
    assert parsed == expected_due


def test_list_tasks_endpoint(monkeypatch, now):
    dummy = make_taskout(now)
    monkeypatch.setattr(
        "src.api.endpoints.tasks.svc_list",
        lambda db, skip, limit, completed, priority: [dummy],
    )

    resp = client.get("/tasks/?skip=2&limit=1&completed=false&priority=2")
    assert resp.status_code == 200

    data = resp.json()
    assert isinstance(data, list)
    assert data[0]["id"] == str(DUMMY_ID)


def test_get_task_endpoint_success(monkeypatch, now):
    dummy = make_taskout(now)
    monkeypatch.setattr(
        "src.api.endpoints.tasks.svc_get",
        lambda db, tid: dummy,
    )

    resp = client.get(f"/tasks/{DUMMY_ID}")
    assert resp.status_code == 200
    assert resp.json()["id"] == str(DUMMY_ID)


def test_get_task_endpoint_not_found(monkeypatch):
    monkeypatch.setattr(
        "src.api.endpoints.tasks.svc_get",
        lambda db, tid: (_ for _ in ()).throw(NotFoundError("not found")),
    )

    resp = client.get(f"/tasks/{DUMMY_ID}")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "not found"


def test_update_task_endpoint_success(monkeypatch, now):
    updated = TaskOut(
        id=DUMMY_ID,
        title="Updated",
        description=None,
        priority=2,
        due_date=now + timedelta(days=1),
        completed=False,
    )
    monkeypatch.setattr(
        "src.api.endpoints.tasks.svc_update",
        lambda db, tid, p: updated,
    )

    resp = client.put(f"/tasks/{DUMMY_ID}", json={"title": "Updated"})
    assert resp.status_code == 200

    data = resp.json()
    assert data["id"] == str(DUMMY_ID)
    assert data["title"] == "Updated"


def test_update_task_endpoint_not_found(monkeypatch):
    monkeypatch.setattr(
        "src.api.endpoints.tasks.svc_update",
        lambda db, tid, p: (_ for _ in ()).throw(NotFoundError("nope")),
    )

    resp = client.put(f"/tasks/{DUMMY_ID}", json={"title": "X"})
    assert resp.status_code == 404
    assert resp.json()["detail"] == "nope"


def test_delete_task_endpoint_success(monkeypatch):
    monkeypatch.setattr(
        "src.api.endpoints.tasks.svc_delete",
        lambda db, tid: None,
    )

    resp = client.delete(f"/tasks/{DUMMY_ID}")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Task deleted successfully."}


def test_delete_task_endpoint_not_found(monkeypatch):
    monkeypatch.setattr(
        "src.api.endpoints.tasks.svc_delete",
        lambda db, tid: (_ for _ in ()).throw(NotFoundError("gone")),
    )

    resp = client.delete(f"/tasks/{DUMMY_ID}")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "gone"
