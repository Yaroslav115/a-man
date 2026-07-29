# Internal Documentation

This directory contains working documentation for maintainers and agents.

## Contents

- `../ARCHITECTURE.md` — canonical architecture for the complete system.
- `TASK_JOURNAL.md` — chronological record of tasks, decisions, and outcomes.
- `CI_CD.md` — current GitLab pipeline behavior and operating guide.
- `services/` — one current-state document for every service.
- `services/SERVICE_TEMPLATE.md` — required structure for new service documents.

## Rules

1. Record every project development task in `TASK_JOURNAL.md`, including code
   writing, documentation, investigation, design, testing, and operational work
   performed on the codebase.
2. Create the journal entry when work starts, record important decisions while
   working, and update its status and outcome when work finishes.
3. Update all affected documentation as part of completing a task. A task is not
   complete while its architecture, service state, parameters, or usage
   documentation is stale.
4. Create or update the relevant service document whenever configuration,
   interfaces, dependencies, deployment, or operational behavior changes.
5. Record actual current values where safe. Mark unknown values as `TBD`.
6. Never store secrets. Record the secret name and where it is managed instead.
7. Use ISO dates (`YYYY-MM-DD`) and include the timezone when time matters.

Runtime application jobs are not written into `TASK_JOURNAL.md`. Each service
must persist its own job history or audit records. In particular, every Voice
Transcriber/Whisper task must be journaled in the application's database.
