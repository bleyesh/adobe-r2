import json
from typing import List, Dict, Tuple
from datetime import datetime


def generate_output_json(
    input_documents: List[str],
    persona: str,
    job_to_be_done: str,
    ranked_sections: List[Tuple[Dict, float]]
) -> Dict:
    """
    Generates the final output JSON in the required format.

    Args:
        input_documents: List of filenames
        persona: Persona role description
        job_to_be_done: Task description
        ranked_sections: List of tuples (section_metadata, similarity_score)

    Returns:
        A dictionary matching the challenge1b_output.json format
    """

    metadata = {
        "input_documents": input_documents,
        "persona": persona,
        "job_to_be_done": job_to_be_done,
        "processing_timestamp": datetime.now().isoformat()
    }

    extracted_sections = []
    subsection_analysis = []

    for rank, (section, _) in enumerate(ranked_sections, start=1):
        extracted_sections.append({
            "document": section["document"],
            "section_title": section.get("section_title", f"Page {section['page_number']}"),
            "importance_rank": rank,
            "page_number": section["page_number"]
        })

        # Basic refinement: take first 1–2 sentences from text
        refined = extract_summary_snippet(section["text"])
        subsection_analysis.append({
            "document": section["document"],
            "refined_text": refined,
            "page_number": section["page_number"]
        })

    return {
        "metadata": metadata,
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }


def extract_summary_snippet(text: str, max_sentences: int = 2) -> str:
    """
    Simple extractive method: returns first 1-2 sentences from a block of text.
    Could be improved with NLP summarization if needed.

    Args:
        text: Full section text
        max_sentences: Number of sentences to return

    Returns:
        A refined summary snippet
    """
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return " ".join(sentences[:max_sentences])
