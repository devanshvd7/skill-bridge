"""File parsing utilities for multi-format document extraction."""

import io
import docx
import fitz  # PyMuPDF

def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """Extract raw text from a file based on its extension."""
    filename = filename.lower()
    
    if filename.endswith(".pdf"):
        return _extract_from_pdf(file_bytes)
    elif filename.endswith(".docx"):
        return _extract_from_docx(file_bytes)
    elif filename.endswith(".txt") or filename.endswith(".md"):
        return file_bytes.decode("utf-8", errors="replace")
    else:
        raise ValueError(f"Unsupported file format: {filename}")

def _extract_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF document."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def _extract_from_docx(file_bytes: bytes) -> str:
    """Extract text from a Word document."""
    doc = docx.Document(io.BytesIO(file_bytes))
    return "\n".join([para.text for para in doc.paragraphs])
