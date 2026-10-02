import os
import json
import re
import sys
from pathlib import Path


# ---------------------------------------------------------
# Make sure Python can find files inside the agent folder
# ---------------------------------------------------------

AGENT_PATH = Path(__file__).resolve().parent

if str(AGENT_PATH) not in sys.path:
    sys.path.insert(0, str(AGENT_PATH))


# ---------------------------------------------------------
# Imports
# ---------------------------------------------------------

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from citation_validator import validate_citations
from claim_verifier import verify_citations
from claim_extractor import extract_claims_from_response
from claim_mapper import map_claims_to_citations
from schemas import LegalAnswer
from tools import search_legal_documents
from section_lookup import lookup_section
from evidence import build_evidence
from local_answer import generate_local_answer


# ---------------------------------------------------------
# Load .env
# ---------------------------------------------------------

load_dotenv(AGENT_PATH / ".env")


# ---------------------------------------------------------
# Tool 1: Legal search
# ---------------------------------------------------------

@tool
def legal_search(query: str) -> dict:
    """Search the verified legal corpus for relevant evidence."""
    return search_legal_documents(query)


# ---------------------------------------------------------
# Tool 2: Exact section lookup
# ---------------------------------------------------------

@tool
def legal_section_lookup(act: str, section: str) -> dict:
    """Look up an exact Act and section from the verified legal corpus."""
    return lookup_section(act, section)


# ---------------------------------------------------------
# System prompt
# ---------------------------------------------------------

PROMPT_VERSION = "v1"
PROMPT_PATH = AGENT_PATH.parent / "prompts" / PROMPT_VERSION / "system.txt"

SYSTEM_PROMPT = PROMPT_PATH.read_text(encoding="utf-8")


# ---------------------------------------------------------
# Language instructions
# ---------------------------------------------------------

LANGUAGE_INSTRUCTIONS = {
    "en": """
Respond in English.

Keep legal section numbers, Act names, subsection references,
and citations exactly identifiable from the retrieved evidence.
""",
    "ml": """
Respond in Malayalam.

Important requirements:

1. Explain the legal information naturally and clearly in Malayalam.

2. Keep legal section numbers exactly as they appear in the evidence.

3. Keep the official Act name and other legal provision names
   identifiable. You may explain them in Malayalam, but do not
   replace or invent their legal identifiers.

4. Every factual legal claim must remain supported by the
   retrieved legal evidence.

5. Do not translate a legal citation into a different section
   number or invent a Malayalam legal citation.

6. Do not provide legal advice or tell the user what they should do.

7. If the available legal corpus does not contain enough evidence,
   say so clearly in Malayalam.

8. For scenario questions, distinguish the user's described facts
   from what the retrieved law establishes.

9. Do not promise a refund, replacement, compensation, liability,
   or any other legal outcome unless the retrieved evidence
   explicitly establishes it.

10. The final answer should be readable Malayalam, not a
    word-by-word machine translation.

11. Preserve the traceability of the answer to the retrieved
    legal provisions.
"""
}


def _get_language_instruction(language: str) -> str:
    """
    Return the response-language instruction.

    English is the safe default for backward compatibility.
    """

    return LANGUAGE_INSTRUCTIONS.get(
        language,
        LANGUAGE_INSTRUCTIONS["en"]
    )


# ---------------------------------------------------------
# Create the AI agent
# ---------------------------------------------------------

def create_agent(model=None, language="en"):

    if model is None:
        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GOOGLE_API_KEY is not configured. "
                "Make sure it is present in agent/.env"
            )

        model = ChatGoogleGenerativeAI(
            model="gemini-3.8-flash",
            temperature=0,
            google_api_key=api_key,
            timeout=15,
            max_retries=1,
        )

    tools = [
        legal_search,
        legal_section_lookup,
    ]

    language_instruction = _get_language_instruction(language)

    prompt = SYSTEM_PROMPT + "\n\n" + language_instruction

    return create_react_agent(
        model,
        tools,
        prompt=prompt,
    )


# ---------------------------------------------------------
# Gemini agent path
# ---------------------------------------------------------

def ask_with_gemini(
    question: str,
    conversation_history=None,
    language="en",
):

    agent = create_agent(language=language)
    messages = []

    for turn in (conversation_history or [])[-6:]:
        previous_question = str(
            turn.get("question", "")
        )[:2000]

        previous_answer = str(
            turn.get("answer", "")
        )[:5000]

        if previous_question and previous_answer:
            messages.append(
                HumanMessage(content=previous_question)
            )

            messages.append(
                AIMessage(content=previous_answer)
            )

    messages.append(
        HumanMessage(content=question)
    )

    result = agent.invoke({
        "messages": messages
    })

    messages = result["messages"]

    # -----------------------------------------------------
    # Token usage
    # -----------------------------------------------------

    total_input_tokens = 0
    total_output_tokens = 0
    total_tokens = 0

    for message in messages:

        usage = getattr(
            message,
            "usage_metadata",
            None
        )

        if usage:
            total_input_tokens += usage.get(
                "input_tokens",
                0
            )

            total_output_tokens += usage.get(
                "output_tokens",
                0
            )

            total_tokens += usage.get(
                "total_tokens",
                0
            )

    print(
        f"Token usage | "
        f"input={total_input_tokens} "
        f"output={total_output_tokens} "
        f"total={total_tokens}"
    )

    # -----------------------------------------------------
    # Final answer
    # -----------------------------------------------------

    final_message = messages[-1]

    raw_response = final_message.content

    # Gemini/LangChain can sometimes return content as a list
    if isinstance(raw_response, list):

        raw_response = "".join(
            item.get("text", "")
            for item in raw_response
            if isinstance(item, dict)
        )

    raw_response = str(raw_response)

    answer_text = raw_response

    # -----------------------------------------------------
    # Remove internal claims JSON from user-facing answer
    # -----------------------------------------------------

    json_match = re.search(
        r"```json\s*(\{.*?\})\s*```",
        answer_text,
        re.DOTALL,
    )

    if json_match:
        answer_text = answer_text[
            :json_match.start()
        ].strip()

    # -----------------------------------------------------
    # Extract structured claim citations
    # -----------------------------------------------------

    structured_claims = extract_claims_from_response(
        raw_response
    )

    claim_citations = map_claims_to_citations(
        structured_claims
    )

    # -----------------------------------------------------
    # Enforce claim-level citation support
    # -----------------------------------------------------

    all_claims_supported = (
        len(claim_citations) > 0
        and all(
            claim.get("supported", False)
            and len(claim.get("citations", [])) > 0
            for claim in claim_citations
        )
    )

    # -----------------------------------------------------
    # Collect citations from tool calls
    # -----------------------------------------------------

    citations = []

    for message in messages:

        tool_name = getattr(
            message,
            "name",
            None
        )

        # -------------------------------------------------
        # Exact section lookup
        # -------------------------------------------------

        if tool_name == "legal_section_lookup":

            try:
                data = json.loads(
                    message.content
                )

            except (
                TypeError,
                json.JSONDecodeError
            ):
                continue

            if data.get("found") is True:

                citations.append({
                    "act": data["act"],
                    "section": str(
                        data["section"]
                    ),
                    "page": data.get("page"),
                    "source": data.get("source"),
                })

        # -------------------------------------------------
        # Legal search
        # -------------------------------------------------

        elif tool_name == "legal_search":

            try:
                data = json.loads(
                    message.content
                )

            except (
                TypeError,
                json.JSONDecodeError
            ):
                continue

            for result in data.get(
                "results",
                []
            ):

                section = result.get(
                    "section_number"
                )

                act = result.get(
                    "act_title"
                )

                if section is not None and act:

                    citations.append({
                        "act": act,
                        "section": str(section),
                        "page": None,
                        "source": result.get(
                            "source",
                            "India Code"
                        ),
                    })

    # -----------------------------------------------------
    # Remove duplicate citations
    # -----------------------------------------------------

    unique_citations = []

    seen = set()

    for citation in citations:

        key = (
            citation["act"].upper(),
            citation["section"],
        )

        if key not in seen:

            seen.add(key)

            unique_citations.append(
                citation
            )

    # -----------------------------------------------------
    # Validate citations
    # -----------------------------------------------------

    validation = verify_citations(
        unique_citations
    )

    supported = (
        validation["valid"]
        and len(unique_citations) > 0
        and all_claims_supported
    )

    # -----------------------------------------------------
    # Return structured answer
    # -----------------------------------------------------

    return LegalAnswer(
        answer=answer_text,
        supported=supported,
        citations=unique_citations,
        claim_citations=claim_citations,
    )


# ---------------------------------------------------------
# Local fallback path
# ---------------------------------------------------------

def ask_with_local_fallback(
    question: str,
    conversation_history=None,
    language="en",
):

    retrieval_query = _query_with_recent_context(
        question,
        conversation_history,
    )

    search_result = search_legal_documents(
        retrieval_query,
        top_k=10
    )

    results = search_result["results"]

    evidence = build_evidence(
        results,
        query=retrieval_query,
        max_sections=5
    )

    answer_result = generate_local_answer(
        question,
        evidence
    )

    # -----------------------------------------------------
    # Validate fallback citations too
    # -----------------------------------------------------

    validation = verify_citations(
        answer_result.get("citations", [])
    )

    supported = (
        answer_result.get("supported", False)
        and validation["valid"]
    )

    return LegalAnswer(
        answer=answer_result["answer"],
        supported=supported,
        citations=answer_result.get(
            "citations",
            []
        ),
        claim_citations=[],
    )


def _query_with_recent_context(
    question,
    conversation_history,
):

    if not conversation_history:
        return question

    follow_up_reference = re.search(
        r"\b(it|this|that|these|those|them|one|former|latter|"
        r"first|second|third|above|previous|same)\b",
        question,
        re.IGNORECASE,
    )

    if not follow_up_reference:
        return question

    previous_turn = conversation_history[-1]

    context = " ".join((
        str(
            previous_turn.get(
                "question",
                ""
            )
        )[:1000],

        str(
            previous_turn.get(
                "answer",
                ""
            )
        )[:3000],
    )).strip()

    context = " ".join(
        context.split()
    )

    if not context:
        return question

    return (
        f"{context} "
        f"Follow-up: {question}"
    )


# ---------------------------------------------------------
# Public agent entry point
# ---------------------------------------------------------

def ask_agent(
    question: str,
    conversation_history=None,
    language="en",
):

    # If the user explicitly asks for a section,
    # use the verified section lookup directly.

    match = re.search(
        r"\bsection\s+(\d+)\b",
        question,
        re.IGNORECASE,
    )

    if match:

        section_number = match.group(1)

        result = lookup_section(
            "Consumer Protection Act, 2019",
            section_number
        )

        if result.get("found"):

            answer = (
                f"Section {section_number} of the "
                f"Consumer Protection Act, 2019 states:\n\n"
                f"{result['text']}"
            )

            # Keep exact section lookup behavior unchanged
            # for English. For Malayalam, preserve the legal
            # provision verbatim so its wording remains
            # traceable to the verified corpus.
            if language == "ml":
                answer = (
                    f"Consumer Protection Act, 2019-ലെ "
                    f"Section {section_number}:\n\n"
                    f"{result['text']}"
                )

            return LegalAnswer(
                question=question,
                answer=answer,
                supported=True,
                citations=[{
                    "act": result["act"],
                    "section": result["section"],
                    "page": result.get("page"),
                    "source": result.get("source"),
                }],
                claim_citations=[]
            )

    # Normal questions still use Gemini,
    # with local RAG fallback.

    try:

        if language == "ml":
            return ask_with_gemini(
                question,
                conversation_history,
                language=language,
            )

        return ask_with_gemini(
            question,
            conversation_history,
        )

    except Exception as exc:

        print(
            f"Gemini unavailable. "
            f"Using local RAG fallback. "
            f"Reason: {type(exc).__name__}"
        )

        if language == "ml":
            return ask_with_local_fallback(
                question,
                conversation_history,
                language=language,
            )

        return ask_with_local_fallback(
            question,
            conversation_history,
        )