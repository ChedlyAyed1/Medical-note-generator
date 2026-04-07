from dataclasses import dataclass
from os import getenv


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


settings = Settings()
