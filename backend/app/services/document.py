import os
from pathlib import Path
from pypdf import PdfReader
from docx import Document as DocxDocument
from app.core.config import get_settings

settings = get_settings()


class DocumentService:
    """Service for document processing"""

    def __init__(self):
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_file(self, filename: str, content: bytes) -> str:
        """Save uploaded file and return path"""
        filepath = self.upload_dir / filename
        with open(filepath, "wb") as f:
            f.write(content)
        return str(filepath)

    async def extract_text(self, filepath: str) -> str:
        """Extract text from document"""
        filepath = Path(filepath)
        suffix = filepath.suffix.lower()

        if suffix == ".pdf":
            return self._extract_from_pdf(filepath)
        elif suffix == ".docx":
            return self._extract_from_docx(filepath)
        elif suffix == ".txt":
            return self._extract_from_txt(filepath)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

    def _extract_from_pdf(self, filepath: Path) -> str:
        """Extract text from PDF"""
        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text

    def _extract_from_docx(self, filepath: Path) -> str:
        """Extract text from DOCX"""
        doc = DocxDocument(filepath)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text

    def _extract_from_txt(self, filepath: Path) -> str:
        """Extract text from TXT"""
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    async def delete_file(self, filepath: str) -> bool:
        """Delete a file"""
        try:
            os.remove(filepath)
            return True
        except:
            return False


# Singleton instance
document_service = DocumentService()
