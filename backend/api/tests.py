import sys
from pathlib import Path
from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

AGENT_PATH = Path(__file__).resolve().parents[2] / "agent"
if str(AGENT_PATH) not in sys.path:
    sys.path.insert(0, str(AGENT_PATH))

from schemas import Citation, LegalAnswer
import agent as legal_agent


class AskAPITests(APITestCase):
    def setUp(self):
        self.url = reverse('ask_question')

    @patch("agent.ask_agent")
    def test_ask_valid_request(self, mock_ask_agent):
        mock_ask_agent.return_value = LegalAnswer(
            answer="Verified answer.",
            supported=True,
            citations=[Citation(
                act="Consumer Protection Act, 2019",
                section="2",
                source="India Code",
            )],
        )
        payload = {
            "session_id": "abc123",
            "question": "What does Section 123 of BNS say?"
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["answer"], "Verified answer.")
        self.assertTrue(response.data["supported"])
        self.assertEqual(response.data["session_id"], "abc123")
        self.assertEqual(response.data["citations"], [{
            "act": "Consumer Protection Act, 2019",
            "section": "2",
            "page": None,
            "source": "India Code",
        }])
        self.assertEqual(response.data["claim_citations"], [])

    @patch("agent.ask_agent")
    def test_ask_valid_request_without_session_id(self, mock_ask_agent):
        mock_ask_agent.return_value = LegalAnswer(
            answer="Verified answer.",
            supported=True,
        )
        payload = {
            "question": "What is the punishment for theft under BNS?"
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["answer"], "Verified answer.")
        self.assertEqual(response.data["supported"], True)
        self.assertEqual(response.data["citations"], [])
        self.assertTrue(response.data["session_id"])

    def test_ask_missing_question(self):
        payload = {
            "session_id": "abc123"
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("question", response.data)

    def test_ask_empty_question(self):
        payload = {
            "session_id": "abc123",
            "question": ""
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("question", response.data)

    def test_ask_whitespace_question(self):
        payload = {
            "session_id": "abc123",
            "question": "   "
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("question", response.data)

    def test_ask_null_question(self):
        payload = {
            "session_id": "abc123",
            "question": None
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("question", response.data)

    def test_get_not_allowed(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class GeminiClientConfigTests(APITestCase):

    @patch.object(legal_agent, "create_react_agent")
    @patch.object(legal_agent, "ChatGoogleGenerativeAI")
    @patch.dict("os.environ", {"GOOGLE_API_KEY": "benchmark-test-key"})
    def test_gemini_uses_single_attempt_and_bounded_timeout(
        self,
        mock_model,
        mock_create_react_agent,
    ):
        legal_agent.create_agent()

        mock_model.assert_called_once_with(
            model="gemini-3.8-flash",
            temperature=0,
            google_api_key="benchmark-test-key",
            timeout=15,
            max_retries=1,
        )
        mock_create_react_agent.assert_called_once()
