from rest_framework import serializers


class AudioUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    patient_reference = serializers.CharField(max_length=64, required=False, allow_blank=True)
    encounter_reference = serializers.CharField(max_length=64, required=False, allow_blank=True)
    language = serializers.CharField(max_length=16, required=False, allow_blank=True)
