from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import AskRequestSerializer


class AskQuestionView(APIView):
    """
    POST /api/ask/
    Endpoint for querying legal information.
    Validates that the question exists and is non-empty.
    Returns a mock response for now until RAG/Agent verification is integrated.
    """

    def post(self, request, *args, **kwargs):
        serializer = AskRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Future integration point: RAG pipeline & Legal Verification Agent
        mock_response = {
            "answer": "This is a temporary mock answer.",
            "supported": True,
            "citations": []
        }
        return Response(mock_response, status=status.HTTP_200_OK)
