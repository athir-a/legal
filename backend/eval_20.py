import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
RAG_PATH = PROJECT_ROOT.parent / "rag"

if str(RAG_PATH) not in sys.path:
    sys.path.insert(0, str(RAG_PATH))

from retriever import search

TESTS = [
    ("What are the rights of consumers?", "2"),
    ("What is the definition of consumer?", "2"),
    ("What is the definition of defect?", "2"),
    ("What is the definition of deficiency?", "2"),
    ("What is the definition of unfair trade practice?", "2"),
    ("What is the definition of misleading advertisement?", "2"),
    ("What is the Central Consumer Protection Authority?", "10"),
    ("What are the powers of the Central Authority?", "18"),
    ("What is the procedure for filing a consumer complaint?", "35"),
    ("Who can file a consumer complaint?", "35"),
    ("What is the limitation period for filing a complaint?", "69"),
    ("What is product liability?", "82"),
    ("When is a product manufacturer liable?", "84"),
    ("When is a product seller liable?", "86"),
    ("When is a product service provider liable?", "87"),
    ("What is mediation under the Act?", "74"),
    ("What is the Consumer Mediation Cell?", "75"),
    ("What is an appeal from the District Commission?", "41"),
    ("What is an appeal from the State Commission?", "51"),
    ("What is an appeal from the National Commission?", "67"),
]

hits1 = 0
hits3 = 0
hits5 = 0

for i, (question, expected_section) in enumerate(TESTS, 1):
    results = search(question, top_k=5)

    sections = [
        str(r.get("section_number", r.get("section", "")))
        for r in results
    ]

    hit1 = expected_section == (sections[0] if sections else "")
    hit3 = expected_section in sections[:3]
    hit5 = expected_section in sections[:5]

    hits1 += hit1
    hits3 += hit3
    hits5 += hit5

    print(
        f"{i:02d}. "
        f"expected={expected_section:<3} "
        f"retrieved={sections} "
        f"Hit@1={'Y' if hit1 else 'N'} "
        f"Hit@3={'Y' if hit3 else 'N'} "
        f"Hit@5={'Y' if hit5 else 'N'}"
    )

print()
print("=== 20-QUESTION EVALUATION ===")
print(f"Hit@1: {hits1}/20 = {hits1/20*100:.1f}%")
print(f"Hit@3: {hits3}/20 = {hits3/20*100:.1f}%")
print(f"Hit@5: {hits5}/20 = {hits5/20*100:.1f}%")
