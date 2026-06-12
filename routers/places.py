from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from db import get_session
from entities import Places as PlaceModel
from entities import Project as ProjectModel

router = APIRouter(prefix="/projects/{project_id}/places")


def place_exists(external_place_id: str) -> bool:
    url = f"https://api.artic.edu/api/v1/artworks/{external_place_id}?fields=id,title"
    try:
        with urlopen(url, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
            data = payload.get("data", {})
            return str(data.get("id")) == str(external_place_id)
    except (HTTPError, URLError, TimeoutError, ValueError, OSError):
        return False


class PlaceBase(BaseModel):
    external_place_id: str
    visited: bool = False


class PlaceCreate(PlaceBase):
    pass


class PlaceUpdate(BaseModel):
    visited: Optional[bool] = None


class PlaceGet(BaseModel):
    id: int
    project_id: int
    external_place_id: str
    visited: bool

    class Config:
        from_attributes = True


@router.post("", response_model=PlaceGet)
def add_place(project_id: int, data: PlaceCreate, session=Depends(get_session)):
    project = session.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not place_exists(data.external_place_id):
        raise HTTPException(status_code=404, detail="Place not found in Art Institute API")

    places_count = (
        session.query(PlaceModel)
        .filter(PlaceModel.project_id == project_id)
        .count()
    )
    if places_count >= 10:
        raise HTTPException(status_code=400, detail="Project cannot contain more than 10 places")

    already_added = (
        session.query(PlaceModel)
        .filter(PlaceModel.project_id == project_id)
        .filter(PlaceModel.external_place_id == data.external_place_id)
        .first()
    )
    if already_added:
        raise HTTPException(status_code=409, detail="Place already exists in this project")

    place = PlaceModel(
        project_id=project_id,
        external_place_id=data.external_place_id,
        visited=data.visited,
    )
    session.add(place)
    session.commit()
    session.refresh(place)
    return place


@router.get("")
def list_places(project_id: int, session=Depends(get_session)):
    return session.query(PlaceModel).filter(PlaceModel.project_id == project_id).all()


@router.get("/{place_id}", response_model=PlaceGet)
def get_place(project_id: int, place_id: int, session=Depends(get_session)):
    place = (
        session.query(PlaceModel)
        .filter(PlaceModel.project_id == project_id)
        .filter(PlaceModel.id == place_id)
        .first()
    )
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    return place


@router.patch("/{place_id}", response_model=PlaceGet)
def update_place(project_id: int, place_id: int, data: PlaceUpdate, session=Depends(get_session)):
    place = (
        session.query(PlaceModel)
        .filter(PlaceModel.project_id == project_id)
        .filter(PlaceModel.id == place_id)
        .first()
    )
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")

    if data.visited is not None:
        place.visited = data.visited

    session.commit()
    session.refresh(place)
    return place
