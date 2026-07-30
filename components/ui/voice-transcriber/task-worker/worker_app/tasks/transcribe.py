"""Execute a queued transcription and persist every terminal state."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import psycopg
from a_man_whisper import PythonWhisperEngine, TranscriptionResult
from celery import Task
from psycopg.types.json import Jsonb
from redis import Redis

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

    selected_model = model or os.getenv("TRANSCRIBER_MODEL", "small")
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
        updates="""
            started_at = NOW(),
            worker_id = %(worker_id)s,
            requested_model = %(model)s,
            engine_name = 'python-whisper',
            attempt_number = attempt_number + 1
        """,
        parameters={"worker_id": worker_id, "model": model},
        payload={"worker_id": worker_id, "model": model},
    )


def _set_completed(job_id: str, *, result: dict[str, Any]) -> None:
    _transition(
        job_id,
        "completed",
        updates="""
            completed_at = NOW(),
            transcript_text = %(text)s,
            detected_language = %(language)s,
            result = %(result)s
        """,
        parameters={
            "text": result["text"],
            "language": result["language"],
            "result": Jsonb(result),
        },
        payload={},
    )


def _set_failed(job_id: str, *, error: dict[str, str]) -> None:
    _transition(
        job_id,
        "failed",
        updates="failed_at = NOW(), error = %(error)s",
        parameters={"error": Jsonb(error)},
        payload={"error_type": error["type"]},
    )


def _transition(
    job_id: str,
    status: str,
    *,
    updates: str,
    parameters: dict[str, object],
    payload: dict[str, object],
) -> None:
    database_url = os.environ["TRANSCRIBER_DATABASE_URL"]
    values = {"job_id": job_id, "status": status, **parameters}
    with psycopg.connect(database_url) as connection, connection.transaction():
        connection.execute(
            f"""
            UPDATE transcription_jobs
            SET status = %(status)s, updated_at = NOW(), {updates}
            WHERE id = %(job_id)s
            """,
            values,
        )
        connection.execute(
            """
            INSERT INTO transcription_job_events (
                job_id, status, occurred_at, payload
            ) VALUES (%(job_id)s, %(status)s, NOW(), %(payload)s)
            """,
            {
                "job_id": job_id,
                "status": status,
                "payload": Jsonb(payload),
            },
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
