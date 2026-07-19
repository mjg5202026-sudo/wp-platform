"""PDF Parser — 使用 PyMuPDF 解析 PDF，支持扫描件 OCR。"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Optional

import fitz

from config import FileFormat, parser_config
from src.ocr.engine import OcrEngine
from src.parsers.base import BaseParser, PageContent, ParseResult


class PdfParser(BaseParser):
    """PDF 解析器。

    文字版 PDF：直接使用 PyMuPDF 提取文本。
    扫描件 PDF：渲染页面为图片后调用 OCR 引擎。
    """

    def __init__(self, ocr_engine: Optional[OcrEngine] = None) -> None:
        self._ocr = ocr_engine or OcrEngine()

    @property
    def supported_formats(self) -> set[FileFormat]:
        return {FileFormat.PDF}

    def parse(
        self,
        file_path: Path,
        *,
        page_limit: Optional[int] = None,
        ocr: bool = False,
    ) -> ParseResult:
        start = time.perf_counter()
        limit = page_limit or parser_config.pdf_page_limit
        try:
            doc = fitz.open(file_path)
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            return ParseResult(
                file_path=file_path,
                file_format=FileFormat.PDF,
                content="",
                success=False,
                error_message=f"PDF 打开失败: {e}",
                processing_time_ms=round(elapsed, 2),
            )

        try:
            total_pages = len(doc)
            pages_to_read = min(total_pages, limit) if limit else total_pages

            if ocr:
                result = self._parse_with_ocr(doc, file_path, pages_to_read, total_pages, start)
            else:
                result = self._parse_text(doc, file_path, pages_to_read, total_pages, start)

            return result
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            return ParseResult(
                file_path=file_path,
                file_format=FileFormat.PDF,
                content="",
                success=False,
                error_message=f"PDF 解析失败: {e}",
                processing_time_ms=round(elapsed, 2),
            )
        finally:
            doc.close()

    def _parse_text(
        self,
        doc: fitz.Document,
        file_path: Path,
        pages_to_read: int,
        total_pages: int,
        start: float,
    ) -> ParseResult:
        full_text_parts: list[str] = []
        page_contents: list[PageContent] = []

        for page_num in range(pages_to_read):
            page = doc[page_num]
            text = page.get_text().strip()
            page_obj = PageContent(page_number=page_num + 1, text=text)
            page_contents.append(page_obj)
            if text:
                full_text_parts.append(text)

            try:
                tabs = page.find_tables()
                if tabs:
                    for tab in tabs:
                        table_data = tab.extract()
                        if table_data:
                            page_obj.tables.append(table_data)
            except Exception:
                pass

        content = "\n\n".join(full_text_parts) if full_text_parts else ""
        meta = self._extract_metadata(doc, file_path)

        elapsed = (time.perf_counter() - start) * 1000
        return ParseResult(
            file_path=file_path,
            file_format=FileFormat.PDF,
            content=content,
            pages=page_contents,
            metadata={**meta, "total_pages": total_pages, "pages_extracted": pages_to_read},
            success=True,
            processing_time_ms=round(elapsed, 2),
        )

    def _parse_with_ocr(
        self,
        doc: fitz.Document,
        file_path: Path,
        pages_to_read: int,
        total_pages: int,
        start: float,
    ) -> ParseResult:
        from PIL import Image
        import io

        full_text_parts: list[str] = []
        page_contents: list[PageContent] = []

        for page_num in range(pages_to_read):
            page = doc[page_num]
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")

            image = Image.open(io.BytesIO(img_data))
            text = self._ocr.recognize(image)
            page_obj = PageContent(page_number=page_num + 1, text=text)
            page_contents.append(page_obj)
            if text:
                full_text_parts.append(text)

        content = "\n\n".join(full_text_parts) if full_text_parts else ""
        meta = self._extract_metadata(doc, file_path)

        elapsed = (time.perf_counter() - start) * 1000
        return ParseResult(
            file_path=file_path,
            file_format=FileFormat.PDF,
            content=content,
            pages=page_contents,
            metadata={**meta, "total_pages": total_pages, "pages_extracted": pages_to_read},
            ocr_applied=True,
            ocr_engine="tesseract",
            success=True,
            processing_time_ms=round(elapsed, 2),
        )

    def _extract_metadata(self, doc: fitz.Document, file_path: Path) -> dict:
        meta: dict = {}
        pdf_meta = doc.metadata or {}
        for key in ("title", "author", "subject", "keywords", "producer", "creator"):
            val = pdf_meta.get(key)
            if val:
                meta[key] = val
        meta["file_name"] = file_path.name
        meta["file_size_bytes"] = file_path.stat().st_size
        return meta
