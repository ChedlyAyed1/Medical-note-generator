from django.contrib import admin

from apps.notes.models import AudioRecording, ClinicalNote, TranscriptSegment, TranscriptionJob

admin.site.register(AudioRecording)
admin.site.register(TranscriptionJob)
admin.site.register(TranscriptSegment)
admin.site.register(ClinicalNote)
