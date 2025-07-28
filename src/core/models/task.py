from sqlalchemy import Column, Integer, String, Boolean, DateTime
from src.core.database import Base

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True) # Optional
    priority = Column(Integer,  nullable=False) # Required (1=High, 2=Medium, 3=Low)
    due_date = Column(DateTime(timezone=True), nullable=False)
    completed = Column(Boolean, default=False) # Defaults to incomplete
