"""SQLAlchemy implementation of the durable PostgreSQL job journal."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID

from a_man_database.models import TranscriptionJob, TranscriptionJobEvent
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.models import (
    JobStatus,
    NewTranscriptionJob,
    TranscriptionJobStatus,
    utc_now,
)


class PostgresJobRepository:
    """Persist jobs and append-only lifecycle events."""

    def __init__(self, sessions: async_sessionmaker[AsyncSession]) -> None:
        self._sessions = sessions

    async def create(self, job: NewTranscriptionJob) -> None:
        async with self._sessions.begin() as session:
            record = TranscriptionJob(
                id=job.id,
                status=JobStatus.CREATED,
                audio_path=str(job.audio_path),
                source_type=job.source_type,
                original_filename=job.original_filename,
                content_type=job.content_type,
                size_bytes=job.size_bytes,
                language=job.language,
                include_segments=job.include_segments,
                requested_model=job.model,
                attempt_number=0,
                created_at=job.created_at,
                updated_at=job.created_at,
            )
            record.events.append(
                TranscriptionJobEvent(
                    status=JobStatus.CREATED,
                    occurred_at=job.created_at,
                    payload={},
                )
            )
            session.add(record)

    async def get(self, job_id: UUID) -> TranscriptionJobStatus | None:
        """Return the durable current state for a job, if it exists."""

        async with self._sessions() as session:
            record = await session.scalar(
                select(TranscriptionJob).where(TranscriptionJob.id == job_id)
            )
        if record is None:
            return None
        return TranscriptionJobStatus(
            task_id=record.id,
            status=JobStatus(record.status),
            audio_path=Path(record.audio_path),
            created_at=record.created_at,
            updated_at=record.updated_at,
            started_at=record.started_at,
            completed_at=record.completed_at,
            failed_at=record.failed_at,
            cancelled_at=record.cancelled_at,
            result=record.result,
            error=record.error,
        )

    async def mark_queued(self, job_id: UUID) -> None:
        await self._transition(job_id, JobStatus.QUEUED, payload={})

    async def mark_queue_failed(self, job_id: UUID, reason: str) -> None:
        await self._transition(
            job_id,
            JobStatus.FAILED,
            payload={"stage": "queue_submission", "reason": reason},
        )

    async def _transition(
        self,
        job_id: UUID,
        status: JobStatus,
        *,
        payload: dict[str, str],
    ) -> None:
        now = utc_now()
        async with self._sessions.begin() as session:
            await session.execute(
                update(TranscriptionJob)
                .where(TranscriptionJob.id == job_id)
                .values(status=status, updated_at=now)
            )
            session.add(
                TranscriptionJobEvent(
                    job_id=job_id,
                    status=status,
                    occurred_at=now,
                    payload=payload,
                )
            )
