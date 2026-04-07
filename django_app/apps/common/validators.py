from pathlib import Path

from django.core.exceptions import ValidationError

AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".mp4", ".aac", ".flac", ".ogg"}


def validate_audio_extension(file_obj) -> None:
    suffix = Path(file_obj.name).suffix.lower()
    if suffix not in AUDIO_EXTENSIONS:
        raise ValidationError(f"Unsupported audio format: {suffix or 'missing extension'}")
