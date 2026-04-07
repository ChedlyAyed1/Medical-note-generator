import pytest

from apps.notes.services import create_transcription_job
from apps.notes.tests.factories import build_audio_file


@pytest.mark.django_db
def test_create_transcription_job_persists_audio_and_job():
    job = create_transcription_job(
        uploaded_file=build_audio_file(),
        patient_reference="patient-001",
        encounter_reference="enc-001",
        language="en",
    )

    assert job.audio_recording.original_filename == "visit.wav"
    assert job.language == "en"
