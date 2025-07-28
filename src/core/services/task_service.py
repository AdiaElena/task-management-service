from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session

from src.core.exceptions import NotFoundError
from src.core.config import DEFAULT_PAGE_LIMIT
from src.core.repositories.task_repository import (
    create_task as repo_create,
    get_task   as repo_get,
    get_tasks  as repo_list,
    count_tasks as repo_count,
    update_task as repo_update,
    delete_task as repo_delete,
)
from src.core.schemas.task import TaskCreate, TaskUpdate, TaskOut


def create_task(db: Session, payload: TaskCreate) -> TaskOut:
    """
    Business logic for creating a new Task.

    1. Calls repository to persist the Task.
    2. Wraps the returned model in a TaskOut schema.

    :param db: SQLAlchemy session
    :param payload: TaskCreate schema with new task data
    :return: TaskOut schema representing the created task
    """
    task = repo_create(db, payload)
    return TaskOut.model_validate(task)


def get_task(db: Session, task_id: UUID) -> TaskOut:
    """
    Business logic for retrieving a single Task by ID.

    Raises NotFoundError if no task exists with the given ID.

    :param db: SQLAlchemy session
    :param task_id: ID of the task to fetch
    :raises NotFoundError: if task not found
    :return: TaskOut schema
    """
    task = repo_get(db, task_id)
    if task is None:
        raise NotFoundError(f"Task with id {task_id} not found")
    return TaskOut.model_validate(task)


def list_tasks(
    db: Session,
    skip: int = 0,
    limit: Optional[int] = None,
    completed: Optional[bool] = None,
    priority: Optional[int] = None,
) -> List[TaskOut]:
    """
    Business logic for listing Tasks with optional filters and pagination.

    :param db: SQLAlchemy session
    :param skip: number of records to skip (offset)
    :param limit: maximum records to return
    :param completed: optional completion filter
    :param priority: optional priority filter
    :return: list of TaskOut schemas
    """

    effective_limit = limit if limit is not None else DEFAULT_PAGE_LIMIT

    tasks = repo_list(
        db, 
        skip=skip, 
        limit=effective_limit, 
        completed=completed, 
        priority=priority
    )
    return [TaskOut.model_validate(t) for t in tasks]


def list_tasks_with_count(
    db: Session,
    skip: int = 0,
    limit: Optional[int] = None,
    completed: Optional[bool] = None,
    priority: Optional[int] = None,
) -> Tuple[List[TaskOut], int]:
    """
    Business logic for listing Tasks along with total count for pagination metadata.

    Use this to return both a page of results and the overall count in one call,
    ensuring consistent filters and reducing duplicate repository calls.

    :param db: SQLAlchemy session
    :param skip: offset for pagination
    :param limit: maximum records to return
    :param completed: optional completion filter
    :param priority: optional priority filter
    :return: (list of TaskOut, total count of matching tasks)
    """
    effective_limit = limit if limit is not None else DEFAULT_PAGE_LIMIT
    total = repo_count(
        db, 
        completed=completed, 
        priority=priority
    )
    tasks = repo_list(
        db, 
        skip=skip, 
        limit=effective_limit, 
        completed=completed, 
        priority=priority
    )
    return ([TaskOut.model_validate(t) for t in tasks], total)


def update_task(db: Session, task_id: UUID, patch: TaskUpdate) -> TaskOut:
    """
    Business logic for updating an existing Task.

    Workflow:
    1. Verifies the task exists, else raises NotFoundError.
    2. Calls repository to apply patch.
    3. Returns the updated TaskOut schema.

    :param db: SQLAlchemy session
    :param task_id: ID of the task to update
    :param patch: TaskUpdate schema with fields to modify
    :raises NotFoundError: if task not found
    :return: TaskOut schema of updated task
    """
    existing = repo_get(db, task_id)
    if existing is None:
        raise NotFoundError(f"Task with id {task_id} not found")
    updated = repo_update(db, task_id, patch)
    return TaskOut.model_validate(updated)


def delete_task(db: Session, task_id: UUID) -> None:
    """
    Business logic for deleting a Task.

    Workflow:
    1. Verifies the task exists, else raises NotFoundError.
    2. Calls repository to delete the task.

    :param db: SQLAlchemy session
    :param task_id: ID of the task to delete
    :raises NotFoundError: if task not found
    :return: None
    """
    existing = repo_get(db, task_id)
    if existing is None:
        raise NotFoundError(f"Task with id {task_id} not found")
    repo_delete(db, task_id)
