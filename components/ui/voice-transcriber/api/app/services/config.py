"""Disk-backed configuration for the audio recorder UI."""

from __future__ import annotations

import json
from pathlib import Path

from app.domain.models import AudioRecordConfig


class AudioRecordConfigStore:
    """Read and atomically replace the recorder configuration JSON file."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def read(self) -> AudioRecordConfig:
        if not self._path.exists():
            config = AudioRecordConfig()
            self.write(config)
            return config
        return AudioRecordConfig.model_validate_json(self._path.read_text())

    def write(self, config: AudioRecordConfig) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self._path.with_suffix(f"{self._path.suffix}.tmp")
        temporary_path.write_text(
            json.dumps(config.model_dump(), indent=2) + "\n",
            encoding="utf-8",
        )
        temporary_path.replace(self._path)
