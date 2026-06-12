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
    if "places" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("places")}
    if "external_place_id" not in columns:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE places ADD COLUMN external_place_id VARCHAR NOT NULL DEFAULT ''"
                )
            )
