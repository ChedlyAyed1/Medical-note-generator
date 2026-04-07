from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.exceptions import DomainError
from apps.notes.api.serializers import TranscriptionJobSerializer
from apps.notes.selectors import get_job_by_id
from apps.notes.services import transcribe_job


class JobDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, _request, job_id):
        job = get_job_by_id(job_id=job_id)
        serializer = TranscriptionJobSerializer(job)
        return Response(serializer.data)


class JobTranscriptionRunView(APIView):
    permission_classes = [AllowAny]

    def post(self, _request, job_id):
        job = get_job_by_id(job_id=job_id)

        try:
            job = transcribe_job(job=job)
        except DomainError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TranscriptionJobSerializer(job)
        return Response(serializer.data, status=status.HTTP_200_OK)
