
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
from langchain_core.messages import HumanMessage
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

SYSTEM_PROMPT = """
You are a legal information research assistant.

Your job is to provide information supported ONLY by the verified legal corpus.

Rules:

1. Never invent a legal section or citation.

2. Use legal_search when you need relevant evidence.

3. Use legal_section_lookup when the user asks about a specific Act
   and section.

4. Only make claims supported by tool results.

5. If the corpus does not contain enough evidence, say that the
   information could not be verified from the available corpus.

6. Do not provide legal advice or tell the user what they should do.

7. Every factual legal claim must be traceable to a specific section
   in the retrieved evidence.

8. When possible, cite the most specific section or subsection
   supporting each claim.

9. Do not cite unrelated retrieved sections merely because they were
   returned by the search tool.

10. When answering a question about the Consumer Protection Act, 2019,
    use the verified corpus rather than relying on your own knowledge.

11. Keep the answer concise and clear.

12. At the end of your response, produce a JSON object with this
    structure:

    {
      "claims": [
        {
          "claim": "A factual legal claim from the answer",
          "section": "2"
        }
      ]
    }

13. The section must correspond to a provision actually present in
    the verified legal corpus.

14. Do not invent sections.

15. The final user-facing answer should still be natural and readable.
"""


# ---------------------------------------------------------
# Create the AI agent
# ---------------------------------------------------------

def create_agent():

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
    )

    tools = [
        legal_search,
        legal_section_lookup,
    ]

    return create_react_agent(
        model,
        tools,
        prompt=SYSTEM_PROMPT,
    )


# ---------------------------------------------------------
# Gemini agent path
# ---------------------------------------------------------

def ask_with_gemini(question: str):

    agent = create_agent()

    result = agent.invoke({
        "messages": [
            HumanMessage(content=question)
        ]
    })

    messages = result["messages"]

    # -----------------------------------------------------
    # Token usage
    # -----------------------------------------------------

    total_input_tokens = 0
    total_output_tokens = 0
    total_tokens = 0

    for message in messages:

        usage = getattr(message, "usage_metadata", None)

        if usage:
            total_input_tokens += usage.get("input_tokens", 0)
            total_output_tokens += usage.get("output_tokens", 0)
            total_tokens += usage.get("total_tokens", 0)

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
        answer_text = answer_text[:json_match.start()].strip()

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

        tool_name = getattr(message, "name", None)

        # -------------------------------------------------
        # Exact section lookup
        # -------------------------------------------------

        if tool_name == "legal_section_lookup":

            try:
                data = json.loads(message.content)

            except (TypeError, json.JSONDecodeError):
                continue

            if data.get("found") is True:

                citations.append({
                    "act": data["act"],
                    "section": str(data["section"]),
                    "page": data.get("page"),
                    "source": data.get("source"),
                })

        # -------------------------------------------------
        # Legal search
        # -------------------------------------------------

        elif tool_name == "legal_search":

            try:
                data = json.loads(message.content)

            except (TypeError, json.JSONDecodeError):
                continue

            for result in data.get("results", []):

                section = result.get("section_number")
                act = result.get("act_title")

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
            unique_citations.append(citation)

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

def ask_with_local_fallback(question: str):

    search_result = search_legal_documents(
        question,
        top_k=3
    )

    results = search_result["results"]

    evidence = build_evidence(
        results,
        query=question,
        max_sections=3
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


# ---------------------------------------------------------
# Public agent entry point
# ---------------------------------------------------------

def ask_agent(question: str):
    import re

    # If the user explicitly asks for a section,
    # use the verified section lookup directly.
    match = re.search(r"\bsection\s+(\d+)\b", question, re.IGNORECASE)

    if match:
        section_number = match.group(1)

        result = lookup_section(
            "Consumer Protection Act, 2019",
            section_number
        )

        if result.get("found"):
            return LegalAnswer(
                question=question,
                answer=(
                    f"Section {section_number} of the "
                    f"Consumer Protection Act, 2019 states:\n\n"
                    f"{result['text']}"
                ),
                supported=True,
                citations=[{
                    "act": result["act"],
                    "section": result["section"],
                    "page": result.get("page"),
                    "source": result.get("source"),
                }],
                claim_citations=[]
            )

    # Normal questions still use Gemini, with local RAG fallback.
    try:
        return ask_with_gemini(question)

    except Exception as exc:
        print(
            f"Gemini unavailable. "
            f"Using local RAG fallback. "
            f"Reason: {type(exc).__name__}"
        )

        return ask_with_local_fallback(question)