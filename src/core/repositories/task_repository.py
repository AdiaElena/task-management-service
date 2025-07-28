from typing import Optional, List
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.config import DEFAULT_PAGE_LIMIT, MAX_PAGE_SIZE
from src.core.models.task import Task
from src.core.schemas.task import TaskCreate, TaskUpdate

def create_task(db: Session, task: TaskCreate) -> Task:
    """
    Create a new Task record in the database.

    :param db: SQLAlchemy session
    :param task: TaskCreate schema containing task details
    :return: Persisted Task model instance
    """
    db_task = Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_task(db: Session, task_id: int) -> Optional[Task]:
    """
    Retrieve a Task by its ID.

    :param db: SQLAlchemy session
    :param task_id: ID of the task to retrieve
    :return: Task instance or None if not found
    """
    return db.query(Task).filter(Task.id == task_id).first()

def get_tasks(
    db: Session,
    skip: int = 0,
    limit: int = DEFAULT_PAGE_LIMIT,
    completed: Optional[bool] = None,
    priority: Optional[int] = None,
) -> List[Task]:
    """
    Retrieve a list of tasks with optional filtering and pagination.

    :param db: SQLAlchemy session
    :param skip: Number of records to skip (offset)
    :param limit: Maximum number of records to return (capped by MAX_PAGE_SIZE)
    :param completed: Optional filter by completion status
    :param priority: Optional filter by priority (1=High, 2=Medium, 3=Low)
    :return: List of Task instances
    """
    effective_limit = min(limit, MAX_PAGE_SIZE)
    query = db.query(Task).order_by(Task.id)
    if completed is not None:
        query = query.filter(Task.completed == completed)
    if priority is not None:
        query = query.filter(Task.priority == priority)
    return query.offset(skip).limit(effective_limit).all()

def count_tasks(
    db: Session,
    completed: Optional[bool] = None,
    priority: Optional[int] = None,
) -> int:
    """
    Count total tasks with optional filtering, for pagination metadata.

    :param db: SQLAlchemy session
    :param completed: Optional filter by completion status
    :param priority: Optional filter by priority
    :return: Total count of matching tasks
    """
    query = db.query(func.count(Task.id))
    if completed is not None:
        query = query.filter(Task.completed == completed)
    if priority is not None:
        query = query.filter(Task.priority == priority)
    return query.scalar() or 0

def update_task(db: Session, task_id: int, task_update: TaskUpdate) -> Task:
    """
    Update an existing Task. Fields omitted in the update schema remain unchanged;
    explicit null values overwrite existing data.

    :param db: SQLAlchemy session
    :param task_id: ID of the task to update
    :param task_update: TaskUpdate schema with new values
    :return: Updated Task instance
    """
    task = get_task(db, task_id)
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task

def delete_task(db: Session, task_id: int) -> None:
    """
    Delete a Task by its ID.]

    :param db: SQLAlchemy session
    :param task_id: ID of the task to delete
    :return: None
    """
    task = get_task(db, task_id)
    if task:
        db.delete(task)
        db.commit()
