"""Tests for OCR necessity detector."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from config import OcrMode
from src.detectors.ocr_needed import _pdf_has_no_text_layer, is_ocr_needed
from src.parsers.pdf_parser import PdfParser


class TestIsOcrNeeded:
    def test_force_mode(self, tmp_path: Path) -> None:
        f = tmp_path / "test.pdf"
        f.write_text("text")
        assert is_ocr_needed(f, OcrMode.FORCE) is True

    def test_skip_mode(self, tmp_path: Path) -> None:
        f = tmp_path / "test.pdf"
        f.write_text("text")
        assert is_ocr_needed(f, OcrMode.SKIP) is False

    def test_image_file_needs_ocr(self, tmp_path: Path) -> None:
        f = tmp_path / "photo.png"
        f.write_text("fake")
        assert is_ocr_needed(f, OcrMode.AUTO) is True

    def test_docx_no_ocr(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.docx"
        f.write_text("fake")
        assert is_ocr_needed(f, OcrMode.AUTO) is False

    def test_xlsx_no_ocr(self, tmp_path: Path) -> None:
        f = tmp_path / "data.xlsx"
        f.write_text("fake")
        assert is_ocr_needed(f, OcrMode.AUTO) is False


class TestPdfHasNoTextLayer:
    def test_text_pdf(self, tmp_path: Path) -> None:
        f = tmp_path / "text.pdf"
        f.write_text("fake")

        with patch("fitz.open") as mock_open:
            mock_doc = MagicMock()
            mock_doc.__len__.return_value = 1
            mock_open.return_value = mock_doc

            mock_page = MagicMock()
            mock_page.get_text.return_value = "This is a text PDF with lots of content " * 10
            mock_doc.__getitem__.return_value = mock_page

            assert _pdf_has_no_text_layer(f) is False

    def test_scanned_pdf(self, tmp_path: Path) -> None:
        f = tmp_path / "scanned.pdf"
        f.write_text("fake")

        with patch("fitz.open") as mock_open:
            mock_doc = MagicMock()
            mock_doc.__len__.return_value = 1
            mock_open.return_value = mock_doc

            mock_page = MagicMock()
            mock_page.get_text.return_value = "   \n  \n"
            mock_doc.__getitem__.return_value = mock_page

            assert _pdf_has_no_text_layer(f) is True

    def test_fitz_error(self, tmp_path: Path) -> None:
        f = tmp_path / "bad.pdf"
        f.write_text("fake")

        with patch("fitz.open") as mock_open:
            mock_open.side_effect = Exception("Corrupt")
            assert _pdf_has_no_text_layer(f) is True

    def test_with_real_pdf_parser(self, tmp_path: Path) -> None:
        """Integration smoke test: parser + detector."""
        parser = PdfParser()
        f = tmp_path / "smoke.pdf"
        f.write_text("fake")

        with patch("fitz.open") as mock_open:
            mock_doc = MagicMock()
            mock_doc.__len__.return_value = 1
            mock_open.return_value = mock_doc
            mock_page = MagicMock()
            mock_page.get_text.return_value = "Hello " * 20
            mock_page.find_tables.return_value = []
            mock_doc.__getitem__.return_value = mock_page
            mock_doc.metadata = {}

            result = parser.parse(f)
            assert result.success is True
            assert len(result.content) > 0
