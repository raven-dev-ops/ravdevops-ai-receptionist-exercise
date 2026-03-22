from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
Base = declarative_base()

SQLITE_COLUMN_UPDATES = {
    "call_logs": {
        "request_id": "ALTER TABLE call_logs ADD COLUMN request_id VARCHAR(64) NOT NULL DEFAULT ''",
        "retrieval_diagnostics": (
            "ALTER TABLE call_logs ADD COLUMN retrieval_diagnostics JSON NOT NULL DEFAULT '[]'"
        ),
    },
    "appointments": {
        "request_id": "ALTER TABLE appointments ADD COLUMN request_id VARCHAR(64) NOT NULL DEFAULT ''",
        "normalized_time_local": (
            "ALTER TABLE appointments ADD COLUMN normalized_time_local VARCHAR(128) NOT NULL DEFAULT ''"
        ),
        "timezone": "ALTER TABLE appointments ADD COLUMN timezone VARCHAR(64) NOT NULL DEFAULT ''",
    },
}
SQLITE_INDEX_UPDATES = [
    "CREATE INDEX IF NOT EXISTS ix_call_logs_request_id ON call_logs (request_id)",
    "CREATE INDEX IF NOT EXISTS ix_appointments_request_id ON appointments (request_id)",
]


def _upgrade_sqlite_schema() -> None:
    if engine.dialect.name != "sqlite":
        return

    inspector = inspect(engine)
    with engine.begin() as connection:
        for table_name, updates in SQLITE_COLUMN_UPDATES.items():
            if not inspector.has_table(table_name):
                continue
            existing_columns = {column["name"] for column in inspector.get_columns(table_name)}
            for column_name, statement in updates.items():
                if column_name not in existing_columns:
                    connection.exec_driver_sql(statement)

        for statement in SQLITE_INDEX_UPDATES:
            connection.exec_driver_sql(statement)


def init_db() -> None:
    from app.models import db_models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _upgrade_sqlite_schema()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
