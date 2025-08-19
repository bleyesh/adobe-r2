import os
import json
import argparse

from .parser import parse_documents
from .embedder import load_model, encode_single, encode_texts
from .ranker import rank_sections
from .output_generator import generate_output_json
from typing import Dict


def load_input_json(input_path: str) -> Dict:
    with open(input_path, "r") as f:
        return json.load(f)


def main(input_dir: str):
    # 1. Load input config
    input_json_path = os.path.join(input_dir, "challenge1b_input.json")
    input_data = load_input_json(input_json_path)

    documents_info = input_data["documents"]
    persona = input_data["persona"]["role"]
    job = input_data["job_to_be_done"]["task"]

    input_pdf_dir = os.path.join(input_dir, "PDFs")
    document_filenames = [doc["filename"] for doc in documents_info]

    print(f"🧾 Processing {len(document_filenames)} documents for '{persona}' task...")

    # 2. Parse documents into page-level sections
    parsed_docs = parse_documents(input_pdf_dir, document_filenames)
    print(f"🔍 Parsed {sum(len(pages) for pages in parsed_docs.values())} total pages from {len(parsed_docs)} documents")

    section_chunks = []
    for doc_name, pages in parsed_docs.items():
        for page in pages:
            section_chunks.append({
                "document": doc_name,
                "page_number": page["page_number"],
                "section_title": page.get("section_title", f"Page {page['page_number']}"),
                "text": page["text"]
            })

    # Filter short/noisy text chunks
    MIN_TEXT_LEN = 100
    section_chunks = [s for s in section_chunks if len(s["text"]) >= MIN_TEXT_LEN]
    print(f"🔎 Filtered to {len(section_chunks)} sections with text length >= {MIN_TEXT_LEN}")

    # 3. Load model and encode everything
    print("📦 Loading embedding model...")
    model = load_model()

    task_query = f"{persona.strip()}: {job.strip()}"
    task_embedding = encode_single(task_query)

    print(f"🔍 Encoding {len(section_chunks)} document sections...")
    section_texts = [section["text"] for section in section_chunks]
    section_embeddings = encode_texts(section_texts)

    # 4. Rank and extract top sections
    print("📊 Ranking relevant sections...")
    top_sections = rank_sections(task_embedding, section_embeddings, section_chunks, top_n=5)

    print("\n🏆 Top 5 Sections:")
    for rank, (section, score) in enumerate(top_sections, start=1):
        print(f"Rank {rank}: {section['document']} → {section['section_title']} (score={score:.4f})")

    # Show bottom 5 sections for diagnostics
    print("\n📉 Bottom 5 Sections (lowest scoring):")
    all_with_scores = [
        (meta, float(task_embedding @ emb.T)) for meta, emb in zip(section_chunks, section_embeddings)
    ]
    bottom_sections = sorted(all_with_scores, key=lambda x: x[1])[:5]
    for section, score in bottom_sections:
        print(f"↓ {section['document']} → {section['section_title']} (score={score:.4f})")

    # 5. Generate output JSON
    print("\n📝 Generating final output...")
    output_data = generate_output_json(
        input_documents=document_filenames,
        persona=persona,
        job_to_be_done=job,
        ranked_sections=top_sections
    )

    # 6. Save to file
    output_path = os.path.join(input_dir, "challenge1b_output.json")
    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"✅ Output saved to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Persona-Driven PDF Analysis")
    parser.add_argument("--input_dir", type=str, required=True, help="Path to Collection folder")
    args = parser.parse_args()

    main(args.input_dir)
