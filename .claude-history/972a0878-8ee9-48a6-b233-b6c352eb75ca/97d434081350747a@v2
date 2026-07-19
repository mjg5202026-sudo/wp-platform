"""Tests for Image parser."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from config import FileFormat
from src.ocr.engine import OcrEngine
from src.parsers.image_parser import ImageParser


class TestImageParser:
    def test_supported_formats(self) -> None:
        parser = ImageParser(ocr_engine=MagicMock())
        for fmt in (FileFormat.PNG, FileFormat.JPG, FileFormat.JPEG, FileFormat.TIFF):
            assert fmt in parser.supported_formats

    def test_parse_success(self, tmp_path: Path) -> None:
        mock_ocr = MagicMock(spec=OcrEngine)
        mock_ocr.preprocess_image.return_value = MagicMock()
        mock_ocr.recognize.return_value = "Hello World\nThis is OCR"
        parser = ImageParser(ocr_engine=mock_ocr)

        img_path = tmp_path / "test.png"
        _create_minimal_png(img_path)

        result = parser.parse(img_path)

        assert result.success is True
        assert result.ocr_applied is True
        assert result.ocr_engine == "tesseract"
        assert result.content == "Hello World\nThis is OCR"
        assert "image_width" in result.metadata

    def test_parse_runtime_error(self, tmp_path: Path) -> None:
        mock_ocr = MagicMock(spec=OcrEngine)
        mock_ocr.preprocess_image.return_value = MagicMock()
        mock_ocr.recognize.side_effect = RuntimeError("Tesseract not available")
        parser = ImageParser(ocr_engine=mock_ocr)

        img_path = tmp_path / "test.png"
        _create_minimal_png(img_path)

        result = parser.parse(img_path)
        assert result.success is False
        assert "Tesseract not available" in (result.error_message or "")

    def test_parse_file_error(self, tmp_path: Path) -> None:
        parser = ImageParser(ocr_engine=MagicMock(spec=OcrEngine))
        img_path = tmp_path / "corrupt.png"
        img_path.write_text("not an image")

        result = parser.parse(img_path)
        assert result.success is False


def _create_minimal_png(path: Path) -> None:
    """Create a minimal valid PNG file for testing."""
    import struct
    import zlib

    width, height = 1, 1
    raw_data = b'\x00' + b'\xff\xff\xff'

    def chunk(chunk_type: bytes, data: bytes) -> bytes:
        c = chunk_type + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)

    ihdr = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    idat = zlib.compress(raw_data)

    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n')
        f.write(chunk(b'IHDR', ihdr))
        f.write(chunk(b'IDAT', idat))
        f.write(chunk(b'IEND', b''))
