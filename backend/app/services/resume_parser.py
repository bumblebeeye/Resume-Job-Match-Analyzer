from io import BytesIO
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from pypdf import PdfReader

from app.core.config import settings


class ResumeParserError(ValueError):
    pass


async def save_resume_file(upload_file: UploadFile) -> tuple[str, str, bytes]:
    if not upload_file.filename:
        raise ResumeParserError("Uploaded file must include a filename.")

    raw_bytes = await upload_file.read()
    extension = Path(upload_file.filename).suffix.lower() or ".bin"
    stored_filename = f"{uuid4().hex}{extension}"

    storage_path = Path(settings.resume_storage_path)
    storage_path.mkdir(parents=True, exist_ok=True)
    full_path = storage_path / stored_filename
    full_path.write_bytes(raw_bytes)

    return str(full_path), stored_filename, raw_bytes


def extract_resume_text(filename: str, file_bytes: bytes) -> str:
    extension = Path(filename).suffix.lower()

    if extension == ".pdf":
        return _extract_pdf_text(file_bytes)
    if extension in {".txt", ".md"}:
        return file_bytes.decode("utf-8", errors="ignore").strip()

    raise ResumeParserError(
        "Unsupported file type. Phase 1 supports PDF, TXT, and MD uploads."
    )


def _extract_pdf_text(file_bytes: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(file_bytes))
        pages = [(page.extract_text() or "").strip() for page in reader.pages]
        text = "\n".join(page for page in pages if page).strip()
    except Exception as exc:  # pragma: no cover - parser errors depend on source file
        raise ResumeParserError(f"Could not parse the uploaded PDF: {exc}") from exc

    if not text:
        raise ResumeParserError(
            "The PDF was uploaded but no readable text was found. "
            "Try exporting the resume as a text-based PDF."
        )

    return text

