import os

from citation_validator import validate_citations
from schemas import LegalAnswer
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from tools import search_legal_documents
from section_lookup import lookup_section

load_dotenv()


@tool
def legal_search(query: str) -> dict:
    """Search the verified legal corpus for relevant evidence."""
    return search_legal_documents(query)


@tool
def legal_section_lookup(act: str, section: str) -> dict:
    """Look up an exact Act and section from the verified legal corpus."""
    return lookup_section(act, section)


SYSTEM_PROMPT = """
You are a legal information research assistant.

Your job is to provide information supported by the verified legal corpus.

Rules:
1. Never invent a legal section or citation.
2. Use legal_search when you need relevant evidence.
3. Use legal_section_lookup when the user asks about a specific Act and section.
4. Only make claims supported by tool results.
5. If the corpus does not contain enough evidence, say that the information
   could not be verified from the available corpus.
6. Do not provide legal advice or tell the user what they should do.
7. Include the Act and section when supported by the evidence.
"""


def create_agent():
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY is not configured. "
            "Add it to agent/.env before running the agent."
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


def ask_agent(question: str):
    agent = create_agent()

    result = agent.invoke({
        "messages": [HumanMessage(content=question)]
    })

    messages = result["messages"]
        # Track token usage for hackathon reporting
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
        f"Token usage | input={total_input_tokens} "
        f"output={total_output_tokens} total={total_tokens}"
    )

    final_message = messages[-1]
    answer_text = final_message.content

    if isinstance(answer_text, list):
        answer_text = "".join(
            item.get("text", "")
            for item in answer_text
            if isinstance(item, dict)
        )

    # Collect verified evidence returned by our tools
    citations = []

    import json

    for message in messages:
        tool_name = getattr(message, "name", None)

        if tool_name == "legal_section_lookup":
            data = json.loads(message.content)

            if data.get("found") is True:
                citations.append({
                    "act": data["act"],
                    "section": str(data["section"]),
                    "page": data.get("page"),
                    "source": data.get("source"),
                })

        elif tool_name == "legal_search":
            data = json.loads(message.content)

            for result in data.get("results", []):
                if result.get("section") is not None:
                    citations.append({
                        "act": result.get("act", ""),
                        "section": str(result.get("section")),
                        "page": result.get("page"),
                        "source": result.get("source"),
                    })

    # Remove duplicate citations
    unique_citations = []

    seen = set()

    for citation in citations:
        key = (
            citation["act"].upper(),
            citation["section"]
        )

        if key not in seen:
            seen.add(key)
            unique_citations.append(citation)

    # Validate every citation against the verified corpus
    validation = validate_citations(unique_citations)

    supported = validation["valid"] and len(unique_citations) > 0

    return LegalAnswer(
        answer=answer_text,
        supported=supported,
        citations=unique_citations,
    )