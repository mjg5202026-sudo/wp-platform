"""Tests for Markdown converter."""

from __future__ import annotations

from pathlib import Path

import pytest

from config import FileFormat
from src.converters.markdown import _format_table, convert_to_markdown, save_markdown, save_metadata
from src.parsers.base import ParseResult, TableContent


class TestConvertToMarkdown:
    def test_basic_conversion(self) -> None:
        result = ParseResult(
            file_path=Path("test.pdf"),
            file_format=FileFormat.PDF,
            content="Hello world",
            metadata={"title": "Test"},
            success=True,
        )
        md = convert_to_markdown(result, title="My Document")
        assert "# My Document" in md
        assert "Hello world" in md
        assert "**OCR**: 否" in md
        assert "pdf" in md

    def test_with_ocr_info(self) -> None:
        result = ParseResult(
            file_path=Path("scan.png"),
            file_format=FileFormat.PNG,
            content="OCR text",
            ocr_applied=True,
            ocr_engine="tesseract",
            processing_time_ms=1500.0,
            success=True,
        )
        md = convert_to_markdown(result)
        assert "**OCR**: 是" in md
        assert "**OCR 引擎**: `tesseract`" in md
        assert "**处理耗时**: 1500ms" in md

    def test_with_tables(self) -> None:
        result = ParseResult(
            file_path=Path("data.xlsx"),
            file_format=FileFormat.XLSX,
            content="Sheet data",
            tables=[
                TableContent(
                    name="Sheet1",
                    headers=["A", "B", "C"],
                    rows=[["1", "2", "3"], ["4", "5", "6"]],
                    sheet_name="Sheet1",
                )
            ],
            success=True,
        )
        md = convert_to_markdown(result)
        assert "## 表格" in md
        assert "| A | B | C |" in md
        assert "| 1 | 2 | 3 |" in md

    def test_no_content(self) -> None:
        result = ParseResult(
            file_path=Path("empty.pdf"),
            file_format=FileFormat.PDF,
            content="",
            success=True,
        )
        md = convert_to_markdown(result)
        assert "*(无文本内容)*" in md


class TestFormatTable:
    def test_with_headers(self) -> None:
        table = TableContent(name="Test", headers=["X", "Y"], rows=[["1", "2"]], sheet_name="S1")
        lines = _format_table(table)
        assert "### Test" in lines
        assert "| X | Y |" in lines[1]

    def test_no_headers(self) -> None:
        table = TableContent(name="", headers=[], rows=[["a", "b"]], sheet_name="S1")
        lines = _format_table(table)
        assert len(lines) >= 2


class TestSaveFunctions:
    def test_save_markdown(self, tmp_path: Path) -> None:
        result = ParseResult(
            file_path=Path("doc.pdf"),
            file_format=FileFormat.PDF,
            content="# Content",
            success=True,
        )
        md_path = save_markdown(result, tmp_path)
        assert md_path.exists()
        content = md_path.read_text("utf-8")
        assert "# Content" in content

    def test_save_metadata(self, tmp_path: Path) -> None:
        result = ParseResult(
            file_path=Path("doc.pdf"),
            file_format=FileFormat.PDF,
            content="text",
            success=True,
            processing_time_ms=100.0,
            metadata={"author": "Me"},
        )
        meta_path = save_metadata(result, tmp_path)
        assert meta_path.exists()
        import json
        data = json.loads(meta_path.read_text("utf-8"))
        assert data["file_name"] == "doc.pdf"
        assert data["success"] is True
        assert data["metadata"]["author"] == "Me"
