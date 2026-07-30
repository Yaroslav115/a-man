"""Celery application configuration."""

from __future__ import annotations

import os

from celery import Celery

redis_url = os.getenv("TRANSCRIBER_REDIS_URL", "redis://redis:6379/0")

app = Celery(
    "voice-transcriber",
    broker=redis_url,
    backend=redis_url,
    include=["worker_app.tasks.transcribe"],
)
app.conf.update(
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    task_track_started=True,
)
