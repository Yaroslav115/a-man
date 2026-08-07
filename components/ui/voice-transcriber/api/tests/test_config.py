"""Tests for disk-backed audio recorder configuration."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from app.main import app, get_audio_record_config_store
from app.services.config import AudioRecordConfigStore
from fastapi.testclient import TestClient


@pytest.fixture
def config_path(tmp_path: Path) -> Path:
    return tmp_path / "config" / "audio-record.json"


@pytest.fixture
def client(config_path: Path) -> Iterator[TestClient]:
    app.dependency_overrides[get_audio_record_config_store] = lambda: (
        AudioRecordConfigStore(config_path)
    )
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_get_creates_default_config_on_disk(
    client: TestClient, config_path: Path
) -> None:
    response = client.get("/v1/config/audio-record")

    assert response.status_code == 200
    assert response.json() == {
        "push_to_talk_enabled": False,
        "push_to_talk_key": "Space",
    }
    assert config_path.is_file()


def test_put_persists_config(client: TestClient, config_path: Path) -> None:
    expected = {"push_to_talk_enabled": True, "push_to_talk_key": "KeyV"}

    response = client.put("/v1/config/audio-record", json=expected)

    assert response.status_code == 200
    assert response.json() == expected
    assert client.get("/v1/config/audio-record").json() == expected
    assert '"push_to_talk_key": "KeyV"' in config_path.read_text()


def test_rejects_empty_push_to_talk_key(client: TestClient) -> None:
    response = client.put(
        "/v1/config/audio-record",
        json={"push_to_talk_enabled": True, "push_to_talk_key": ""},
    )

    assert response.status_code == 422
