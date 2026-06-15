import fitz  # PyMuPDF
from typing import Dict, Any, Generator

class PDFLoader:
    @staticmethod
    def extract_text(pdf_bytes: bytes) -> Generator[Dict[str, Any], None, None]:
        """
        Extracts text from a PDF byte array.
        Yields status updates including current page and total pages.
        """
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            total_pages = len(doc)
            
            if total_pages == 0:
                yield {"status": "error", "message": "The PDF file contains no pages.", "total_pages": 0, "current_page": 0, "text": ""}
                return
            
            yield {"status": "started", "message": f"Successfully loaded PDF. Total pages: {total_pages}", "total_pages": total_pages, "current_page": 0, "text": ""}
            
            full_text = []
            for page_num in range(total_pages):
                page = doc[page_num]
                page_text = page.get_text()
                full_text.append(page_text)
                
                yield {
                    "status": "processing",
                    "message": f"Extracting text from page {page_num + 1}/{total_pages}...",
                    "total_pages": total_pages,
                    "current_page": page_num + 1,
                    "text": ""
                }
                
            combined_text = "\n--- PAGE BREAK ---\n".join(full_text)
            
            yield {
                "status": "completed",
                "message": f"Extraction completed. Extracted {len(combined_text)} characters from {total_pages} pages.",
                "total_pages": total_pages,
                "current_page": total_pages,
                "text": combined_text
            }
            
        except Exception as e:
            yield {
                "status": "error",
                "message": f"Error parsing PDF: {str(e)}",
                "total_pages": 0,
                "current_page": 0,
                "text": ""
            }
