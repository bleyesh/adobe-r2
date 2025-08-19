# Challenge 1B: Persona-Driven Document Intelligence

## Overview

This solution extracts and ranks relevant document sections based on persona and job requirements using semantic analysis. It processes PDF collections through transformer-based embeddings to identify the most pertinent content for specific roles and objectives, designed for the Challenge 1B hackathon with strict performance and size constraints.

## Universal Approach

- **Semantic Understanding**: Uses transformer-based embeddings for relevance scoring
- **Domain-Agnostic**: Supports any persona-task-document combination  
- **Performance Optimized**: Runs within 60-second constraint on CPU-only systems
- **Lightweight**: Compact MiniLM model (~80MB) under 1GB total footprint
- **Offline Capable**: No internet connectivity required during execution

## Quick Start

### Prerequisites
- Python 3.9+
- Docker (for containerized deployment)

### Local Development Setup
```bash
# Clone or extract the project
cd challenge1b

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Test with sample collection
python3 src/main.py --input_dir "Challenge_1b/Collection 1"
```

### Docker Deployment (Competition Format)

#### Build the Image
```bash
docker build --platform linux/amd64 -t challenge1b:latest .
```

#### Run the Container
```bash
# Default: Collection 1
docker run --rm -v $(pwd):/app --network none challenge1b:latest

# Specific collection
docker run --rm -v $(pwd):/app --network none challenge1b:latest "Challenge_1b/Collection 2"
```

The container will:
- Process all PDFs from specified collection directory
- Generate `challenge1b_output.json` with ranked sections
- Work completely offline (no network access)
- Complete analysis within 60-second time limit

## File Structure

```
├── src/
│   ├── main.py              # Main orchestration script
│   ├── parser.py            # PDF text extraction using PyMuPDF
│   ├── embedder.py          # Semantic embedding generation
│   ├── ranker.py            # Section relevance ranking
│   └── output_generator.py  # JSON output formatting
|
├── Challenge_1b/            # Test collections
│   ├── Collection 1/        # Travel planning scenario
│   ├── Collection 2/        # HR forms management
│   └── Collection 3/        # Menu planning scenario
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container configuration
├── run.sh                  # Execution script
└── README.md               # This documentation
```

## Algorithm Approach

### 1. PDF Parsing
- Extracts text from each PDF page using PyMuPDF
- Identifies potential section titles using font size heuristics
- Structures content into analyzable page-level chunks
- Handles various document formats and layouts

### 2. Semantic Representation
- **Task Query**: Combines persona role and job into semantic query
- **Dense Embeddings**: Uses all-MiniLM-L6-v2 transformer model
- **Normalization**: L2 normalized vectors for cosine similarity
- **Batch Processing**: Efficient encoding of multiple sections

### 3. Relevance Ranking
- **Cosine Similarity**: Measures semantic distance between task and sections
- **Score-based Ranking**: Sorts sections by relevance to persona requirements
- **Top-N Selection**: Extracts 5-7 most relevant sections
- **Importance Assignment**: Assigns ranks based on similarity scores

### 4. Output Generation
- Matches exact JSON schema required by challenge
- Generates extractive summaries (first 1-2 sentences)
- Preserves document metadata and page references
- Includes processing timestamps for tracking

## Performance Characteristics

- **Speed**: ≤60 seconds per collection (multiple PDFs)
- **Memory**: CPU-only processing, efficient memory usage
- **Size**: <1GB total footprint with pre-cached models
- **Architecture**: AMD64 compatible, no GPU required
- **Network**: Completely offline operation after model caching
- **Universal**: Works across travel, HR, food, and other domains
- **Scalable**: Handles collections with 5-15 documents efficiently


## Usage Examples

### Single Collection Processing
```bash
python3 src/main.py --input_dir "Challenge_1b/Collection 1"
```

### Batch Processing via Docker
```bash
# Process Collection 1 (default)
docker run -v $(pwd):/app challenge1b:latest

# Process specific collection
docker run -v $(pwd):/app challenge1b:latest "Challenge_1b/Collection 3"
```

### Expected Output Format
```json
{
  "metadata": {
    "input_documents": ["list"],
    "persona": "User Persona",
    "job_to_be_done": "Task description"
  },
  "extracted_sections": [
    {
      "document": "source.pdf",
      "section_title": "Title",
      "importance_rank": 1,
      "page_number": 1
    }
  ],
  "subsection_analysis": [
    {
      "document": "source.pdf",
      "refined_text": "Content",
      "page_number": 1
    }
  ]
}
```

## Constraints Met

✅ **Execution Time**: ≤60 seconds for complete collection analysis  
✅ **Model Size**: ≤1GB total footprint (MiniLM ~80MB)  
✅ **Network**: No internet access required during processing  
✅ **Runtime**: CPU only (AMD64), optimized for available resources  
✅ **Platform**: linux/amd64 Docker compatibility  
✅ **Universal**: Works across domains (travel, HR, food, etc.)  
✅ **Semantic**: Understands context and relevance, not just keywords  

## Competition Submission

This solution is ready for Challenge 1B hackathon submission with:
- Working Dockerfile in root directory
- All dependencies and models contained within container
- Automated processing for any persona-task combination
- Performance within all specified constraints
- Domain-agnostic approach works across document types
- Private repository maintained until competition deadline

## Supported Scenarios

- **Travel Planning**: Extract destinations, activities, tips from tourism guides
- **HR Management**: Identify form procedures, compliance requirements from manuals  
- **Menu Planning**: Find recipes, dietary considerations from cooking resources
- **Business Analysis**: Extract relevant procedures, policies from documentation
- **Technical Documentation**: Identify implementation steps, requirements from guides