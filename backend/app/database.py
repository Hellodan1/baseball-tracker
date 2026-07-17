"""
SQLite engine + session dependency for FastAPI.
"""
import os
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy import event


DB_PATH = os.environ.get("DATABASE_URL", f"sqlite:///{os.getcwd()}/data/baseball.db")

# Ensure the data directory exists
db_dir = os.path.dirname(DB_PATH.replace("sqlite:///", ""))
os.makedirs(db_dir, exist_ok=True)

engine = create_engine(
    DB_PATH,
    connect_args={"check_same_thread": False} if DB_PATH.startswith("sqlite") else {},
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    dbapi_connection.execute("PRAGMA foreign_keys=ON")


def init_db() -> None:
    """Create all tables. Call on app startup."""
    import app.models  # noqa: F401
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency: yields a database session per request."""
    with Session(engine) as session:
        yield session