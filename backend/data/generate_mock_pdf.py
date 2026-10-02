"""
generate_mock_pdf.py - Synthetic Mock Legal Document Generator
Part of the Verified Legal Research Assistant Corpus Pipeline.

Generates a clearly labelled, synthetic multi-page PDF for testing extraction,
cleaning, chunking, and metadata attribution without pretending to be real law.
"""

import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak


def generate_synthetic_mock_pdf(output_path: str) -> str:
    """
    Builds a two-page synthetic mock legal PDF for pipeline verification.
    """
    dest = Path(output_path)
    dest.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(dest),
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'MockTitle',
        parent=styles['Heading1'],
        fontSize=14,
        leading=18,
        alignment=1, # Center
        spaceAfter=10
    )
    
    subtitle_style = ParagraphStyle(
        'MockSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        alignment=1,
        textColor='#777777',
        spaceAfter=15
    )

    section_style = ParagraphStyle(
        'MockSection',
        parent=styles['Normal'],
        fontSize=10,
        leading=15,
        spaceAfter=12
    )

    story = []

    # --- PAGE 1 ---
    story.append(Paragraph("THE SYNTHETIC MOCK ACT, 2026", title_style))
    story.append(Paragraph("[SYNTHETIC TEST CORPUS - NOT REAL LAW - FOR PIPELINE TESTING ONLY]", subtitle_style))
    story.append(Paragraph("An Act for testing legal text extraction, chunking, and citation pipelines in the Verified Legal Research Assistant project.", section_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        "<b>Section 1.</b> Short title, extent and commencement.—(1) This Act may be called the Synthetic Mock Act, 2026.<br/>"
        "(2) It extends to all testing environments of the project.<br/>"
        "(3) It shall come into force immediately and serves solely as mock verification data.",
        section_style
    ))

    story.append(Paragraph(
        "<b>Section 2.</b> Definitions.—In this Act, unless the context otherwise requires,—<br/>"
        "(a) <i>\"mock document\"</i> means synthetic text generated strictly for testing;<br/>"
        "(b) <i>\"pipeline\"</i> means the verified legal text extraction and chunking workflow;<br/>"
        "(c) <i>\"verifier\"</i> means a component ensuring answers cite substantiated corpus evidence.",
        section_style
    ))

    story.append(PageBreak())

    # --- PAGE 2 ---
    story.append(Paragraph("THE SYNTHETIC MOCK ACT, 2026 (CONTINUED)", title_style))
    story.append(Paragraph("[SYNTHETIC TEST CORPUS - NOT REAL LAW - FOR PIPELINE TESTING ONLY]", subtitle_style))

    story.append(Paragraph(
        "<b>Section 3.</b> Evidence verification requirement.—(1) A legal research assistant shall deliver information "
        "only when supported by verified legal evidence in the corpus.<br/>"
        "(2) If a relevant provision cannot be substantiated by verified text, the system must not invent an answer.",
        section_style
    ))

    story.append(Paragraph(
        "<b>Section 4.</b> Penalty for fabricated law.—(1) Any component generating unsubstantiated or hallucinated "
        "provisions shall be flagged for verification failure.<br/>"
        "(2) Citations must accurately reference the Act name, section number, and exact extracted text.",
        section_style
    ))

    doc.build(story)
    return str(dest)


if __name__ == "__main__":
    out = "data/raw/synthetic_mock_act.pdf"
    generate_synthetic_mock_pdf(out)
    print(f"Generated synthetic test PDF at: {out}")
