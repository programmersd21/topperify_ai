"""
Topperify AI - PDF Parser
Extracts text from uploaded PDFs using PyMuPDF (fitz).
Handles corrupt, empty, and image-only PDFs gracefully.
"""

import fitz  # PyMuPDF
import streamlit as st


@st.cache_data(show_spinner=False)
def extract_text_from_pdf(pdf_bytes: bytes) -> dict:
    """
    Extract text from PDF bytes.

    Returns:
        dict with keys:
            - "success": bool
            - "text": str (full extracted text)
            - "pages": int (total page count)
            - "error": str | None
    """
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception:
        return {
            "success": False,
            "text": "",
            "pages": 0,
            "error": "Could not read this PDF. Please upload a valid PDF file.",
        }

    total_pages = doc.page_count

    if total_pages == 0:
        doc.close()
        return {
            "success": False,
            "text": "",
            "pages": 0,
            "error": "This PDF has no pages.",
        }

    full_text = []
    for page_num in range(total_pages):
        try:
            page = doc.load_page(page_num)
            page_text = page.get_text("text")
            if page_text and page_text.strip():
                full_text.append(page_text.strip())
        except Exception:
            continue

    doc.close()

    combined = "\n\n".join(full_text)

    if not combined.strip():
        return {
            "success": False,
            "text": "",
            "pages": total_pages,
            "error": "This PDF appears to be image-based or empty. Text extraction failed.",
        }

    return {
        "success": True,
        "text": combined,
        "pages": total_pages,
        "error": None,
    }


def chunk_text(text: str, max_chars: int = 30000) -> list[str]:
    """
    Split text into chunks that fit within Gemini's context window.
    Splits on paragraph boundaries to preserve context.
    """
    if len(text) <= max_chars:
        return [text]

    chunks = []
    paragraphs = text.split("\n\n")
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) + 2 > max_chars:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = para
        else:
            current_chunk = current_chunk + "\n\n" + para if current_chunk else para

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks if chunks else [text[:max_chars]]
