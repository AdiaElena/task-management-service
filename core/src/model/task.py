from sqlalchemy import Column, Integer, String, Boolean, DateTime
from core.src.database import Base
import datetime

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    priority = Column(Integer, default=2)
    due_date = Column(DateTime)
    completed = Column(Boolean, default=False)
