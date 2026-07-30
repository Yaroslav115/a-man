"""Stable API and job models for asynchronous transcription."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class JobStatus(StrEnum):
    """Lifecycle states persisted for a transcription job."""

    CREATED = "created"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AudioSourceType(StrEnum):
    """How the API obtained the audio reference."""

    SERVER_PATH = "server_path"
    UPLOAD = "upload"


class TranscriptionOptions(BaseModel):
    """Engine-independent transcription options."""

    language: str | None = Field(default=None, min_length=2, max_length=32)
    include_segments: bool = True
    model: str | None = Field(default=None, min_length=1, max_length=100)


class PathTranscriptionRequest(TranscriptionOptions):
    """Request using a file already visible to the API and worker."""

    audio_path: Path

    @field_validator("audio_path")
    @classmethod
    def require_absolute_path(cls, value: Path) -> Path:
        if not value.is_absolute():
            raise ValueError("audio_path must be an absolute server-local path")
        return value


@dataclass(frozen=True)
class NewTranscriptionJob:
    """Complete data needed to persist and enqueue a new job."""

    id: UUID
    audio_path: Path
    source_type: AudioSourceType
    original_filename: str | None
    content_type: str | None
    size_bytes: int | None
    language: str | None
    include_segments: bool
    model: str | None
    created_at: datetime


class TranscriptionJobAccepted(BaseModel):
    """Response returned after a job is durably recorded and queued."""

    model_config = ConfigDict(from_attributes=True)

    task_id: UUID
    status: JobStatus = JobStatus.QUEUED
    audio_path: Path
    created_at: datetime


def utc_now() -> datetime:
    """Return a timezone-aware timestamp for persisted events."""

    return datetime.now(UTC)
