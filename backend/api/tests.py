from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class AskAPITests(APITestCase):
    def setUp(self):
        self.url = reverse('ask_question')

    def test_ask_valid_request(self):
        payload = {
            "session_id": "abc123",
            "question": "What does Section 123 of BNS say?"
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            "answer": "This is a temporary mock answer.",
            "supported": True,
            "citations": []
        })

    def test_ask_valid_request_without_session_id(self):
        payload = {
            "question": "What is the punishment for theft under BNS?"
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["answer"], "This is a temporary mock answer.")
        self.assertEqual(response.data["supported"], True)
        self.assertEqual(response.data["citations"], [])

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
