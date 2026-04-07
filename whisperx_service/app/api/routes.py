from fastapi import APIRouter, File, Form, UploadFile

from app.schemas.transcription import HealthResponse, TranscriptionResponse
from app.services.preprocessing import cleanup_temp_file, persist_upload_to_temp
from app.services.transcriber import transcribe_file

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def healthcheck() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post("/api/v1/transcriptions", response_model=TranscriptionResponse)
async def create_transcription(
    file: UploadFile = File(...),
    language: str = Form(default="en"),
) -> TranscriptionResponse:
    temp_path = await persist_upload_to_temp(file)
    try:
        result = transcribe_file(file_path=temp_path, language=language)
        return TranscriptionResponse(**result)
    finally:
        cleanup_temp_file(temp_path)
