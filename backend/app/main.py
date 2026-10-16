from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text
from sqlalchemy.orm import Session

from .config import settings
from .db import get_db
from .routers import appointments, doctors

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Clinic appointment booking API: doctors, appointments and the front-desk workflow.",
)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_methods=["*"], allow_headers=["*"])
Instrumentator(excluded_handlers=["/metrics", "/health", "/ready"]).instrument(app).expose(
    app, endpoint="/metrics", include_in_schema=False
)

app.include_router(doctors.router)
app.include_router(appointments.router)


@app.get("/", tags=["ops"])
def root():
    return {"service": settings.app_name, "version": settings.app_version, "docs": "/docs"}


@app.get("/health", tags=["ops"])
@app.get("/api/health", tags=["ops"], include_in_schema=False)
def health():
    """Liveness: the process is up and serving HTTP."""
    return {"status": "UP"}


@app.get("/ready", tags=["ops"])
def ready(db: Session = Depends(get_db)):
    """Readiness: the database is reachable, so traffic can be served."""
    db.execute(text("SELECT 1"))
    return {"status": "READY"}
