from django.db import models

from apps.common.models import TimeStampedUUIDModel
from apps.common.validators import validate_audio_extension


class AudioRecording(TimeStampedUUIDModel):
    file = models.FileField(upload_to="audio/%Y/%m/%d/", validators=[validate_audio_extension])
    original_filename = models.CharField(max_length=255)
    patient_reference = models.CharField(max_length=64, blank=True)
    encounter_reference = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"AudioRecording({self.original_filename})"
