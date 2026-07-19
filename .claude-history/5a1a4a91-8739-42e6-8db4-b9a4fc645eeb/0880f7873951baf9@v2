"""Tests for PDF parser."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.ocr.engine import OcrEngine
from src.parsers.base import FileFormat
from src.parsers.pdf_parser import PdfParser


class TestPdfParserTextMode:
    def test_supported_formats(self) -> None:
        parser = PdfParser(ocr_engine=MagicMock(spec=OcrEngine))
        assert FileFormat.PDF in parser.supported_formats

    @patch("fitz.open")
    def test_parse_text_pdf(self, mock_open: MagicMock, tmp_path: Path) -> None:
        parser = PdfParser(ocr_engine=MagicMock(spec=OcrEngine))

        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 2
        mock_open.return_value = mock_doc

        mock_page1 = MagicMock()
        mock_page1.get_text.return_value = "Page 1 content"
        mock_page1.find_tables.return_value = []
        mock_page2 = MagicMock()
        mock_page2.get_text.return_value = "Page 2 content"
        mock_page2.find_tables.return_value = []
        mock_doc.__getitem__.side_effect = [mock_page1, mock_page2]
        mock_doc.metadata = {"title": "Test PDF", "author": "Tester"}

        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_text("fake pdf content")

        result = parser.parse(pdf_path)

        assert result.success is True
        assert result.file_format == FileFormat.PDF
        assert "Page 1 content" in result.content
        assert "Page 2 content" in result.content
        assert result.metadata["total_pages"] == 2
        assert result.pages is not None
        assert len(result.pages) == 2

    @patch("fitz.open")
    def test_parse_empty_pdf(self, mock_open: MagicMock, tmp_path: Path) -> None:
        parser = PdfParser(ocr_engine=MagicMock(spec=OcrEngine))

        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 1
        mock_open.return_value = mock_doc
        mock_page = MagicMock()
        mock_page.get_text.return_value = ""
        mock_page.find_tables.return_value = []
        mock_doc.__getitem__.return_value = mock_page
        mock_doc.metadata = {}

        pdf_path = tmp_path / "empty.pdf"
        pdf_path.write_text("")

        result = parser.parse(pdf_path)
        assert result.success is True
        assert result.content == ""

    @patch("fitz.open")
    def test_parse_error(self, mock_open: MagicMock, tmp_path: Path) -> None:
        parser = PdfParser(ocr_engine=MagicMock(spec=OcrEngine))
        mock_open.side_effect = RuntimeError("file corrupted")

        pdf_path = tmp_path / "corrupt.pdf"
        pdf_path.write_text("not a pdf")

        result = parser.parse(pdf_path)
        assert result.success is False


class TestPdfParserOcrMode:
    @patch("PIL.Image.open")
    @patch("fitz.open")
    def test_parse_with_ocr(
        self, mock_fitz_open: MagicMock, mock_pil_open: MagicMock, tmp_path: Path
    ) -> None:
        mock_ocr = MagicMock(spec=OcrEngine)
        mock_ocr.recognize.return_value = "OCR extracted text"
        parser = PdfParser(ocr_engine=mock_ocr)

        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 1
        mock_fitz_open.return_value = mock_doc

        mock_page = MagicMock()
        mock_pixmap = MagicMock()
        mock_pixmap.tobytes.return_value = b"fake_png_bytes"
        mock_page.get_pixmap.return_value = mock_pixmap
        mock_doc.__getitem__.return_value = mock_page
        mock_doc.metadata = {}

        mock_pil_open.return_value = MagicMock()

        pdf_path = tmp_path / "scanned.pdf"
        pdf_path.write_text("fake")

        result = parser.parse(pdf_path, ocr=True)

        assert result.success is True
        assert result.ocr_applied is True
        assert result.ocr_engine == "tesseract"
        assert "OCR extracted text" in result.content
