# syntax=docker/dockerfile:1

FROM python:3.12-slim AS api

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN groupadd --system transcriber \
    && useradd --system --gid transcriber --create-home transcriber
RUN mkdir -p /data/audio \
    && chown -R transcriber:transcriber /data

WORKDIR /opt/a-man

COPY requirements-api.txt .
RUN python -m pip install --no-cache-dir -r requirements-api.txt

COPY components/ui/voice-transcriber/api ./api

USER transcriber
WORKDIR /opt/a-man/api

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


FROM python:3.12-slim AS worker

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/opt/a-man/task-worker:/opt/a-man/python-whisper

RUN apt-get update \
    && apt-get install --yes --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system transcriber \
    && useradd --system --gid transcriber --create-home transcriber
RUN mkdir -p /data/audio /models \
    && chown -R transcriber:transcriber /data /models

WORKDIR /opt/a-man

COPY requirements-worker.txt .
RUN python -m pip install \
        --no-cache-dir \
        --index-url https://download.pytorch.org/whl/cpu \
        torch
RUN python -m pip install --no-cache-dir -r requirements-worker.txt \
    && python -m pip install --no-cache-dir --no-deps \
        "openai-whisper>=20240930"

COPY components/ui/voice-transcriber/task-worker ./task-worker
COPY components/ui/voice-transcriber/transcription-engines/python-whisper \
    ./python-whisper

USER transcriber

CMD ["celery", "-A", "worker_app.celery_app:app", "worker", "--loglevel=INFO"]


FROM postgres:16-alpine AS migrator

COPY components/ui/voice-transcriber/database/migrations /migrations
COPY components/ui/voice-transcriber/deploy/migrate.sh /usr/local/bin/migrate
RUN chmod 755 /usr/local/bin/migrate

ENTRYPOINT ["migrate"]
