"""Image Parser — 使用 OCR 识别图片文字。"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Optional

from PIL import Image

from config import FileFormat, parser_config
from src.ocr.engine import OcrEngine
from src.parsers.base import BaseParser, ParseResult


class ImageParser(BaseParser):
    """图片解析器（OCR 识别）。"""

    def __init__(self, ocr_engine: Optional[OcrEngine] = None) -> None:
        self._ocr = ocr_engine or OcrEngine()

    @property
    def supported_formats(self) -> set[FileFormat]:
        return {FileFormat.PNG, FileFormat.JPG, FileFormat.JPEG, FileFormat.TIFF, FileFormat.BMP}

    def parse(
        self,
        file_path: Path,
        *,
        lang: Optional[str] = None,
    ) -> ParseResult:
        start = time.perf_counter()
        try:
            image = Image.open(file_path)
            preprocessed = self._ocr.preprocess_image(image)
            text = self._ocr.recognize(preprocessed, lang=lang)

            full_text = text.strip()
            meta = self._extract_metadata(file_path, image)

            elapsed = (time.perf_counter() - start) * 1000
            return ParseResult(
                file_path=file_path,
                file_format=self._detect_format(file_path),
                content=full_text,
                metadata=meta,
                ocr_applied=True,
                ocr_engine="tesseract",
                success=True,
                processing_time_ms=round(elapsed, 2),
            )

        except RuntimeError as e:
            elapsed = (time.perf_counter() - start) * 1000
            return ParseResult(
                file_path=file_path,
                file_format=self._detect_format(file_path),
                content="",
                success=False,
                error_message=str(e),
                processing_time_ms=round(elapsed, 2),
            )
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            return ParseResult(
                file_path=file_path,
                file_format=self._detect_format(file_path),
                content="",
                success=False,
                error_message=f"图片解析失败: {e}",
                processing_time_ms=round(elapsed, 2),
            )

    def _extract_metadata(self, file_path: Path, image: Image.Image) -> dict:
        """提取图片元数据。"""
        meta: dict = {
            "file_name": file_path.name,
            "file_size_bytes": file_path.stat().st_size,
            "image_width": image.width,
            "image_height": image.height,
            "image_mode": image.mode,
            "image_format": image.format or "",
        }
        # 尝试提取 EXIF
        try:
            import exifread
            with open(file_path, "rb") as f:
                tags = exifread.process_file(f, details=False)
            for key in ("Image Make", "Image Model", "Image DateTime", "EXIF DateTimeOriginal"):
                if key in tags:
                    meta[f"exif_{key.lower().replace(' ', '_')}"] = str(tags[key])
        except Exception:
            pass
        return meta

    def _detect_format(self, file_path: Path) -> FileFormat:
        from src.utils.file_utils import detect_format
        return detect_format(file_path)
