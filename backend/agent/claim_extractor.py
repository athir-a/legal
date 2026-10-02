import json
import re


def extract_claims_from_response(text):
    """
    Extract the structured claims JSON embedded in the LLM response.
    """

    if not isinstance(text, str):
        return []

    text = text.strip()

    # Look for a fenced JSON block.
    match = re.search(
        r"```json\s*(\{.*?\})\s*```",
        text,
        re.DOTALL,
    )

    if match:
        json_text = match.group(1)
    else:
        # Fall back to looking for a JSON object containing "claims".
        start = text.find('{"claims"')

        if start == -1:
            return []

        json_text = text[start:]

    try:
        data = json.loads(json_text)
    except json.JSONDecodeError:
        return []

    claims = data.get("claims", [])

    if not isinstance(claims, list):
        return []

    valid_claims = []

    for item in claims:
        if not isinstance(item, dict):
            continue

        claim = str(item.get("claim", "")).strip()
        section = str(item.get("section", "")).strip()

        if not claim or not section:
            continue

        valid_claims.append({
            "claim": claim,
            "citations": [
                {
                    "act": "Consumer Protection Act, 2019",
                    "section": section,
                    "source": "India Code",
                }
            ],
        })

    return valid_claims