from functools import lru_cache

from app.core.config import settings


@lru_cache(maxsize=1)
def get_transcription_model():
    import whisperx

    return whisperx.load_model(
        settings.model_name,
        device=settings.device,
        compute_type=settings.compute_type,
    )


def transcribe_file(*, file_path: str, language: str = "") -> dict:
    import whisperx

    model = get_transcription_model()
    audio = whisperx.load_audio(file_path)
    result = model.transcribe(audio, batch_size=settings.batch_size, language=language or None)

    if settings.align_output and result.get("segments"):
        align_model, metadata = whisperx.load_align_model(
            language_code=result["language"],
            device=settings.device,
        )
        aligned = whisperx.align(
            result["segments"],
            align_model,
            metadata,
            audio,
            settings.device,
            return_char_alignments=False,
        )
        result["segments"] = aligned.get("segments", result["segments"])
        result["text"] = aligned.get("text", result.get("text", ""))

    segments = [
        {
            "start": segment.get("start", 0.0),
            "end": segment.get("end", 0.0),
            "text": segment.get("text", "").strip(),
            "speaker": segment.get("speaker", ""),
        }
        for segment in result.get("segments", [])
    ]

    return {
        "text": result.get("text", "").strip(),
        "language": result.get("language", language or ""),
        "segments": segments,
    }
