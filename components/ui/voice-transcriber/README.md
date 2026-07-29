# Voice Transcriber

The Voice Transcriber is a UI subcomponent that converts audio into text. It can
be embedded as a widget in A-Man or run independently through its demo frontend.

This directory currently contains structure and documentation only. No runtime
code or deployment configuration has been implemented.

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

## Engine strategy

The first engine will use Python Whisper. It will later be replaceable by
whisper.cpp without changing the widget, public API, job model, or Celery
workflow.

The API and task worker must depend on a stable transcription contract, not on a
specific Whisper implementation.
