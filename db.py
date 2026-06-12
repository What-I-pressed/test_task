from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./travel_guide.db"

engine = create_engine(
    DATABASE_URL
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_schema():
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())

    if "places" in table_names:
        place_columns = {column["name"] for column in inspector.get_columns("places")}
        if "external_place_id" not in place_columns:
            with engine.begin() as connection:
                connection.execute(
                    text(
                        "ALTER TABLE places ADD COLUMN external_place_id VARCHAR NOT NULL DEFAULT ''"
                    )
                )

    if "projects" in table_names:
        project_columns = {column["name"] for column in inspector.get_columns("projects")}
        if "completed" not in project_columns:
            with engine.begin() as connection:
                connection.execute(
                    text(
                        "ALTER TABLE projects ADD COLUMN completed BOOLEAN NOT NULL DEFAULT 0"
                    )
                )
