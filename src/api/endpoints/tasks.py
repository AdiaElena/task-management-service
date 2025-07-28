from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import UUID 

from src.core.config import DEFAULT_PAGE_LIMIT, MAX_PAGE_SIZE
from src.core.schemas.task import TaskCreate, TaskUpdate, TaskOut
from src.core.exceptions import NotFoundError
from src.core.services.task_service import (
    create_task   as svc_create,
    get_task      as svc_get,
    list_tasks    as svc_list,
    list_tasks_with_count as svc_list_with_count,
    update_task   as svc_update,
    delete_task   as svc_delete,
)
from src.api.dependencies import get_db

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post(
    "/",
    response_model=TaskOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Task",
)
def create_task_endpoint(
    payload: TaskCreate,
    db: Session = Depends(get_db),
) -> TaskOut:
    """
    Create a new task.

    - **title**: the title of the task
    - **description**: optional longer description
    - **priority**: 1 (High), 2 (Medium), or 3 (Low)
    - **due_date**: ISO 8601 datetime string

    Returns the created Task.
    """
    return svc_create(db, payload)


@router.get(
    "/",
    response_model=List[TaskOut],
    summary="List Tasks with filters & pagination",
)
def list_tasks_endpoint(
    skip: int = Query(
        0, ge=0, description="Number of tasks to skip (offset)"
    ),
    limit: int = Query(
        DEFAULT_PAGE_LIMIT,
        ge=1,
        le=MAX_PAGE_SIZE,
        description=f"Maximum tasks to return (capped at {MAX_PAGE_SIZE})",
    ),
    completed: Optional[bool] = Query(
        None, description="Filter by completion status"
    ),
    priority: Optional[int] = Query(
        None,
        ge=1,
        le=3,
        description="Filter by priority (1=High, 2=Medium, 3=Low)",
    ),
    db: Session = Depends(get_db),
) -> List[TaskOut]:
    """
    Retrieve tasks, optionally filtered by `completed` and/or `priority`,
    with `skip`/`limit` pagination.
    """
    return svc_list(
        db,
        skip=skip,
        limit=limit,
        completed=completed,
        priority=priority,
    )


@router.get(
    "/{task_id}",
    response_model=TaskOut,
    summary="Get a Task by ID",
)
def get_task_endpoint(
    task_id: UUID,
    db: Session = Depends(get_db),
) -> TaskOut:
    """
    Retrieve a single task by its ID.
    """
    try:
        return svc_get(db, task_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.put(
    "/{task_id}",
    response_model=TaskOut,
    summary="Update an existing Task",
)
def update_task_endpoint(
    task_id: UUID,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
) -> TaskOut:
    """
    Update one or more fields of a task:

    - Omitting a field leaves it unchanged  
    - Explicitly setting a field to `null` clears it
    """
    try:
        return svc_update(db, task_id, payload)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


class DeleteResponse(BaseModel):
    message: str


@router.delete(
    "/{task_id}",
    response_model=DeleteResponse,
    summary="Delete a Task",
)
def delete_task_endpoint(
    task_id: UUID,
    db: Session = Depends(get_db),
) -> DeleteResponse:
    """
    Delete a task by its ID.
    Returns a confirmation message.
    """
    try:
        svc_delete(db, task_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    return DeleteResponse(message="Task deleted successfully.")
