# A-Man GitLab CI/CD

## Current scope

The initial pipeline validates Python quality and runs the global test suite. It
does not publish packages or deploy services because A-Man does not yet contain a
package or deployable runtime.

The pipeline is defined in the repository-root `.gitlab-ci.yml`.

## Execution model

GitLab creates a pipeline, assigns each job to a compatible runner, and executes
that job in an isolated `python:3.12-slim` container. Files produced by one job do
not automatically exist in another job. Cache accelerates dependency downloads;
artifacts preserve declared outputs for people and later jobs.

```text
pipeline creation
       |
       +------------------+
       |                  |
     ruff               mypy
       |                  |
       +--------+---------+
                |
              pytest
                |
       reports and artifacts
```

## Top-level keywords

### `workflow`

`workflow: rules` decides whether GitLab creates a pipeline at all:

1. Create a merge-request pipeline for merge-request events.
2. Suppress a branch-push pipeline when that branch already has an open merge
   request. This prevents duplicate pipelines for the same commit.
3. Create pipelines for Git tags.
4. Create pipelines for branch pushes.

Rules are evaluated from top to bottom, and the first matching rule wins.

### `stages`

Stages establish the broad order:

1. `validate`
2. `test`

Jobs in the same stage can run concurrently. A later stage normally waits for
the earlier stage to succeed.

### `variables`

- `PIP_CACHE_DIR` places downloaded Python packages inside the project directory
  so GitLab can cache them.
- `PIP_DISABLE_PIP_VERSION_CHECK` removes an irrelevant pip network check.
- `PYTHONDONTWRITEBYTECODE` prevents `.pyc` files in CI.
- `PYTHONUNBUFFERED` sends Python output directly to the job log.

No secrets belong in this file. Future credentials must be stored as masked and
protected GitLab CI/CD variables.

### `default`

Defaults apply to all jobs:

- `image` selects the job container.
- `interruptible` allows an obsolete pipeline to be cancelled when a newer
  commit replaces it.
- `before_script` displays the Python version and installs development tools.
- `cache` reuses pip downloads when `requirements-dev.txt` is unchanged.

A cache is an optimization and must never be required for correctness.

## Jobs

### `ruff`

Ruff performs two separate checks:

- `ruff check .` checks imports, common errors, and selected Python rules.
- `ruff format --check .` verifies formatting without modifying files.

`needs: []` lets the job start immediately.

### `mypy`

Mypy checks static types in the test entry point and global test suite. Its scope
will expand when application packages are created.

### `pytest`

The test job calls the same `main.py` entry point developers use locally. It
depends explicitly on both validation jobs through `needs`, so it begins only
after Ruff and mypy succeed.

The job produces:

- `report.xml` — JUnit test results displayed by GitLab.
- `coverage.xml` — Cobertura coverage data displayed in the merge request.
- Terminal coverage output in the job log.

`artifacts: when: always` uploads reports even when tests fail, which makes
failed pipelines diagnosable. They expire after one week.

## Run the same checks locally

Install the development dependencies:

```bash
python3 -m pip install -r requirements-dev.txt
```

Run exactly the three CI checks:

```bash
python3 -m ruff check .
python3 -m ruff format --check .
python3 -m mypy main.py tests
python3 main.py \
  --junitxml=report.xml \
  --cov=main \
  --cov-branch \
  --cov-report=term-missing \
  --cov-report=xml:coverage.xml
```

Generated reports and tool caches are excluded by `.gitignore`.

## Failure behavior

A nonzero command exit code fails its job. A failed validation job prevents the
test job from starting. A failed required job makes the entire pipeline fail and
should block merging into protected `main`.

## Planned extensions

Add stages only when the corresponding deliverables exist:

- Package-build verification after Python packages are defined.
- PostgreSQL and Redis integration jobs after those services are implemented.
- Container-image publishing after deployable services exist.
- Slow CPU and GPU Whisper jobs on suitable runners.
- Development and production deployment jobs with protected environments.

Package publishing and deployment must consume already-tested, immutable
artifacts rather than rebuilding different outputs.

