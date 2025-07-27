from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# Base class for common fields
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: int = Field(..., ge=1, le=3)  # Required, range 1-3
    due_date: datetime

# Schema used for task creation
class TaskCreate(TaskBase):
    pass # all required fields defined above;

# Schema for updating tasks (all optional)
class TaskUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    priority: Optional[int] = Field(None, ge=1, le=3)
    due_date: Optional[datetime]
    completed: Optional[bool]

# Output schema
class TaskOut(TaskBase):
    id: int
    completed: bool

    class Config:
        orm_mode = True
