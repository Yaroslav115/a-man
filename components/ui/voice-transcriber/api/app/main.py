"""Application factory and ASGI entry point."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import cast

from a_man_database import sqlalchemy_url
from celery import Celery
from fastapi import FastAPI
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.routes.config import create_config_router
from app.routes.transcriptions import create_transcription_router
from app.services.config import AudioRecordConfigStore
from app.services.postgres import PostgresJobRepository
from app.services.queue import RedisCeleryTaskQueue
from app.services.storage import LocalAudioStorage
from app.services.transcription import TranscriptionSubmissionService


@lru_cache(maxsize=1)
def get_engine() -> AsyncEngine:
    return create_async_engine(
        sqlalchemy_url(os.environ["TRANSCRIBER_DATABASE_URL"]),
        pool_pre_ping=True,
    )


@lru_cache(maxsize=1)
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(get_engine(), expire_on_commit=False)


@lru_cache(maxsize=1)
def get_redis() -> Redis:
    return cast(Redis, Redis.from_url(os.environ["TRANSCRIBER_REDIS_URL"]))


@lru_cache(maxsize=1)
def get_celery_app() -> Celery:
    redis_url = os.environ["TRANSCRIBER_REDIS_URL"]
    return Celery("voice-transcriber", broker=redis_url, backend=redis_url)


def get_submission_service() -> TranscriptionSubmissionService:
    return TranscriptionSubmissionService(
        get_job_repository(),
        RedisCeleryTaskQueue(
            get_celery_app(),
            get_redis(),
            state_ttl_seconds=int(
                os.getenv("TRANSCRIBER_REDIS_STATE_TTL_SECONDS", "86400")
            ),
        ),
    )


def get_job_repository() -> PostgresJobRepository:
    return PostgresJobRepository(get_session_factory())


@lru_cache(maxsize=1)
def get_audio_storage() -> LocalAudioStorage:
    return LocalAudioStorage(
        Path(os.getenv("TRANSCRIBER_AUDIO_ROOT", "/var/lib/a-man/audio"))
    )


@lru_cache(maxsize=1)
def get_audio_record_config_store() -> AudioRecordConfigStore:
    return AudioRecordConfigStore(
        Path(
            os.getenv(
                "TRANSCRIBER_CONFIG_PATH",
                "/var/lib/a-man/config/audio-record.json",
            )
        )
    )


def create_app() -> FastAPI:
    application = FastAPI(
        title="A-Man Voice Transcriber API",
        version="0.1.0",
    )
    application.include_router(
        create_transcription_router(
            get_submission_service,
            get_audio_storage,
            get_job_repository,
        )
    )
    application.include_router(create_config_router(get_audio_record_config_store))

    @application.on_event("shutdown")
    async def close_connections() -> None:
        if get_redis.cache_info().currsize:
            await get_redis().aclose()
            get_redis.cache_clear()

        if get_engine.cache_info().currsize:
            await get_engine().dispose()
            get_engine.cache_clear()
            get_session_factory.cache_clear()

    return application


app = create_app()
