# PDF Analysis Platform - Setup & Usage Guide

This guide provides step-by-step instructions to set up and run the PDF Analysis Platform Flask app. Follow these steps to prepare your environment and launch the application for evaluation or submission.

---

## 1. Prerequisites
- **Python 3.8+** (Recommended: Python 3.11 or newer)
- **pip** (Python package manager)

---

## 2. Clone or Download the Repository
If you haven't already, download or clone the project and navigate to the main project directory:

```bash
cd /path/to/adobe-r2
```


---

## 3. Create and Activate a Virtual Environment
It is recommended to use a Python virtual environment to avoid dependency conflicts.

```bash
# Create a virtual environment named 'venv'
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

---

## 4. Install Python Dependencies
Install all required packages for the Flask app:

```bash
pip install -r flask_pdf_app/requirements.txt
```


---

## 5. Run the Flask Application
From the **parent project directory** (where this README is located), start the Flask app with:

```bash
python flask_pdf_app/app.py
```

- You will see log messages indicating the availability of Challenge 1A and 1B.

---

## 6. Access the Web Interface
Open your browser and navigate to:

```
http://localhost:5000
```

You can now use the PDF Analysis Platform to upload and analyze PDF documents.

---

## 7. Deactivate the Virtual Environment (Optional)
When you are done, you can deactivate the virtual environment:

```bash
deactivate
```

---

## Notes
- No code or configuration changes are required to run the app as described above.
- For any issues, ensure all dependencies are installed and you are running the correct Python version.

