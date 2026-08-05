"""Execute a queued transcription and persist every terminal state."""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any
from uuid import UUID

from a_man_database import TranscriptionJob, TranscriptionJobEvent, sqlalchemy_url
from a_man_whisper import PythonWhisperEngine, TranscriptionResult
from celery import Task
from redis import Redis
from sqlalchemy import create_engine, update
from sqlalchemy.orm import Session, sessionmaker

from worker_app.celery_app import app

TASK_KEY_PREFIX = "voice-transcriber:task:"


@lru_cache(maxsize=4)
def _get_engine(model: str) -> PythonWhisperEngine:
    return PythonWhisperEngine(
        model,
        device=os.getenv("TRANSCRIBER_DEVICE") or None,
        download_root=os.getenv("TRANSCRIBER_MODEL_CACHE") or None,
    )


@lru_cache(maxsize=1)
def _get_redis() -> Redis:
    return Redis.from_url(os.environ["TRANSCRIBER_REDIS_URL"])


@lru_cache(maxsize=1)
def _get_sessions() -> sessionmaker[Session]:
    engine = create_engine(
        sqlalchemy_url(os.environ["TRANSCRIBER_DATABASE_URL"]),
        pool_pre_ping=True,
    )
    return sessionmaker(engine, expire_on_commit=False)


@app.task(bind=True, name="voice_transcriber.transcribe")
def transcribe(
    task: Task,
    *,
    job_id: str,
    audio_path: str,
    language: str | None,
    include_segments: bool,
    model: str | None,
) -> dict[str, Any]:
    """Run Whisper and synchronize PostgreSQL journal and Redis state."""

    selected_model = model or os.getenv("TRANSCRIBER_MODEL") or "small"
    worker_id = getattr(task.request, "hostname", None)
    _set_processing(job_id, worker_id=worker_id, model=selected_model)
    _cache_state(job_id, "processing")

    try:
        result = _get_engine(selected_model).transcribe(
            Path(audio_path),
            language=language,
            include_segments=include_segments,
        )
        normalized = _serialize_result(result)
        _set_completed(job_id, result=normalized)
        _cache_state(job_id, "completed", result=normalized)
        return normalized
    except Exception as error:
        normalized_error = {
            "type": type(error).__name__,
            "message": str(error),
        }
        _set_failed(job_id, error=normalized_error)
        _cache_state(job_id, "failed", error=normalized_error)
        raise


def _set_processing(job_id: str, *, worker_id: str | None, model: str) -> None:
    _transition(
        job_id,
        "processing",
        values={
            "started_at": datetime.now(UTC),
            "worker_id": worker_id,
            "requested_model": model,
            "engine_name": "python-whisper",
            "attempt_number": TranscriptionJob.attempt_number + 1,
        },
        payload={"worker_id": worker_id, "model": model},
    )


def _set_completed(job_id: str, *, result: dict[str, Any]) -> None:
    _transition(
        job_id,
        "completed",
        values={
            "completed_at": datetime.now(UTC),
            "transcript_text": result["text"],
            "detected_language": result["language"],
            "result": result,
        },
        payload={},
    )


def _set_failed(job_id: str, *, error: dict[str, str]) -> None:
    _transition(
        job_id,
        "failed",
        values={"failed_at": datetime.now(UTC), "error": error},
        payload={"error_type": error["type"]},
    )


def _transition(
    job_id: str,
    status: str,
    *,
    values: dict[str, object],
    payload: dict[str, object],
) -> None:
    occurred_at = datetime.now(UTC)
    typed_job_id = UUID(job_id)
    with _get_sessions().begin() as session:
        session.execute(
            update(TranscriptionJob)
            .where(TranscriptionJob.id == typed_job_id)
            .values(status=status, updated_at=occurred_at, **values)
        )
        session.add(
            TranscriptionJobEvent(
                job_id=typed_job_id,
                status=status,
                occurred_at=occurred_at,
                payload=payload,
            )
        )


def _cache_state(
    job_id: str,
    status: str,
    *,
    result: dict[str, Any] | None = None,
    error: dict[str, str] | None = None,
) -> None:
    ttl = int(os.getenv("TRANSCRIBER_REDIS_STATE_TTL_SECONDS", "86400"))
    value: dict[str, object] = {"task_id": job_id, "status": status}
    if result is not None:
        value["result"] = result
    if error is not None:
        value["error"] = error
    _get_redis().set(
        f"{TASK_KEY_PREFIX}{job_id}",
        json.dumps(value),
        ex=ttl,
    )


def _serialize_result(result: TranscriptionResult) -> dict[str, Any]:
    return {
        "text": result.text,
        "language": result.language,
        "model": result.model,
        "segments": [
            {
                "start": segment.start,
                "end": segment.end,
                "text": segment.text,
            }
            for segment in result.segments
        ],
    }
