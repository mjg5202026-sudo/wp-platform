"""Word Parser — 使用 python-docx 解析 Word 文档。"""

from __future__ import annotations

import time
from pathlib import Path

from docx import Document as DocxDocument

from config import FileFormat, parser_config
from src.parsers.base import BaseParser, ParseResult, TableContent


class WordParser(BaseParser):
    """Word 文档解析器。"""

    @property
    def supported_formats(self) -> set[FileFormat]:
        return {FileFormat.DOCX}

    def parse(self, file_path: Path) -> ParseResult:
        start = time.perf_counter()
        try:
            doc = DocxDocument(file_path)
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            return ParseResult(
                file_path=file_path,
                file_format=FileFormat.DOCX,
                content="",
                success=False,
                error_message=f"Word 打开失败: {e}",
                processing_time_ms=round(elapsed, 2),
            )

        try:
            paragraphs: list[str] = []
            for para in doc.paragraphs:
                text = para.text.strip()
                if text:
                    style = para.style.name.lower() if para.style else ""
                    if "heading" in style:
                        level = style.replace("heading ", "").replace("heading", "")
                        prefix = "#" * max(1, int(level)) if level.isdigit() else "##"
                        paragraphs.append(f"{prefix} {text}")
                    else:
                        paragraphs.append(text)

            tables: list[TableContent] = []
            for i, table in enumerate(doc.tables):
                headers: list[str] = []
                rows: list[list[str]] = []
                for row_idx, row in enumerate(table.rows):
                    cells = [cell.text.strip() for cell in row.cells]
                    if row_idx == 0:
                        headers = cells
                    else:
                        rows.append(cells)
                tables.append(TableContent(
                    name=f"Table {i + 1}",
                    headers=headers,
                    rows=rows,
                ))

            if parser_config.docx_extract_headers:
                for section in doc.sections:
                    if section.header and section.header.paragraphs:
                        header_texts = [p.text.strip() for p in section.header.paragraphs if p.text.strip()]
                        if header_texts:
                            paragraphs.insert(0, f"*Header: {' | '.join(header_texts)}*")

            content = "\n\n".join(paragraphs) if paragraphs else "(空文档)"
            meta = self._extract_metadata(doc, file_path)

            elapsed = (time.perf_counter() - start) * 1000
            return ParseResult(
                file_path=file_path,
                file_format=FileFormat.DOCX,
                content=content,
                tables=tables or None,
                metadata=meta,
                success=True,
                processing_time_ms=round(elapsed, 2),
            )

        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            return ParseResult(
                file_path=file_path,
                file_format=FileFormat.DOCX,
                content="",
                success=False,
                error_message=f"Word 解析失败: {e}",
                processing_time_ms=round(elapsed, 2),
            )

    def _extract_metadata(self, doc: object, file_path: Path) -> dict:
        meta: dict = {
            "file_name": file_path.name,
            "file_size_bytes": file_path.stat().st_size,
        }
        try:
            core_props = doc.core_properties
            for attr in ("title", "author", "subject", "keywords", "category", "comments", "created", "modified"):
                val = getattr(core_props, attr, None)
                if val:
                    meta[attr] = str(val)
        except Exception:
            pass
        return meta
