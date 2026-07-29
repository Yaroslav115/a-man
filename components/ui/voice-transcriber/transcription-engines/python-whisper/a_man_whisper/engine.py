"""Stable adapter around the Python Whisper package."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Any, Protocol, cast


class WhisperModel(Protocol):
    """The part of the Whisper model API used by this adapter."""

    def transcribe(self, audio: str, **options: object) -> Mapping[str, Any]:
        """Transcribe an audio file."""


ModelLoader = Callable[[str, str | None, str | None], WhisperModel]


@dataclass(frozen=True)
class TranscriptionSegment:
    """A normalized time-bounded part of a transcript."""

    start: float
    end: float
    text: str


@dataclass(frozen=True)
class TranscriptionResult:
    """Engine-independent transcription output."""

    text: str
    language: str | None
    segments: tuple[TranscriptionSegment, ...]
    model: str


class TranscriptionError(RuntimeError):
    """A normalized failure raised by the transcription engine."""


def _load_whisper_model(
    model_name: str, device: str | None, download_root: str | None
) -> WhisperModel:
    whisper = import_module("whisper")
    return cast(
        WhisperModel,
        whisper.load_model(
            model_name,
            device=device,
            download_root=download_root,
        ),
    )


class PythonWhisperEngine:
    """Load one Whisper model and expose normalized transcription results."""

    def __init__(
        self,
        model_name: str,
        *,
        device: str | None = None,
        download_root: str | Path | None = None,
        model_loader: ModelLoader = _load_whisper_model,
    ) -> None:
        if not model_name.strip():
            raise ValueError("model_name must not be empty")

        self.model_name = model_name
        self.device = device
        self._model = model_loader(
            model_name,
            device,
            str(download_root) if download_root is not None else None,
        )

    def transcribe(
        self,
        audio_path: str | Path,
        *,
        language: str | None = None,
        include_segments: bool = True,
    ) -> TranscriptionResult:
        """Transcribe a local audio file and normalize Whisper's response."""

        path = Path(audio_path)
        if not path.is_file():
            raise FileNotFoundError(f"Audio file does not exist: {path}")

        options: dict[str, object] = {
            "verbose": False,
            "word_timestamps": include_segments,
        }
        if language is not None:
            options["language"] = language
        if self.device == "cpu":
            options["fp16"] = False

        try:
            raw_result = self._model.transcribe(str(path), **options)
            return TranscriptionResult(
                text=str(raw_result.get("text", "")).strip(),
                language=_optional_string(raw_result.get("language")),
                segments=(
                    _normalize_segments(raw_result.get("segments", ()))
                    if include_segments
                    else ()
                ),
                model=self.model_name,
            )
        except (KeyError, TypeError, ValueError) as error:
            raise TranscriptionError(
                f"Whisper returned an invalid result: {error}"
            ) from error
        except Exception as error:
            raise TranscriptionError(
                f"Whisper transcription failed: {error}"
            ) from error


def _optional_string(value: object) -> str | None:
    return str(value) if value is not None else None


def _normalize_segments(value: object) -> tuple[TranscriptionSegment, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise TypeError("segments must be a sequence")

    segments: list[TranscriptionSegment] = []
    for item in value:
        if not isinstance(item, Mapping):
            raise TypeError("each segment must be a mapping")
        segments.append(
            TranscriptionSegment(
                start=float(item["start"]),
                end=float(item["end"]),
                text=str(item.get("text", "")).strip(),
            )
        )
    return tuple(segments)
