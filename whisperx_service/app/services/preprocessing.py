import os
import tempfile
from pathlib import Path

from fastapi import UploadFile


async def persist_upload_to_temp(file: UploadFile) -> str:
    suffix = Path(file.filename or "audio.wav").suffix or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as handle:
        contents = await file.read()
        handle.write(contents)
        return handle.name


def cleanup_temp_file(file_path: str) -> None:
    if os.path.exists(file_path):
        os.remove(file_path)
