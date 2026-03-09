"""Helpers for validating and processing essay resource uploads."""

from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from io import BytesIO
from typing import Iterable

from fastapi import HTTPException, status

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover - optional runtime fallback
    PdfReader = None  # type: ignore[assignment]

try:
    from azure.ai.documentintelligence import DocumentIntelligenceClient
    from azure.core.credentials import AzureKeyCredential
except ImportError:  # pragma: no cover - optional during local development
    DocumentIntelligenceClient = None  # type: ignore[assignment]
    AzureKeyCredential = None  # type: ignore[assignment]

try:
    from PIL import Image
except ImportError:  # pragma: no cover - pillow is an optional runtime dependency
    Image = None  # type: ignore[assignment]


ALLOWED_IMAGE_TYPES: set[str] = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
}
ALLOWED_PDF_TYPES: set[str] = {"application/pdf"}
MAX_IMAGE_BYTES = 1_000_000  # ~1 MB raw payload to comfortably fit Cosmos' 2 MB item cap
MAX_IMAGE_BASE64_LENGTH = 1_500_000  # guardrail after base64 expansion
MAX_IMAGE_DIMENSION = 1600  # px
DEFAULT_DOCUMENT_INTELLIGENCE_MODEL = "prebuilt-read"


def ensure_supported_file(content_type: str | None) -> None:
    """Validate that the uploaded file type is supported."""

    if content_type in ALLOWED_IMAGE_TYPES | ALLOWED_PDF_TYPES:
        return
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unsupported file type. Only images and PDFs are allowed.",
    )


@dataclass(slots=True)
class ProcessedUpload:
    """Normalised representation of an uploaded file ready for persistence."""

    content_type: str
    file_name: str
    encoded_content: str | None
    extracted_text: str | None
    metadata: dict[str, str]
    binary: bytes | None


def normalise_objectives(objectives: Iterable[str] | str) -> list[str]:
    """Ensure objective payloads are consistently represented as a list."""

    if isinstance(objectives, str):
        stripped = objectives.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            try:
                import json as _json

                parsed = _json.loads(stripped)
                if isinstance(parsed, list):
                    return [str(item) for item in parsed]
            except Exception:  # pragma: no cover - defensive branch
                return [objectives]
        if "," in objectives:
            return [item.strip() for item in objectives.split(",") if item.strip()]
        return [objectives]
    return [str(item) for item in objectives]


def read_upload_bytes(data: bytes | bytearray | memoryview) -> bytes:
    """Return an immutable bytes object regardless of the supplied buffer type."""

    if isinstance(data, bytes):
        return data
    return bytes(data)


def extract_pdf_text(payload: bytes) -> str:
    """Extract plain text from a PDF payload."""

    if PdfReader is None:
        return ""

    reader = PdfReader(BytesIO(payload))
    buffer: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text:
            buffer.append(text)
    return "\n".join(buffer).strip()


def extract_text_with_doc_intelligence(payload: bytes, content_type: str) -> str | None:
    """Extract text using Azure AI Document Intelligence when configured."""

    endpoint = os.environ.get("DOCUMENT_INTELLIGENCE_ENDPOINT", "").strip()
    if not endpoint or DocumentIntelligenceClient is None:
        return None

    model = os.environ.get("DOCUMENT_INTELLIGENCE_MODEL", DEFAULT_DOCUMENT_INTELLIGENCE_MODEL).strip()
    if not model:
        model = DEFAULT_DOCUMENT_INTELLIGENCE_MODEL

    key = os.environ.get("DOCUMENT_INTELLIGENCE_KEY", "").strip()
    if not key or AzureKeyCredential is None:
        return None

    try:
        client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        poller = client.begin_analyze_document(
            model_id=model,
            body=payload,
            content_type=content_type,
        )
        result = poller.result()
    except Exception:  # pragma: no cover - network/service failures fallback to local extraction
        return None

    content = (getattr(result, "content", "") or "").strip()
    if content:
        return content

    lines: list[str] = []
    for page in getattr(result, "pages", []) or []:
        for line in getattr(page, "lines", []) or []:
            text = (getattr(line, "content", "") or "").strip()
            if text:
                lines.append(text)
    joined = "\n".join(lines).strip()
    return joined or None


def encode_base64(payload: bytes) -> str:
    """Return a UTF-8 base64 representation of the supplied payload."""

    return base64.b64encode(payload).decode("utf-8")


def process_image(payload: bytes, file_name: str, content_type: str) -> ProcessedUpload:
    """Capture lightweight information about an uploaded image."""

    metadata: dict[str, str] = {
        "file_name": file_name,
        "content_type": content_type,
        "hint": "Image available as base64."
    }
    original_size = len(payload)
    if original_size > MAX_IMAGE_BYTES:
        optimised, optimisation_metadata = _optimise_image_payload(payload)
        payload = optimised
        metadata.update(optimisation_metadata)
    encoded = encode_base64(payload)
    if len(encoded) > MAX_IMAGE_BASE64_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image is too large to store. Please upload a file under 1 MB.",
        )
    width: str | None = None
    height: str | None = None
    image_format: str | None = None
    if Image is not None:
        try:
            with Image.open(BytesIO(payload)) as img:
                width, height = str(img.width), str(img.height)
                image_format = str(img.format or "")
        except Exception:  # pragma: no cover - best effort metadata only
            width = height = image_format = None
    if width and height:
        metadata["dimensions"] = f"{width}x{height}"
    if image_format:
        metadata["format"] = image_format

    extracted_text = extract_text_with_doc_intelligence(payload, content_type)
    if extracted_text:
        metadata["hint"] = "Text extracted from image via Document Intelligence."
        metadata["ocr_source"] = "document_intelligence"

    return ProcessedUpload(
        content_type=content_type,
        file_name=file_name,
        encoded_content=encoded,
        extracted_text=extracted_text,
        metadata=metadata,
        binary=payload,
    )


def process_pdf(payload: bytes, file_name: str, content_type: str) -> ProcessedUpload:
    """Extract text content from a PDF payload and return metadata."""

    extracted_by = "pypdf"
    text = extract_text_with_doc_intelligence(payload, content_type)
    if text:
        extracted_by = "document_intelligence"
    else:
        text = extract_pdf_text(payload)
    metadata = {
        "file_name": file_name,
        "content_type": content_type,
        "hint": "Text extracted from PDF.",
        "ocr_source": extracted_by,
    }
    return ProcessedUpload(
        content_type=content_type,
        file_name=file_name,
        encoded_content=None,
        extracted_text=text,
        metadata=metadata,
        binary=payload,
    )


def process_upload(payload: bytes, file_name: str, content_type: str) -> ProcessedUpload:
    """Route uploads through the appropriate processor."""

    ensure_supported_file(content_type)
    if content_type in ALLOWED_PDF_TYPES:
        return process_pdf(payload, file_name, content_type)
    return process_image(payload, file_name, content_type)


def _optimise_image_payload(payload: bytes) -> tuple[bytes, dict[str, str]]:
    """Attempt to downscale or compress large images to fit within Cosmos limits."""

    if Image is None:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image exceeds 1 MB and cannot be resized on the server. Please upload a smaller image.",
        )

    try:
        with Image.open(BytesIO(payload)) as img:
            img = img.convert("RGB")
            img.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION))
            for quality in (85, 75, 65, 55):
                buffer = BytesIO()
                img.save(buffer, format="JPEG", optimize=True, quality=quality)
                candidate = buffer.getvalue()
                if len(candidate) <= MAX_IMAGE_BYTES:
                    return candidate, {
                        "hint": "Image downscaled for storage.",
                        "original_size_bytes": str(len(payload)),
                        "stored_size_bytes": str(len(candidate)),
                        "stored_format": "JPEG",
                    }
    except Exception:
        pass

    raise HTTPException(
        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        detail="Image file is too large even after compression attempts. Please upload an image under 1 MB.",
    )
