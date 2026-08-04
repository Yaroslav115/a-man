# A-Man Tests

Pytest is the global test framework and runner. The root configuration discovers
tests in this directory and in every component under `components/`.

## Python version

A-Man supports Python 3.11 and 3.12. Python 3.12 is the preferred local version
and is selected by the repository's `.python-version` file when using pyenv or
another compatible version manager. Python 3.10 is not supported.

Confirm the active interpreter before installing dependencies or running tests:

```bash
python --version
python -m pip install -r requirements-dev.txt
```

## Commands

Run the normal local suite, excluding slow and GPU-dependent tests:

```bash
python main.py
```

Run the complete suite:

```bash
python main.py -m ""
```

Pytest can also be called directly:

```bash
python -m pytest
```

Run one category:

```bash
python main.py -m unit
python main.py -m integration
python main.py -m e2e
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
