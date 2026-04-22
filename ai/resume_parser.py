import pdfplumber
from docx import Document
from PIL import Image
import os

try:
    import pytesseract
    OCR_AVAILABLE = True
except:
    OCR_AVAILABLE = False


def extract_resume_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    # ---------- PDF ----------
    if ext == ".pdf":
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""

        # OCR fallback
        if not text.strip() and OCR_AVAILABLE:
            images = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    images.append(page.to_image(resolution=300).original)

            ocr_text = ""
            for img in images:
                ocr_text += pytesseract.image_to_string(img)

            return ocr_text

        return text

    # ---------- DOCX ----------
    if ext == ".docx":
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)

    # ---------- IMAGE ----------
    if OCR_AVAILABLE:
        img = Image.open(file_path)
        return pytesseract.image_to_string(img)

    return "OCR not available on server"
