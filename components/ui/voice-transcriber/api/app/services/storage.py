"""Persistent storage for uploaded audio."""

from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

MAX_UPLOAD_BYTES = 500 * 1024 * 1024
UPLOAD_CHUNK_BYTES = 1024 * 1024


class LocalAudioStorage:
    """Store uploads on a volume shared by the API and task worker."""

    def __init__(self, root: Path, max_bytes: int = MAX_UPLOAD_BYTES) -> None:
        self._root = root.resolve()
        self._max_bytes = max_bytes

    async def store(self, upload: UploadFile) -> tuple[Path, int]:
        self._root.mkdir(parents=True, exist_ok=True)
        suffix = Path(upload.filename or "").suffix.lower()[:16]
        path = self._root / f"{uuid4()}{suffix}"
        size = 0
        try:
            with path.open("xb") as destination:
                while chunk := await upload.read(UPLOAD_CHUNK_BYTES):
                    size += len(chunk)
                    if size > self._max_bytes:
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"Audio file exceeds {self._max_bytes} bytes",
                        )
                    destination.write(chunk)
                destination.flush()
                os.fsync(destination.fileno())
        except BaseException:
            path.unlink(missing_ok=True)
            raise

        if size == 0:
            path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Audio file is empty",
            )
        return path, size
