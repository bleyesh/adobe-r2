import fitz  # PyMuPDF
import json
import re
import os
from typing import List, Dict, Tuple, Optional
import sys
import unicodedata

class PDFOutlineExtractor:
    def __init__(self):
        # Simple numbering patterns that work universally
        self.numbering_patterns = [
            r'^\d+\.\s+',                    # 1. 2. 3.
            r'^\d+\.\d+\s+',                 # 1.1 1.2 2.1
            r'^\d+\.\d+\.\d+\s+',            # 1.1.1 1.1.2
            r'^[A-Z]\.\s+',                  # A. B. C.
            r'^[a-z]\)\s+',                  # a) b) c)
            r'^\([a-z]\)\s+',                # (a) (b) (c)
            r'^\([0-9]+\)\s+',               # (1) (2) (3)
            r'^[IVX]+\.\s+',                 # I. II. III. IV. V.
            r'^[ivx]+\.\s+',                 # i. ii. iii. iv. v.
        ]
        
    def normalize_text(self, text: str) -> str:
        """Simple text normalization"""
        # Remove diacritics and convert to lowercase
        normalized = unicodedata.normalize('NFD', text)
        normalized = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
        return normalized.lower().strip()
        
    def extract_text_with_formatting(self, pdf_path: str) -> List[Dict]:
        """Extract text with font information from PDF"""
        doc = fitz.open(pdf_path)
        pages_data = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")
            
            page_data = {
                'page_num': page_num + 1,
                'lines': []
            }
            
            for block in blocks['blocks']:
                if 'lines' in block:
                    for line in block['lines']:
                        line_text = ''
                        font_sizes = []
                        flags_list = []
                        bboxes = []
                        
                        for span in line['spans']:
                            text = span['text'].strip()
                            if text:
                                line_text += text + ' '
                                font_sizes.append(span['size'])
                                flags_list.append(span['flags'])
                                bboxes.append(span['bbox'])
                        
                        if line_text.strip():
                            # Use max font size and flags for the line
                            page_data['lines'].append({
                                'text': line_text.strip(),
                                'size': max(font_sizes) if font_sizes else 10,
                                'flags': max(flags_list) if flags_list else 0,
                                'bbox': bboxes[0] if bboxes else [0, 0, 0, 0]
                            })
            
            pages_data.append(page_data)
        
        doc.close()
        return pages_data
    
    def extract_title(self, pages_data: List[Dict]) -> str:
        """Extract document title from first page using largest bold text"""
        if not pages_data:
            return ""
        
        first_page = pages_data[0]
        
        # Look for largest font size text on first page
        title_candidates = []
        max_size = 0
        
        for line in first_page['lines']:
            size = line['size']
            text = line['text'].strip()
            
            # Skip very short text or page numbers
            if len(text) < 5 or re.match(r'^page\s+\d+', text.lower()):
                continue
            
            if size > max_size:
                max_size = size
                title_candidates = [text]
            elif size == max_size:
                title_candidates.append(text)
        
        if title_candidates:
            # Join title parts with spaces and clean up
            title = '  '.join(title_candidates).strip()  # Use double space like expected
            return title
        
        return ""
    
    def is_heading(self, text: str, font_size: float, flags: int, page_num: int, context: Dict) -> Optional[str]:
        """Determine if text is a heading and what level (simple universal approach)"""
        text = text.strip()
        
        # Skip very short or very long text
        if len(text) < 3 or len(text) > 120:
            return None
        
        # Skip common non-heading patterns (basic universal patterns)
        if re.match(r'^(page|página|seite|pagina|страница)\s+\d+', text.lower()):
            return None
        if re.match(r'^(copyright|©|\d{4})', text.lower()):
            return None
        
        # Skip single letters or numbers
        if re.match(r'^[A-Za-z0-9\u4e00-\u9fff\u0600-\u06ff]{1,2}$', text):
            return None
        
        text_lower = text.lower().strip()
        is_bold = bool(flags & 16)
        
        
        # Check for numbered sections (highest priority for clear headings)
        for pattern in self.numbering_patterns:
            if re.match(pattern, text):
                # Additional check: if it looks like a section title (short and descriptive)
                if len(text.split()) <= 12:  # Reasonable heading length
                    # Determine heading level based on pattern complexity
                    if re.match(r'^\d+\.\d+\.\d+\s+', text):  # 1.1.1
                        return 'H3'
                    elif re.match(r'^\d+\.\d+\s+', text):     # 1.1
                        return 'H2'
                    elif re.match(r'^\d+\.\s+', text):        # 1.
                        return 'H1'
                    elif re.match(r'^[A-Z]\.\s+', text):      # A.
                        return 'H2'
                    elif re.match(r'^[IVX]+\.\s+', text, re.IGNORECASE):  # Roman numerals
                        return 'H1' if text.isupper() else 'H2'
                    else:
                        return 'H2'  # Default for other patterns
        
        # Font size based classification (works universally)
        # Size 16.0+ = H1 (like "Acknowledgements", "1. Introduction")
        if font_size >= 15.5 and len(text.split()) <= 15:
            # Check if it starts with uppercase (works for most languages)
            if text[0].isupper():
                return 'H1'
        
        # Size 14.0 = H2 (like "2.1 Intended Audience", "2.2 Career Paths")  
        elif font_size >= 13.5 and font_size < 15.5 and len(text.split()) <= 15:
            if text[0].isupper():
                return 'H2'
        
        # Font-based classification (fallback)
        avg_font_size = context.get('avg_font_size', 10)
        
        # H1: Large font (>=14) and bold, or very large font
        if ((font_size >= 14 and is_bold) or font_size >= 16):
            # Make sure it's not too long (likely paragraph) and starts with uppercase
            if text[0].isupper() and len(text.split()) <= 12:
                return 'H1'
        
        # H2: Medium font (12-14) and bold
        elif font_size >= 12 and is_bold:
            if text[0].isupper() and len(text.split()) <= 18:
                return 'H2'
        
        # H3: Smaller but still bold and title case
        elif font_size >= 10 and is_bold:
            if text[0].isupper() and len(text.split()) <= 25:
                return 'H3'
        
        return None
    
    def calculate_font_statistics(self, pages_data: List[Dict]) -> Dict:
        """Calculate font statistics"""
        sizes = []
        for page_data in pages_data:
            for line in page_data['lines']:
                sizes.append(line['size'])
        
        if sizes:
            avg_size = sum(sizes) / len(sizes)
        else:
            avg_size = 10
        
        return {'avg_font_size': avg_size}
    
    def extract_outline(self, pdf_path: str) -> Dict:
        """Extract title and outline from PDF"""
        try:
            pages_data = self.extract_text_with_formatting(pdf_path)
            
            if not pages_data:
                return {"title": "", "outline": []}
            
            # Extract title
            title = self.extract_title(pages_data)
            title_parts = set(part.strip() for part in title.split() if len(part.strip()) > 2)
            
            # Calculate font statistics
            context = self.calculate_font_statistics(pages_data)
            
            # Extract headings
            outline = []
            seen_headings = set()
            
            for page_data in pages_data:
                page_num = page_data['page_num'] - 1  # Adjust page numbering to match expected output
                if page_num <= 0:  # Skip page 0 or negative
                    continue
                
                for line in page_data['lines']:
                    text = line['text'].strip()
                    if not text:
                        continue
                    
                    # Skip if this text is part of the title (to avoid duplicates)
                    if text.strip() in title_parts:
                        continue
                    
                    level = self.is_heading(
                        text, 
                        line['size'], 
                        line['flags'], 
                        page_num, 
                        context
                    )
                    
                    if level:
                        # Clean the text but preserve trailing spaces like expected output
                        clean_text = text.strip() + ' '  # Add trailing space like expected
                        
                        # Avoid duplicates by checking exact match
                        heading_key = (level, clean_text.strip())
                        if heading_key not in seen_headings:
                            outline.append({
                                "level": level,
                                "text": clean_text,
                                "page": page_num
                            })
                            seen_headings.add(heading_key)
            
            return {
                "title": title + '  ',  # Add trailing spaces like expected
                "outline": outline
            }
            
        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
            return {"title": "", "outline": []}

def process_single_pdf(pdf_path: str, output_path: str):
    """Process a single PDF file"""
    extractor = PDFOutlineExtractor()
    result = extractor.extract_outline(pdf_path)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    
    print(f"Processed: {pdf_path} -> {output_path}")

def process_directory(input_dir: str, output_dir: str):
    """Process all PDF files in input directory"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(input_dir, filename)
            json_filename = filename[:-4] + '.json'
            output_path = os.path.join(output_dir, json_filename)
            
            process_single_pdf(pdf_path, output_path)

if __name__ == "__main__":
    if len(sys.argv) == 3:
        pdf_path = sys.argv[1]
        output_path = sys.argv[2]
        process_single_pdf(pdf_path, output_path)
    else:
        input_dir = "/app/input"
        output_dir = "/app/output"
        process_directory(input_dir, output_dir)
