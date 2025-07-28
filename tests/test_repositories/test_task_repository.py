import pytest
from datetime import datetime, timedelta, timezone

from src.core.config import DEFAULT_PAGE_LIMIT, MAX_PAGE_SIZE
from src.core.database import Base, engine, SessionLocal
from src.core.repositories.task_repository import (
    create_task,
    get_task,
    get_tasks,
    count_tasks,
    update_task,
    delete_task,
)
from src.core.schemas.task import TaskCreate, TaskUpdate


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_create_and_get_task(db):
    payload = TaskCreate(
        title="Test Task",
        description="Test Description",
        priority=1,
        due_date=datetime.now(timezone.utc) + timedelta(days=1),
    )
    created = create_task(db, payload)

    fetched = get_task(db, created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.title == "Test Task"


def test_get_task_returns_none_for_missing(db):
    assert get_task(db, 9999) is None


def test_update_task(db):
    payload = TaskCreate(
        title="Old Title",
        description="Old Description",
        priority=2,
        due_date=datetime.now(timezone.utc) + timedelta(days=1),
    )
    task = create_task(db, payload)

    updated = update_task(db, task.id, TaskUpdate(title="New Title"))
    assert updated.title == "New Title"
    assert updated.description == "Old Description"


def test_update_task_allows_null_to_clear_field(db):
    payload = TaskCreate(
        title="Title",
        description="Will be cleared",
        priority=2,
        due_date=datetime.now(timezone.utc) + timedelta(days=1),
    )
    task = create_task(db, payload)

    cleared = update_task(db, task.id, TaskUpdate(description=None))
    assert cleared.description is None


def test_delete_task(db):
    payload = TaskCreate(
        title="Delete Task",
        description="Delete me",
        priority=3,
        due_date=datetime.now(timezone.utc) + timedelta(days=1),
    )
    task = create_task(db, payload)
    delete_task(db, task.id)

    assert get_task(db, task.id) is None


def test_get_tasks_filters_and_pagination(db):
    now = datetime.now(timezone.utc) + timedelta(days=1)
    # create 5 tasks with varying completed and priority
    for i in range(5):
        t = create_task(
            db,
            TaskCreate(
                title=f"Task {i}",
                description=None,
                priority=(i % 3) + 1,
                due_date=now,
            ),
        )
        if i % 2 == 0:
            update_task(db, t.id, TaskUpdate(completed=True))

    completed = get_tasks(db, completed=True)
    assert all(t.completed for t in completed)

    prio2 = get_tasks(db, priority=2)
    assert all(t.priority == 2 for t in prio2)

    page = get_tasks(db, skip=2, limit=2)
    assert len(page) == 2
    assert page[0].id == 3 and page[1].id == 4


def test_count_tasks(db):
    now = datetime.now(timezone.utc) + timedelta(days=1)
    for i in range(3):
        create_task(
            db,
            TaskCreate(
                title=f"C{i}",
                description=None,
                priority=1,
                due_date=now,
            ),
        )
    assert count_tasks(db) == 3

    t = get_tasks(db)[0]
    update_task(db, t.id, TaskUpdate(completed=True))
    assert count_tasks(db, completed=True) == 1


def test_default_limit_and_ordering(db):
    now = datetime.now(timezone.utc) + timedelta(days=1)
    # create more than default limit tasks
    total = DEFAULT_PAGE_LIMIT + 5
    tasks = []
    for i in range(total):
        t = create_task(
            db,
            TaskCreate(
                title=f"TL{i}", description=None, priority=1, due_date=now
            ),
        )
        tasks.append(t)
    result = get_tasks(db)
    # default limit applies and ordering by id
    assert len(result) == DEFAULT_PAGE_LIMIT
    assert result[0].id == tasks[0].id and result[-1].id == tasks[DEFAULT_PAGE_LIMIT - 1].id


def test_limit_cap(db):
    now = datetime.now(timezone.utc) + timedelta(days=1)
    total = MAX_PAGE_SIZE + 10
    for i in range(total):
        create_task(
            db,
            TaskCreate(
                title=f"MC{i}", description=None, priority=1, due_date=now
            ),
        )
    result = get_tasks(db, limit=MAX_PAGE_SIZE + 10)
    assert len(result) == MAX_PAGE_SIZE
