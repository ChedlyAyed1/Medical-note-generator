from django.shortcuts import get_object_or_404

from apps.notes.models import ClinicalNote


def get_note_by_id(*, note_id):
    queryset = ClinicalNote.objects.select_related("job", "job__audio_recording")
    return get_object_or_404(queryset, id=note_id)
