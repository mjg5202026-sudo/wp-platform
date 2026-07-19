"""OCR engine — Tesseract 封装，含失败降级逻辑。"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PIL import Image

from config import parser_config


class OcrEngine:
    """OCR 引擎封装。

    主引擎: Tesseract (pytesseract)
    后续可扩展: PaddleOCR 作为更高精度的选项
    """

    def __init__(self, lang: Optional[str] = None) -> None:
        self.lang = lang or parser_config.ocr_lang
        self._pytesseract_available: Optional[bool] = None
        self._cv2_available: Optional[bool] = None

    @property
    def is_tesseract_available(self) -> bool:
        """检查 Tesseract 是否可用。"""
        if self._pytesseract_available is not None:
            return self._pytesseract_available
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            self._pytesseract_available = True
        except (OSError, ImportError):
            self._pytesseract_available = False
        return self._pytesseract_available

    def recognize(
        self,
        image: Image.Image,
        *,
        lang: Optional[str] = None,
        confidence_threshold: Optional[float] = None,
    ) -> str:
        """对图片执行 OCR。

        Args:
            image: PIL Image 对象。
            lang: OCR 语言（覆盖默认值）。
            confidence_threshold: 置信度阈值。

        Returns:
            识别出的文本。

        Raises:
            RuntimeError: 所有 OCR 引擎均不可用。
        """
        threshold = confidence_threshold if confidence_threshold is not None else parser_config.ocr_confidence_threshold
        lang = lang or self.lang

        if self.is_tesseract_available:
            return self._recognize_tesseract(image, lang=lang)
        raise RuntimeError("没有可用的 OCR 引擎 (pytesseract 不可用)")

    def _recognize_tesseract(self, image: Image.Image, lang: str) -> str:
        """使用 Tesseract 进行 OCR。"""
        import pytesseract
        try:
            text = pytesseract.image_to_string(
                image,
                lang=lang,
                config="--oem 3 --psm 6",
            )
            return text.strip()
        except OSError as e:
            raise RuntimeError(f"Tesseract OCR 失败: {e}") from e

    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """预处理图片以提升 OCR 准确率。"""
        if self._cv2_available is None:
            try:
                import cv2  # noqa: F401
                self._cv2_available = True
            except ImportError:
                self._cv2_available = False

        if not self._cv2_available:
            return image  # opencv 不可用时跳过预处理

        import cv2
        import numpy as np

        img_array = np.array(image.convert("RGB"))
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        denoised = cv2.fastNlMeansDenoising(gray, h=30)
        _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return Image.fromarray(binary)
