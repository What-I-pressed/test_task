from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from db import get_session
from entities import Project as ProjectModel

router = APIRouter(prefix="/projects")


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None


class ProjectGet(ProjectBase):
    id: int

    class Config:
        from_attributes = True


@router.post("", response_model=ProjectGet)
def create_project(data: ProjectCreate, session=Depends(get_session)):
    project = ProjectModel(
        name=data.name,
        description=data.description,
        start_date=data.start_date,
    )
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


@router.get("")
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

    session.delete(project)
    session.commit()
    return {"message": "Project deleted"}
