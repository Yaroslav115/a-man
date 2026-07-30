"""Asynchronous transcription job submission."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol
from uuid import UUID, uuid4

from app.domain.models import (
    AudioSourceType,
    JobStatus,
    NewTranscriptionJob,
    TranscriptionJobAccepted,
    TranscriptionOptions,
    utc_now,
)


class JobRepository(Protocol):
    """Durable transcription job journal."""

    async def create(self, job: NewTranscriptionJob) -> None:
        """Persist a job and its created event atomically."""

    async def mark_queued(self, job_id: UUID) -> None:
        """Record successful queue submission."""

    async def mark_queue_failed(self, job_id: UUID, reason: str) -> None:
        """Record queue submission failure."""


class TaskQueue(Protocol):
    """Transient task queue and state cache."""

    async def enqueue(self, job: NewTranscriptionJob) -> None:
        """Publish a job using its public UUID as the queue task ID."""


class TranscriptionSubmissionService:
    """Coordinate durable job creation with transient queue publication."""

    def __init__(self, repository: JobRepository, task_queue: TaskQueue) -> None:
        self._repository = repository
        self._task_queue = task_queue

    async def submit(
        self,
        audio_path: Path,
        *,
        source_type: AudioSourceType,
        options: TranscriptionOptions,
        original_filename: str | None = None,
        content_type: str | None = None,
        size_bytes: int | None = None,
    ) -> TranscriptionJobAccepted:
        job = NewTranscriptionJob(
            id=uuid4(),
            audio_path=audio_path,
            source_type=source_type,
            original_filename=original_filename,
            content_type=content_type,
            size_bytes=size_bytes,
            language=options.language,
            include_segments=options.include_segments,
            model=options.model,
            created_at=utc_now(),
        )
        await self._repository.create(job)
        try:
            await self._repository.mark_queued(job.id)
            await self._task_queue.enqueue(job)
        except Exception as error:
            await self._repository.mark_queue_failed(job.id, type(error).__name__)
            raise

        return TranscriptionJobAccepted(
            task_id=job.id,
            audio_path=job.audio_path,
            created_at=job.created_at,
            status=JobStatus.QUEUED,
        )
