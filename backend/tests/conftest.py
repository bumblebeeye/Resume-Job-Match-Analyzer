from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.session import get_db
from app.main import app
from app.models.analysis import Analysis
from app.models.base import Base
from app.models.job_description import JobDescription
from app.models.resume import Resume


@compiles(JSONB, "sqlite")
def _compile_jsonb_sqlite(_type, _compiler, **_kw) -> str:
    return "JSON"


@pytest.fixture()
def client(tmp_path: Path) -> Generator[TestClient, None, None]:
    # Keep tests hermetic: isolated DB and isolated upload directory per test run.
    db_file = tmp_path / "test.sqlite3"
    engine = create_engine(
        f"sqlite+pysqlite:///{db_file}",
        connect_args={"check_same_thread": False},
    )
    testing_session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    Base.metadata.create_all(
        bind=engine,
        tables=[Resume.__table__, JobDescription.__table__, Analysis.__table__],
    )

    def override_get_db() -> Generator[Session, None, None]:
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    upload_dir = tmp_path / "resumes"
    upload_dir.mkdir(parents=True, exist_ok=True)

    original_storage_path = settings.resume_storage_path
    original_ai_enabled = settings.ai_suggestions_enabled
    original_ai_key = settings.gemini_api_key

    settings.resume_storage_path = str(upload_dir)
    settings.ai_suggestions_enabled = False
    settings.gemini_api_key = None

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    settings.resume_storage_path = original_storage_path
    settings.ai_suggestions_enabled = original_ai_enabled
    settings.gemini_api_key = original_ai_key

    Base.metadata.drop_all(bind=engine)
    engine.dispose()
