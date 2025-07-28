from src.core.database import Base, engine
from src.core.models.task import Task

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database created successfully!")

if __name__ == "__main__":
    init_db()
