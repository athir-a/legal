import json

from pathlib import Path

from rag.retriever import search


BASE_DIR = Path(__file__).resolve().parent.parent
QUESTIONS_FILE = BASE_DIR / "evaluation" / "golden_questions.json"


def main():
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        questions = json.load(f)

    results = []

    for item in questions:
        question = item["question"]
        expected = set(item["expected_sections"])

        retrieved = search(question, top_k=5)

        retrieved_sections = [
            str(result["section_number"])
            for result in retrieved
        ]

        hit1 = bool(
            set(retrieved_sections[:1]) & expected
        )

        hit3 = bool(
            set(retrieved_sections[:3]) & expected
        )

        hit5 = bool(
            set(retrieved_sections[:5]) & expected
        )

        results.append({
            "id": item["id"],
            "question": question,
            "expected": sorted(expected),
            "retrieved": retrieved_sections,
            "hit@1": hit1,
            "hit@3": hit3,
            "hit@5": hit5,
        })

        print(f"\nQ{item['id']}: {question}")
        print(f"Expected : {sorted(expected)}")
        print(f"Retrieved: {retrieved_sections}")
        print(
            f"Hit@1={hit1} | "
            f"Hit@3={hit3} | "
            f"Hit@5={hit5}"
        )

    total = len(results)

    hit1_count = sum(r["hit@1"] for r in results)
    hit3_count = sum(r["hit@3"] for r in results)
    hit5_count = sum(r["hit@5"] for r in results)

    print("\n" + "=" * 50)
    print("RETRIEVAL EVALUATION")
    print("=" * 50)

    print(f"Questions: {total}")
    print(f"Hit@1: {hit1_count}/{total} = {hit1_count / total:.1%}")
    print(f"Hit@3: {hit3_count}/{total} = {hit3_count / total:.1%}")
    print(f"Hit@5: {hit5_count}/{total} = {hit5_count / total:.1%}")

    output_file = BASE_DIR / "evaluation" / "retrieval_results.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nDetailed results saved to: {output_file}")


if __name__ == "__main__":
    main()