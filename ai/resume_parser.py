import pdfplumber
from docx import Document
import pytesseract
from PIL import Image
import os


def extract_resume_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    # ---------- PDF ----------
    if ext == ".pdf":
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""

        # OCR fallback for scanned PDFs
        if text.strip():
            return text
        else:
            images = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    images.append(page.to_image(resolution=300).original)

            ocr_text = ""
            for img in images:
                ocr_text += pytesseract.image_to_string(img)

            return ocr_text

    # ---------- DOCX ----------
    if ext == ".docx":
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)

    # ---------- IMAGE ----------
    img = Image.open(file_path)
    return pytesseract.image_to_string(img)
