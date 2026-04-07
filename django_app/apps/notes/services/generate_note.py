from django.conf import settings

from apps.common.exceptions import InvalidStateError
from apps.notes.clients import GroqClient
from apps.notes.models import ClinicalNote, TranscriptionJob


def generate_clinical_note_for_job(
    *,
    job: TranscriptionJob,
    client: GroqClient | None = None,
    note_type: str | None = None,
) -> ClinicalNote:
    if job.status != TranscriptionJob.Status.COMPLETED:
        raise InvalidStateError("The transcript must be completed before generating a note.")

    transcript_text = "\n".join(segment.text for segment in job.segments.all())
    if not transcript_text.strip():
        raise InvalidStateError("No transcript text is available for this job.")

    client = client or GroqClient()
    note_type = note_type or settings.DEFAULT_NOTE_TYPE

    prompt_name = "soap_note_v1.txt" if note_type == ClinicalNote.NoteType.SOAP else "summary_v1.txt"
    result = client.generate_note(
        transcript_text=transcript_text,
        note_type=note_type,
        prompt_name=prompt_name,
    )

    note, _created = ClinicalNote.objects.update_or_create(
        job=job,
        defaults={
            "note_type": result["note_type"],
            "model_name": result["model_name"],
            "prompt_version": result["prompt_version"],
            "content": result["content"],
            "structured_content": {"source": "groq"},
        },
    )
    return note
