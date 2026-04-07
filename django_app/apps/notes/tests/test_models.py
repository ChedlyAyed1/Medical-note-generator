import pytest

from apps.notes.models import AudioRecording, TranscriptionJob


@pytest.mark.django_db
def test_transcription_job_defaults():
    recording = AudioRecording.objects.create(
        file="audio/test.wav",
        original_filename="test.wav",
    )
    job = TranscriptionJob.objects.create(audio_recording=recording)

    assert job.status == TranscriptionJob.Status.PENDING
