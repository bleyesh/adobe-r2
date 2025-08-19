## Overview

This solution addresses Challenge 1B: Persona-Driven Document Intelligence, which requires analyzing a diverse set of documents based on a persona and job-to-be-done. The goal is to identify, rank, and extract the most relevant sections and sub-sections, returning the results in a structured JSON format. The system is generic and efficient, supporting any domain, persona, or task while meeting strict runtime and size constraints.

---

## Architecture & Methodology

The pipeline is composed of five major stages:

### 1. PDF Parsing

We use `PyMuPDF` to extract text from each PDF page. The parser processes visual text blocks and identifies potential section titles using heuristics (e.g., largest font size, bold spans). Each page is stored with its text, page number, and an inferred section title. This information becomes the unit of semantic analysis.

### 2. Persona-Task Representation

The persona and task are combined into a single semantic query string, e.g.,  
`"HR Professional: Create and manage fillable forms for onboarding."`

This text is embedded into a fixed-size vector using the compact transformer model `all-MiniLM-L6-v2` from `sentence-transformers`. This embedding serves as the reference for evaluating the relevance of all document sections.

### 3. Section Chunk Embedding

Each parsed section (typically page-level or heading-based) is embedded into a dense vector using the same model. Embeddings are normalized to enable fast cosine similarity scoring against the persona-task embedding.

### 4. Relevance Ranking

Cosine similarity is computed between the task embedding and each section embedding. The sections are sorted in descending order of similarity. The top N (usually 5–7) are selected for the `extracted_sections` output. Each selected section is also assigned an `importance_rank` based on position in the list.

### 5. Subsection Analysis

For each selected section, the first 1–2 sentences are extracted as a proxy for a refined, context-rich summary. This lightweight extractive method ensures relevance while meeting the 60-second runtime requirement without additional model overhead. The result is stored in the `subsection_analysis` output.

---

## Optimization & Constraints

- **Model size ≤ 1GB**: We use a pre-cached MiniLM model (~80MB).
- **Runtime ≤ 60s**: Optimized batch embedding and lightweight text processing ensure speed.
- **CPU-only**: No GPU operations are required.
- **Offline-capable**: All models and code run without internet.
- **Dockerized**: The system is wrapped in a clean Docker container for reproducible execution.

---

## Generalizability

This solution is domain-agnostic and supports diverse personas and tasks:
- Travel planning using tourism guides
- HR compliance using software manuals
- Menu design using cooking PDFs

The semantic relevance engine ensures the system generalizes across use cases while preserving accuracy and performance.

---

## Conclusion

This approach offers a robust, efficient, and general-purpose solution to the Challenge 1B problem. It extracts highly relevant content from multi-document inputs, driven by the user's intent and role, while respecting technical constraints and output formatting standards.
