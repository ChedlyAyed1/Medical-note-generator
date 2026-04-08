import pytest

from apps.common.exceptions import InvalidStateError
from apps.notes.clients.whisperx_client import WhisperXResult, WhisperXSegment
from apps.notes.models import TranscriptSegment, TranscriptionJob
from apps.notes.services import create_transcription_job, transcribe_job
from apps.notes.tests.factories import build_audio_file


class FakeWhisperXClient:
    def __init__(self, result: WhisperXResult) -> None:
        self.result = result
        self.calls: list[dict] = []

    def transcribe(self, *, file_path: str, language: str = "") -> WhisperXResult:
        self.calls.append({"file_path": file_path, "language": language})
        return self.result


class FailingWhisperXClient:
    def __init__(self, message: str = "WhisperX service call failed.") -> None:
        self.message = message

    def transcribe(self, *, file_path: str, language: str = "") -> WhisperXResult:
        raise RuntimeError(self.message)


def _create_job(settings, tmp_path, *, language: str = "en") -> TranscriptionJob:
    settings.MEDIA_ROOT = tmp_path / "media"
    return create_transcription_job(
        uploaded_file=build_audio_file(),
        patient_reference="patient-001",
        encounter_reference="enc-001",
        language=language,
    )


@pytest.mark.django_db
def test_transcribe_job_marks_job_completed_and_persists_segments(settings, tmp_path):
    job = _create_job(settings, tmp_path, language="en")
    client = FakeWhisperXClient(
        WhisperXResult(
            text="hello world",
            language="en",
            segments=[
                WhisperXSegment(start=0.0, end=1.0, text="hello", speaker="spk1", metadata={"raw": 1}),
                WhisperXSegment(start=1.0, end=2.0, text="world", speaker="spk2", metadata={"raw": 2}),
            ],
            raw_payload={"text": "hello world", "language": "en"},
        )
    )

    transcribe_job(job=job, client=client)
    job.refresh_from_db()

    assert client.calls == [{"file_path": job.audio_recording.file.path, "language": "en"}]
    assert job.status == TranscriptionJob.Status.COMPLETED
    assert job.language == "en"
    assert job.error_message == ""
    assert job.started_at is not None
    assert job.finished_at is not None
    assert job.raw_payload == {"text": "hello world", "language": "en"}

    segments = list(job.segments.order_by("segment_index"))
    assert len(segments) == 2
    assert segments[0].text == "hello"
    assert segments[0].speaker == "spk1"
    assert segments[0].metadata == {"raw": 1}
    assert segments[1].text == "world"
    assert segments[1].speaker == "spk2"


@pytest.mark.django_db
def test_transcribe_job_replaces_existing_segments_on_retry(settings, tmp_path):
    job = _create_job(settings, tmp_path, language="en")
    job.status = TranscriptionJob.Status.FAILED
    job.save(update_fields=["status", "updated_at"])
    TranscriptSegment.objects.create(
        job=job,
        segment_index=0,
        start=0.0,
        end=0.5,
        speaker="old",
        text="stale",
        metadata={"stale": True},
    )
    client = FakeWhisperXClient(
        WhisperXResult(
            text="fresh",
            language="en",
            segments=[WhisperXSegment(start=0.0, end=1.0, text="fresh", speaker="spk1", metadata={})],
            raw_payload={"text": "fresh", "language": "en"},
        )
    )

    transcribe_job(job=job, client=client)

    segments = list(job.segments.order_by("segment_index"))
    assert len(segments) == 1
    assert segments[0].text == "fresh"
    assert segments[0].speaker == "spk1"


@pytest.mark.django_db
def test_transcribe_job_marks_job_failed_when_client_raises(settings, tmp_path):
    job = _create_job(settings, tmp_path, language="en")

    with pytest.raises(RuntimeError, match="timed out"):
        transcribe_job(job=job, client=FailingWhisperXClient("WhisperX service call timed out."))

    job.refresh_from_db()
    assert job.status == TranscriptionJob.Status.FAILED
    assert job.error_message == "WhisperX service call timed out."
    assert job.finished_at is not None
    assert job.segments.count() == 0


@pytest.mark.django_db
def test_transcribe_job_rejects_invalid_job_state(settings, tmp_path):
    job = _create_job(settings, tmp_path, language="en")
    job.status = TranscriptionJob.Status.COMPLETED
    job.save(update_fields=["status", "updated_at"])

    with pytest.raises(InvalidStateError, match="Only pending or failed jobs can be transcribed."):
        transcribe_job(
            job=job,
            client=FakeWhisperXClient(
                WhisperXResult(text="", language="en", segments=[], raw_payload={}),
            ),
        )
