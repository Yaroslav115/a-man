# Task Journal

## 2026-08-06 — Add the base React demo frontend

- Status: completed.
- Request: Start the demo frontend without widgets and verify it with a small,
  fast test.
- Changes: Added a React and TypeScript application shell built by Vite, a
  minimal ready-state page, and one Vitest/Testing Library render smoke test.
- Scope: No chat, voice, microphone, WebSocket, or backend integration is
  included in this slice.
- Verification: The single test passes in under one second, the production build
  succeeds, and `npm audit` reports zero vulnerabilities after updating Vite and
  Vitest to patched releases.

## 2026-08-06 — Adopt WebSocket chat and live-voice architecture

- Status: architecture documented; implementation pending.
- Request: Make the reusable widget chat-capable, support a standalone demo and
  embedded mode, and adopt WebSocket transport.
- Decision: Build one reusable Chat Widget containing history, an editable
  composer, and voice input. The standalone demo hosts that same widget.
- Decision: Use one authenticated conversation WebSocket for chat commands,
  streamed agent responses, live-audio control, and binary microphone frames.
- Decision: Retain HTTP for recorded-file upload, durable task/result lookup,
  conversation history, health checks, and reconnect reconciliation.
- Contract direction: Versioned JSON envelopes, UUID command IDs, ordered server
  sequences, acknowledgements, deduplication, heartbeat, explicit terminal
  events, and reconnect/resume semantics.
- Constraint: A final voice transcript fills the editable composer and is never
  automatically submitted to an agent.
- Next: Define the versioned protocol schemas and Controller ownership, then
  implement the Chat Widget, demo host, WebSocket gateway, and live-stream
  transcriber adapter with integration tests.

## 2026-08-06 — Add durable transcription status lookup

- Status: completed; runtime verification requires Python 3.11 or 3.12.
- Request: Retrieve the status of the task ID returned by transcription
  submission.
- Changes: Added `GET /v1/transcriptions/{task_id}`, a PostgreSQL repository
  lookup, response models for lifecycle timestamps and terminal result/error
  data, and API coverage for success, unknown IDs, and invalid UUIDs.
- Verification: Ruff, mypy, and diff checks pass. The host's Python 3.10 cannot
  collect the Python 3.11+ test suite.

## 2026-08-05 — Adopt SQLAlchemy and Alembic

- Request: Prepare the growing project for a larger persistence model by
  replacing direct SQL and the custom migration runner.
- Result:
  - Added shared typed SQLAlchemy 2.x mappings for transcription jobs/events.
  - Converted the FastAPI repository to async SQLAlchemy sessions and Celery
    lifecycle updates to synchronous SQLAlchemy sessions.
  - Replaced numbered SQL files and `schema_migrations` with Alembic; baseline
    revision `0001` adopts an existing legacy schema without recreating it.
  - Preserved the one-shot Compose migration service and PostgreSQL/Psycopg 3.

## 2026-08-04 — Formalize Python 3.11+ support

- Status: completed
- Request: Formally move the project from its stale Python 3.10 tooling target to
  Python 3.11 or newer.
- Decision: Support Python 3.11 and 3.12, with Python 3.12 as the preferred local
  and container runtime. Defer Python 3.13 until the Whisper scientific dependency
  stack is explicitly verified there.
- Changes:
  - Added project metadata declaring `requires-python = ">=3.11,<3.13"`.
  - Updated Ruff and mypy to use Python 3.11 as the minimum language target.
  - Added `.python-version` selecting Python 3.12 for compatible version managers.
  - Documented the supported versions and local test setup.
- Verification: Ruff, formatting, mypy, and diff checks pass. The default test
  suite passes in a Python 3.12 container: 13 passed and one opt-in Whisper
  integration test was deselected.

## 2026-07-30 — Add the transcriber Docker Compose stack

- Status: completed
- Request: Create Docker images and Compose services for the backend, worker,
  Redis, and PostgreSQL.
- Changes:
  - Added separate FastAPI, CPU-only Whisper worker, and migration image targets.
  - Added PostgreSQL 16 and Redis 7 services with health checks and persistence.
  - Added shared audio storage and persistent Whisper model cache volumes.
  - Added a repeatable migration runner with a `schema_migrations` ledger.
  - Added a development environment template and operation documentation.
- Verification: Compose configuration resolves successfully; all project images
  build; PostgreSQL and Redis become healthy; migration `001` applies; Celery
  registers `voice_transcriber.transcribe`; and the API OpenAPI endpoint returns
  HTTP 200 with a healthy container state.
- Next: Add Compose-backed integration tests and a GPU worker override.

## 2026-07-30 — Implement asynchronous transcription submission core

- Status: completed
- Request: Create the FastAPI backend with one server-path route and one upload
  route, and process audio asynchronously through Redis, Celery, and PostgreSQL.
- Decision: Keep file submission on HTTP. At the time, WebSocket was reserved
  for future live microphone streaming and status delivery was undecided. The
  2026-08-06 architecture decision supersedes the real-time portion: WebSocket
  now carries chat and live voice, while file-job status uses durable HTTP.
- Changes:
  - Added two HTTP `202` submission routes with a shared response contract.
  - Persist uploaded audio to worker-visible storage before submission.
  - Added PostgreSQL job and append-only event schemas.
  - Use one UUID as public job ID and Celery task ID.
  - Added Redis queued-state caching and Celery publication.
  - Added a Celery worker task that records processing, completion, and failure.
  - Added isolated route and submission-service tests.
- Constraint: API and worker must mount the same audio-storage volume.
- Next: Add job status/result and cancellation endpoints, deployment services,
  database migration execution, authentication, and retention policy.

## 2026-07-28 — Implement the initial GitLab pipeline

- Status: completed
- Request: Create working pipeline code that can be studied in depth.
- Decision: Begin with real validation and test jobs; defer package publishing
  and deployment until corresponding artifacts and services exist.
- Changes:
  - Added branch, merge-request, and tag pipeline creation rules without duplicate
    branch pipelines for open merge requests.
  - Added parallel Ruff and mypy jobs followed by the global pytest job.
  - Added pip caching, interruptible jobs, JUnit results, coverage reports, and
    expiring diagnostic artifacts.
  - Added Ruff and mypy configuration and development dependencies.
  - Added repository ignore rules and a detailed CI/CD operating guide.
- Verification: All pipeline commands pass locally. The GitLab-specific
  configuration must additionally be checked by GitLab CI Lint after the project
  is created or connected.
- Next: Initialize/connect the Git repository and validate the configuration in
  the target GitLab project.

## 2026-07-28 — Create the global Python test structure

- Status: completed
- Request: Create the filesystem structure for global tests and write its main
  entry-point script.
- Decision: Use pytest as both the Python test framework and global test
  orchestrator.
- Changes:
  - Added root pytest discovery and strict marker configuration.
  - Added global unit, integration, end-to-end, and cross-component test
    directories.
  - Added `main.py`, which defaults to running tests that are neither slow nor
    GPU-dependent and forwards explicit pytest arguments.
  - Added shared fixture infrastructure, entry-point regression tests, developer
    dependencies, and test usage documentation.
- Verification: The entry-point suite passes with pytest.
- Next: Add component tests as runtime contracts and implementations are defined.

## 2026-07-27 — Separate development and Whisper task journals

- Status: completed
- Clarification: Code-writing and other project-development tasks belong in this
  Markdown journal.
- Decision: Runtime Whisper transcription tasks must also be journaled, but in a
  separate persistent PostgreSQL job and event history.
- Reason: Development history and application runtime history have different
  volume, privacy, retention, and querying requirements.
- Changes:
  - Clarified the internal documentation rules.
  - Added runtime task-journal requirements to the Voice Transcriber architecture
    and service record.
- Next: Define the transcription job and event schemas before implementing the
  FastAPI and Celery workflow.

## 2026-07-27 — Establish mandatory documentation discipline

- Status: completed
- Request: Ensure every task is recorded in the journal and reflected in project
  documentation.
- Changes:
  - Made journal coverage mandatory for all project task types.
  - Defined documentation updates as part of task completion.
  - Required affected architecture, service, parameter, and usage documents to
    remain synchronized with the implemented state.
- Ongoing rule: Future tasks must include journal and documentation maintenance.

## 2026-07-27 — Scaffold the Voice Transcriber

- Status: completed
- Request: Create the module structure without application code.
- Changes:
  - Added directories for the widget, standalone demo, FastAPI backend, Celery
    worker, PostgreSQL migrations, contracts, deployment, and tests.
  - Added separate engine directories for Python Whisper and whisper.cpp.
  - Documented the module and its current service state.
- Decision: Python Whisper is the initial engine.
- Decision: whisper.cpp is the planned performance-oriented replacement.
- Constraint: The public API, frontend, job model, and task workflow must depend on
  a stable transcription-engine contract rather than either implementation.
- Next: Define the contract and Docker services before writing implementation code.

## 2026-07-27 — Define the global three-element architecture

- Status: completed
- Request: Establish the system's main idea.
- Decision: The system consists of the User Interface, Agent, and Controller.
- Decision: The UI supports text, speech, and future input/output modes.
- Decision: The Controller connects the UI to one selected Agent; the UI does not
  communicate directly with agents.
- Changes:
  - Updated the total architecture to version 0.2.
  - Added the core interaction flow and initial interface boundaries.
  - Updated the standard project overview.
- Open design question: Determine whether agent selection lasts for one message,
  one task, or an entire session.

## 2026-07-27 — Add total architecture document

- Status: completed
- Request: Create one document describing the architecture of the entire system.
- Changes:
  - Created `docs/ARCHITECTURE.md` as the canonical system architecture.
  - Linked it from the standard and internal documentation indexes.
- Current state: The architecture structure is ready; undecided values are
  explicitly marked `TBD`.
- Next: Define requirements, select the first components, and replace relevant
  `TBD` entries with verified decisions and current values.

## 2026-07-27 — Initialize project documentation

- Status: completed
- Request: Create the project directory and establish standard and internal
  documentation.
- Changes:
  - Created `/home/yaroslav/a-man`.
  - Created the standard documentation area.
  - Created the internal task journal.
  - Created the service-documentation area and template.
- Decisions:
  - Standard and internal documentation are kept separate.
  - Each service will have one document describing its complete current state.
  - Sensitive values will not be stored in documentation.
- Next: Define the project goals, architecture, and first service.
