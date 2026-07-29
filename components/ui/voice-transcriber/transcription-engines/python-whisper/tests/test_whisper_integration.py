"""Real-model smoke test for the Python Whisper adapter."""

from __future__ import annotations

import os
import wave
from pathlib import Path

import pytest
from a_man_whisper import PythonWhisperEngine


@pytest.mark.integration
@pytest.mark.slow
def test_real_whisper_transcribes_audio_file(tmp_path: Path) -> None:
    if os.getenv("RUN_WHISPER_INTEGRATION") != "1":
        pytest.skip("set RUN_WHISPER_INTEGRATION=1 to load a real Whisper model")

    audio_path = tmp_path / "silence.wav"
    _write_silence(audio_path)

    engine = PythonWhisperEngine(
        os.getenv("WHISPER_MODEL", "small"),
        device=os.getenv("WHISPER_DEVICE", "cpu"),
        download_root=os.getenv("WHISPER_CACHE_DIR"),
    )
    result = engine.transcribe(
        audio_path,
        language="en",
        include_segments=False,
    )

    assert isinstance(result.text, str)
    assert result.language == "en"
    assert result.model == os.getenv("WHISPER_MODEL", "small")
    assert result.segments == ()


def _write_silence(path: Path) -> None:
    sample_rate = 16_000
    with wave.open(str(path), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(sample_rate)
        audio.writeframes(b"\x00\x00" * sample_rate)
