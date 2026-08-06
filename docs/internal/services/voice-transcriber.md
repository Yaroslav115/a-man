# Service: voice-transcriber

## Record

| Field | Current value |
|---|---|
| Owner | TBD |
| Status | asynchronous file core implemented; Chat Widget and WebSocket streaming planned |
| Version | 0.1 |
| Environment | local development |
| Repository/path | `components/ui/voice-transcriber/` |
| Runtime | Docker Compose stack |
| Deployment target | TBD |
| Last verified | 2026-08-06 |

## Purpose

Provide reusable audio-to-text transcription for the A-Man user interface while
remaining usable as a standalone module.

## Planned parts

| Part | Technology | Current state |
|---|---|---|
| Reusable widget | Web frontend, TBD | Directory created |
| Standalone demo | React, TypeScript, Vite | Base application and render smoke test implemented |
| Public backend | FastAPI | Submission and durable job-status routes implemented |
| Task orchestration | Celery | Transcription task implemented |
| Queue/broker | Redis | Queue and TTL state cache integrated |
| Persistent data | PostgreSQL with SQLAlchemy 2.x | Initial Alembic job/event revision implemented |
| Initial transcription engine | Python Whisper | Worker adapter implemented |
| Optimized transcription engine | whisper.cpp | Reserved directory created |

## Architecture constraint

All callers and orchestration code must depend on a stable transcription-engine
contract. Engine-specific behavior must be isolated so Python Whisper can be
replaced by whisper.cpp without changing the public API or task workflow.

## Interfaces and configuration

- `POST /v1/transcriptions/path` queues a shared server-local path.
- `POST /v1/transcriptions/upload` persists and queues an uploaded file.
- `GET /v1/transcriptions/{task_id}` returns durable status and outcome data.
- The planned Chat Widget uses one Controller WebSocket for conversation events,
  streamed responses, and live microphone audio.
- The planned standalone demo hosts that same widget rather than maintaining a
  separate frontend implementation.
- `TRANSCRIBER_DATABASE_URL` configures PostgreSQL.
- `TRANSCRIBER_REDIS_URL` configures the Celery broker/result backend and state.
- `TRANSCRIBER_AUDIO_ROOT` configures shared uploaded-audio storage.
- `TRANSCRIBER_MODEL`, `TRANSCRIBER_DEVICE`, and
  `TRANSCRIBER_MODEL_CACHE` configure the initial Whisper engine.
- `TRANSCRIBER_REDIS_STATE_TTL_SECONDS` controls transient state retention.

PostgreSQL is authoritative; Redis state is a disposable acceleration layer.
The API and worker share SQLAlchemy mappings, while Alembic owns schema
evolution and is executed by the Compose `migrate` service.

## Local operation

The Compose definition is
`components/ui/voice-transcriber/deploy/compose.yaml`. It builds distinct API,
worker, and migration targets and runs official PostgreSQL 16 Alpine and Redis 7
Alpine images. Development values are documented in `.env.example`; real
credentials belong only in the ignored `.env` file.

## Runtime task journaling

Every Whisper transcription task must be stored in PostgreSQL with an append-only
history of its lifecycle events. At minimum, the journal must make creation,
queuing, processing, retries, completion, failure, and cancellation traceable.
The engine name and version must be recorded so results remain attributable after
the transition from Python Whisper to whisper.cpp.

The exact schema, retention period, and privacy policy are TBD.

## Planned real-time interface

The Controller exposes the planned conversation socket at
`/v1/conversations/{conversation_id}/stream` and routes voice frames to this
service. The WebSocket protocol uses versioned JSON command/event envelopes and
binary audio frames. Commands require unique IDs; server events require ordered
conversation sequences for acknowledgement, deduplication, reconnect, and
recovery. PostgreSQL remains authoritative, and HTTP history/task endpoints
reconcile a client after delivery gaps.

The WebSocket endpoint, chat persistence/controller integration, live-stream
engine adapter, authentication, origin policy, replay window, frame limits,
backpressure, and timeouts are not implemented yet.

## Security

Audio and transcripts may contain sensitive information. Retention, access,
deletion, transport encryption, and audit requirements must be defined before
production use. Secrets must not be stored in this document.

## Change History

| Date | Change | Author/agent |
|---|---|---|
| 2026-07-30 | Added API, CPU Whisper worker, and migration images plus PostgreSQL/Redis Compose services and persistent volumes | Codex |
| 2026-07-30 | Implemented asynchronous API submission, job journal migration, Redis/Celery publication, and worker lifecycle updates | Codex |
| 2026-08-05 | Replaced direct Psycopg SQL and the custom migration ledger with shared SQLAlchemy mappings and Alembic revisions | Codex |
| 2026-07-27 | Created initial directory structure and engine-replacement boundary | Codex |
| 2026-08-06 | Adopted a reusable Chat Widget and WebSocket target architecture for chat streaming and live voice | Codex |
| 2026-08-06 | Added the minimal React standalone-demo shell and fast render smoke test | Codex |
