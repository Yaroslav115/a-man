"""Global test entry point for the A-Man project."""

from __future__ import annotations

import sys
from collections.abc import Sequence

import pytest

DEFAULT_ARGUMENTS = ("-m", "not slow and not requires_gpu")


def main(arguments: Sequence[str] | None = None) -> int:
    """Run every pytest suite in the project.

    Explicit command-line arguments replace the default local-test selection.
    """

    selected_arguments = list(arguments if arguments is not None else sys.argv[1:])
    if not selected_arguments:
        selected_arguments = list(DEFAULT_ARGUMENTS)
    return pytest.main(selected_arguments)


if __name__ == "__main__":
    raise SystemExit(main())
