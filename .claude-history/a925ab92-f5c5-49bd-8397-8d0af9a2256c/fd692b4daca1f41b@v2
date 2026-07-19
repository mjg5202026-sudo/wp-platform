"""Tests for DocumentReader orchestrator."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from config import OcrMode
from src.reader import DocumentReader


@pytest.fixture
def reader() -> DocumentReader:
    return DocumentReader(ocr_mode=OcrMode.AUTO)


class TestDocumentReader:
    def test_init(self, reader: DocumentReader) -> None:
        assert reader.ocr_mode == OcrMode.AUTO
        assert len(reader._parsers) == 4

    def test_set_ocr_lang(self, reader: DocumentReader) -> None:
        reader.set_ocr_lang("eng")
        for parser in reader._parsers:
            if hasattr(parser, "_ocr"):
                assert parser._ocr.lang == "eng"

    def test_no_supported_files(self, reader: DocumentReader, tmp_path: Path) -> None:
        f = tmp_path / "test.txt"
        f.write_text("hello")
        results = reader.read(tmp_path)
        assert results == []

    def test_read_nonexistent(self, reader: DocumentReader) -> None:
        results = reader.read(Path("nonexistent"))
        assert results == []

    @patch("src.reader.is_ocr_needed", return_value=False)
    @patch("src.parsers.pdf_parser.fitz.open")
    def test_read_pdf_with_text(
        self, mock_fitz_open: MagicMock, mock_ocr_check: MagicMock,
        reader: DocumentReader, tmp_path: Path,
    ) -> None:
        """PDF with text content — direct text extraction path."""
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 1
        mock_fitz_open.return_value = mock_doc

        mock_page = MagicMock()
        mock_page.get_text.return_value = "Real PDF text content here"
        mock_page.find_tables.return_value = []
        mock_doc.__getitem__.return_value = mock_page
        mock_doc.metadata = {}

        f = tmp_path / "text.pdf"
        f.write_text("pdf content")

        results = reader.read(f)
        assert len(results) == 1
        assert results[0].success is True
        assert results[0].content == "Real PDF text content here"
        assert results[0].ocr_applied is False

    @patch("src.reader.is_ocr_needed", return_value=True)
    @patch("PIL.Image.open")
    @patch("src.parsers.pdf_parser.fitz.open")
    def test_read_scanned_pdf(
        self, mock_fitz_open: MagicMock, mock_pil_open: MagicMock,
        mock_ocr_check: MagicMock, reader: DocumentReader, tmp_path: Path,
    ) -> None:
        """Scanned PDF — OCR extraction path."""
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 1
        mock_fitz_open.return_value = mock_doc

        mock_ocr = MagicMock()
        mock_ocr.recognize.return_value = "OCR extracted text"
        # Inject mock OCR into the PdfParser
        reader._parsers[0]._ocr = mock_ocr

        mock_page = MagicMock()
        mock_page.get_text.return_value = ""
        mock_page.find_tables.return_value = []
        mock_pixmap = MagicMock()
        mock_pixmap.tobytes.return_value = b"fake_png_bytes"
        mock_page.get_pixmap.return_value = mock_pixmap
        mock_doc.__getitem__.return_value = mock_page
        mock_doc.metadata = {}
        mock_pil_open.return_value = MagicMock()

        f = tmp_path / "scanned.pdf"
        f.write_text("pdf content")

        results = reader.read(f)
        assert len(results) == 1
        assert results[0].success is True
        assert results[0].ocr_applied is True

    def test_read_one_no_match(self, reader: DocumentReader, tmp_path: Path) -> None:
        f = tmp_path / "test.txt"
        f.write_text("hello")
        result = reader.read_one(f)
        assert result is None

    @patch("src.reader.DocumentReader.read")
    def test_process_and_save(self, mock_read: MagicMock, reader: DocumentReader, tmp_path: Path) -> None:
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.file_path = Path("test.pdf")
        mock_result.file_format.value = "pdf"
        mock_result.content = "# Content"
        mock_result.metadata = {"file_name": "test.pdf"}
        mock_result.ocr_applied = False
        mock_result.ocr_engine = None
        mock_result.processing_time_ms = 100.0
        mock_result.error_message = None
        mock_read.return_value = [mock_result]

        output_dir = tmp_path / "output"
        saved = reader.process_and_save(tmp_path, output_dir)

        assert len(saved) >= 2  # markdown + metadata
        assert (output_dir / "test.md").exists()
        assert (output_dir / "test_metadata.json").exists()
