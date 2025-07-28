import re
import pytest
from datetime import datetime, timedelta, timezone
from uuid import UUID

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

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

def assert_uuid(u: str):
    # raises if invalid
    assert UUID_RE.match(u), f"Not a valid UUID4 string: {u}"
    # also round‐trip through uuid module
    UUID(u)

def test_create_and_get_task(db):
    due = datetime.now(timezone.utc) + timedelta(days=1)
    payload = TaskCreate(
        title="Test Task",
        description="Test Description",
        priority=1,
        due_date=due,
    )
    created = create_task(db, payload)

    # id is a valid UUID
    assert_uuid(created.id)
    assert created.title == "Test Task"
    assert created.completed is False

    fetched = get_task(db, created.id)
    assert fetched is not None
    assert fetched.id == created.id

def test_get_task_returns_none_for_missing(db):
    assert get_task(db, "00000000-0000-0000-0000-000000000000") is None

def test_update_task(db):
    due = datetime.now(timezone.utc) + timedelta(days=1)
    task = create_task(db, TaskCreate(
        title="Old",
        description="Desc",
        priority=2,
        due_date=due,
    ))

    updated = update_task(db, task.id, TaskUpdate(title="New"))
    assert updated.id == task.id
    assert updated.title == "New"
    # other fields unchanged
    assert updated.description == "Desc"

def test_update_task_allows_null_to_clear_field(db):
    due = datetime.now(timezone.utc) + timedelta(days=1)
    task = create_task(db, TaskCreate(
        title="T",
        description="To clear",
        priority=3,
        due_date=due,
    ))
    cleared = update_task(db, task.id, TaskUpdate(description=None))
    assert cleared.id == task.id
    assert cleared.description is None

def test_delete_task(db):
    due = datetime.now(timezone.utc) + timedelta(days=1)
    task = create_task(db, TaskCreate(
        title="Del",
        description="X",
        priority=1,
        due_date=due,
    ))
    delete_task(db, task.id)
    assert get_task(db, task.id) is None

def test_get_tasks_filters_and_pagination(db):
    due = datetime.now(timezone.utc) + timedelta(days=1)
    created = []
    for i in range(5):
        t = create_task(db, TaskCreate(
            title=f"T{i}",
            description=None,
            priority=(i % 3) + 1,
            due_date=due,
        ))
        created.append(t)
        if i % 2 == 0:
            update_task(db, t.id, TaskUpdate(completed=True))

    # filter by completed
    done = get_tasks(db, completed=True)
    assert len(done) == 3
    assert all(task.completed for task in done)

    # filter by priority=2
    p2 = get_tasks(db, priority=2)
    assert all(task.priority == 2 for task in p2)

    # pagination: skip 2, limit 2
    page = get_tasks(db, skip=2, limit=2)
    assert len(page) == 2

def test_count_tasks(db):
    due = datetime.now(timezone.utc) + timedelta(days=1)
    for _ in range(3):
        create_task(db, TaskCreate(
            title="C",
            description=None,
            priority=1,
            due_date=due,
        ))
    assert count_tasks(db) == 3
    # mark one done
    all_tasks = get_tasks(db)
    update_task(db, all_tasks[0].id, TaskUpdate(completed=True))
    assert count_tasks(db, completed=True) == 1

def test_default_limit(db):
    due = datetime.now(timezone.utc) + timedelta(days=1)
    total = DEFAULT_PAGE_LIMIT + 5
    for i in range(total):
        create_task(db, TaskCreate(
            title=str(i),
            description=None,
            priority=1,
            due_date=due,
        ))
    # default uses DEFAULT_PAGE_LIMIT
    page = get_tasks(db)
    assert len(page) == DEFAULT_PAGE_LIMIT

def test_limit_cap(db):
    due = datetime.now(timezone.utc) + timedelta(days=1)
    total = MAX_PAGE_SIZE + 10
    for i in range(total):
        create_task(db, TaskCreate(
            title=str(i),
            description=None,
            priority=1,
            due_date=due,
        ))
    # even if we ask for more, we cap at MAX_PAGE_SIZE
    page = get_tasks(db, limit=MAX_PAGE_SIZE + 10)
    assert len(page) == MAX_PAGE_SIZE
