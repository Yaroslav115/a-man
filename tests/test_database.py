"""Unit tests for shared database configuration and metadata."""

from a_man_database import Base, sqlalchemy_url


def test_normalizes_postgresql_url_for_psycopg_three() -> None:
    assert (
        sqlalchemy_url("postgresql://user:secret@database/app")
        == "postgresql+psycopg://user:secret@database/app"
    )


def test_shared_metadata_contains_job_journal() -> None:
    assert set(Base.metadata.tables) == {
        "transcription_jobs",
        "transcription_job_events",
    }
