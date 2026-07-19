"""Tests for Excel parser."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from config import FileFormat
from src.parsers.excel_parser import ExcelParser


@pytest.fixture
def excel_parser() -> ExcelParser:
    return ExcelParser()


class TestExcelParser:
    def test_supported_formats(self, excel_parser: ExcelParser) -> None:
        assert FileFormat.XLSX in excel_parser.supported_formats

    @patch("src.parsers.excel_parser.openpyxl.load_workbook")
    def test_parse_simple(self, mock_load: MagicMock, excel_parser: ExcelParser, tmp_path: Path) -> None:
        mock_wb = MagicMock()
        mock_ws = MagicMock()
        mock_ws.iter_rows.return_value = [
            ("Name", "Age", "City"),
            ("Alice", "30", "Beijing"),
            ("Bob", "25", "Shanghai"),
        ]
        mock_ws.sheet_state = "visible"
        mock_wb.__getitem__.return_value = mock_ws
        mock_wb.sheetnames = ["Sheet1"]
        mock_load.return_value = mock_wb

        xlsx_path = tmp_path / "test.xlsx"
        xlsx_path.write_text("fake")

        result = excel_parser.parse(xlsx_path)

        assert result.success is True
        assert result.file_format == FileFormat.XLSX
        assert result.tables is not None
        assert len(result.tables) == 1
        assert result.tables[0].headers == ["Name", "Age", "City"]
        assert len(result.tables[0].rows) == 2
        assert "Name" in result.content

    @patch("src.parsers.excel_parser.openpyxl.load_workbook")
    def test_parse_hidden_sheets(self, mock_load: MagicMock, excel_parser: ExcelParser, tmp_path: Path) -> None:
        mock_wb = MagicMock()

        mock_ws_visible = MagicMock()
        mock_ws_visible.iter_rows.return_value = [("A",)]
        mock_ws_visible.sheet_state = "visible"
        mock_ws_hidden = MagicMock()
        mock_ws_hidden.sheet_state = "hidden"

        def getitem(name):
            return {"Visible": mock_ws_visible, "Hidden": mock_ws_hidden}[name]

        mock_wb.__getitem__.side_effect = getitem
        mock_wb.sheetnames = ["Visible", "Hidden"]
        mock_load.return_value = mock_wb

        xlsx_path = tmp_path / "hidden.xlsx"
        xlsx_path.write_text("fake")

        result = excel_parser.parse(xlsx_path)
        assert result.success is True
        assert len(result.tables) == 1  # Only visible sheet

    @patch("src.parsers.excel_parser.openpyxl.load_workbook")
    def test_parse_error(self, mock_load: MagicMock, excel_parser: ExcelParser, tmp_path: Path) -> None:
        mock_load.side_effect = Exception("Corrupt file")

        xlsx_path = tmp_path / "corrupt.xlsx"
        xlsx_path.write_text("not xlsx")

        result = excel_parser.parse(xlsx_path)
        assert result.success is False
