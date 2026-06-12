from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from db import get_session
from entities import Places as PlaceModel
from entities import Project as ProjectModel
from services.artic import place_exists

router = APIRouter(prefix="/projects")


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None


class ProjectPlaceCreate(BaseModel):
    external_place_id: str


class ProjectCreate(ProjectBase):
    places: Optional[List[ProjectPlaceCreate]] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None


class ProjectGet(ProjectBase):
    id: int
    completed: bool

    class Config:
        from_attributes = True


def sync_project_completed(session, project_id: int):
    project = session.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if not project:
        return

    places = (
        session.query(PlaceModel)
        .filter(PlaceModel.project_id == project_id)
        .all()
    )
    project.completed = bool(places) and all(place.visited for place in places)


@router.post("", response_model=ProjectGet)
def create_project(data: ProjectCreate, session=Depends(get_session)):
    places_data = data.places or []
    if len(places_data) > 10:
        raise HTTPException(status_code=400, detail="Project cannot contain more than 10 places")

    seen = set()
    for place_data in places_data:
        if place_data.external_place_id in seen:
            raise HTTPException(status_code=409, detail="Place already exists in this project")
        seen.add(place_data.external_place_id)
        if not place_exists(place_data.external_place_id):
            raise HTTPException(status_code=404, detail="Place not found in Art Institute API")

    project = ProjectModel(
        name=data.name,
        description=data.description,
        start_date=data.start_date,
    )
    session.add(project)
    session.flush()

    for place_data in places_data:
        session.add(
            PlaceModel(
                project_id=project.id,
                external_place_id=place_data.external_place_id,
                visited=False,
            )
        )

    session.flush()
    sync_project_completed(session, project.id)
    session.commit()
    session.refresh(project)
    return project


@router.get("", response_model=List[ProjectGet])
def list_projects(session=Depends(get_session)):
    return session.query(ProjectModel).all()


@router.get("/{project_id}", response_model=ProjectGet)
def get_project(project_id: int, session=Depends(get_session)):
    project = session.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=ProjectGet)
def update_project(project_id: int, data: ProjectUpdate, session=Depends(get_session)):
    project = session.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if data.name is not None:
        project.name = data.name
    if data.description is not None:
        project.description = data.description
    if data.start_date is not None:
        project.start_date = data.start_date

    session.commit()
    session.refresh(project)
    return project


@router.delete("/{project_id}")
def delete_project(project_id: int, session=Depends(get_session)):
    project = session.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    visited_place = (
        session.query(PlaceModel)
        .filter(PlaceModel.project_id == project_id)
        .filter(PlaceModel.visited.is_(True))
        .first()
    )
    if visited_place:
        raise HTTPException(status_code=409, detail="Project cannot be deleted because it has visited places")

    session.delete(project)
    session.commit()
    return {"message": "Project deleted"}
