from dataclasses import dataclass
from pathlib import Path

import httpx
from django.conf import settings

from apps.common.exceptions import ExternalServiceError


@dataclass(slots=True)
class WhisperXSegment:
    start: float
    end: float
    text: str
    speaker: str = ""
    metadata: dict | None = None


@dataclass(slots=True)
class WhisperXResult:
    text: str
    language: str
    segments: list[WhisperXSegment]
    raw_payload: dict


class WhisperXClient:
    def __init__(self, base_url: str | None = None, timeout: float = 120.0) -> None:
        self.base_url = (base_url or settings.WHISPERX_BASE_URL).rstrip("/")
        self.timeout = timeout

    def transcribe(self, *, file_path: str, language: str = "") -> WhisperXResult:
        upload_name = Path(file_path).name
        data = {"language": language}

        try:
            with Path(file_path).open("rb") as file_handle:
                response = httpx.post(
                    f"{self.base_url}/api/v1/transcriptions",
                    files={"file": (upload_name, file_handle)},
                    data=data,
                    timeout=self.timeout,
                )
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ExternalServiceError("WhisperX service call failed.") from exc

        payload = response.json()
        segments = [
            WhisperXSegment(
                start=segment.get("start", 0.0),
                end=segment.get("end", 0.0),
                text=segment.get("text", ""),
                speaker=segment.get("speaker", ""),
                metadata=segment,
            )
            for segment in payload.get("segments", [])
        ]

        return WhisperXResult(
            text=payload.get("text", ""),
            language=payload.get("language", ""),
            segments=segments,
            raw_payload=payload,
        )
