from src.core.database import Base, engine

def init_db():
    """Create all database tables defined on Base."""
    with engine.begin() as conn:
        Base.metadata.create_all(bind=conn)
    print("✅ Database created successfully!")

if __name__ == "__main__":
    init_db()
