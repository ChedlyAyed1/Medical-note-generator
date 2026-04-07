from dataclasses import dataclass
from os import getenv
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR.parent / ".env")
load_dotenv(BASE_DIR / ".env")


def env_bool(name: str, default: bool = False) -> bool:
    return getenv(name, str(default)).lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True, slots=True)
class Settings:
    model_name: str = getenv("WHISPERX_MODEL_NAME", "base")
    device: str = getenv("WHISPERX_DEVICE", "cpu")
    compute_type: str = getenv("WHISPERX_COMPUTE_TYPE", "int8")
    batch_size: int = int(getenv("WHISPERX_BATCH_SIZE", "4"))
    align_output: bool = env_bool("WHISPERX_ALIGN_OUTPUT", True)
    enable_diarization: bool = env_bool("WHISPERX_ENABLE_DIARIZATION", False)
    hf_token: str = getenv("WHISPERX_HF_TOKEN", "")
    min_speakers: int | None = int(getenv("WHISPERX_MIN_SPEAKERS", "0")) or None
    max_speakers: int | None = int(getenv("WHISPERX_MAX_SPEAKERS", "0")) or None


settings = Settings()
