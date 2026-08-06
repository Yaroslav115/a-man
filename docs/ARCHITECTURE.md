# A-Man — Total Architecture

## Document Status

| Field | Current value |
|---|---|
| Status | Initial draft |
| Architecture version | 0.4 |
| Last updated | 2026-08-06 |
| Last verified | 2026-08-06 |

This is the canonical system-wide architecture document. It describes how all
agents, services, data stores, interfaces, and infrastructure fit together.
Detailed current values for an individual service belong in that service's
document under `internal/services/`.

## 1. Core Idea

The complete A-Man system consists of three primary elements:

1. **User Interface (UI)** — receives user input and presents system output using
   text, speech, and other future interaction modes.
2. **Agent** — processes the user's request and produces a result.
3. **Controller** — connects the UI to one selected agent and manages the
   interaction between them.

The controller is the central coordination point. The UI does not communicate
directly with agents. For each interaction, the controller selects or identifies
one agent, forwards normalized user input to it, receives its response, and sends
that response back to the UI.

```text
User
  ↕
User Interface (text, speech, other I/O)
  ↕
Controller
  ↕
One selected Agent
```

The initial global rule is **one UI interaction is connected to one agent through
the controller**. Multi-agent delegation may be designed later, but it is not part
of the current core architecture.

## 2. Goals and Scope

A-Man is a system for working with agents. Detailed functional goals, users,
constraints, and success criteria are still to be defined.

### In scope

- Multimodal user input and output
- Controller-based selection of one agent
- Communication between the UI, controller, and selected agent
- Agent lifecycle and task execution
- Tools and service integrations
- Shared state, artifacts, and documentation
- Permissions, approvals, and auditability
- Monitoring and operational control

### Out of scope

- TBD

## 3. Architecture Principles

1. All UI-to-agent communication passes through the controller.
2. The controller connects each interaction to one selected agent.
3. Input and output formats are independent from agent logic.
4. Agents receive only the context and permissions needed for their task.
5. Every important task, decision, action, and result is traceable.
6. Service boundaries and interfaces are explicit and versioned.
7. Current operational values are documented separately from secret values.
8. Failures are isolated, observable, and recoverable.
9. Humans retain control over sensitive or irreversible actions.

## 4. System Context

### Actors

| Actor | Role | Current status |
|---|---|---|
| Human operator | Defines goals, reviews work, and approves sensitive actions | Planned |
| Agent | Plans or performs bounded tasks using approved tools | Planned |
| External system | Provides data or executes integrated actions | TBD |

### External boundaries

| System | Purpose | Interface | Trust boundary |
|---|---|---|---|
| TBD | TBD | TBD | TBD |

## 5. Logical Architecture

The system has three mandatory logical elements. Supporting capabilities may be
implemented inside these elements initially and separated into services later.

| Element | Responsibility | Current implementation |
|---|---|---|
| User Interface | Capture text, speech, or other input; present agent output | TBD |
| Controller | Normalize input, select one agent, manage the interaction, and return output | TBD |
| Agent | Understand the request, perform the task, and produce a response | TBD |

### Supporting capabilities

| Capability | Likely owner | Responsibility |
|---|---|---|
| Input/output adapters | UI | Convert text, speech, and future modalities to and from common messages |
| Agent registry | Controller | Describe available agents and their capabilities |
| Agent selection | Controller | Choose one suitable agent for an interaction |
| Session state | Controller | Maintain the active UI-to-agent relationship and conversation state |
| Tool execution | Agent/controller boundary, TBD | Validate and execute approved tool operations |
| Policy and approval | Controller | Enforce permissions and request human approval |
| State and memory | TBD | Store task state and approved durable context |
| Artifact storage | TBD | Store generated files and outputs |
| Observability | All elements | Collect logs, metrics, traces, and audit events |

## 6. Agent Architecture

| Agent type | Responsibility | Inputs | Outputs | Permissions |
|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD |

Document the following when agent design is established:

- Agent lifecycle and state transitions
- Delegation and coordination rules
- Context construction and isolation
- Tool discovery and invocation
- Retry, timeout, cancellation, and recovery behavior
- Approval and escalation conditions
- Output validation and quality controls

## 7. Data Architecture

| Data category | Owner | Storage | Retention | Classification |
|---|---|---|---|---|
| Tasks and status | TBD | TBD | TBD | TBD |
| Agent messages and events | TBD | TBD | TBD | TBD |
| Artifacts | TBD | TBD | TBD | TBD |
| Configuration | TBD | TBD | TBD | TBD |
| Audit records | TBD | TBD | TBD | TBD |

Schemas, consistency requirements, backup strategy, and migration rules are TBD.

## 8. Interface Architecture

| Producer | Consumer | Interface/event | Protocol | Version |
|---|---|---|---|---|
| UI | Controller | Normalized user input | TBD | TBD |
| Controller | Agent | Agent request | TBD | TBD |
| Agent | Controller | Agent response/status | TBD | TBD |
| Controller | UI | Displayable/performable output | TBD | TBD |

### UI real-time transport

The reusable Chat Widget maintains one authenticated WebSocket connection at
`/v1/conversations/{conversation_id}/stream` to the Controller for an active
conversation. The connection carries versioned JSON
events for user messages, streamed agent output, voice-stream control and audio
chunks, acknowledgements, status changes, cancellation, errors, and heartbeat
traffic. The standalone demo hosts the same Chat Widget and uses the same
protocol; it does not implement a separate chat client.

HTTP remains the durable request/response interface for conversation history,
file upload, completed transcription lookup, health checks, and recovery after a
disconnected WebSocket. PostgreSQL remains authoritative; WebSocket delivery is
not itself durable. Every client-originated command has a unique `message_id`,
and server events carry a monotonically increasing conversation sequence so a
client can reconnect with its last received sequence and reconcile missed state.

The initial WebSocket envelope is:

```json
{
  "version": 1,
  "type": "chat.message.send",
  "message_id": "uuid",
  "conversation_id": "uuid",
  "sequence": null,
  "timestamp": "RFC-3339 timestamp",
  "payload": {}
}
```

Binary WebSocket frames carry live audio only after a `voice.stream.start`
command establishes encoding, sample rate, channel count, and stream ID. JSON
control frames never contain base64 audio. File-based recordings continue to
use the existing HTTP transcription API.

All interfaces should define authentication, authorization, validation, error
semantics, retry safety, timeouts, and compatibility expectations.

## 9. Deployment Architecture

| Environment | Purpose | Hosting | Network boundary | Status |
|---|---|---|---|---|
| Local development | Development and testing | Local machine | Local | Planned |
| Test | Automated and integration testing | TBD | TBD | TBD |
| Production | User-facing operation | TBD | TBD | TBD |

Build, release, scaling, availability, disaster recovery, and rollback designs are
TBD.

## 10. Security Architecture

- Identity and authentication: TBD
- Authorization model: TBD
- Agent and tool permissions: TBD
- Human approval gates: TBD
- Network controls: TBD
- Secret management: TBD
- Encryption: TBD
- Audit logging: TBD
- Threat model: TBD

Secrets must never be stored in documentation.

## 11. Observability and Operations

- Health checks: TBD
- Structured logs: TBD
- Metrics and service-level objectives: TBD
- Distributed tracing: TBD
- Audit events: TBD
- Dashboards and alerts: TBD
- Incident response: TBD

### Testing

Pytest is the global test framework and orchestrator. The root `pyproject.toml`
collects both system-wide tests under `tests/` and component-owned tests under
`components/`. The root `main.py` is the standard test entry point.

Tests are classified with `unit`, `integration`, `e2e`, `slow`, and
`requires_gpu` markers. The default local run excludes slow and GPU-dependent
tests. Each component remains independently testable, while any component failure
causes the global run to fail.

### Continuous integration

GitLab CI/CD is the initial automation platform. Branch, merge-request, and tag
pipelines run in isolated Python containers. Ruff and mypy validation jobs run in
parallel; the global pytest job runs only after both succeed and publishes JUnit
and coverage reports. Packaging and deployment stages will be introduced only
when versioned packages and deployable services exist.

## 12. Key Workflows

### UI-to-agent interaction

1. The user provides text, speech, or another supported input through the UI.
2. The UI converts the input into a normalized message for the controller.
3. The controller validates the message, context, and permissions.
4. The controller selects one suitable agent or uses the agent already assigned
   to the active session.
5. The controller sends the request and required context to that agent.
6. The agent processes the request, uses approved tools if needed, and returns a
   response or status.
7. The controller validates and converts the agent result into a UI response.
8. The UI presents the result using the appropriate output mode.
9. The controller records relevant task state and audit information.

For an interactive chat session, steps 2–8 use the Chat Widget's WebSocket. The
Controller acknowledges accepted user messages, streams ordered response deltas,
and emits a terminal message event. On reconnect, the UI supplies the last
received sequence and retrieves durable history over HTTP if replay is not
available.

### Live voice-to-chat interaction

1. The Chat Widget opens or reuses its authenticated conversation WebSocket.
2. The user starts recording and the widget sends `voice.stream.start`.
3. The widget sends encoded microphone chunks as binary frames with bounded
   client buffering and backpressure handling.
4. The Controller routes the stream to the Voice Transcriber and returns partial
   and final transcript events.
5. The final transcript is placed in the editable chat composer; it is not sent
   to an agent automatically.
6. The user edits and sends the message through the normal chat message event.
7. Stop, cancellation, timeout, disconnect, and permission failures produce
   explicit terminal events and release stream resources.

Workflows for changing the selected agent, failure recovery, cancellation, and
scheduled tasks are TBD.

## 13. Architecture Decisions

Formal architecture decisions should be recorded here until a dedicated decision
record process is introduced.

| Date | Decision | Rationale | Status |
|---|---|---|---|
| 2026-07-27 | Maintain one canonical total architecture document | Keeps the complete system design discoverable and consistent | Accepted |
| 2026-07-27 | Use UI, Controller, and Agent as the three primary elements | Establishes a small and clear global system model | Accepted |
| 2026-07-27 | Route all UI-to-agent communication through the Controller | Centralizes agent selection, session control, policy, and observability | Accepted |
| 2026-07-27 | Connect an interaction to one agent | Defines the initial routing model and avoids premature multi-agent complexity | Accepted |
| 2026-07-28 | Use pytest as the global test framework and runner | Provides one Python entry point while preserving component-owned suites | Accepted |
| 2026-07-28 | Use GitLab CI/CD with incremental pipeline stages | Gives immediate validation without pretending unimplemented packaging or deployment exists | Accepted |
| 2026-08-06 | Use WebSocket as the Chat Widget's real-time conversation and live-audio transport | Supports streamed agent output, partial transcription, interruption, and future bidirectional interaction over one session | Accepted |
| 2026-08-06 | Retain HTTP beside WebSocket for durable resources and recovery | Keeps uploads, history, lookup, health, and reconnect reconciliation explicit and retryable | Accepted |

## 14. Risks and Open Questions

- How does the controller select the correct agent?
- Is an agent selected for one message, one task, or the entire session?
- Which common message format supports text, speech, and future I/O modes?
- How can the user view or change the currently selected agent?
- Which actions require human approval?
- Which services and external integrations are needed?
- What persistence, privacy, and retention requirements apply?
- What availability and scale targets must the system meet?
- Where will each environment be hosted?

## 15. Service Map

The authoritative per-service records are stored in `internal/services/`.

| Service | Responsibility | Dependencies | Status | Documentation |
|---|---|---|---|---|
| Voice Transcriber | Convert UI audio input to text for the reusable Chat Widget and standalone demo | FastAPI, WebSocket/HTTP, PostgreSQL, Redis, Celery, replaceable Whisper engine | Asynchronous file backend implemented; live streaming planned | `internal/services/voice-transcriber.md` |

## 16. Change History

| Date | Version | Change |
|---|---|---|
| 2026-07-27 | 0.1 | Created the initial total architecture document |
| 2026-07-27 | 0.2 | Defined UI, Controller, and Agent as the three primary system elements |
| 2026-07-27 | 0.2 | Added Voice Transcriber as the first UI subcomponent |
| 2026-07-28 | 0.3 | Established the global pytest structure and test entry point |
| 2026-07-28 | 0.3 | Added the initial GitLab validation and test pipeline |
| 2026-08-06 | 0.4 | Adopted WebSocket for real-time chat and live voice while retaining HTTP for durable operations and recovery |
