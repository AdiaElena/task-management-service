from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.endpoints.tasks import router as tasks_router
from src.core.config import ALLOWED_ORIGINS

app = FastAPI(
    title="Task Management Service",
    description="A simple task CRUD API built with FastAPI",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Healthcheck
@app.get("/", tags=["root"])
async def read_root():
    """
    Health check and service info endpoint.
    """
    return {
        "status": "ok",
        "service": "Task Management Service",
        "version": app.version,
    }

# Mount all /tasks routes
app.include_router(tasks_router)

# CLI entrypoint
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
