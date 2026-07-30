"""API contracts for both asynchronous audio submission methods."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import pytest
from app.domain.models import (
    AudioSourceType,
    JobStatus,
    TranscriptionJobAccepted,
    TranscriptionOptions,
)
from app.main import app, get_audio_storage, get_submission_service
from fastapi.testclient import TestClient

TASK_ID = UUID("a19d42c3-1cd7-47ca-ad4d-53d9068e564a")
CREATED_AT = datetime(2026, 7, 30, 12, 0, tzinfo=UTC)


class FakeSubmissionService:
    def __init__(self) -> None:
        self.submissions: list[tuple[Path, AudioSourceType, TranscriptionOptions]] = []

    async def submit(
        self,
        audio_path: Path,
        *,
        source_type: AudioSourceType,
        options: TranscriptionOptions,
        original_filename: str | None = None,
        content_type: str | None = None,
        size_bytes: int | None = None,
    ) -> TranscriptionJobAccepted:
        assert audio_path.is_file()
        self.submissions.append((audio_path, source_type, options))
        return TranscriptionJobAccepted(
            task_id=TASK_ID,
            status=JobStatus.QUEUED,
            audio_path=audio_path,
            created_at=CREATED_AT,
        )


@pytest.fixture
def submission_service() -> FakeSubmissionService:
    return FakeSubmissionService()


@pytest.fixture
def client(
    tmp_path: Path,
    submission_service: FakeSubmissionService,
) -> Iterator[TestClient]:
    from app.services.storage import LocalAudioStorage

    app.dependency_overrides[get_submission_service] = lambda: submission_service
    app.dependency_overrides[get_audio_storage] = lambda: LocalAudioStorage(
        tmp_path / "uploads"
    )
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_queues_server_path(
    client: TestClient,
    submission_service: FakeSubmissionService,
    tmp_path: Path,
) -> None:
    audio_path = tmp_path / "sample.wav"
    audio_path.write_bytes(b"audio")

    response = client.post(
        "/v1/transcriptions/path",
        json={
            "audio_path": str(audio_path),
            "language": "uk",
            "include_segments": False,
        },
    )

    assert response.status_code == 202
    assert response.json() == {
        "task_id": str(TASK_ID),
        "status": "queued",
        "audio_path": str(audio_path),
        "created_at": "2026-07-30T12:00:00Z",
    }
    assert submission_service.submissions[0][1] == AudioSourceType.SERVER_PATH


def test_path_must_exist(client: TestClient, tmp_path: Path) -> None:
    response = client.post(
        "/v1/transcriptions/path",
        json={"audio_path": str(tmp_path / "missing.wav")},
    )

    assert response.status_code == 404


def test_stores_upload_and_queues_its_path(
    client: TestClient,
    submission_service: FakeSubmissionService,
) -> None:
    response = client.post(
        "/v1/transcriptions/upload",
        files={"audio": ("sample.wav", b"audio", "audio/wav")},
        data={"language": "en", "include_segments": "true"},
    )

    assert response.status_code == 202
    stored_path, source_type, options = submission_service.submissions[0]
    assert stored_path.read_bytes() == b"audio"
    assert source_type == AudioSourceType.UPLOAD
    assert options.language == "en"
    assert response.json()["audio_path"] == str(stored_path)


def test_rejects_empty_upload(client: TestClient) -> None:
    response = client.post(
        "/v1/transcriptions/upload",
        files={"audio": ("empty.wav", b"", "audio/wav")},
    )

    assert response.status_code == 422
