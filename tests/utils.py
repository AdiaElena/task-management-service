import uuid
from datetime import datetime, timezone
from uuid import UUID

class DummyTaskModel:
    """
    In‑memory stand‑in for the Task ORM model,
    with Pydantic hooks so TaskOut.model_validate works.
    """
    def __init__(
        self,
        id: UUID,
        title: str,
        description: str,
        priority: int,
        due_date: datetime,
        completed: bool = False,
    ):
        self.id = id
        self.title = title
        self.description = description
        self.priority = priority
        self.due_date = due_date
        self.completed = completed

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        return v

def make_dummy_task(id: UUID | None = None) -> DummyTaskModel:
    """
    Factory for a DummyTaskModel instance.
    By default emits a fresh UUID4 instance.
    """
    return DummyTaskModel(
        id = id or uuid.uuid4(),
        title = "Dummy",
        description = "Desc",
        priority = 2,
        due_date = datetime.now(timezone.utc),
        completed = False,
    )
