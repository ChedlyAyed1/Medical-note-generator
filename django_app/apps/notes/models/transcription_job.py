from django.db import models

from apps.common.models import TimeStampedUUIDModel


class TranscriptionJob(TimeStampedUUIDModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        FAILED = "failed", "Failed"
        COMPLETED = "completed", "Completed"

    audio_recording = models.ForeignKey(
        "notes.AudioRecording",
        on_delete=models.CASCADE,
        related_name="jobs",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    language = models.CharField(max_length=16, blank=True)
    raw_payload = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"TranscriptionJob({self.id}, {self.status})"
