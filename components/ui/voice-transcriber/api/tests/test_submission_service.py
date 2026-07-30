"""Unit tests for durable creation followed by queue publication."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID

import pytest
from app.domain.models import AudioSourceType, NewTranscriptionJob, TranscriptionOptions
from app.services.transcription import TranscriptionSubmissionService


class MemoryRepository:
    def __init__(self) -> None:
        self.created: list[NewTranscriptionJob] = []
        self.queued: list[UUID] = []
        self.failed: list[UUID] = []

    async def create(self, job: NewTranscriptionJob) -> None:
        self.created.append(job)

    async def mark_queued(self, job_id: UUID) -> None:
        self.queued.append(job_id)

    async def mark_queue_failed(self, job_id: UUID, reason: str) -> None:
        self.failed.append(job_id)


class MemoryQueue:
    def __init__(self, *, fail: bool = False) -> None:
        self.jobs: list[NewTranscriptionJob] = []
        self.fail = fail

    async def enqueue(self, job: NewTranscriptionJob) -> None:
        if self.fail:
            raise RuntimeError("Redis unavailable")
        self.jobs.append(job)


@pytest.mark.asyncio
async def test_persists_and_marks_queued_before_publication(tmp_path: Path) -> None:
    repository = MemoryRepository()
    queue = MemoryQueue()
    service = TranscriptionSubmissionService(repository, queue)

    response = await service.submit(
        tmp_path / "audio.wav",
        source_type=AudioSourceType.UPLOAD,
        options=TranscriptionOptions(language="uk"),
    )

    assert repository.created[0] is queue.jobs[0]
    assert repository.queued == [response.task_id]
    assert response.status == "queued"


@pytest.mark.asyncio
async def test_records_queue_failure(tmp_path: Path) -> None:
    repository = MemoryRepository()
    service = TranscriptionSubmissionService(repository, MemoryQueue(fail=True))

    with pytest.raises(RuntimeError, match="Redis unavailable"):
        await service.submit(
            tmp_path / "audio.wav",
            source_type=AudioSourceType.UPLOAD,
            options=TranscriptionOptions(),
        )

    assert repository.failed == [repository.created[0].id]
