# Voice Transcriber Architecture

## Status

| Field | Current value |
|---|---|
| Status | Structure only |
| Initial transcription engine | Python Whisper |
| Planned optimized engine | whisper.cpp |
| Public backend | FastAPI |
| Task processing | Celery with Redis |
| Persistent database | PostgreSQL |

## Component flow

```text
Widget or standalone demo
          ↓
       FastAPI
          ↓
  PostgreSQL job record
          ↓
    Redis/Celery queue
          ↓
   Celery task worker
          ↓
 Transcription-engine contract
          ↓
 Python Whisper initially
 whisper.cpp later
```

## Replacement boundary

Every transcription engine must accept the same logical request and return the
same logical result. The contract will define at least:

- Audio input reference or stream
- Language selection or automatic detection
- Model/profile selection
- Transcription options
- Text result
- Detected language
- Segments and timestamps when requested
- Processing metadata
- Normalized errors
- Cancellation and timeout behavior

Engine-specific configuration must stay inside its engine implementation.
FastAPI, Celery tasks, database records, and frontend clients must not import or
depend on Python Whisper or whisper.cpp details.

## Engine directories

- `transcription-engines/python-whisper/` — initial implementation.
- `transcription-engines/whisper-cpp/` — later optimized implementation.

Only one engine needs to be active initially. Engine selection will eventually be
controlled by configuration and dependency injection.

## Transcription task journal

Every transcription request must have a persistent database record and an
append-only event history. This runtime journal is separate from the project's
development journal.

The task record should eventually include:

- Unique task identifier
- Creation, queue, start, completion, failure, and cancellation timestamps
- Current status and complete status-transition history
- Selected engine and engine version
- Selected model and safe transcription parameters
- Input metadata without exposing sensitive audio content
- Attempt number, retry history, worker identifier, and processing duration
- Result reference and normalized error details
- Requesting user/session reference, subject to privacy requirements
- Correlation identifier for logs and traces

Sensitive audio, transcript content, secrets, and credentials must not be copied
into audit events unnecessarily. Retention and deletion rules remain TBD.
