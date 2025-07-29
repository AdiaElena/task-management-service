from typing import Generator
from sqlalchemy.orm import Session

from src.core.database import SessionLocal

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a SQLAlchemy Session and
    ensures it’s closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
