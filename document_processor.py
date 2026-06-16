# document_processor.py — PDF & Document processing for batch conversion

import os
from pathlib import Path
from typing import List, Tuple
try:
    import PyPDF2
    from pdf2image import convert_from_path
except ImportError:
    PyPDF2 = None
    convert_from_path = None

from braille_engine import text_to_braille

class DocumentProcessor:
    """Handles PDF, TXT, and batch document conversions."""
    
    @staticmethod
    def read_text_file(file_path: str) -> str:
        """Read text from .txt file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"
    
    @staticmethod
    def read_pdf_text(pdf_path: str) -> Tuple[str, str]:
        """
        Extract text from PDF file.
        Returns (text, status_message)
        """
        if not PyPDF2:
            return '', 'PyPDF2 not installed. Install: pip install PyPDF2'
        
        try:
            text_content = []
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    text_content.append(text)
            
            full_text = '\n'.join(text_content)
            return full_text, f"✓ Extracted {num_pages} pages from PDF"
        
        except Exception as e:
            return '', f"PDF read error: {str(e)}"
    
    @staticmethod
    def save_text_file(content: str, file_path: str) -> Tuple[bool, str]:
        """Save text to file. Returns (success, message)."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, f"✓ Saved to {Path(file_path).name}"
        except Exception as e:
            return False, f"Save error: {str(e)}"
    
    @staticmethod
    def batch_convert_files(input_dir: str, output_dir: str, language: str = 'English') -> Tuple[int, str]:
        """
        Convert all .txt files in directory to braille.
        Returns (files_processed, status_message)
        """
        try:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            txt_files = list(Path(input_dir).glob('*.txt'))
            if not txt_files:
                return 0, "No .txt files found in directory"
            
            processed = 0
            for txt_file in txt_files:
                try:
                    text = DocumentProcessor.read_text_file(str(txt_file))
                    braille_text = text_to_braille(text, language)
                    
                    output_file = Path(output_dir) / f"{txt_file.stem}_braille.txt"
                    success, _ = DocumentProcessor.save_text_file(braille_text, str(output_file))
                    if success:
                        processed += 1
                except:
                    pass
            
            return processed, f"✓ Converted {processed}/{len(txt_files)} files"
        
        except Exception as e:
            return 0, f"Batch error: {str(e)}"
    
    @staticmethod
    def export_embosser_format(braille_text: str, file_path: str) -> Tuple[bool, str]:
        """
        Export braille in embosser format (prepare for physical braille printing).
        This is a simplified version - real embossers use specific formats.
        """
        try:
            # Group braille into lines suitable for embosser (80 chars per line)
            lines = []
            current_line = []
            char_count = 0
            
            for char in braille_text:
                if char == '\n':
                    lines.append(''.join(current_line))
                    current_line = []
                    char_count = 0
                else:
                    current_line.append(char)
                    char_count += 1
                    if char_count >= 80:
                        lines.append(''.join(current_line))
                        current_line = []
                        char_count = 0
            
            if current_line:
                lines.append(''.join(current_line))
            
            embosser_content = '\n'.join(lines)
            success, msg = DocumentProcessor.save_text_file(embosser_content, file_path)
            
            if success:
                return True, f"✓ Embosser file ready: {Path(file_path).name}"
            return False, msg
        
        except Exception as e:
            return False, f"Export error: {str(e)}"
    
    @staticmethod
    def convert_pdf_to_braille(pdf_path: str, output_txt_path: str, 
                               language: str = 'English') -> Tuple[bool, str]:
        """Convert PDF file to Braille text file."""
        text, status = DocumentProcessor.read_pdf_text(pdf_path)
        
        if not text:
            return False, status
        
        braille_text = text_to_braille(text, language)
        success, msg = DocumentProcessor.save_text_file(braille_text, output_txt_path)
        
        return success, msg
    
    @staticmethod
    def get_file_info(file_path: str) -> dict:
        """Get metadata about a file."""
        try:
            path = Path(file_path)
            return {
                'name': path.name,
                'size_kb': path.stat().st_size / 1024,
                'type': path.suffix,
                'exists': path.exists(),
            }
        except:
            return {}

# Global instance
doc_processor = DocumentProcessor()
