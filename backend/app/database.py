"""
SQLite engine + session dependency for FastAPI.
"""
import os
from sqlmodel import SQLModel, Session, create_engine

DB_PATH = os.environ.get("DATABASE_URL", f"sqlite:///{os.getcwd()}/data/baseball.db")

engine = create_engine(
    DB_PATH,
    connect_args={"check_same_thread": False} if DB_PATH.startswith("sqlite") else {},
)


def init_db() -> None:
    """Create all tables. Call on app startup."""
    import app.models  # noqa: F401 — ensure models are imported
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency: yields a database session per request."""
    with Session(engine) as session:
        yield session
