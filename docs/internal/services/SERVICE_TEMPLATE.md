# Service: <service-name>

## Record

| Field | Current value |
|---|---|
| Owner | TBD |
| Status | planned |
| Version | TBD |
| Environment | TBD |
| Repository/path | TBD |
| Runtime | TBD |
| Deployment target | TBD |
| Last verified | TBD |

## Purpose

Describe what the service does, its responsibilities, and what is outside its
scope.

## Interfaces

| Interface | Protocol | Address/port | Authentication | Notes |
|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD |

## Configuration

| Parameter | Current value | Default | Required | Source | Notes |
|---|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD | TBD |

For sensitive parameters, write `<managed secret>` as the current value and name
the secret manager or environment-variable source. Never record the secret itself.

## Dependencies

| Dependency | Type | Current version/address | Required | Notes |
|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD |

## Data and Storage

Document databases, schemas, volumes, retention, backups, migrations, and data
ownership. Use `N/A` when the service stores no data.

## Agent Responsibilities

Document which agents interact with this service, their allowed actions, required
inputs, outputs, tools, permissions, and escalation conditions.

## Build, Run, and Test

```text
Build: TBD
Run: TBD
Test: TBD
Health check: TBD
```

## Deployment

Describe environments, deployment procedure, rollback procedure, scaling, and
release dependencies.

## Observability

Document health endpoints, logs, metrics, traces, dashboards, alerts, and common
failure signals.

## Security

Document authentication, authorization, network exposure, data classification,
secret locations, and relevant security constraints.

## Operational Procedures

Describe startup, shutdown, recovery, backup/restore, routine maintenance, and
incident response.

## Known Issues and Risks

- TBD

## Change History

| Date | Change | Author/agent |
|---|---|---|
| TBD | Initial record | TBD |
