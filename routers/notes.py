from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from db import get_session
from entities import Note as NoteModel
from entities import Places as PlaceModel
from routers.auth import require_auth

router = APIRouter(prefix="/projects/{project_id}/places/{place_id}/notes")


class NoteBase(BaseModel):
    content: str


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    content: Optional[str] = None


class NoteGet(NoteBase):
    id: int
    project_place_id: int

    class Config:
        from_attributes = True


def get_place(project_id: int, place_id: int, session):
    place = (
        session.query(PlaceModel)
        .filter(PlaceModel.project_id == project_id)
        .filter(PlaceModel.id == place_id)
        .first()
    )
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    return place


def get_note(project_id: int, place_id: int, note_id: int, session):
    note = (
        session.query(NoteModel)
        .join(PlaceModel, NoteModel.project_place_id == PlaceModel.id)
        .filter(PlaceModel.project_id == project_id)
        .filter(PlaceModel.id == place_id)
        .filter(NoteModel.id == note_id)
        .first()
    )
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.post("", response_model=NoteGet)
def create_note(project_id: int, place_id: int, data: NoteCreate, session=Depends(get_session), current_user=Depends(require_auth)):
    place = get_place(project_id, place_id, session)
    note = NoteModel(project_place_id=place.id, content=data.content)
    session.add(note)
    session.commit()
    session.refresh(note)
    return note


@router.get("", response_model=List[NoteGet])
def list_notes(project_id: int, place_id: int, session=Depends(get_session)):
    get_place(project_id, place_id, session)
    return (
        session.query(NoteModel)
        .filter(NoteModel.project_place_id == place_id)
        .all()
    )


@router.get("/{note_id}", response_model=NoteGet)
def get_single_note(project_id: int, place_id: int, note_id: int, session=Depends(get_session)):
    return get_note(project_id, place_id, note_id, session)


@router.patch("/{note_id}", response_model=NoteGet)
def update_note(
    project_id: int,
    place_id: int,
    note_id: int,
    data: NoteUpdate,
    session=Depends(get_session),
    current_user=Depends(require_auth),
):
    note = get_note(project_id, place_id, note_id, session)

    if data.content is not None:
        note.content = data.content

    session.commit()
    session.refresh(note)
    return note


@router.delete("/{note_id}")
def delete_note(project_id: int, place_id: int, note_id: int, session=Depends(get_session), current_user=Depends(require_auth)):
    note = get_note(project_id, place_id, note_id, session)
    session.delete(note)
    session.commit()
    return {"message": "Note deleted"}
