from rest_framework import serializers

from apps.notes.models import ClinicalNote


class ClinicalNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicalNote
        fields = (
            "id",
            "job",
            "note_type",
            "model_name",
            "prompt_version",
            "content",
            "structured_content",
            "generated_at",
        )
