from django.utils import timezone

from apps.common.exceptions import InvalidStateError
from apps.notes.clients import WhisperXClient
from apps.notes.models import TranscriptSegment, TranscriptionJob


def transcribe_job(*, job: TranscriptionJob, client: WhisperXClient | None = None) -> TranscriptionJob:
    if job.status not in {TranscriptionJob.Status.PENDING, TranscriptionJob.Status.FAILED}:
        raise InvalidStateError("Only pending or failed jobs can be transcribed.")

    client = client or WhisperXClient()

    job.status = TranscriptionJob.Status.RUNNING
    job.started_at = timezone.now()
    job.error_message = ""
    job.save(update_fields=["status", "started_at", "error_message", "updated_at"])

    try:
        result = client.transcribe(
            file_path=job.audio_recording.file.path,
            language=job.language,
        )
    except Exception as exc:
        job.status = TranscriptionJob.Status.FAILED
        job.error_message = str(exc)
        job.finished_at = timezone.now()
        job.save(update_fields=["status", "error_message", "finished_at", "updated_at"])
        raise

    job.segments.all().delete()
    TranscriptSegment.objects.bulk_create(
        [
            TranscriptSegment(
                job=job,
                segment_index=index,
                start=segment.start,
                end=segment.end,
                speaker=segment.speaker,
                text=segment.text,
                metadata=segment.metadata or {},
            )
            for index, segment in enumerate(result.segments)
        ]
    )

    job.status = TranscriptionJob.Status.COMPLETED
    job.language = result.language or job.language
    job.raw_payload = result.raw_payload
    job.error_message = ""
    job.finished_at = timezone.now()
    job.save(
        update_fields=[
            "status",
            "language",
            "raw_payload",
            "error_message",
            "finished_at",
            "updated_at",
        ]
    )

    return job
