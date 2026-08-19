"""
OCR.py — Optical Character Recognition Service
"""

import os
from PIL import Image


def ocr_core(filename: str) -> str:
    """Extract text from an image file using pytesseract."""
    try:
        import pytesseract
        text = pytesseract.image_to_string(Image.open(filename))
        return text.strip()
    except Exception as e:
        return f"OCR processing unavailable: {e}"
