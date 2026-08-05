"""SQLAlchemy mappings shared by the API, worker, and Alembic."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for voice-transcriber persistence mappings."""


class TranscriptionJob(Base):
    """Durable state for one asynchronous transcription request."""

    __tablename__ = "transcription_jobs"
    __table_args__ = (
        CheckConstraint(
            "status IN ('created', 'queued', 'processing', 'completed', "
            "'failed', 'cancelled')",
            name="transcription_jobs_status_check",
        ),
        CheckConstraint(
            "source_type IN ('server_path', 'upload')",
            name="transcription_jobs_source_type_check",
        ),
        CheckConstraint(
            "size_bytes IS NULL OR size_bytes >= 0",
            name="transcription_jobs_size_bytes_check",
        ),
        CheckConstraint(
            "attempt_number >= 0",
            name="transcription_jobs_attempt_number_check",
        ),
        Index("transcription_jobs_status_created_at_idx", "status", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True)
    status: Mapped[str] = mapped_column(String(32))
    audio_path: Mapped[str] = mapped_column(Text)
    source_type: Mapped[str] = mapped_column(String(32))
    original_filename: Mapped[str | None] = mapped_column(Text)
    content_type: Mapped[str | None] = mapped_column(String(255))
    size_bytes: Mapped[int | None] = mapped_column(BigInteger)
    language: Mapped[str | None] = mapped_column(String(32))
    include_segments: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=text("true")
    )
    requested_model: Mapped[str | None] = mapped_column(String(100))
    engine_name: Mapped[str | None] = mapped_column(String(100))
    engine_version: Mapped[str | None] = mapped_column(String(100))
    attempt_number: Mapped[int] = mapped_column(
        Integer, default=0, server_default=text("0")
    )
    worker_id: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    transcript_text: Mapped[str | None] = mapped_column(Text)
    detected_language: Mapped[str | None] = mapped_column(String(32))
    result: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    error: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    events: Mapped[list[TranscriptionJobEvent]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )


class TranscriptionJobEvent(Base):
    """Append-only record of a transcription lifecycle transition."""

    __tablename__ = "transcription_job_events"
    __table_args__ = (
        Index(
            "transcription_job_events_job_id_occurred_at_idx",
            "job_id",
            "occurred_at",
            "id",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    job_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("transcription_jobs.id", ondelete="CASCADE"),
    )
    status: Mapped[str] = mapped_column(String(32))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, server_default=text("'{}'::jsonb")
    )
    job: Mapped[TranscriptionJob] = relationship(back_populates="events")
