"""Redis/Celery implementation of transcription task submission."""

from __future__ import annotations

import json

from celery import Celery
from redis.asyncio import Redis
from starlette.concurrency import run_in_threadpool

from app.domain.models import JobStatus, NewTranscriptionJob

TASK_NAME = "voice_transcriber.transcribe"
REDIS_TASK_PREFIX = "voice-transcriber:task:"


class RedisCeleryTaskQueue:
    """Cache initial state in Redis and publish work through Celery."""

    def __init__(
        self,
        celery_app: Celery,
        redis: Redis,
        *,
        state_ttl_seconds: int,
    ) -> None:
        self._celery = celery_app
        self._redis = redis
        self._state_ttl_seconds = state_ttl_seconds

    async def enqueue(self, job: NewTranscriptionJob) -> None:
        key = f"{REDIS_TASK_PREFIX}{job.id}"
        state = json.dumps(
            {
                "task_id": str(job.id),
                "status": JobStatus.QUEUED,
                "audio_path": str(job.audio_path),
                "created_at": job.created_at.isoformat(),
            }
        )
        await self._redis.set(key, state, ex=self._state_ttl_seconds)
        try:
            await run_in_threadpool(
                self._celery.send_task,
                TASK_NAME,
                task_id=str(job.id),
                kwargs={
                    "job_id": str(job.id),
                    "audio_path": str(job.audio_path),
                    "language": job.language,
                    "include_segments": job.include_segments,
                    "model": job.model,
                },
            )
        except BaseException:
            await self._redis.delete(key)
            raise
