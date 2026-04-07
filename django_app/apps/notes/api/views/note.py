from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.exceptions import DomainError
from apps.notes.api.serializers import ClinicalNoteSerializer
from apps.notes.selectors import get_job_by_id, get_note_by_id
from apps.notes.services import generate_clinical_note_for_job


class ClinicalNoteDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, _request, note_id):
        note = get_note_by_id(note_id=note_id)
        serializer = ClinicalNoteSerializer(note)
        return Response(serializer.data)


class JobGenerateNoteView(APIView):
    permission_classes = [AllowAny]

    def post(self, _request, job_id):
        job = get_job_by_id(job_id=job_id)

        try:
            note = generate_clinical_note_for_job(job=job)
        except DomainError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ClinicalNoteSerializer(note)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
