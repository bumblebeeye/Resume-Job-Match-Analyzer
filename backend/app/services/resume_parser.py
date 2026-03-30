from io import BytesIO
import logging
from pathlib import Path
from uuid import uuid4

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import UploadFile
from pypdf import PdfReader

from app.core.config import settings

logger = logging.getLogger(__name__)

SUPPORTED_RESUME_CONTENT_TYPES = {
    ".pdf": {"application/pdf"},
    ".txt": {"text/plain"},
    ".md": {"text/markdown", "text/plain", "text/x-markdown"},
}


class ResumeParserError(ValueError):
    pass


async def save_resume_file(upload_file: UploadFile) -> tuple[str, str, bytes]:
    if not upload_file.filename:
        raise ResumeParserError("Uploaded file must include a filename.")

    extension = Path(upload_file.filename).suffix.lower() or ".bin"
    _validate_resume_file_metadata(extension=extension, content_type=upload_file.content_type)

    raw_bytes = await upload_file.read()
    _validate_resume_file_size(len(raw_bytes))

    stored_filename = f"{uuid4().hex}{extension}"

    if settings.s3_bucket_name:
        s3_object_key = _build_s3_object_key(stored_filename)
        uploaded = _upload_to_s3(
            object_key=s3_object_key,
            content=raw_bytes,
            content_type=upload_file.content_type,
        )
        if uploaded:
            s3_uri = f"s3://{settings.s3_bucket_name}/{s3_object_key}"
            return s3_uri, stored_filename, raw_bytes
        logger.warning("S3 upload failed; falling back to local filesystem storage.")

    storage_path = Path(settings.resume_storage_path)
    storage_path.mkdir(parents=True, exist_ok=True)
    full_path = storage_path / stored_filename
    full_path.write_bytes(raw_bytes)

    return str(full_path), stored_filename, raw_bytes


def _build_s3_object_key(stored_filename: str) -> str:
    prefix = settings.s3_resume_prefix.strip().strip("/")
    if prefix:
        return f"{prefix}/{stored_filename}"
    return stored_filename


def _upload_to_s3(object_key: str, content: bytes, content_type: str | None) -> bool:
    client_kwargs: dict[str, str] = {}
    if settings.aws_region and settings.aws_region.strip():
        client_kwargs["region_name"] = settings.aws_region.strip()

    try:
        s3_client = boto3.client("s3", **client_kwargs)
        put_kwargs: dict[str, str | bytes] = {
            "Bucket": settings.s3_bucket_name or "",
            "Key": object_key,
            "Body": content,
        }
        if content_type:
            put_kwargs["ContentType"] = content_type
        s3_client.put_object(**put_kwargs)
        return True
    except (BotoCoreError, ClientError, ValueError) as exc:
        logger.warning("Failed to upload resume to S3: %s", exc)
        return False


def _validate_resume_file_metadata(extension: str, content_type: str | None) -> None:
    allowed_content_types = SUPPORTED_RESUME_CONTENT_TYPES.get(extension)
    if not allowed_content_types:
        raise ResumeParserError(
            "Unsupported file type. Phase 1 supports PDF, TXT, and MD uploads."
        )

    normalized_content_type = (content_type or "").strip().lower()
    if not normalized_content_type or normalized_content_type not in allowed_content_types:
        supported_types = ", ".join(sorted(allowed_content_types))
        raise ResumeParserError(
            f"Unsupported content type for {extension} files. Use one of: {supported_types}."
        )


def _validate_resume_file_size(file_size_bytes: int) -> None:
    if file_size_bytes <= settings.max_resume_upload_bytes:
        return

    raise ResumeParserError(
        f"Uploaded file exceeds the {_format_file_size(settings.max_resume_upload_bytes)} limit."
    )


def _format_file_size(file_size_bytes: int) -> str:
    megabyte = 1024 * 1024
    kilobyte = 1024

    if file_size_bytes % megabyte == 0:
        return f"{file_size_bytes // megabyte} MB"
    if file_size_bytes % kilobyte == 0:
        return f"{file_size_bytes // kilobyte} KB"
    if file_size_bytes == 1:
        return "1 byte"
    return f"{file_size_bytes} bytes"


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
