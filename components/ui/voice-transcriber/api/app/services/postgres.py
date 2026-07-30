"""PostgreSQL implementation of the durable job journal."""

from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool

from app.domain.models import JobStatus, NewTranscriptionJob, utc_now


class PostgresJobRepository:
    """Persist jobs and append-only lifecycle events."""

    def __init__(self, pool: AsyncConnectionPool) -> None:
        self._pool = pool

    async def create(self, job: NewTranscriptionJob) -> None:
        async with (
            self._pool.connection() as connection,
            connection.transaction(),
        ):
            await connection.execute(
                """
                    INSERT INTO transcription_jobs (
                        id, status, audio_path, source_type, original_filename,
                        content_type, size_bytes, language, include_segments,
                        requested_model, created_at, updated_at
                    ) VALUES (
                        %(id)s, %(status)s, %(audio_path)s, %(source_type)s,
                        %(original_filename)s, %(content_type)s, %(size_bytes)s,
                        %(language)s, %(include_segments)s, %(requested_model)s,
                        %(created_at)s, %(created_at)s
                    )
                    """,
                {
                    "id": job.id,
                    "status": JobStatus.CREATED,
                    "audio_path": str(job.audio_path),
                    "source_type": job.source_type,
                    "original_filename": job.original_filename,
                    "content_type": job.content_type,
                    "size_bytes": job.size_bytes,
                    "language": job.language,
                    "include_segments": job.include_segments,
                    "requested_model": job.model,
                    "created_at": job.created_at,
                },
            )
            await self._append_event(connection, job.id, JobStatus.CREATED, payload={})

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
        async with (
            self._pool.connection() as connection,
            connection.transaction(),
        ):
            await connection.execute(
                """
                    UPDATE transcription_jobs
                    SET status = %(status)s, updated_at = %(now)s
                    WHERE id = %(id)s
                    """,
                {"id": job_id, "status": status, "now": now},
            )
            await self._append_event(
                connection, job_id, status, payload=payload, occurred_at=now
            )

    async def _append_event(
        self,
        connection: AsyncConnection[Any],
        job_id: UUID,
        status: JobStatus,
        *,
        payload: dict[str, str],
        occurred_at: object | None = None,
    ) -> None:
        await connection.execute(
            """
            INSERT INTO transcription_job_events (
                job_id, status, occurred_at, payload
            ) VALUES (%(job_id)s, %(status)s, %(occurred_at)s, %(payload)s)
            """,
            {
                "job_id": job_id,
                "status": status,
                "occurred_at": occurred_at or utc_now(),
                "payload": json.dumps(payload),
            },
        )
