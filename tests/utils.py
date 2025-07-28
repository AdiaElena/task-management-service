from datetime import datetime, timezone

class DummyTaskModel:
    """
    In‑memory stand‑in for the Task ORM model,
    with Pydantic hooks so TaskOut.model_validate works.
    """
    def __init__(self, id: int, title: str, description: str,
                 priority: int, due_date, completed: bool = False):
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


def make_dummy_task(id: int = 123) -> DummyTaskModel:
    """Factory for a DummyTaskModel instance."""
    return DummyTaskModel(
        id=id,
        title="Dummy",
        description="Desc",
        priority=2,
        due_date=datetime.now(timezone.utc),
        completed=False,
    )
