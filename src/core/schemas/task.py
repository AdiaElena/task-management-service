from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from uuid import UUID

# Base class for common fields
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: int = Field(..., ge=1, le=3, description="1=High, 2=Medium, 3=Low")  # Required, range 1-3
    due_date: datetime

    model_config = ConfigDict(
        extra="ignore",         # ignore any unexpected fields
    )

# Schema used for task creation
class TaskCreate(TaskBase):
    pass # all required fields defined above;

# Schema for updating tasks (all optional)
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=3)
    due_date: Optional[datetime] = None
    completed: Optional[bool] = None

    model_config = ConfigDict(extra="ignore")

# Output schema
class TaskOut(TaskBase):
    id: UUID
    completed: bool

    model_config = ConfigDict(
        from_attributes=True,
    )
