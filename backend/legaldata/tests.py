import os
import sys

from django.test import TestCase

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if os.path.join(PROJECT_ROOT, 'agent') not in sys.path:
    sys.path.insert(0, os.path.join(PROJECT_ROOT, 'agent'))

from tools import expand_legal_query, search_legal_documents
from retriever import search as tfidf_search
from evidence import build_evidence, extract_relevant_text
from local_answer import generate_local_answer
from agent import _query_with_recent_context, ask_with_local_fallback
from legaldata.models import LegalChunk, LegalDocument


class SearchLegalDocumentsFallbackTests(TestCase):

    def test_search_returns_tfidf_results_when_db_corpus_is_empty(self):
        result = search_legal_documents(
            'What are the rights of consumers under the Consumer Protection Act, 2019?',
            top_k=5,
        )

        self.assertGreater(len(result.get('results', [])), 0)
        self.assertIn('section_number', result['results'][0])


class LegalQueryExpansionTests(TestCase):

    def test_defective_laptop_scenario_adds_generic_defect_terms(self):
        expanded = expand_legal_query(
            "new laptop arrived with a motherboard defect and will not boot"
        ).casefold()

        self.assertIn("defective product", expanded)
        self.assertIn("manufacturing defect", expanded)

    def test_seller_refusal_adds_seller_defect_and_remedy_terms(self):
        expanded = expand_legal_query(
            "seller refused to replace my faulty product"
        ).casefold()

        self.assertIn("product seller", expanded)
        self.assertIn("defective product", expanded)
        self.assertIn("replace goods", expanded)
        self.assertIn("consumer redressal", expanded)

    def test_online_service_center_scenario_adds_both_concepts(self):
        expanded = expand_legal_query(
            "online store told me to contact the authorized service center"
        ).casefold()

        self.assertIn("e-commerce entity", expanded)
        self.assertIn("product service provider", expanded)

    def test_compensation_for_defective_goods_adds_redressal_terms(self):
        expanded = expand_legal_query(
            "customer wants compensation for defective goods"
        ).casefold()

        self.assertIn("defective product", expanded)
        self.assertIn("consumer redressal", expanded)
        self.assertIn("compensation", expanded)

    def test_existing_legal_language_is_preserved(self):
        query = "When is a product manufacturer liable for a manufacturing defect?"

        expanded = expand_legal_query(query)

        self.assertTrue(expanded.startswith(query))
        self.assertIn("product manufacturer", expanded.casefold())
        self.assertIn("manufacturing defect", expanded.casefold())

    def test_defect_definition_adds_statutory_terminology(self):
        expanded = expand_legal_query(
            "What does the Act mean by a defect in goods?"
        ).casefold()

        self.assertIn("defect means any fault", expanded)
        self.assertIn("shortcoming quality quantity potency purity standard", expanded)

    def test_case_specific_compensation_question_is_not_defect_definition(self):
        query = (
            "What exact compensation did the Supreme Court award in 2022 "
            "in Sharma v. ABC Electronics for a refrigerator defect?"
        )

        self.assertNotIn(
            "defect means any fault",
            expand_legal_query(query).casefold(),
        )

    def test_complaint_filing_expansion_uses_filing_concepts(self):
        expanded = expand_legal_query(
            "Who can file a consumer complaint and how may it be filed?"
        ).casefold()

        self.assertIn("consumer complaint filed by consumer", expanded)
        self.assertIn("recognised consumer association", expanded)
        self.assertIn("electronically", expanded)

    def test_post_admission_complaint_procedure_is_not_filing_expanded(self):
        query = (
            "What procedure does the District Commission follow "
            "after admitting a complaint?"
        )

        expanded = expand_legal_query(query).casefold()

        self.assertNotIn("persons entitled to file", expanded)
        self.assertNotIn("recognised consumer association", expanded)

    def test_descriptive_online_store_phrase_adds_ecommerce_terms(self):
        expanded = expand_legal_query(
            "An online electronics store sold me a product."
        ).casefold()

        self.assertIn("e-commerce entity", expanded)

    def test_ecommerce_measure_question_adds_measurement_terminology(self):
        expanded = expand_legal_query(
            "What consumer-protection measures may be prescribed for e-commerce entities?"
        ).casefold()

        self.assertIn("measures to prevent unfair trade practices in e-commerce", expanded)

    def test_unrelated_question_gets_no_unrelated_expansion(self):
        query = "How does rainfall affect the migration of monarch butterflies?"

        self.assertEqual(expand_legal_query(query), query)

    def test_expansion_is_bounded_and_contains_no_section_numbers(self):
        query = (
            "A faulty damaged online product seller sent me to a service center "
            "and refused refund replacement repair compensation"
        )
        added_terms = expand_legal_query(query)[len(query):].split()

        self.assertLessEqual(len(added_terms), 40)
        self.assertFalse(any(term.isdigit() for term in added_terms))

    def test_known_benchmark_misses_retrieve_expected_sections(self):
        cases = (
            ("What does the Act mean by a defect in goods?", "2"),
            ("Who can file a consumer complaint and how may it be filed?", "35"),
            (
                "What consumer-protection measures may be prescribed for e-commerce entities?",
                "94",
            ),
        )

        for question, expected_section in cases:
            with self.subTest(question=question):
                results = tfidf_search(
                    question,
                    top_k=10,
                    retrieval_query=expand_legal_query(question),
                )
                expected = next(
                    item for item in results
                    if str(item.get("section_number")) == expected_section
                )
                self.assertGreaterEqual(expected["score"], 0.30)

    def test_laptop_scenario_retrieves_multiple_supported_concepts(self):
        question = (
            "I ordered a brand-new laptop for ₹64,000 from an online electronics "
            "store. When it arrived, the internal motherboard was malfunctioning "
            "and it would not boot. I reported it within 24 hours, but the seller "
            "refused a replacement or refund, telling me to contact the authorized "
            "brand service center instead."
        )

        results = tfidf_search(
            question,
            top_k=10,
            retrieval_query=expand_legal_query(question),
        )
        adequately_scored = {
            str(item["section_number"])
            for item in results
            if item["score"] >= 0.30
        }

        self.assertTrue({"83", "84", "85", "86"}.issubset(adequately_scored))

    def test_corpus_gap_question_remains_below_evidence_floor(self):
        question = (
            "What exact compensation did the Supreme Court award in 2022 in "
            "Sharma v. ABC Electronics for a refrigerator defect?"
        )

        results = tfidf_search(
            question,
            top_k=10,
            retrieval_query=expand_legal_query(question),
        )

        self.assertLess(max(item["score"] for item in results), 0.30)


class LocalAnswerCitationTests(TestCase):

    @staticmethod
    def evidence_for(*sections):
        return [
            {
                "act": "Consumer Protection Act, 2019",
                "section": str(section),
                "section_title": "Test provision.",
                "text": "Verified provision text for this section.",
                "source": "India Code",
                "retrieval_score": 0.9,
            }
            for section in sections
        ]

    def test_product_liability_cites_all_sections_83_through_87(self):
        result = generate_local_answer(
            "What is product liability under the Consumer Protection Act, 2019?",
            self.evidence_for(83, 84, 85, 86, 87),
        )

        self.assertEqual(
            {citation["section"] for citation in result["citations"]},
            {"83", "84", "85", "86", "87"},
        )
        self.assertTrue(all(f"Section {section} —" in result["answer"] for section in (83, 84, 85, 86, 87)))

    def test_consumer_rights_cites_section_2(self):
        result = generate_local_answer(
            "What are the rights of consumers under the Consumer Protection Act, 2019?",
            self.evidence_for(2),
        )

        self.assertEqual([item["section"] for item in result["citations"]], ["2"])
        self.assertIn("### Section 2 — Test provision.", result["answer"])
        self.assertIn("Evidence excerpt:\nVerified provision text", result["answer"])

    def test_limitation_period_cites_section_69(self):
        result = generate_local_answer(
            "What is the limitation period for filing a consumer complaint?",
            self.evidence_for(69),
        )

        self.assertEqual([item["section"] for item in result["citations"]], ["69"])
        self.assertIn("### Section 69 — Test provision.", result["answer"])
        self.assertEqual(result["answer"].count("### Section"), 1)

    def test_generic_multi_section_answer_preserves_each_citation(self):
        result = generate_local_answer(
            "Which provisions govern complaints and limitation?",
            self.evidence_for(35, 69),
        )

        self.assertEqual(
            [item["section"] for item in result["citations"]],
            ["35", "69"],
        )
        self.assertIn("Section 35 —", result["answer"])
        self.assertIn("Section 69 —", result["answer"])

    def test_long_evidence_is_identified_as_an_excerpt(self):
        evidence = self.evidence_for(69)
        evidence[0]["text"] = "A legal passage. " * 100

        result = generate_local_answer(
            "What is the limitation period?",
            evidence,
        )

        self.assertIn("Evidence excerpt:", result["answer"])
        self.assertTrue(result["answer"].endswith("…"))

    def test_insufficient_evidence_stays_unsupported_without_citations(self):
        result = generate_local_answer("What is the legal answer?", [])

        self.assertFalse(result["supported"])
        self.assertEqual(result["citations"], [])

    def test_explicit_follow_up_uses_previous_turn_context(self):
        prior_turn = {
            "question": "What are the basic rights of consumers?",
            "answer": "Section 2 describes consumer rights, including information and redressal.",
        }

        query = _query_with_recent_context(
            "Explain the second one.",
            [prior_turn],
        )

        self.assertIn(prior_turn["question"], query)
        self.assertIn(prior_turn["answer"], query)
        self.assertTrue(query.endswith("Follow-up: Explain the second one."))

    def test_standalone_corpus_gap_query_ignores_prior_legal_context(self):
        prior_turn = {
            "question": "What is product liability?",
            "answer": "Sections 82 to 86 discuss product liability.",
        }
        question = (
            "What exact compensation did the Supreme Court award in 2022 "
            "in Sharma v. ABC Electronics for a refrigerator defect?"
        )

        self.assertEqual(
            _query_with_recent_context(question, [prior_turn]),
            question,
        )
        result = ask_with_local_fallback(question, [prior_turn])
        self.assertFalse(result.supported)
        self.assertEqual(result.citations, [])


class ScenarioSynthesisTests(TestCase):
    @staticmethod
    def product_evidence():
        provisions = (
            ("82", "Application of Chapter", "This Chapter applies to every claim for compensation under a product liability action for harm caused by a defective product manufactured by a product manufacturer or serviced by a product service provider or sold by a product seller."),
            ("83", "Product liability action", "A product liability action may be brought against a product manufacturer, product service provider or product seller for harm caused by a defective product."),
            ("84", "Liability of product manufacturer", "A product manufacturer shall be liable if a product contains a manufacturing defect, is defective in design, deviates from manufacturing specifications, or does not conform to the express warranty."),
            ("85", "Liability of product service provider", "A product service provider shall be liable if the service provided was faulty or imperfect or deficient or inadequate in quality, nature or manner of performance."),
            ("86", "Liability of product sellers", "A product seller who is not a product manufacturer shall be liable if he exercised substantial control over the product, altered or modified it, or made an express warranty that the product failed to meet."),
        )
        return [
            {
                "act": "Consumer Protection Act, 2019",
                "section": section,
                "section_title": title,
                "text": text,
                "source": "India Code",
                "retrieval_score": 0.8,
            }
            for section, title, text in provisions
        ]

    def test_laptop_scenario_explains_facts_without_promising_remedy(self):
        question = (
            "I ordered a brand-new laptop for ₹64,000 from an online electronics "
            "store. When it arrived, the internal motherboard was malfunctioning "
            "and it would not boot. I reported it within 24 hours, but the seller "
            "refused a replacement or refund, telling me to contact the authorized "
            "brand service center instead."
        )

        result = generate_local_answer(question, self.product_evidence())

        self.assertTrue(result["supported"])
        self.assertIn("What the retrieved law means for your situation", result["answer"])
        self.assertIn("How the retrieved provisions relate to the facts you described", result["answer"])
        self.assertIn("What the retrieved provisions do not establish", result["answer"])
        self.assertIn("You described:", result["answer"])
        self.assertIn("malfunctioning", result["answer"])
        self.assertIn("manufacturer", result["answer"].casefold())
        self.assertIn("product seller", result["answer"].casefold())
        self.assertIn("product service provider", result["answer"].casefold())
        self.assertNotIn("online or e-commerce transaction", result["answer"].casefold())
        self.assertIn("including a manufacturing defect", result["answer"])
        self.assertIn("faulty, deficient, or inadequate", result["answer"])
        self.assertIn("substantial control over the product", result["answer"])
        self.assertNotIn("the seller must refund", result["answer"].casefold())
        self.assertNotIn("you are entitled to a replacement", result["answer"].casefold())
        self.assertNotIn("Section 39", result["answer"])
        self.assertEqual(
            {citation["section"] for citation in result["citations"]},
            {"82", "83", "84", "85", "86"},
        )
        self.assertIn("Evidence excerpt:", result["answer"])

    def test_appliance_story_uses_the_same_generic_scenario_path(self):
        question = (
            "I bought an appliance online and it arrived damaged. "
            "The seller says I must deal with the manufacturer."
        )

        result = generate_local_answer(question, self.product_evidence())

        self.assertIn("What the retrieved law means for your situation", result["answer"])
        self.assertIn("I bought an appliance online", result["answer"])
        self.assertIn("Section 84", result["answer"])
        self.assertIn("Section 86", result["answer"])

    def test_short_non_laptop_narratives_use_scenario_format(self):
        for question in (
            "My online store sent me the wrong phone.",
            "I paid for a service but the service was never provided.",
            "A product I purchased developed a defect.",
            "A company refused to honour the warranty.",
        ):
            with self.subTest(question=question):
                result = generate_local_answer(question, self.product_evidence())
                self.assertIn(
                    "What the retrieved law means for your situation",
                    result["answer"],
                )

    def test_simple_question_does_not_get_scenario_sections(self):
        result = generate_local_answer(
            "What is product liability?",
            self.product_evidence(),
        )

        self.assertNotIn("What the retrieved law means for your situation", result["answer"])
        self.assertTrue(result["answer"].startswith("Retrieved legal provisions:"))

    def test_remedy_question_only_cites_provided_evidence(self):
        evidence = self.product_evidence()[:2]
        result = generate_local_answer(
            "I bought a product and the seller refused my refund.",
            evidence,
        )

        self.assertEqual(
            {citation["section"] for citation in result["citations"]},
            {"82", "83"},
        )
        self.assertNotIn("Section 39", result["answer"])
        self.assertIn("do not by themselves establish", result["answer"])

    def test_scenario_without_selected_evidence_remains_unsupported(self):
        question = "I bought a product and the seller refused to help when it failed."

        result = generate_local_answer(question, [])

        self.assertFalse(result["supported"])
        self.assertEqual(result["citations"], [])
        self.assertNotIn("What the retrieved law means for your situation", result["answer"])


class EvidenceSectionTitleTests(TestCase):

    def test_consumer_rights_query_selects_rights_definition(self):
        text = (
            '(7) "consumer" means a person who buys goods.\n\n'
            '(9) "consumer rights" includes the right to be informed.'
        )

        excerpt = extract_relevant_text(
            text,
            "What are the rights of consumers?",
        )

        self.assertIn('(9) "consumer rights"', excerpt)
        self.assertNotIn('(7) "consumer"', excerpt)

    def test_concatenated_section_heading_is_removed_from_title(self):
        document = LegalDocument.objects.create(
            act_id="CPA-2019",
            act_title="Consumer Protection Act, 2019",
            section_number="83",
            section_title=(
                "Section 83. Product liability action "
                "84. Liability of product manufacturer."
            ),
            text="Product liability action text.",
            source="India Code",
        )
        chunk = LegalChunk.objects.create(
            document=document,
            chunk_index=0,
            text="Product liability action text.",
        )

        evidence = build_evidence(
            [{
                "chunk_id": chunk.id,
                "document_id": document.id,
                "section_number": "83",
                "section_title": document.section_title,
                "act_title": document.act_title,
                "score": 0.9,
                "source": document.source,
            }],
            query="What is product liability?",
        )

        self.assertEqual(evidence[0]["section_title"], "Product liability action")
        self.assertTrue(evidence[0]["text"].startswith("Product liability action text."))
        self.assertNotIn("84. Liability of product manufacturer", evidence[0]["text"])

    def test_adjacent_chunk_overlap_is_not_repeated_in_evidence(self):
        document = LegalDocument.objects.create(
            act_id="CPA-2019",
            act_title="Consumer Protection Act, 2019",
            section_number="2",
            section_title="Section 2. Definitions.",
            text="",
            source="India Code",
        )
        first_text = "Opening text. " + ("shared statutory passage " * 20)
        overlap = first_text[-150:]
        chunk = LegalChunk.objects.create(
            document=document,
            chunk_index=0,
            text=first_text,
        )
        LegalChunk.objects.create(
            document=document,
            chunk_index=1,
            text=overlap + " concluding provision.",
        )

        evidence = build_evidence(
            [{
                "chunk_id": chunk.id,
                "document_id": document.id,
                "section_number": "2",
                "section_title": document.section_title,
                "act_title": document.act_title,
                "score": 0.9,
                "source": document.source,
            }],
            query="What provisions are included?",
        )

        self.assertEqual(evidence[0]["text"].count("shared statutory passage"), 20)
        self.assertIn("concluding provision.", evidence[0]["text"])

    def test_chunk_overlap_does_not_insert_break_inside_a_word(self):
        document = LegalDocument.objects.create(
            act_id="CPA-2019",
            act_title="Consumer Protection Act, 2019",
            section_number="2",
            section_title="Section 2. Definitions.",
            text="",
            source="India Code",
        )
        first_text = ("x" * 145) + "inspec"
        first_chunk = LegalChunk.objects.create(
            document=document,
            chunk_index=0,
            text=first_text,
        )
        second_chunk = LegalChunk.objects.create(
            document=document,
            chunk_index=1,
            text=first_text[-150:] + "tion continues.",
        )

        evidence = build_evidence(
            [{
                "chunk_id": first_chunk.id,
                "document_id": document.id,
                "section_number": "2",
                "section_title": document.section_title,
                "act_title": document.act_title,
                "score": 0.9,
            }],
            query="Explain this provision.",
        )

        self.assertIn("inspection continues.", evidence[0]["text"])
        self.assertNotIn("inspec\n\ntion", evidence[0]["text"])

    def test_low_score_secondary_section_is_not_presented_as_evidence(self):
        strong_document = LegalDocument.objects.create(
            act_id="CPA-2019",
            act_title="Consumer Protection Act, 2019",
            section_number="69",
            section_title="Section 69. Limitation period.",
            text="Strong evidence.",
            source="India Code",
        )
        weak_document = LegalDocument.objects.create(
            act_id="CPA-2019",
            act_title="Consumer Protection Act, 2019",
            section_number="38",
            section_title="Section 38. Procedure.",
            text="Weak secondary evidence.",
            source="India Code",
        )
        strong_chunk = LegalChunk.objects.create(
            document=strong_document,
            chunk_index=0,
            text="Strong evidence.",
        )
        weak_chunk = LegalChunk.objects.create(
            document=weak_document,
            chunk_index=0,
            text="Weak secondary evidence.",
        )

        evidence = build_evidence(
            [
                {
                    "chunk_id": strong_chunk.id,
                    "document_id": strong_document.id,
                    "section_number": "69",
                    "section_title": strong_document.section_title,
                    "act_title": strong_document.act_title,
                    "score": 0.69,
                },
                {
                    "chunk_id": weak_chunk.id,
                    "document_id": weak_document.id,
                    "section_number": "38",
                    "section_title": weak_document.section_title,
                    "act_title": weak_document.act_title,
                    "score": 0.18,
                },
            ],
            query="What is the limitation period?",
        )

        self.assertEqual([item["section"] for item in evidence], ["69"])
