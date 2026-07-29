"""Tests for the global test entry point."""

from __future__ import annotations

from unittest.mock import patch

import main


def test_main_uses_fast_local_suite_by_default() -> None:
    with patch("main.pytest.main", return_value=0) as pytest_main:
        exit_code = main.main([])

    assert exit_code == 0
    pytest_main.assert_called_once_with(["-m", "not slow and not requires_gpu"])


def test_main_forwards_explicit_pytest_arguments() -> None:
    with patch("main.pytest.main", return_value=3) as pytest_main:
        exit_code = main.main(["-m", "integration", "-q"])

    assert exit_code == 3
    pytest_main.assert_called_once_with(["-m", "integration", "-q"])
