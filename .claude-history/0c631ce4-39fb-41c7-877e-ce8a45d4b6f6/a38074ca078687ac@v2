"""Tests for Word parser."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from config import FileFormat
from src.parsers.word_parser import WordParser


@pytest.fixture
def word_parser() -> WordParser:
    return WordParser()


class TestWordParser:
    def test_supported_formats(self, word_parser: WordParser) -> None:
        assert FileFormat.DOCX in word_parser.supported_formats

    @patch("src.parsers.word_parser.DocxDocument")
    def test_parse_paragraphs(self, mock_docx: MagicMock, word_parser: WordParser, tmp_path: Path) -> None:
        mock_doc = MagicMock()
        mock_doc.paragraphs = [
            _make_para("Heading 1", "Heading 1"),
            _make_para("This is a paragraph.", "Normal"),
            _make_para("Sub Heading", "Heading 2"),
            _make_para("Another paragraph.", "Normal"),
        ]
        mock_doc.tables = []
        mock_doc.sections = []
        mock_docx.return_value = mock_doc

        mock_props = MagicMock()
        mock_props.title = "Test Doc"
        mock_props.author = "Author"
        mock_props.subject = None
        mock_props.keywords = None
        mock_props.category = None
        mock_props.comments = None
        mock_props.created = None
        mock_props.modified = None
        mock_doc.core_properties = mock_props

        docx_path = tmp_path / "test.docx"
        docx_path.write_text("fake")

        result = word_parser.parse(docx_path)

        assert result.success is True
        assert result.file_format == FileFormat.DOCX
        assert "# Heading 1" in result.content
        assert "## Sub Heading" in result.content

    @patch("src.parsers.word_parser.DocxDocument")
    def test_parse_with_table(self, mock_docx: MagicMock, word_parser: WordParser, tmp_path: Path) -> None:
        mock_doc = MagicMock()
        mock_doc.paragraphs = [_make_para("Data", "Normal")]
        mock_doc.sections = []

        mock_table = MagicMock()
        mock_cell_a = MagicMock()
        mock_cell_a.text = "A"
        mock_cell_b = MagicMock()
        mock_cell_b.text = "B"
        mock_cell_1 = MagicMock()
        mock_cell_1.text = "1"
        mock_cell_2 = MagicMock()
        mock_cell_2.text = "2"
        mock_row1 = MagicMock()
        mock_row1.cells = [mock_cell_a, mock_cell_b]
        mock_row2 = MagicMock()
        mock_row2.cells = [mock_cell_1, mock_cell_2]
        mock_table.rows = [mock_row1, mock_row2]
        mock_doc.tables = [mock_table]

        mock_docx.return_value = mock_doc
        mock_props = MagicMock()
        mock_props.title = None
        mock_props.author = None
        mock_props.subject = None
        mock_props.keywords = None
        mock_props.category = None
        mock_props.comments = None
        mock_props.created = None
        mock_props.modified = None
        mock_doc.core_properties = mock_props

        docx_path = tmp_path / "table.docx"
        docx_path.write_text("fake")

        result = word_parser.parse(docx_path)
        assert result.success is True
        assert result.tables is not None
        assert len(result.tables) == 1
        assert result.tables[0].headers == ["A", "B"]


def _make_para(text: str, style_name: str) -> MagicMock:
    para = MagicMock()
    para.text = text
    para.style.name = style_name
    return para
