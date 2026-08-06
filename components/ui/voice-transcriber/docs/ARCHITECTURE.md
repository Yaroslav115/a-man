# Voice Transcriber Architecture

## Status

| Field | Current value |
|---|---|
| Status | Initial asynchronous submission and worker core implemented |
| Initial transcription engine | Python Whisper |
| Planned optimized engine | whisper.cpp |
| Public backend | FastAPI |
| Task processing | Celery with Redis |
| Persistent database | PostgreSQL |
| Local deployment | Docker Compose |

## Component flow

```text
Reusable Chat Widget or standalone demo host
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

## Client modes

The frontend is one reusable Chat Widget with conversation history, an editable
message composer, and voice input. It is delivered in two modes:

- The standalone demo is a complete page that hosts the production Chat Widget
  and adds configuration and diagnostic controls.
- Embedded mode distributes only the Chat Widget library; the containing
  application supplies configuration and receives widget events.

Recording, streaming, transcription state, and API code belong to the widget and
must not be duplicated in the demo host. Voice transcription fills the editable
composer and never submits a chat message without a user action.

## HTTP submission contract

File transcription uses HTTP rather than WebSocket. The path and upload routes
persist a job and its initial event in PostgreSQL, cache queued state in Redis,
publish a Celery message whose task ID equals the public job UUID, and return
HTTP `202`. Uploaded files are stored on a volume shared by the API and worker.

Clients poll `GET /v1/transcriptions/{task_id}` for durable file-job state and
results. These routes remain supported alongside live streaming for imported
files, fallback operation, repeatable tests, and recovery.

## WebSocket contract

WebSocket is the target real-time transport for chat, streamed agent responses,
and live microphone transcription. The Chat Widget owns one connection per
active conversation rather than opening a second socket for voice. Versioned
JSON envelopes carry control and text events; binary frames carry encoded audio.

Initial client event types:

- `chat.message.send`
- `chat.response.cancel`
- `voice.stream.start`
- `voice.stream.stop`
- `voice.stream.cancel`
- `connection.resume`
- `ping`

Initial server event types:

- `command.accepted`
- `chat.response.delta`
- `chat.response.completed`
- `voice.transcript.partial`
- `voice.transcript.final`
- `task.status.changed`
- `error`
- `pong`

Every command uses a UUID `message_id` for acknowledgement and deduplication.
Server events are ordered by a per-conversation sequence. Reconnection uses the
last received sequence; durable HTTP history and task lookup reconcile state if
the server cannot replay the complete gap.

After `voice.stream.start` is accepted, binary audio frames belong to the
negotiated stream until a final stop, cancellation, error, timeout, or
disconnect. Start metadata declares stream ID, MIME/codec, sample rate, and
channels. Implementations must define frame-size limits, backpressure, idle and
maximum-duration timeouts, authentication, origin validation, and per-user
concurrency limits before production use.

PostgreSQL is the durable source of truth. Redis contains transient queue data
and a TTL-bound current-state cache; losing Redis state must not erase the job
journal.

## Container topology

The development Compose stack runs separate API, Celery worker, migration,
PostgreSQL, and Redis containers. Named volumes preserve PostgreSQL data, Redis
AOF data, uploaded audio, and downloaded Whisper models. The API and worker
share the audio volume; only the worker mounts the model cache. Health checks
gate startup on PostgreSQL migration completion and Redis availability.

SQLAlchemy 2.x defines the shared persistence schema. The API uses async
sessions and the Celery worker uses synchronous sessions through Psycopg 3.
Alembic owns ordered schema revisions and runs as the one-shot migration
service. Revision `0001` safely adopts databases created by the former SQL
migration runner as its baseline.

The default worker image installs CPU-only PyTorch. GPU-specific images and
Compose overrides remain future work.

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

Alembic revision `0001_create_transcription_jobs` establishes the initial
`transcription_jobs` record and append-only `transcription_job_events` journal.
The worker records processing and terminal transitions in both PostgreSQL and
the Redis state cache.

Sensitive audio, transcript content, secrets, and credentials must not be copied
into audit events unnecessarily. Retention and deletion rules remain TBD.

## Delivery status

The HTTP file workflow, task worker, persistence, status lookup, and local
Compose backend are implemented. The Chat Widget, demo host, Controller
WebSocket endpoint, live-audio transport, partial transcription, reconnect
replay, and cancellation protocol described above are the accepted target
architecture and remain to be implemented.
