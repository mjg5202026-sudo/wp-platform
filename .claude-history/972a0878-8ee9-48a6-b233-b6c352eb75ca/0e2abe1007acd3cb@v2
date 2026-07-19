"""Base parser — 解析器基类与数据模型。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from config import FileFormat


@dataclass
class PageContent:
    """单页内容。"""
    page_number: int
    text: str
    tables: list[list[list[str]]] = field(default_factory=list)
    images: list[Path] = field(default_factory=list)


@dataclass
class TableContent:
    """表格内容。"""
    name: str
    headers: list[str]
    rows: list[list[str]]
    sheet_name: str = ""


@dataclass
class ParseResult:
    """统一解析结果。"""
    file_path: Path
    file_format: FileFormat
    content: str                              # 纯文本 / Markdown
    pages: Optional[list[PageContent]] = None
    tables: Optional[list[TableContent]] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    ocr_applied: bool = False
    ocr_engine: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None
    processing_time_ms: float = 0.0


class BaseParser(ABC):
    """解析器抽象基类。"""

    @abstractmethod
    def parse(self, file_path: Path) -> ParseResult:
        """解析文件并返回结构化结果。"""
        ...

    @property
    @abstractmethod
    def supported_formats(self) -> set[FileFormat]:
        """返回此解析器支持的文件格式集合。"""
        ...

    def can_handle(self, file_path: Path) -> bool:
        """判断是否能处理此文件。"""
        from src.utils.file_utils import detect_format
        return detect_format(file_path) in self.supported_formats
