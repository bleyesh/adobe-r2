from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import os
import json
import tempfile
import shutil
from werkzeug.utils import secure_filename

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# -------- App setup --------
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# -------- Optional imports (Challenge modules) --------
try:
    # Challenge 1A lives in: Challenge_1a_Solution/process_pdfs.py
    from Challenge_1a_Solution.process_pdfs import PDFOutlineExtractor
    CHALLENGE_1A_AVAILABLE = True
except ImportError:
    print("Warning: Challenge 1A not available")
    CHALLENGE_1A_AVAILABLE = False

try:
    # Challenge 1B lives in: Challenge_1b_Solution/src/*.py
    from Challenge_1b_Solution.src.main import main as challenge1b_main
    from Challenge_1b_Solution.src.parser import parse_documents
    from Challenge_1b_Solution.src.embedder import load_model, encode_single, encode_texts
    from Challenge_1b_Solution.src.ranker import rank_sections
    from Challenge_1b_Solution.src.output_generator import generate_output_json
    CHALLENGE_1B_AVAILABLE = True
except ImportError:
    import traceback
    traceback.print_exc()   # ← shows the exact missing thing
    print("Warning: Challenge 1B not available")
    CHALLENGE_1B_AVAILABLE = False


# -------- Helpers --------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# -------- Routes --------
@app.route('/')
def index():
    return render_template(
        'index.html',
        challenge_1a_available=CHALLENGE_1A_AVAILABLE,
        challenge_1b_available=CHALLENGE_1B_AVAILABLE
    )


@app.route('/challenge1a')
def challenge1a():
    if not CHALLENGE_1A_AVAILABLE:
        flash('Challenge 1A is not available. Please check the installation.', 'error')
        return redirect(url_for('index'))
    return render_template('challenge1a.html')


@app.route('/challenge1b')
def challenge1b():
    if not CHALLENGE_1B_AVAILABLE:
        flash('Challenge 1B is not available. Please check the installation.', 'error')
        return redirect(url_for('index'))
    return render_template('challenge1b.html')


@app.route('/api/challenge1a/extract', methods=['POST'])
def extract_outline():
    if not CHALLENGE_1A_AVAILABLE:
        return jsonify({'error': 'Challenge 1A is not available'}), 400

    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    files = request.files.getlist('files')
    if not files or files[0].filename == '':
        return jsonify({'error': 'No files selected'}), 400

    results = []
    temp_dir = None

    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        extractor = PDFOutlineExtractor()

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(temp_dir, filename)
                file.save(file_path)

                try:
                    # Extract outline using Challenge 1A
                    outline_data = extractor.extract_outline(file_path)
                    results.append({
                        'filename': file.filename,
                        'success': True,
                        'outline': outline_data
                    })
                except Exception as e:
                    results.append({
                        'filename': file.filename,
                        'success': False,
                        'error': str(e)
                    })
            else:
                results.append({
                    'filename': file.filename,
                    'success': False,
                    'error': 'Invalid file type. Only PDF files are allowed.'
                })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        # Cleanup
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    return jsonify({'results': results})


@app.route('/api/challenge1b/analyze', methods=['POST'])
def analyze_documents():
    if not CHALLENGE_1B_AVAILABLE:
        return jsonify({'error': 'Challenge 1B is not available'}), 400

    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    files = request.files.getlist('files')
    persona = request.form.get('persona', '').strip()
    job_to_be_done = request.form.get('job_to_be_done', '').strip()

    if not files or files[0].filename == '':
        return jsonify({'error': 'No files selected'}), 400

    if not persona or not job_to_be_done:
        return jsonify({'error': 'Please provide both persona and job to be done'}), 400

    temp_dir = None

    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        pdf_dir = os.path.join(temp_dir, 'PDFs')
        os.makedirs(pdf_dir)

        document_filenames = []

        # Save uploaded files
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(pdf_dir, filename)
                file.save(file_path)
                document_filenames.append(filename)

        if not document_filenames:
            return jsonify({'error': 'No valid PDF files found'}), 400

        # Parse documents into page-level sections
        parsed_docs = parse_documents(pdf_dir, document_filenames)
        print(f"🔍 Parsed {sum(len(pages) for pages in parsed_docs.values())} total pages from {len(parsed_docs)} documents")

        section_chunks = []
        for doc_name, pages in parsed_docs.items():
            for page in pages:
                # Always use the original filename if possible
                section_chunks.append({
                    "document": doc_name if doc_name else page.get("filename", "Unknown Document"),
                    "page_number": page["page_number"],
                    "section_title": page.get("section_title", f"Page {page['page_number']}") ,
                    "text": page["text"]
                })

        # Filter short/noisy text chunks
        MIN_TEXT_LEN = 100
        section_chunks = [s for s in section_chunks if len(s["text"]) >= MIN_TEXT_LEN]
        print(f"🔎 Filtered to {len(section_chunks)} sections with text length >= {MIN_TEXT_LEN}")

        if not section_chunks:
            return jsonify({'error': 'No meaningful text content found in the documents'}), 400

        # Load model and encode everything
        print("📦 Loading embedding model...")
        model = load_model()

        task_query = f"{persona.strip()}: {job_to_be_done.strip()}"
        task_embedding = encode_single(task_query)

        print(f"🔍 Encoding {len(section_chunks)} document sections...")
        section_texts = [section["text"] for section in section_chunks]
        section_embeddings = encode_texts(section_texts)

        # Rank and extract top sections
        print("📊 Ranking relevant sections...")
        top_sections = rank_sections(task_embedding, section_embeddings, section_chunks, top_n=5)

        print("\n🏆 Top 5 Sections:")
        for rank, (section, score) in enumerate(top_sections, start=1):
            print(f"Rank {rank}: {section['document']} → {section['section_title']} (score={score:.4f})")

        # Generate output JSON
        print("\n📝 Generating final output...")
        output_data = generate_output_json(
            input_documents=document_filenames,
            persona=persona,
            job_to_be_done=job_to_be_done,
            ranked_sections=top_sections
        )

        return jsonify(output_data)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

    finally:
        # Cleanup
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'OK',
        'challenge_1a_available': CHALLENGE_1A_AVAILABLE,
        'challenge_1b_available': CHALLENGE_1B_AVAILABLE
    })


if __name__ == '__main__':
    print("🚀 Starting PDF Analysis Flask App")
    print(f"📁 Challenge 1A Available: {CHALLENGE_1A_AVAILABLE}")
    print(f"🎯 Challenge 1B Available: {CHALLENGE_1B_AVAILABLE}")
    print("🌐 Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)
