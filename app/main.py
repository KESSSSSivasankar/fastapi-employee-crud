from __future__ import annotations

from fastapi import FastAPI

from .database import Base, engine
from .routers.employees import router as employees_router

app = FastAPI(title="Employee CRUD API", version="1.0.0")


@app.on_event("startup")
def _startup_create_tables() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(employees_router)
