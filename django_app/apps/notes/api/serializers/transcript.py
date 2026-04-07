from rest_framework import serializers

from apps.notes.models import ClinicalNote, TranscriptionJob


class AudioRecordingSummarySerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    original_filename = serializers.CharField(read_only=True)
    patient_reference = serializers.CharField(read_only=True)
    encounter_reference = serializers.CharField(read_only=True)
    file = serializers.FileField(read_only=True)


class TranscriptSegmentSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    segment_index = serializers.IntegerField(read_only=True)
    start = serializers.FloatField(read_only=True)
    end = serializers.FloatField(read_only=True)
    speaker = serializers.CharField(read_only=True)
    text = serializers.CharField(read_only=True)
    metadata = serializers.JSONField(read_only=True)


class ClinicalNotePreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicalNote
        fields = ("id", "note_type", "model_name", "generated_at")


class TranscriptionJobSerializer(serializers.ModelSerializer):
    audio_recording = AudioRecordingSummarySerializer(read_only=True)
    segments = TranscriptSegmentSerializer(many=True, read_only=True)
    clinical_note = ClinicalNotePreviewSerializer(read_only=True)

    class Meta:
        model = TranscriptionJob
        fields = (
            "id",
            "status",
            "language",
            "error_message",
            "created_at",
            "updated_at",
            "started_at",
            "finished_at",
            "audio_recording",
            "segments",
            "clinical_note",
        )
