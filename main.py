from fastapi import FastAPI

from db import engine, ensure_schema
from entities.base import Base
from entities.project import Project
from entities.places import Places
from entities.notes import Note
from routers.projects import router as projects_router
from routers.places import router as places_router
from routers.notes import router as notes_router

app = FastAPI()

app.include_router(projects_router)
app.include_router(places_router)
app.include_router(notes_router)

Base.metadata.create_all(bind=engine)
ensure_schema()
