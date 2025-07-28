# Task Management Service

A CRUD REST API built with **FastAPI**, **SQLAlchemy**, and **SQLite**.  
This service lets you create, read, update, and delete tasks, each with a title, description, priority, due date, and completion status.

---

## Features

- **CRUD endpoints** for tasks  
- **Pagination** & **filtering** (by `completed` and `priority`)  
- **UUID**‑backed primary keys  
- **Layered architecture**:  
  - **Repository** (DB access)  
  - **Service** (business logic)  
  - **API** (HTTP layer)  
- **Auto‑generated OpenAPI** docs with FastAPI  
- **Comprehensive test suite** (unit tests at each layer + API tests)  

---

## Prerequisites

- **Python 3.10+**  
- **pip** (or **poetry**)  
- **Docker** & **docker‑compose**  

---

## Running Locally

1. **Create & activate a virtual environment**  
    python -m venv .venv
    source .venv/bin/activate    # macOS/Linux
    .venv\Scripts\activate       # Windows

2. **Install dependencies**  
    pip install -r requirements.txt

3. **Configure environment (.env file)**
    DATABASE_URL=sqlite:///./tasks.db
    DEFAULT_PAGE_LIMIT=20
    MAX_PAGE_SIZE=50
    ALLOWED_ORIGINS=*

4. **Initialise database (This creates tasks.db (SQLite) with the tasks table.)**
    python -m src.core.init_db

5. **Start the server**
    uvicorn src.main:app --reload

## Useful Links
- Server live at: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- Redoc UI: http://127.0.0.1:8000/redoc

## You can also spin up the service in Docker:
docker build -t task‑service .
docker run -d \
  --name task‑service \
  -p 8000:8000 \
  -e DATABASE_URL=sqlite:///./tasks.db \
  task‑service

## Testing

This project includes **unit tests** at three layers:

1. **Repository tests** (`tests/test_repositories/…`):  
   - Runs against a fresh SQLite in‑memory DB  
2. **Service tests** (`tests/test_services/…`):  
   - Mocks repository calls to validate business logic in isolation  
3. **API tests** (`tests/test_api/…`):  
   - Uses FastAPI’s `TestClient` and mocks the service layer  

**Run them all with**:  
pytest
