# Voice Transcriber

The Voice Transcriber is a UI subcomponent that converts audio into text. It can
be embedded as a widget in A-Man or run independently through its demo frontend.

The first runtime slice implements asynchronous file submission through FastAPI,
durable PostgreSQL job journaling, Redis/Celery queue publication, and a Python
Whisper Celery task. Durable job-status and result lookup is available through
the API. A reusable Chat Widget, standalone demo host, and WebSocket-based live
audio/chat transport are the next planned runtime slice.

## Structure

| Path | Responsibility |
|---|---|
| `widget/` | Reusable frontend widget |
| `demo/` | Standalone test frontend |
| `api/` | FastAPI backend |
| `task-worker/` | Celery task orchestration |
| `transcription-engines/` | Replaceable speech-to-text implementations |
| `contracts/` | Stable API and engine-boundary definitions |
| `database/` | Shared SQLAlchemy mappings and Alembic migrations |
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

Use `GET /v1/transcriptions/{task_id}` to read the durable current status. A
completed response includes the normalized transcription in `result`; a failed
response includes normalized failure details in `error`.

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
one-shot migration service runs `alembic upgrade head`; Alembic records the
active revision in `alembic_version`. Both API and worker use the mappings in
`database/a_man_database` so schema types and constraints have one definition.

## Engine strategy

The first engine will use Python Whisper. It will later be replaceable by
whisper.cpp without changing the widget, public API, job model, or Celery
workflow.

The API and task worker must depend on a stable transcription contract, not on a
specific Whisper implementation.

## Planned Chat Widget and WebSocket mode

One reusable Chat Widget will provide message history, an editable composer, and
voice input. The standalone demo will host this same widget; embedded mode will
ship the widget without a separate application shell.

The widget will use one conversation WebSocket for chat commands, streamed agent
responses, live microphone control, and binary audio chunks. HTTP remains the
interface for file uploads, durable task lookup, history, health, and reconnect
recovery. The current repository implements the HTTP transcription workflow;
the WebSocket and frontend portions are documented architecture, not yet runtime
functionality.

## Demo frontend

The standalone demo currently contains a minimal React application shell. It
does not contain chat or voice widgets yet. Run its fast render test and
production build with:

```bash
cd components/ui/voice-transcriber/demo
npm install
npm test
npm run build
```

For local development, run `npm run dev` and open the URL printed by Vite.
