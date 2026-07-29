"""Functional tests for the Python Whisper adapter."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from a_man_whisper import PythonWhisperEngine, TranscriptionError


class FakeModel:
    def __init__(
        self,
        result: dict[str, Any] | None = None,
        error: Exception | None = None,
    ) -> None:
        self.result = result or {}
        self.error = error
        self.calls: list[tuple[str, dict[str, object]]] = []

    def transcribe(self, audio: str, **options: object) -> dict[str, Any]:
        self.calls.append((audio, options))
        if self.error is not None:
            raise self.error
        return self.result


@pytest.fixture
def audio_file(tmp_path: Path) -> Path:
    path = tmp_path / "speech.wav"
    path.write_bytes(b"test audio")
    return path


@pytest.mark.unit
def test_transcribe_normalizes_text_language_and_segments(audio_file: Path) -> None:
    model = FakeModel(
        {
            "text": "  hello world  ",
            "language": "en",
            "segments": [
                {"start": 0, "end": 1.25, "text": " hello"},
                {"start": 1.25, "end": 2, "text": "world "},
            ],
        }
    )
    engine = PythonWhisperEngine(
        "small",
        device="cpu",
        model_loader=lambda _name, _device, _root: model,
    )

    result = engine.transcribe(audio_file, language="en")

    assert result.text == "hello world"
    assert result.language == "en"
    assert result.model == "small"
    assert [
        (segment.start, segment.end, segment.text) for segment in result.segments
    ] == [
        (0.0, 1.25, "hello"),
        (1.25, 2.0, "world"),
    ]
    assert model.calls == [
        (
            str(audio_file),
            {
                "verbose": False,
                "word_timestamps": True,
                "language": "en",
                "fp16": False,
            },
        )
    ]


@pytest.mark.unit
def test_transcribe_supports_empty_result_without_segments(audio_file: Path) -> None:
    model = FakeModel()
    engine = PythonWhisperEngine(
        "small",
        model_loader=lambda _name, _device, _root: model,
    )

    result = engine.transcribe(audio_file, include_segments=False)

    assert result.text == ""
    assert result.language is None
    assert result.segments == ()
    assert model.calls[0][1]["word_timestamps"] is False


@pytest.mark.unit
def test_transcribe_rejects_missing_audio_before_calling_model(
    tmp_path: Path,
) -> None:
    model = FakeModel()
    engine = PythonWhisperEngine(
        "small",
        model_loader=lambda _name, _device, _root: model,
    )

    with pytest.raises(FileNotFoundError, match="Audio file does not exist"):
        engine.transcribe(tmp_path / "missing.wav")

    assert model.calls == []


@pytest.mark.unit
def test_transcribe_normalizes_model_failure(audio_file: Path) -> None:
    model = FakeModel(error=RuntimeError("decoder unavailable"))
    engine = PythonWhisperEngine(
        "small",
        model_loader=lambda _name, _device, _root: model,
    )

    with pytest.raises(TranscriptionError, match="decoder unavailable"):
        engine.transcribe(audio_file)


@pytest.mark.unit
def test_engine_rejects_empty_model_name() -> None:
    with pytest.raises(ValueError, match="model_name must not be empty"):
        PythonWhisperEngine(" ")
