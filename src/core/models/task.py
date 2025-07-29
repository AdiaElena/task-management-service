import uuid
from sqlalchemy import CHAR, Column, String, Integer, Boolean, DateTime
from src.core.database import Base

class Task(Base):
    __tablename__ = "tasks"

    # Store UUID4 as a 36‑char string
    id = Column(
        CHAR(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
        unique=True,
    )

    title       = Column(String,  nullable=False, comment="Short task title")
    description = Column(String,  nullable=True,  comment="Optional longer description")
    priority    = Column(Integer, nullable=False, comment="1=High, 2=Medium, 3=Low")
    due_date    = Column(DateTime, nullable=False, comment="When the task is due")
    completed   = Column(Boolean, default=False, nullable=False, comment="Completion status")

    def __repr__(self) -> str:
        return f"<Task id={self.id} title={self.title!r}>"
