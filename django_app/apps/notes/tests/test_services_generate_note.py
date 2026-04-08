import pytest

from apps.common.exceptions import InvalidStateError
from apps.notes.models import ClinicalNote, TranscriptSegment, TranscriptionJob
from apps.notes.services import create_transcription_job, generate_clinical_note_for_job
from apps.notes.tests.factories import build_audio_file


class FakeGroqClient:
    def __init__(self, result: dict) -> None:
        self.result = result
        self.calls: list[dict] = []

    def generate_note(self, *, transcript_text: str, note_type: str, prompt_name: str) -> dict:
        self.calls.append(
            {
                "transcript_text": transcript_text,
                "note_type": note_type,
                "prompt_name": prompt_name,
            }
        )
        return self.result


def _create_completed_job(settings, tmp_path, *, language: str = "en") -> TranscriptionJob:
    settings.MEDIA_ROOT = tmp_path / "media"
    job = create_transcription_job(
        uploaded_file=build_audio_file(),
        patient_reference="patient-001",
        encounter_reference="enc-001",
        language=language,
    )
    job.status = TranscriptionJob.Status.COMPLETED
    job.save(update_fields=["status", "updated_at"])
    return job


@pytest.mark.django_db
def test_generate_clinical_note_for_completed_job_persists_note(settings, tmp_path):
    job = _create_completed_job(settings, tmp_path)
    TranscriptSegment.objects.create(
        job=job,
        segment_index=0,
        start=0.0,
        end=1.0,
        speaker="spk1",
        text="first line",
        metadata={},
    )
    TranscriptSegment.objects.create(
        job=job,
        segment_index=1,
        start=1.0,
        end=2.0,
        speaker="spk2",
        text="second line",
        metadata={},
    )
    client = FakeGroqClient(
        {
            "note_type": ClinicalNote.NoteType.SOAP,
            "model_name": "openai/gpt-oss-120b",
            "prompt_version": "soap_note_v1",
            "content": "Generated SOAP note",
        }
    )

    note = generate_clinical_note_for_job(job=job, client=client)

    assert client.calls == [
        {
            "transcript_text": "first line\nsecond line",
            "note_type": "soap",
            "prompt_name": "soap_note_v1.txt",
        }
    ]
    assert note.job == job
    assert note.note_type == ClinicalNote.NoteType.SOAP
    assert note.model_name == "openai/gpt-oss-120b"
    assert note.prompt_version == "soap_note_v1"
    assert note.content == "Generated SOAP note"
    assert note.structured_content == {"source": "groq"}


@pytest.mark.django_db
def test_generate_clinical_note_updates_existing_note(settings, tmp_path):
    job = _create_completed_job(settings, tmp_path)
    TranscriptSegment.objects.create(
        job=job,
        segment_index=0,
        start=0.0,
        end=1.0,
        speaker="spk1",
        text="summary input",
        metadata={},
    )
    existing_note = ClinicalNote.objects.create(
        job=job,
        note_type=ClinicalNote.NoteType.SOAP,
        model_name="old-model",
        prompt_version="soap_note_v1",
        content="Old content",
        structured_content={"source": "old"},
    )
    client = FakeGroqClient(
        {
            "note_type": ClinicalNote.NoteType.SUMMARY,
            "model_name": "openai/gpt-oss-120b",
            "prompt_version": "summary_v1",
            "content": "Updated summary note",
        }
    )

    note = generate_clinical_note_for_job(
        job=job,
        client=client,
        note_type=ClinicalNote.NoteType.SUMMARY,
    )

    assert note.id == existing_note.id
    assert ClinicalNote.objects.filter(job=job).count() == 1
    assert client.calls[0]["prompt_name"] == "summary_v1.txt"
    assert note.note_type == ClinicalNote.NoteType.SUMMARY
    assert note.prompt_version == "summary_v1"
    assert note.content == "Updated summary note"
    assert note.structured_content == {"source": "groq"}


@pytest.mark.django_db
def test_generate_clinical_note_requires_completed_job(settings, tmp_path):
    job = _create_completed_job(settings, tmp_path)
    job.status = TranscriptionJob.Status.PENDING
    job.save(update_fields=["status", "updated_at"])

    with pytest.raises(InvalidStateError, match="The transcript must be completed before generating a note."):
        generate_clinical_note_for_job(
            job=job,
            client=FakeGroqClient(
                {
                    "note_type": ClinicalNote.NoteType.SOAP,
                    "model_name": "openai/gpt-oss-120b",
                    "prompt_version": "soap_note_v1",
                    "content": "Should not be used",
                }
            ),
        )


@pytest.mark.django_db
def test_generate_clinical_note_requires_non_empty_transcript(settings, tmp_path):
    job = _create_completed_job(settings, tmp_path)
    TranscriptSegment.objects.create(
        job=job,
        segment_index=0,
        start=0.0,
        end=1.0,
        speaker="spk1",
        text="   ",
        metadata={},
    )

    with pytest.raises(InvalidStateError, match="No transcript text is available for this job."):
        generate_clinical_note_for_job(
            job=job,
            client=FakeGroqClient(
                {
                    "note_type": ClinicalNote.NoteType.SOAP,
                    "model_name": "openai/gpt-oss-120b",
                    "prompt_version": "soap_note_v1",
                    "content": "Should not be used",
                }
            ),
        )
