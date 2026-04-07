from django.urls import path

from apps.notes.api.views import (
    AudioUploadView,
    ClinicalNoteDetailView,
    JobDetailView,
    JobGenerateNoteView,
    JobTranscriptionRunView,
)

urlpatterns = [
    path("uploads/", AudioUploadView.as_view(), name="audio-upload"),
    path("jobs/<uuid:job_id>/", JobDetailView.as_view(), name="job-detail"),
    path("jobs/<uuid:job_id>/transcribe/", JobTranscriptionRunView.as_view(), name="job-transcribe"),
    path(
        "jobs/<uuid:job_id>/generate-note/",
        JobGenerateNoteView.as_view(),
        name="job-generate-note",
    ),
    path("<uuid:note_id>/", ClinicalNoteDetailView.as_view(), name="note-detail"),
]
