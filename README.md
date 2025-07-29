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
     python init_db.py

5. **Start the server**
    uvicorn src.main:app --reload

## You can also spin up the service in Docker:
docker-compose up --build

## Useful Links
- Server live at: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- Redoc UI: http://localhost:8000/redoc

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

## Example API Requests

**Create a Task**
curl -X POST http://localhost:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "priority": 2,
    "due_date": "2025-08-01T12:00:00Z"
  }'

**List Tasks (with Pagination & Filters)**
curl "http://localhost:8000/tasks/?skip=0&limit=10&completed=false&priority=2"

**Retrieve a Single Task**
curl http://localhost:8000/tasks/3fa85f64-5717-4562-b3fc-2c963f66afa6

**Update a Task**
curl -X PUT http://localhost:8000/tasks/3fa85f64-5717-4562-b3fc-2c963f66afa6 \
  -H "Content-Type: application/json" \
  -d '{
    "completed": true,
    "description": null
  }'

**Delete a Task**
curl -X DELETE http://localhost:8000/tasks/3fa85f64-5717-4562-b3fc-2c963f66afa6

