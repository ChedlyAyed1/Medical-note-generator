from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"


class TranscriptionSegmentResponse(BaseModel):
    start: float = Field(default=0.0)
    end: float = Field(default=0.0)
    text: str = ""
    speaker: str = ""


class TranscriptionResponse(BaseModel):
    text: str
    language: str
    segments: list[TranscriptionSegmentResponse]
