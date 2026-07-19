"""Tests for OCR engine."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.ocr.engine import OcrEngine


@pytest.fixture
def ocr_engine() -> OcrEngine:
    eng = OcrEngine(lang="eng")
    eng._pytesseract_available = None
    return eng


class TestOcrEngine:
    def test_init(self, ocr_engine: OcrEngine) -> None:
        assert ocr_engine.lang == "eng"
        assert ocr_engine._pytesseract_available is None

    @patch("pytesseract.get_tesseract_version")
    def test_tesseract_available(self, mock_ver: MagicMock, ocr_engine: OcrEngine) -> None:
        mock_ver.return_value = "5.0"
        assert ocr_engine.is_tesseract_available is True

    @patch("pytesseract.get_tesseract_version")
    def test_tesseract_not_available(self, mock_ver: MagicMock, ocr_engine: OcrEngine) -> None:
        mock_ver.side_effect = OSError("not found")
        ocr_engine._pytesseract_available = None
        assert ocr_engine.is_tesseract_available is False

    def test_recognize_success(self, ocr_engine: OcrEngine) -> None:
        ocr_engine._pytesseract_available = True
        with patch("pytesseract.image_to_string") as mock_ts:
            mock_ts.return_value = "Hello World\n"
            result = ocr_engine.recognize(MagicMock(), lang="eng")

        assert result == "Hello World"
        mock_ts.assert_called_once()

    def test_recognize_no_engine(self, ocr_engine: OcrEngine) -> None:
        ocr_engine._pytesseract_available = False
        with pytest.raises(RuntimeError, match="没有可用的 OCR 引擎"):
            ocr_engine.recognize(MagicMock())

    def test_preprocess_image_no_cv2(self, ocr_engine: OcrEngine) -> None:
        ocr_engine._cv2_available = False
        mock_image = MagicMock()
        result = ocr_engine.preprocess_image(mock_image)
        assert result is mock_image
