from django.db import transaction

from apps.notes.models import AudioRecording, TranscriptionJob


@transaction.atomic
def create_transcription_job(
    *,
    uploaded_file,
    patient_reference: str = "",
    encounter_reference: str = "",
    language: str = "",
) -> TranscriptionJob:
    recording = AudioRecording.objects.create(
        file=uploaded_file,
        original_filename=uploaded_file.name,
        patient_reference=patient_reference,
        encounter_reference=encounter_reference,
    )

    return TranscriptionJob.objects.create(
        audio_recording=recording,
        language=language,
    )
