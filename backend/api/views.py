from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import AskRequestSerializer
from legaldata.models import ChatSession, ChatMessage

import sys
from pathlib import Path
import uuid
import logging
import time


logger = logging.getLogger(__name__)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
AGENT_PATH = PROJECT_ROOT / "agent"

if str(AGENT_PATH) not in sys.path:
    sys.path.insert(0, str(AGENT_PATH))


class AskQuestionView(APIView):
    """
    POST /api/ask/

    Routes the question through ask_agent() and stores the
    conversation in MySQL-backed session memory.
    """

    def post(self, request, *args, **kwargs):

        # --------------------------------------------------------------
        # 0. Correlation ID and request timer
        # --------------------------------------------------------------

        correlation_id = request.headers.get(
            "X-Correlation-ID",
            str(uuid.uuid4())
        )

        start_time = time.perf_counter()

        # --------------------------------------------------------------
        # 1. Validate request
        # --------------------------------------------------------------

        serializer = AskRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        question = serializer.validated_data["question"]

        # --------------------------------------------------------------
        # 2. Get or create session
        # --------------------------------------------------------------

        session_id = request.data.get("session_id")

        if not session_id:
            session_id = str(uuid.uuid4())

        chat_session, _ = ChatSession.objects.get_or_create(
            session_id=session_id
        )

        # --------------------------------------------------------------
        # 3. Run legal agent
        # --------------------------------------------------------------

        try:
            from agent import ask_agent

            legal_answer = ask_agent(question)

            # ----------------------------------------------------------
            # 4. Save conversation to MySQL
            # ----------------------------------------------------------

            ChatMessage.objects.create(
                session=chat_session,
                question=question,
                answer=legal_answer.answer,
                supported=legal_answer.supported,
            )

            # ----------------------------------------------------------
            # 5. Build response
            # ----------------------------------------------------------

            response = Response(
                {
                    "correlation_id": correlation_id,
                    "session_id": session_id,
                    "question": question,
                    "answer": legal_answer.answer,
                    "supported": legal_answer.supported,
                    "citations": [
                        c.model_dump()
                        for c in legal_answer.citations
                    ],
                    "claim_citations": [
                        cc.model_dump()
                        for cc in legal_answer.claim_citations
                    ],
                },
                status=status.HTTP_200_OK
            )

            # ----------------------------------------------------------
            # 6. Calculate latency
            # ----------------------------------------------------------

            latency_ms = round(
                (time.perf_counter() - start_time) * 1000,
                2
            )

            # ----------------------------------------------------------
            # 7. Add correlation ID to response header
            # ----------------------------------------------------------

            response["X-Correlation-ID"] = correlation_id

            # ----------------------------------------------------------
            # 8. Structured log
            # ----------------------------------------------------------

            logger.info(
                "legal_request_completed",
                extra={
                    "correlation_id": correlation_id,
                    "session_id": session_id,
                    "status": 200,
                    "latency_ms": latency_ms,
                },
            )

            return response

        except Exception as exc:

            latency_ms = round(
                (time.perf_counter() - start_time) * 1000,
                2
            )

            logger.error(
                "legal_request_failed",
                extra={
                    "correlation_id": correlation_id,
                    "session_id": session_id,
                    "status": 500,
                    "latency_ms": latency_ms,
                    "error": str(exc),
                },
            )

            response = Response(
                {
                    "error": (
                        "The legal research service "
                        "could not process the request."
                    ),
                    "detail": str(exc),
                    "correlation_id": correlation_id,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

            response["X-Correlation-ID"] = correlation_id

            return response