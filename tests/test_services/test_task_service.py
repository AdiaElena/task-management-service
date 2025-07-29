import pytest
from typing import List
from datetime import datetime, timezone

from src.core.services.task_service import (
    create_task,
    get_task,
    list_tasks,
    list_tasks_with_count,
    update_task,
    delete_task,
)
from src.core.schemas.task import TaskCreate, TaskUpdate, TaskOut
from src.core.exceptions import NotFoundError

from tests.utils import DummyTaskModel 
from tests.conftest import session, dummy_task 

NOT_FOUND_UUID = "00000000-0000-0000-0000-000000000000"


def test_create_task_unit(monkeypatch, dummy_task, session):
    def fake_repo_create(db, payload):
        assert db is session
        assert isinstance(payload, TaskCreate)
        return dummy_task

    monkeypatch.setattr(
        "src.core.services.task_service.repo_create",
        fake_repo_create,
    )

    payload = TaskCreate(
        title="New",
        description="Desc",
        priority=1,
        due_date=dummy_task.due_date,
    )
    out: TaskOut = create_task(session, payload)
    assert isinstance(out, TaskOut)
    assert out.id == dummy_task.id
    assert out.title == dummy_task.title


def test_get_task_unit_success(monkeypatch, dummy_task, session):
    monkeypatch.setattr(
        "src.core.services.task_service.repo_get",
        lambda db, tid: dummy_task
    )
    out = get_task(session, dummy_task.id)
    assert isinstance(out, TaskOut)
    assert out.id == dummy_task.id


def test_get_task_unit_not_found(monkeypatch, session):
    monkeypatch.setattr(
        "src.core.services.task_service.repo_get",
        lambda db, tid: None
    )
    with pytest.raises(NotFoundError):
        get_task(session, NOT_FOUND_UUID)


def test_list_tasks_unit(monkeypatch, dummy_task, session):
    monkeypatch.setattr(
        "src.core.services.task_service.repo_list",
        lambda db, skip, limit, completed, priority: [dummy_task],
    )
    outs: List[TaskOut] = list_tasks(
        session,
        skip=0,
        limit=5,
        completed=None,
        priority=None
    )
    assert len(outs) == 1
    assert outs[0].id == dummy_task.id


def test_list_tasks_with_count_unit(monkeypatch, dummy_task, session):
    monkeypatch.setattr(
        "src.core.services.task_service.repo_count",
        lambda db, completed, priority: 7
    )
    monkeypatch.setattr(
        "src.core.services.task_service.repo_list",
        lambda db, skip, limit, completed, priority: [dummy_task, dummy_task],
    )
    page, total = list_tasks_with_count(
        session,
        skip=1,
        limit=2,
        completed=None,
        priority=None
    )
    assert total == 7
    assert len(page) == 2


def test_update_task_unit_success(monkeypatch, dummy_task, session):
    monkeypatch.setattr(
        "src.core.services.task_service.repo_get",
        lambda db, tid: dummy_task
    )
    updated = DummyTaskModel(**vars(dummy_task))
    updated.title = "Updated"

    def fake_repo_update(db, tid, patch):
        assert isinstance(patch, TaskUpdate)
        assert patch.title == "Updated"
        return updated

    monkeypatch.setattr(
        "src.core.services.task_service.repo_update",
        fake_repo_update,
    )

    out = update_task(session, dummy_task.id, TaskUpdate(title="Updated"))
    assert out.id == dummy_task.id
    assert out.title == "Updated"


def test_update_task_unit_not_found(monkeypatch, session):
    monkeypatch.setattr(
        "src.core.services.task_service.repo_get",
        lambda db, tid: None
    )
    with pytest.raises(NotFoundError):
        update_task(session, NOT_FOUND_UUID, TaskUpdate(title="X"))


def test_delete_task_unit_success(monkeypatch, dummy_task, session):
    monkeypatch.setattr(
        "src.core.services.task_service.repo_get",
        lambda db, tid: dummy_task
    )
    called = {}
    monkeypatch.setattr(
        "src.core.services.task_service.repo_delete",
        lambda db, tid: called.setdefault("deleted", tid)
    )

    delete_task(session, dummy_task.id)
    assert called.get("deleted") == dummy_task.id


def test_delete_task_unit_not_found(monkeypatch, session):
    monkeypatch.setattr(
        "src.core.services.task_service.repo_get",
        lambda db, tid: None
    )
    with pytest.raises(NotFoundError):
        delete_task(session, NOT_FOUND_UUID)
