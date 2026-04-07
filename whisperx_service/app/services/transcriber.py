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


@lru_cache(maxsize=1)
def get_diarization_model():
    from whisperx.diarize import DiarizationPipeline

    if not settings.hf_token:
        raise ValueError("WHISPERX_HF_TOKEN is required when diarization is enabled.")

    return DiarizationPipeline(
        token=settings.hf_token,
        device=settings.device,
    )


def normalize_speaker_labels(segments: list[dict]) -> list[dict]:
    speaker_map: dict[str, str] = {}
    next_index = 1

    for segment in segments:
        raw_speaker = (segment.get("speaker") or "").strip()
        if not raw_speaker:
            continue
        if raw_speaker not in speaker_map:
            speaker_map[raw_speaker] = f"spk{next_index}"
            next_index += 1
        segment["speaker"] = speaker_map[raw_speaker]

    return segments


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

    if settings.enable_diarization:
        diarization_model = get_diarization_model()
        diarize_segments = diarization_model(
            audio,
            min_speakers=settings.min_speakers,
            max_speakers=settings.max_speakers,
        )
        result = whisperx.assign_word_speakers(diarize_segments, result, fill_nearest=True)

    segments = [
        {
            "start": segment.get("start", 0.0),
            "end": segment.get("end", 0.0),
            "text": segment.get("text", "").strip(),
            "speaker": segment.get("speaker", ""),
        }
        for segment in result.get("segments", [])
    ]
    segments = normalize_speaker_labels(segments)

    full_text = result.get("text", "").strip()
    if not full_text:
        full_text = " ".join(segment["text"] for segment in segments if segment["text"]).strip()

    return {
        "text": full_text,
        "language": result.get("language", language or ""),
        "segments": segments,
    }
