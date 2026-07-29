# A-Man Tests

Pytest is the global test framework and runner. The root configuration discovers
tests in this directory and in every component under `components/`.

## Commands

Run the normal local suite, excluding slow and GPU-dependent tests:

```bash
python3 main.py
```

Run the complete suite:

```bash
python3 main.py -m ""
```

Pytest can also be called directly:

```bash
python3 -m pytest
```

Run one category:

```bash
python3 main.py -m unit
python3 main.py -m integration
python3 main.py -m e2e
```

## Directories

| Path | Purpose |
|---|---|
| `global/` | Cross-component contracts and complete system behavior |
| `unit/` | Root-level isolated tests |
| `integration/` | Root-level tests involving multiple modules or services |
| `end_to_end/` | Root-level complete user and system workflows |
| `conftest.py` | Fixtures shared by all collected test suites |

Components keep their tests beside their implementation. Tests must be
independent and deterministic. Unit tests must not require network access,
containers, databases, queues, model downloads, or GPU hardware.
