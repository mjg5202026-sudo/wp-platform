"""Metadata Extractor — 提取文件元数据。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from config import FileFormat
from src.utils.file_utils import detect_format, format_bytes


def extract_basic_metadata(file_path: Path) -> dict[str, Any]:
    """提取文件基础元数据（所有格式通用）。"""
    stat = file_path.stat()
    fmt = detect_format(file_path)
    return {
        "file_name": file_path.name,
        "file_path": str(file_path.resolve()),
        "file_extension": file_path.suffix.lower(),
        "file_format": fmt.value,
        "file_size_bytes": stat.st_size,
        "file_size_display": format_bytes(stat.st_size),
        "created_at": _timestamp_to_iso(stat.st_ctime),
        "modified_at": _timestamp_to_iso(stat.st_mtime),
    }


def _timestamp_to_iso(ts: float) -> str:
    from datetime import datetime
    return datetime.fromtimestamp(ts).isoformat()
