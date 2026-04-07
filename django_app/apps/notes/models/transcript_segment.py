from django.db import models

from apps.common.models import TimeStampedUUIDModel


class TranscriptSegment(TimeStampedUUIDModel):
    job = models.ForeignKey(
        "notes.TranscriptionJob",
        on_delete=models.CASCADE,
        related_name="segments",
    )
    segment_index = models.PositiveIntegerField()
    start = models.FloatField()
    end = models.FloatField()
    speaker = models.CharField(max_length=64, blank=True)
    text = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("segment_index",)
        unique_together = ("job", "segment_index")

    def __str__(self) -> str:
        return f"TranscriptSegment(job={self.job_id}, index={self.segment_index})"
