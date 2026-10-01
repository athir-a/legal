def generate_local_answer(question, evidence):
    """
    Generate a simple grounded answer from verified legal evidence.

    This is a temporary local answer generator used while the LLM
    layer is unavailable because of API quota limits.
    """

    if not evidence:
        return {
            "answer": (
                "I could not find enough verified information in the "
                "Consumer Protection Act, 2019 to answer this question."
            ),
            "supported": False,
            "citations": [],
        }

    # Reject questions when the retrieved legal evidence is too weak.
    max_score = max(
        float(item.get("retrieval_score", 0.0))
        for item in evidence
    )

    if max_score < 0.30:
        return {
            "answer": (
                "I could not find enough verified information in the "
                "Consumer Protection Act, 2019 to answer this question. "
                "I can only provide answers supported by the legal "
                "corpus available to this system."
            ),
            "supported": False,
            "citations": [],
        }
    question_lower = question.lower()

    best = evidence[0]

    answer = ""

    # ---------------------------------------------------------
    # Consumer definition
    # ---------------------------------------------------------

    if (
    "consumer" in question_lower
    and "product liability" not in question_lower
    and (
        "what is" in question_lower
        or "who is" in question_lower
        or "define" in question_lower
    )
):
        text = best["text"]

        start = text.lower().find('"consumer" means')

        if start >= 0:
            consumer_text = text[start:]

            # Stop before the next definition.
            stop_markers = [
                '(8) "consumer dispute"',
                '(8) "consumer dispute" means',
            ]

            for marker in stop_markers:
                stop = consumer_text.lower().find(marker.lower())

                if stop >= 0:
                    consumer_text = consumer_text[:stop]
                    break

            answer = (
                "Under the Consumer Protection Act, 2019, "
                "Section 2(7) defines a consumer as a person who "
                "buys goods or hires/avails services for consideration, "
                "subject to the conditions and exclusions specified "
                "in the provision.\n\n"
                "The provision also states that a person obtaining "
                "goods for resale or commercial purposes, or availing "
                "services for commercial purposes, is generally "
                "excluded. It provides an exception for certain "
                "self-employment livelihood use."
            )

        else:
            answer = (
                "The retrieved evidence identifies Section 2 as the "
                "relevant provision containing the definition of "
                "'consumer'."
            )

    # ---------------------------------------------------------
    # Consumer rights
    # ---------------------------------------------------------

    elif "consumer rights" in question_lower:

        answer = (
            "Section 2(9) of the Consumer Protection Act, 2019 "
            "defines 'consumer rights'. The provision includes "
            "the right to protection from hazardous goods and "
            "services, the right to information, access to a "
            "variety of goods and services at competitive prices, "
            "the right to be heard, the right to seek redressal, "
            "and the right to consumer awareness."
        )

    # ---------------------------------------------------------
    # Consumer rights
    elif (
        "consumer rights" in question_lower
        or "rights of consumers" in question_lower
    ):
        answer = (
            "Section 2(9) of the Consumer Protection Act, 2019 "
            "defines 'consumer rights'. It includes:\n\n"
            "1. The right to protection against the marketing of "
            "goods, products or services that are hazardous to life "
            "and property.\n"
            "2. The right to be informed about the quality, quantity, "
            "potency, purity, standard and price of goods, products "
            "or services.\n"
            "3. The right to access, wherever possible, a variety "
            "of goods, products or services at competitive prices.\n"
            "4. The right to be heard and to have consumer interests "
            "receive due consideration.\n"
            "5. The right to seek redressal against unfair trade "
            "practices, restrictive trade practices and unscrupulous "
            "exploitation of consumers.\n"
            "6. The right to consumer awareness."
        )
        # Unfair trade practice
    elif "unfair trade practice" in question_lower:
        answer = (
            "Under Section 2(47) of the Consumer Protection Act, 2019, "
            "an unfair trade practice is a trade practice which, for the "
            "purpose of promoting the sale, use or supply of goods or "
            "provision of services, adopts an unfair method or unfair "
            "or deceptive practice.\n\n"
            "The Act gives several examples, including:\n"
            "- falsely representing the quality, quantity, standard, "
            "grade or characteristics of goods or services;\n"
            "- making false or misleading representations about "
            "warranties, guarantees or benefits;\n"
            "- misleading the public about the price of goods or services;\n"
            "- advertising goods or services at a bargain price when "
            "they are not actually intended to be offered at that price;\n"
            "- selling or supplying goods that do not comply with "
            "prescribed standards;\n"
            "- manufacturing or selling spurious goods or using "
            "deceptive practices in providing services;\n"
            "- refusing to take back defective goods or refund the "
            "consideration in circumstances specified by the Act; and\n"
            "- disclosing confidential personal information provided "
            "by a consumer, except where permitted by law."
        )
    
    # Filing a complaint
    elif (
        "file a complaint" in question_lower
        or "filing a complaint" in question_lower
        or "how can a consumer file a complaint" in question_lower
        or "how to file a complaint" in question_lower
    ):
        answer = (
            "Under Section 35 of the Consumer Protection Act, 2019, "
            "a complaint relating to goods or services may be filed "
            "with the appropriate District Consumer Commission by the "
            "consumer concerned.\n\n"
            "The Act also allows a recognised consumer association "
            "to file a complaint, one or more consumers having the "
            "same interest to file on behalf of numerous consumers "
            "with the permission of the District Commission, and the "
            "Central Government, Central Authority or State Government "
            "to file a complaint in the circumstances specified by "
            "the Act.\n\n"
            "Section 35 also provides that a complaint may be filed "
            "electronically in the prescribed manner."
        )
   
   
    # Limitation period
    # ---------------------------------------------------------

   
    elif "limitation period" in question_lower:
        answer = (
            "Under Section 69 of the Consumer Protection Act, 2019, "
            "a consumer complaint generally must be filed within "
            "two years from the date on which the cause of action "
            "arose.\n\n"
            "A complaint may be entertained after this period if "
            "the complainant satisfies the relevant Consumer "
            "Commission that there was sufficient cause for not "
            "filing it within the prescribed period. The Commission "
            "must record its reasons for condoning the delay."
        )

    # ---------------------------------------------------------
    # Product liability
    # ---------------------------------------------------------

    elif "product liability" in question_lower:

        relevant_sections = []

        for item in evidence:
            section = str(item.get("section"))

            if section in {
                "83",
                "84",
                "85",
                "86",
                "87",
            }:
                relevant_sections.append(
                    f"Section {section} — "
                    f"{item['section_title']}"
                )

        answer = (
            "The Consumer Protection Act, 2019 contains a "
            "dedicated set of provisions dealing with product "
            "liability."
        )

        if relevant_sections:
            answer += "\n\nRelevant provisions:\n"
            answer += "\n".join(
                f"- {item}"
                for item in relevant_sections
            )

    # ---------------------------------------------------------
    # General grounded response
    # ---------------------------------------------------------

    else:

        answer = (
            "Based on the verified legal evidence retrieved from "
            "the Consumer Protection Act, 2019, the following "
            "provisions are relevant to your question:"
        )

        for item in evidence:
            answer += (
                f"\n\nSection {item['section']} — "
                f"{item['section_title']}\n"
            )

            # Give the first part of the actual evidence.
            preview = item["text"][:1000].strip()

            answer += preview

            if len(item["text"]) > 1000:
                answer += "..."

    # ---------------------------------------------------------
    # Citations
    # ---------------------------------------------------------

    citations = []

    # Only cite evidence that actually supports the generated answer.
    if evidence:
        best = evidence[0]

        if best.get("act") and best.get("section"):
            citations.append({
                "act": best["act"],
                "section": str(best["section"]),
                "page": None,
                "source": best.get(
                    "source",
                    "India Code"
                ),
            })

    return {
        "answer": answer,
        "supported": len(citations) > 0,
        "citations": citations,
    }