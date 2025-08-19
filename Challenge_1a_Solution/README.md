# PDF Outline Extraction Solution

## Overview

This solution extracts structured outlines (title and headings H1-H4) from PDF documents using Python and PyMuPDF. It uses font-based analysis and universal numbering patterns to work across different document types and languages, designed for the hackathon challenge with strict performance and size constraints.

## Technical Approach

### Core Algorithm Strategy
Our solution employs a **hybrid font-and-pattern analysis approach** that combines:

1. **Font Metadata Analysis**: Extracts font size, bold flags, and positioning data from PDF text spans
2. **Universal Pattern Recognition**: Uses regex patterns to identify numbered sections across different languages
3. **Context-Aware Filtering**: Filters out page numbers, copyright notices, and irrelevant text
4. **Hierarchical Classification**: Maps detected headings to H1-H4 levels based on formatting and structure

### Models and Libraries Used

#### Primary Dependencies
- **PyMuPDF (fitz) v1.26.3**: Core PDF processing library
  - Chosen for its excellent text extraction with font metadata
  - Provides precise font size, formatting flags, and bounding box information
  - Lightweight compared to alternatives like pdfplumber or PyPDF2
  - No OCR required - works with native PDF text
  
### Universal Language Support
- **Font-based Detection**: Analyzes font sizes, bold formatting, and text patterns
- **Universal Numbering**: Supports common numbering systems (1., 1.1, 1.1.1, A., I., etc.)
- **Simple & Fast**: No complex language detection, minimal overhead
- **Unicode Support**: Handles international characters and special fonts

## How to Build and Run

### Prerequisites
- Python 3.9+ (recommended: 3.9-3.11 for best compatibility)
- Docker (for containerized deployment)
- Linux/macOS/Windows (cross-platform compatible)

### Method 1: Docker Deployment

#### Build the Docker Image
```bash
# Build for Linux AMD64 (required for competition)
docker build --platform linux/amd64 -t pdf-extractor:latest .
```

#### Run the Container (Expected Execution Format)
```bash
# Mount input and output directories, run without network access
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none mysolutionname:somerandomidentifier
```

**Container Behavior:**
- Automatically processes all `.pdf` files from `/app/input` directory
- Generates corresponding `.json` files in `/app/output` directory  
- Runs completely offline (no network access required)
- Exits cleanly after processing all files

### Method 2: Direct Script Execution
```bash
# Single file processing
python process_pdfs.py /path/to/input.pdf /path/to/output.json

# Batch processing (uses /app/input and /app/output by default)
python process_pdfs.py
```

The container will:
- Process all PDFs from `/app/input` directory
- Generate corresponding `.json` files in `/app/output`
- Work completely offline (no network access)

## File Structure and Architecture

```
├── process_pdfs.py      # Main PDF processing script (PDFOutlineExtractor class)
├── requirements.txt     # Python dependencies (PyMuPDF v1.26.3 only)
├── Dockerfile          # Multi-stage container configuration
├── README.md           # This comprehensive documentation
├── input/              # Directory for input PDF files
├── output/             # Directory for generated JSON files
└── reference/          # Sample test files and expected outputs
```

## Detailed Algorithm Implementation

### 1. Title Extraction Strategy
```python
# Algorithm: Largest font detection on first page
- Scans first page for maximum font size text
- Filters out page numbers and short text (<5 chars)
- Joins multiple title components with double spaces
- Preserves exact format expected by competition
- Language-agnostic approach (no keyword matching)
```

### 2. Heading Detection Engine
Our heading detection uses a **multi-layered classification system**:

#### Layer 1: Pattern-Based Detection (Highest Priority)
- **Numbered Sections**: `1.`, `2.1`, `2.1.1`, `A.`, `I.`, etc.
- **Lettered Lists**: `a)`, `(b)`, `(1)`, etc.
- **Roman Numerals**: `I.`, `II.`, `iii.`, `iv.`, etc.
- **Hierarchical Mapping**: 
  - `1.` → H1
  - `1.1` → H2  
  - `1.1.1` → H3
  - `A.` → H2
  - `I.` → H1

#### Layer 2: Font-Based Classification (Secondary)
- **H1**: Font size ≥15.5, bold formatting, reasonable length (≤15 words)
- **H2**: Font size 13.5-15.4, bold, uppercase start, ≤15 words
- **H3**: Font size ≥10, bold, title case, ≤25 words
- **Context Filtering**: Excludes page numbers, copyright, single characters

#### Layer 3: Universal Filtering
- **Length Validation**: 3-120 characters (excludes fragments and paragraphs)
- **Format Validation**: Must start with uppercase letter
- **Duplicate Prevention**: Tracks seen headings by level and text
- **Page Number Adjustment**: Converts to 0-based indexing for output

### 3. Output Formatting Compliance
- **JSON Schema**: Matches exact competition requirements
- **Text Preservation**: Maintains trailing spaces in text fields
- **UTF-8 Encoding**: Full international character support
- **Error Handling**: Graceful fallback for malformed PDFs


## Performance Characteristics

### Speed and Efficiency
- **Processing Time**: ~50-200ms per PDF (depends on size and complexity)
- **Memory Usage**: <50MB RAM for typical documents
- **Container Size**: ~150MB (Python 3.9-slim + PyMuPDF)
- **Startup Time**: <2 seconds container initialization

### Scalability
- **Batch Processing**: Handles multiple files sequentially
- **Resource Limits**: Designed for hackathon constraints
- **Error Recovery**: Continues processing if individual files fail
- **Output Validation**: Ensures valid JSON for all outputs
