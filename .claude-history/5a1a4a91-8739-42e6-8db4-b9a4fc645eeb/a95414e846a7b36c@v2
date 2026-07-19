"""Excel Parser — 使用 openpyxl 解析 Excel 文档。"""

from __future__ import annotations

import time
from pathlib import Path

import openpyxl

from config import FileFormat, parser_config
from src.parsers.base import BaseParser, ParseResult, TableContent


class ExcelParser(BaseParser):
    """Excel 解析器。"""

    @property
    def supported_formats(self) -> set[FileFormat]:
        return {FileFormat.XLSX}

    def parse(self, file_path: Path) -> ParseResult:
        start = time.perf_counter()
        try:
            wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            return ParseResult(
                file_path=file_path,
                file_format=FileFormat.XLSX,
                content="",
                success=False,
                error_message=f"Excel 打开失败: {e}",
                processing_time_ms=round(elapsed, 2),
            )

        try:
            all_tables: list[TableContent] = []
            text_parts: list[str] = []

            sheet_limit = parser_config.excel_sheet_limit
            sheets = wb.sheetnames
            if sheet_limit:
                sheets = sheets[:sheet_limit]

            for sheet_name in sheets:
                ws = wb[sheet_name]
                if ws.sheet_state == "hidden" and not parser_config.excel_include_hidden:
                    continue

                text_parts.append(f"## Sheet: {sheet_name}")
                headers: list[str] = []
                rows: list[list[str]] = []

                for row_idx, row in enumerate(ws.iter_rows(values_only=True)):
                    cells = [str(cell) if cell is not None else "" for cell in row]
                    if all(c == "" for c in cells):
                        continue
                    if row_idx == 0:
                        headers = cells
                        text_parts.append("| " + " | ".join(cells) + " |")
                        text_parts.append("| " + " | ".join("---" for _ in cells) + " |")
                    else:
                        rows.append(cells)
                        text_parts.append("| " + " | ".join(cells) + " |")

                all_tables.append(TableContent(
                    name=sheet_name,
                    headers=headers,
                    rows=rows,
                    sheet_name=sheet_name,
                ))

            content = "\n".join(text_parts) if text_parts else "(空工作簿)"

            elapsed = (time.perf_counter() - start) * 1000
            return ParseResult(
                file_path=file_path,
                file_format=FileFormat.XLSX,
                content=content,
                tables=all_tables,
                metadata=self._extract_metadata(file_path),
                success=True,
                processing_time_ms=round(elapsed, 2),
            )
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            return ParseResult(
                file_path=file_path,
                file_format=FileFormat.XLSX,
                content="",
                success=False,
                error_message=f"Excel 解析失败: {e}",
                processing_time_ms=round(elapsed, 2),
            )
        finally:
            try:
                wb.close()
            except Exception:
                pass

    def _extract_metadata(self, file_path: Path) -> dict:
        return {
            "file_name": file_path.name,
            "file_size_bytes": file_path.stat().st_size,
        }
