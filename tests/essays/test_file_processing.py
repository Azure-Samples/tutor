"""Tests for upload processing and OCR fallback behavior in essays service."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
essays_root = repo_root / "apps" / "essays"
if str(essays_root) not in sys.path:
    sys.path.insert(0, str(essays_root))
essays_src = essays_root / "src"
if str(essays_src) not in sys.path:
    sys.path.insert(0, str(essays_src))

file_processing = importlib.import_module("app.file_processing")


class _FakePoller:
    def __init__(self, result):
        self._result = result

    def result(self):
        return self._result


class _FakeResult:
    def __init__(self, content: str):
        self.content = content
        self.pages = []


class _FakeCredential:
    def __init__(self, key: str):
        self.key = key


class _FakeDocIntelClient:
    calls: list[dict[str, object]] = []

    def __init__(self, endpoint: str, credential):
        self.endpoint = endpoint
        self.credential = credential

    def begin_analyze_document(self, model_id: str, body: bytes, content_type: str):
        _FakeDocIntelClient.calls.append(
            {
                "endpoint": self.endpoint,
                "credential": self.credential,
                "model_id": model_id,
                "body": body,
                "content_type": content_type,
            }
        )
        return _FakePoller(_FakeResult("extracted from document intelligence"))


def test_extract_text_with_doc_intelligence_returns_none_without_endpoint(monkeypatch):
    monkeypatch.delenv("DOCUMENT_INTELLIGENCE_ENDPOINT", raising=False)
    monkeypatch.setenv("DOCUMENT_INTELLIGENCE_KEY", "test-key")
    result = file_processing.extract_text_with_doc_intelligence(b"bytes", "application/pdf")
    assert result is None


def test_extract_text_with_doc_intelligence_uses_client(monkeypatch):
    _FakeDocIntelClient.calls.clear()
    monkeypatch.setenv("DOCUMENT_INTELLIGENCE_ENDPOINT", "https://example.cognitiveservices.azure.com")
    monkeypatch.setenv("DOCUMENT_INTELLIGENCE_KEY", "test-key")
    monkeypatch.setenv("DOCUMENT_INTELLIGENCE_MODEL", "prebuilt-read")
    monkeypatch.setattr(file_processing, "DocumentIntelligenceClient", _FakeDocIntelClient)
    monkeypatch.setattr(file_processing, "AzureKeyCredential", _FakeCredential)

    payload = b"dummy-pdf"
    result = file_processing.extract_text_with_doc_intelligence(payload, "application/pdf")

    assert result == "extracted from document intelligence"
    assert len(_FakeDocIntelClient.calls) == 1
    recorded = _FakeDocIntelClient.calls[0]
    assert recorded["model_id"] == "prebuilt-read"
    assert recorded["body"] == payload
    assert recorded["content_type"] == "application/pdf"


def test_process_pdf_prefers_document_intelligence(monkeypatch):
    monkeypatch.setattr(file_processing, "extract_text_with_doc_intelligence", lambda *_args, **_kwargs: "ocr-text")
    monkeypatch.setattr(
        file_processing,
        "extract_pdf_text",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("fallback should not be called")),
    )

    processed = file_processing.process_pdf(b"payload", "essay.pdf", "application/pdf")

    assert processed.extracted_text == "ocr-text"
    assert processed.metadata["ocr_source"] == "document_intelligence"


def test_process_pdf_falls_back_to_pypdf(monkeypatch):
    monkeypatch.setattr(file_processing, "extract_text_with_doc_intelligence", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(file_processing, "extract_pdf_text", lambda *_args, **_kwargs: "fallback-text")

    processed = file_processing.process_pdf(b"payload", "essay.pdf", "application/pdf")

    assert processed.extracted_text == "fallback-text"
    assert processed.metadata["ocr_source"] == "pypdf"


def test_process_image_captures_doc_intelligence_text(monkeypatch):
    monkeypatch.setattr(file_processing, "extract_text_with_doc_intelligence", lambda *_args, **_kwargs: "image-ocr")

    processed = file_processing.process_image(b"small-image-bytes", "image.png", "image/png")

    assert processed.extracted_text == "image-ocr"
    assert processed.metadata["ocr_source"] == "document_intelligence"
