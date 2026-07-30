# Voice Transcriber

The Voice Transcriber is a UI subcomponent that converts audio into text. It can
be embedded as a widget in A-Man or run independently through its demo frontend.

The first runtime slice implements asynchronous file submission through FastAPI,
durable PostgreSQL job journaling, Redis/Celery queue publication, and a Python
Whisper Celery task. Deployment configuration and job-query APIs remain to be
implemented.

## Structure

| Path | Responsibility |
|---|---|
| `widget/` | Reusable frontend widget |
| `demo/` | Standalone test frontend |
| `api/` | FastAPI backend |
| `task-worker/` | Celery task orchestration |
| `transcription-engines/` | Replaceable speech-to-text implementations |
| `contracts/` | Stable API and engine-boundary definitions |
| `database/` | PostgreSQL migrations and database assets |
| `deploy/` | Docker and deployment assets |
| `tests/` | Stack-level integration and end-to-end tests |
| `docs/` | Module-specific design and usage documentation |

## HTTP submission API

Both endpoints return HTTP `202` with `task_id`, `status`, `audio_path`, and
`created_at`:

- `POST /v1/transcriptions/path` accepts JSON containing an absolute path visible
  to both the API and worker.
- `POST /v1/transcriptions/upload` accepts multipart field `audio`; the API saves
  it under `TRANSCRIBER_AUDIO_ROOT` before queueing it.

Required runtime settings are `TRANSCRIBER_DATABASE_URL` and
`TRANSCRIBER_REDIS_URL`. The API and worker must share the configured audio
storage volume.

## Docker Compose

Copy the development settings and start the complete stack:

```bash
cd components/ui/voice-transcriber/deploy
cp .env.example .env
docker compose up --build
```

FastAPI is then available at `http://localhost:8000`, with interactive API
documentation at `http://localhost:8000/docs`.

Use `docker compose down` to stop containers while preserving data. Use
`docker compose down --volumes` only when PostgreSQL, Redis, audio, and model
data should also be deleted.

The stack contains `api`, `worker`, `migrate`, `postgres`, and `redis`. The
one-shot migration service applies each SQL migration once and records it in
`schema_migrations`.

## Engine strategy

The first engine will use Python Whisper. It will later be replaceable by
whisper.cpp without changing the widget, public API, job model, or Celery
workflow.

The API and task worker must depend on a stable transcription contract, not on a
specific Whisper implementation.
