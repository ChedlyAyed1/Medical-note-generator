from django.db import models

from apps.common.models import TimeStampedUUIDModel


class ClinicalNote(TimeStampedUUIDModel):
    class NoteType(models.TextChoices):
        SOAP = "soap", "SOAP"
        SUMMARY = "summary", "Summary"

    job = models.OneToOneField(
        "notes.TranscriptionJob",
        on_delete=models.CASCADE,
        related_name="clinical_note",
    )
    note_type = models.CharField(max_length=32, choices=NoteType.choices, default=NoteType.SOAP)
    model_name = models.CharField(max_length=128)
    prompt_version = models.CharField(max_length=64)
    content = models.TextField()
    structured_content = models.JSONField(default=dict, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-generated_at",)

    def __str__(self) -> str:
        return f"ClinicalNote({self.note_type}, job={self.job_id})"
