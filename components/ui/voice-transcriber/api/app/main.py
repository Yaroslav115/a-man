"""Application factory and ASGI entry point."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from celery import Celery
from fastapi import FastAPI
from psycopg_pool import AsyncConnectionPool
from redis.asyncio import Redis

from app.routes.transcriptions import create_transcription_router
from app.services.postgres import PostgresJobRepository
from app.services.queue import RedisCeleryTaskQueue
from app.services.storage import LocalAudioStorage
from app.services.transcription import TranscriptionSubmissionService


@lru_cache(maxsize=1)
def get_pool() -> AsyncConnectionPool:
    return AsyncConnectionPool(
        os.environ["TRANSCRIBER_DATABASE_URL"],
        open=False,
    )


@lru_cache(maxsize=1)
def get_redis() -> Redis:
    return Redis.from_url(os.environ["TRANSCRIBER_REDIS_URL"])


@lru_cache(maxsize=1)
def get_celery_app() -> Celery:
    redis_url = os.environ["TRANSCRIBER_REDIS_URL"]
    return Celery("voice-transcriber", broker=redis_url, backend=redis_url)


def get_submission_service() -> TranscriptionSubmissionService:
    return TranscriptionSubmissionService(
        PostgresJobRepository(get_pool()),
        RedisCeleryTaskQueue(
            get_celery_app(),
            get_redis(),
            state_ttl_seconds=int(
                os.getenv("TRANSCRIBER_REDIS_STATE_TTL_SECONDS", "86400")
            ),
        ),
    )


@lru_cache(maxsize=1)
def get_audio_storage() -> LocalAudioStorage:
    return LocalAudioStorage(
        Path(os.getenv("TRANSCRIBER_AUDIO_ROOT", "/var/lib/a-man/audio"))
    )


def create_app() -> FastAPI:
    application = FastAPI(
        title="A-Man Voice Transcriber API",
        version="0.1.0",
    )
    application.include_router(
        create_transcription_router(get_submission_service, get_audio_storage)
    )

    @application.on_event("startup")
    async def open_database_pool() -> None:
        if get_submission_service not in application.dependency_overrides:
            await get_pool().open()

    @application.on_event("shutdown")
    async def close_connections() -> None:
        if get_submission_service not in application.dependency_overrides:
            await get_redis().aclose()
            await get_pool().close()

    return application


app = create_app()
