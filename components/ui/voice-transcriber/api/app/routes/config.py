"""HTTP endpoints for recorder configuration."""

from collections.abc import Callable
from typing import Annotated

from fastapi import APIRouter, Depends

from app.domain.models import AudioRecordConfig
from app.services.config import AudioRecordConfigStore


def create_config_router(
    get_store: Callable[[], AudioRecordConfigStore],
) -> APIRouter:
    router = APIRouter(prefix="/v1/config", tags=["configuration"])

    @router.get("/audio-record", response_model=AudioRecordConfig)
    def get_audio_record_config(
        store: Annotated[AudioRecordConfigStore, Depends(get_store)],
    ) -> AudioRecordConfig:
        return store.read()

    @router.put("/audio-record", response_model=AudioRecordConfig)
    def update_audio_record_config(
        config: AudioRecordConfig,
        store: Annotated[AudioRecordConfigStore, Depends(get_store)],
    ) -> AudioRecordConfig:
        store.write(config)
        return config

    return router
