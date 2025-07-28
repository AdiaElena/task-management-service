import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tasks.db")

def _int_env(var: str, default: int) -> int:
    try:
        return int(os.getenv(var, str(default)))
    except (TypeError, ValueError):
        return default

# Pagination defaults
DEFAULT_PAGE_LIMIT = _int_env("DEFAULT_PAGE_LIMIT", 20)

# Maximum allowed page size to cap queries
MAX_PAGE_SIZE = _int_env("MAX_PAGE_SIZE", 50)