# Task Journal

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
