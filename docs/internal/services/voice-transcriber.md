# Service: voice-transcriber

## Record

| Field | Current value |
|---|---|
| Owner | TBD |
| Status | structure created; not implemented |
| Version | 0.1 |
| Environment | local development |
| Repository/path | `components/ui/voice-transcriber/` |
| Runtime | Docker Compose stack, planned |
| Deployment target | TBD |
| Last verified | 2026-07-27 |

## Purpose

Provide reusable audio-to-text transcription for the A-Man user interface while
remaining usable as a standalone module.

## Planned parts

| Part | Technology | Current state |
|---|---|---|
| Reusable widget | Web frontend, TBD | Directory created |
| Standalone demo | Web frontend, TBD | Directory created |
| Public backend | FastAPI | Directory created |
| Task orchestration | Celery | Directory created |
| Queue/broker | Redis | Planned |
| Persistent data | PostgreSQL | Migration directory created |
| Initial transcription engine | Python Whisper | Directory created |
| Optimized transcription engine | whisper.cpp | Reserved directory created |

## Architecture constraint

All callers and orchestration code must depend on a stable transcription-engine
contract. Engine-specific behavior must be isolated so Python Whisper can be
replaced by whisper.cpp without changing the public API or task workflow.

## Interfaces and configuration

Not yet defined. No ports, credentials, model names, image tags, or runtime
parameter values have been selected.

## Runtime task journaling

Every Whisper transcription task must be stored in PostgreSQL with an append-only
history of its lifecycle events. At minimum, the journal must make creation,
queuing, processing, retries, completion, failure, and cancellation traceable.
The engine name and version must be recorded so results remain attributable after
the transition from Python Whisper to whisper.cpp.

The exact schema, retention period, and privacy policy are TBD.

## Security

Audio and transcripts may contain sensitive information. Retention, access,
deletion, transport encryption, and audit requirements must be defined before
production use. Secrets must not be stored in this document.

## Change History

| Date | Change | Author/agent |
|---|---|---|
| 2026-07-27 | Created initial directory structure and engine-replacement boundary | Codex |
