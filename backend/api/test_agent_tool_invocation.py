import json
from pathlib import Path
import sys
from unittest.mock import patch

from django.test import SimpleTestCase, TransactionTestCase
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

AGENT_PATH = Path(__file__).resolve().parents[2] / "agent"
if str(AGENT_PATH) not in sys.path:
    sys.path.insert(0, str(AGENT_PATH))

import agent as legal_agent
from legaldata.models import LegalDocument
from schemas import LegalAnswer


class ScriptedToolCallingModel(FakeMessagesListChatModel):
    """Script only the model's decisions; LangGraph executes production tools."""

    def bind_tools(self, tools, **kwargs):
        object.__setattr__(self, "bound_tool_names", {tool.name for tool in tools})
        return self


class AgentToolInvocationTests(TransactionTestCase):
    def setUp(self):
        LegalDocument.objects.create(
            act_id="CPA-2019-test",
            act_title="Consumer Protection Act, 2019",
            section_number="2",
            section_title="Section 2. Definitions.",
            text='(9) "consumer rights" includes the right to be informed.',
            source="test legal corpus",
        )

    def test_compound_legal_query_invokes_search_then_exact_lookup(self):
        scripted_responses = [
            AIMessage(content="", tool_calls=[{
                "name": "legal_search",
                "args": {
                    "query": "consumer rights Consumer Protection Act, 2019",
                },
                "id": "search-consumer-rights",
                "type": "tool_call",
            }]),
            AIMessage(content="", tool_calls=[{
                "name": "legal_section_lookup",
                "args": {
                    "act": "Consumer Protection Act, 2019",
                    "section": "2",
                },
                "id": "lookup-section-2",
                "type": "tool_call",
            }]),
            AIMessage(
                content=(
                    "The search found consumer-rights provisions, and the "
                    "exact lookup returned the verified Section 2 text."
                )
            ),
        ]
        model = ScriptedToolCallingModel(responses=scripted_responses)
        graph = legal_agent.create_agent(model=model)
        query = (
            "Search for provisions about consumer rights, then verify the "
            "exact text of the provision identified by the search."
        )

        result = graph.invoke({"messages": [HumanMessage(content=query)]})
        invocations = [
            call
            for message in result["messages"]
            if isinstance(message, AIMessage)
            for call in message.tool_calls
        ]
        tool_results = [
            message
            for message in result["messages"]
            if isinstance(message, ToolMessage)
        ]

        self.assertEqual(
            [call["name"] for call in invocations],
            ["legal_search", "legal_section_lookup"],
        )
        self.assertEqual(
            model.bound_tool_names,
            {"legal_search", "legal_section_lookup"},
        )
        self.assertEqual(
            invocations[0]["args"]["query"],
            "consumer rights Consumer Protection Act, 2019",
        )
        self.assertEqual(invocations[1]["args"]["section"], "2")
        self.assertEqual(
            [message.name for message in tool_results],
            ["legal_search", "legal_section_lookup"],
        )

        search_result = json.loads(tool_results[0].content)
        section_result = json.loads(tool_results[1].content)
        self.assertTrue(any(
            str(result.get("section_number")) == "2"
            for result in search_result["results"]
        ))
        self.assertTrue(section_result["found"])
        self.assertEqual(section_result["section"], "2")
        self.assertIn("right to be informed", section_result["text"])
        self.assertIn("verified Section 2", result["messages"][-1].content)


class AgentFallbackRoutingTests(SimpleTestCase):
    @patch.object(legal_agent, "ask_with_local_fallback")
    @patch.object(
        legal_agent,
        "ask_with_gemini",
        side_effect=TimeoutError("Gemini request timed out"),
    )
    def test_gemini_failure_invokes_existing_fallback_once(
        self,
        ask_gemini,
        local_fallback,
    ):
        expected = LegalAnswer(answer="Fallback result.", supported=False)
        local_fallback.return_value = expected

        result = legal_agent.ask_agent("What provisions may be relevant?")

        self.assertIs(result, expected)
        ask_gemini.assert_called_once()
        local_fallback.assert_called_once_with(
            "What provisions may be relevant?",
            None,
        )
class MalayalamLanguageRoutingTests(SimpleTestCase):
    @patch.object(legal_agent, "ask_with_gemini")
    def test_malayalam_language_is_forwarded_to_gemini(self, ask_gemini):
        expected = LegalAnswer(
            answer="ഇത് മലയാളത്തിലുള്ള നിയമ വിശദീകരണമാണ്.",
            supported=True,
        )
        ask_gemini.return_value = expected

        result = legal_agent.ask_agent(
            "What is product liability?",
            language="ml",
        )

        self.assertIs(result, expected)
        ask_gemini.assert_called_once_with(
            "What is product liability?",
            None,
            language="ml",
        )
