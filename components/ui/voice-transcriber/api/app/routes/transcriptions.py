"""HTTP endpoints that submit asynchronous transcription jobs."""

from collections.abc import Callable
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.domain.models import (
    AudioSourceType,
    PathTranscriptionRequest,
    TranscriptionJobAccepted,
    TranscriptionOptions,
)
from app.services.storage import LocalAudioStorage
from app.services.transcription import TranscriptionSubmissionService


def create_transcription_router(
    get_submission_service: Callable[[], TranscriptionSubmissionService],
    get_audio_storage: Callable[[], LocalAudioStorage],
) -> APIRouter:
    router = APIRouter(prefix="/v1/transcriptions", tags=["transcriptions"])

    @router.post(
        "/path",
        response_model=TranscriptionJobAccepted,
        status_code=status.HTTP_202_ACCEPTED,
    )
    async def submit_path(
        request: PathTranscriptionRequest,
        service: Annotated[
            TranscriptionSubmissionService,
            Depends(get_submission_service),
        ],
    ) -> TranscriptionJobAccepted:
        if not request.audio_path.is_file():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audio file does not exist",
            )
        return await _submit(
            service,
            request.audio_path,
            source_type=AudioSourceType.SERVER_PATH,
            options=request,
        )

    @router.post(
        "/upload",
        response_model=TranscriptionJobAccepted,
        status_code=status.HTTP_202_ACCEPTED,
    )
    async def submit_upload(
        audio: Annotated[UploadFile, File(description="Audio file to transcribe")],
        service: Annotated[
            TranscriptionSubmissionService,
            Depends(get_submission_service),
        ],
        storage: Annotated[LocalAudioStorage, Depends(get_audio_storage)],
        language: Annotated[str | None, Form()] = None,
        include_segments: Annotated[bool, Form()] = True,
        model: Annotated[str | None, Form()] = None,
    ) -> TranscriptionJobAccepted:
        try:
            audio_path, size_bytes = await storage.store(audio)
            return await _submit(
                service,
                audio_path,
                source_type=AudioSourceType.UPLOAD,
                options=TranscriptionOptions(
                    language=language,
                    include_segments=include_segments,
                    model=model,
                ),
                original_filename=audio.filename,
                content_type=audio.content_type,
                size_bytes=size_bytes,
            )
        except Exception:
            if "audio_path" in locals():
                audio_path.unlink(missing_ok=True)
            raise
        finally:
            await audio.close()

    return router


async def _submit(
    service: TranscriptionSubmissionService,
    audio_path: Path,
    *,
    source_type: AudioSourceType,
    options: TranscriptionOptions,
    original_filename: str | None = None,
    content_type: str | None = None,
    size_bytes: int | None = None,
) -> TranscriptionJobAccepted:
    try:
        return await service.submit(
            audio_path,
            source_type=source_type,
            options=options,
            original_filename=original_filename,
            content_type=content_type,
            size_bytes=size_bytes,
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Transcription job could not be queued",
        ) from error
