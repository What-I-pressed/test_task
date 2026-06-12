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

## Authentication

Write endpoints require a bearer token that you get after logging in.

Use:

- `POST /auth/register` to create a user
- `POST /auth/login` to receive an access token
- the Postman collection stores the token in `access_token` after login

Example login response:

```json
{
  "access_token": "<token>",
  "token_type": "bearer"
}
```

Then send:

```text
Authorization: Bearer <token>
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
