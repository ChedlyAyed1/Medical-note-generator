from django.shortcuts import get_object_or_404

from apps.notes.models import TranscriptionJob


def get_job_by_id(*, job_id):
    queryset = (
        TranscriptionJob.objects.select_related("audio_recording")
        .prefetch_related("segments")
        .select_related("clinical_note")
    )
    return get_object_or_404(queryset, id=job_id)
