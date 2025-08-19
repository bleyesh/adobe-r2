import fitz  # PyMuPDF
from typing import List, Dict
import os


def extract_pages(pdf_path: str) -> List[Dict]:
    """
    Extracts text from each page of the PDF.
    Tries to identify potential section titles using font size.
    Returns a list of dicts with text and metadata.
    """
    doc = fitz.open(pdf_path)
    pages = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]
        text = ""
        potential_title = ""

        max_font_size = 0
        title_found = False

        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    font_size = span["size"]
                    span_text = span["text"].strip()

                    # Heuristic: track largest-font span as possible title
                    if font_size > max_font_size and len(span_text) > 3:
                        max_font_size = font_size
                        potential_title = span_text

                    text += span_text + " "

        # Clean text
        text = text.strip().replace('\n', ' ').replace('  ', ' ')

        # Add page to list
        pages.append({
            "page_number": page_num + 1,
            "text": text,
            "section_title": potential_title if potential_title else f"Page {page_num + 1}"
        })

    doc.close()
    return pages


def parse_documents(input_folder: str, file_list: List[str]) -> Dict[str, List[Dict]]:
    """
    Parses multiple PDFs and returns a dictionary of document -> list of page data.
    """
    parsed = {}
    for filename in file_list:
        pdf_path = os.path.join(input_folder, filename)
        if os.path.exists(pdf_path):
            parsed[filename] = extract_pages(pdf_path)
        else:
            print(f"[WARNING] File not found: {pdf_path}")
    return parsed
