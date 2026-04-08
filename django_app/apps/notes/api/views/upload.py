from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notes.api.serializers import AudioUploadSerializer, TranscriptionJobSerializer
from apps.notes.services import create_transcription_job


class AudioUploadView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        summary="Upload an audio file and create a transcription job",
        request=AudioUploadSerializer,
        responses={
            201: TranscriptionJobSerializer,
            400: OpenApiResponse(description="Invalid upload payload."),
        },
    )
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
