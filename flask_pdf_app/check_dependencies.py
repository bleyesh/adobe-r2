import sys

def check_dependency(package_name, import_name=None):
    """Check if a package is installed and can be imported"""
    if import_name is None:
        import_name = package_name.replace('-', '_')
    
    try:
        __import__(import_name)
        print(f"✅ {package_name}: OK")
        return True
    except ImportError:
        print(f"❌ {package_name}: NOT INSTALLED")
        return False

def main():
    print("Checking dependencies for PDF Analysis App...\n")
    
    # Basic Flask dependencies
    print("Basic Dependencies:")
    flask_ok = check_dependency("flask")
    werkzeug_ok = check_dependency("werkzeug")
    
    # Challenge 1A dependencies
    print("\nChallenge 1A Dependencies:")
    pymupdf_ok = check_dependency("pymupdf", "fitz")
    
    # Challenge 1B dependencies
    print("\nChallenge 1B Dependencies:")
    transformers_ok = check_dependency("transformers")
    sentence_transformers_ok = check_dependency("sentence-transformers", "sentence_transformers")
    sklearn_ok = check_dependency("scikit-learn", "sklearn")
    numpy_ok = check_dependency("numpy")
    tqdm_ok = check_dependency("tqdm")
    torch_ok = check_dependency("torch")
    
    print("\n" + "="*50)
    print("SUMMARY:")
    print("="*50)
    
    if flask_ok and werkzeug_ok:
        print("✅ Flask web server: READY")
    else:
        print("❌ Flask web server: NOT READY")
    
    if pymupdf_ok:
        print("✅ Challenge 1A (PDF Outline): READY")
    else:
        print("❌ Challenge 1A (PDF Outline): NOT READY")
    
    if all([transformers_ok, sentence_transformers_ok, sklearn_ok, numpy_ok, tqdm_ok]):
        print("✅ Challenge 1B (Persona Analysis): READY")
    else:
        print("❌ Challenge 1B (Persona Analysis): NOT READY")
        
    print("\n" + "="*50)
    
    missing_packages = []
    if not flask_ok:
        missing_packages.append("flask")
    if not pymupdf_ok:
        missing_packages.append("pymupdf")
    if not transformers_ok:
        missing_packages.append("transformers")
    if not sentence_transformers_ok:
        missing_packages.append("sentence-transformers")
    if not sklearn_ok:
        missing_packages.append("scikit-learn")
    if not numpy_ok:
        missing_packages.append("numpy")
    if not tqdm_ok:
        missing_packages.append("tqdm")
    if not torch_ok:
        missing_packages.append("torch")
    
    if missing_packages:
        print("To install missing packages, run:")
        print(f"pip install {' '.join(missing_packages)}")
        print("\nOr run: install_dependencies.bat")
    else:
        print("🎉 All dependencies are installed!")
        print("You can now run: python app.py")

if __name__ == "__main__":
    main()
