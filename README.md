# Travel Planner API

Small FastAPI + SQLAlchemy CRUD app for travel projects, places, and notes.

## What it does

- Create, list, update, and delete travel projects
- Add places from the Art Institute of Chicago API
- Attach notes to places
- Mark places as visited
- Mark projects as completed when all places are visited

## Tech Stack

- FastAPI
- SQLAlchemy
- SQLite

## Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the app:

```bash
uvicorn main:app --reload
```

If you run it from the repository root, use:

```bash
uvicorn test_task.main:app --reload
```

## API Docs

FastAPI docs are available at:

- `http://127.0.0.1:8000/docs`

## Postman

Import this file into Postman:

- `test_task/postman_collection.json`

It contains requests for:

- projects
- places
- notes

## Notes

- SQLite database file: `travel_guide.db`
- Places are validated against the Art Institute of Chicago API before being added
- A project cannot be deleted if it has any visited places
