from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notes.api.serializers import AudioUploadSerializer, TranscriptionJobSerializer
from apps.notes.services import create_transcription_job


class AudioUploadView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AudioUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        job = create_transcription_job(
            uploaded_file=serializer.validated_data["file"],
            patient_reference=serializer.validated_data.get("patient_reference", ""),
            encounter_reference=serializer.validated_data.get("encounter_reference", ""),
            language=serializer.validated_data.get("language", ""),
        )

        response_serializer = TranscriptionJobSerializer(job)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
