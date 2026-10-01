from pathlib import Path
import sys
from unittest.mock import patch

from django.db import OperationalError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

AGENT_PATH = Path(__file__).resolve().parents[2] / "agent"
if str(AGENT_PATH) not in sys.path:
    sys.path.insert(0, str(AGENT_PATH))

from schemas import Citation, LegalAnswer
from legaldata.models import ChatMessage, ChatSession


class SessionContinuityAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("ask_question")

    @patch("agent.ask_agent")
    def test_new_session_persists_messages_and_supplies_prior_turn(self, ask_agent):
        ask_agent.side_effect = [
            LegalAnswer(
                answer="The Act describes consumer rights in Section 2(9).",
                supported=True,
                citations=[Citation(
                    act="Consumer Protection Act, 2019",
                    section="2",
                    source="India Code",
                )],
            ),
            LegalAnswer(
                answer="The retrieved Section 2 text includes the right to information.",
                supported=True,
                citations=[Citation(
                    act="Consumer Protection Act, 2019",
                    section="2",
                    source="India Code",
                )],
            ),
        ]
        session_id = "continuity-session"
        first_question = "What are the basic rights of consumers?"

        first = self.client.post(
            self.url,
            {"session_id": session_id, "question": first_question},
            format="json",
        )
        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertEqual(ask_agent.call_args_list[0].kwargs["conversation_history"], [])

        second = self.client.post(
            self.url,
            {"session_id": session_id, "question": "Explain the second one."},
            format="json",
        )
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(second.data["session_id"], session_id)
        self.assertEqual(
            ask_agent.call_args_list[1].kwargs["conversation_history"],
            [{
                "question": first_question,
                "answer": "The Act describes consumer rights in Section 2(9).",
            }],
        )

        session = ChatSession.objects.get(session_id=session_id)
        self.assertEqual(session.messages.count(), 2)
        self.assertEqual(
            list(session.messages.order_by("created_at").values_list("question", flat=True)),
            [first_question, "Explain the second one."],
        )

    @patch("agent.ask_agent")
    def test_valid_unknown_session_id_creates_a_new_session(self, ask_agent):
        ask_agent.return_value = LegalAnswer(answer="Insufficient evidence.", supported=False)

        response = self.client.post(
            self.url,
            {"session_id": "first-use-session", "question": "A legal question"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(ChatSession.objects.filter(session_id="first-use-session").exists())
        self.assertEqual(ask_agent.call_args.kwargs["conversation_history"], [])

    def test_overlong_session_id_is_rejected(self):
        response = self.client.post(
            self.url,
            {"session_id": "s" * 101, "question": "A legal question"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("session_id", response.data)

    def test_extremely_long_question_is_rejected(self):
        response = self.client.post(
            self.url,
            {"question": "q" * 10001},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("question", response.data)

    def test_malformed_json_returns_bad_request(self):
        response = self.client.generic(
            "POST",
            self.url,
            data="{not-json",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("agent.ask_agent", side_effect=RuntimeError("private database detail"))
    def test_agent_failure_returns_generic_error(self, ask_agent):
        response = self.client.post(
            self.url,
            {"question": "A legal question"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["detail"], "Request processing failed.")
        self.assertNotIn("private database detail", str(response.data))

    @patch("agent.search_legal_documents", side_effect=RuntimeError("private tool output"))
    @patch("agent.ask_with_gemini", side_effect=TimeoutError("model unavailable"))
    def test_search_tool_failure_returns_generic_error(self, ask_gemini, search_documents):
        response = self.client.post(
            self.url,
            {"question": "What provisions may apply?"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["detail"], "Request processing failed.")
        self.assertNotIn("private tool output", str(response.data))
        ask_gemini.assert_called_once()
        search_documents.assert_called_once()

    @patch("api.views.ChatSession.objects.get_or_create", side_effect=OperationalError("private database detail"))
    def test_database_failure_returns_generic_error(self, get_or_create):
        response = self.client.post(
            self.url,
            {"question": "A legal question"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["detail"], "Request processing failed.")
        self.assertNotIn("private database detail", str(response.data))
