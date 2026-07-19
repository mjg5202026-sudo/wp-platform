"""Markdown Converter — 将解析结果转为结构化 Markdown。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from config import OUTPUT_DIR, parser_config
from src.parsers.base import ParseResult, TableContent
from src.utils.file_utils import format_bytes


def convert_to_markdown(result: ParseResult, title: str = "") -> str:
    """将解析结果转为格式化的 Markdown 文本。

    Args:
        result: 解析结果对象。
        title: 文档标题（默认用文件名）。

    Returns:
        格式化的 Markdown 字符串。
    """
    doc_title = title or result.metadata.get("title") or result.file_path.stem
    lines: list[str] = []

    # 标题
    lines.append(f"# {doc_title}")
    lines.append("")

    # 文档信息
    lines.append("## 文档信息")
    lines.append("")
    lines.append(f"- **文件**: `{result.file_path.name}`")
    lines.append(f"- **格式**: `{result.file_format.value}`")
    lines.append(f"- **大小**: {format_bytes(result.metadata.get('file_size_bytes', 0))}")
    lines.append(f"- **OCR**: {'是' if result.ocr_applied else '否'}")
    if result.ocr_engine:
        lines.append(f"- **OCR 引擎**: `{result.ocr_engine}`")
    if result.processing_time_ms > 0:
        lines.append(f"- **处理耗时**: {result.processing_time_ms:.0f}ms")
    lines.append("")

    # 自定义元数据
    extra_keys = {"file_name", "file_size_bytes", "total_pages", "pages_extracted",
                  "image_width", "image_height", "image_mode", "image_format"}
    custom_meta = {k: v for k, v in result.metadata.items() if k not in extra_keys and not k.startswith("exif_")}
    if custom_meta:
        for key, val in custom_meta.items():
            if val:
                lines.append(f"- **{key}**: {val}")
        lines.append("")

    # 内容
    lines.append("## 内容")
    lines.append("")
    if result.content:
        lines.append(result.content)
        lines.append("")
    else:
        lines.append("*(无文本内容)*")
        lines.append("")

    # 表格
    if result.tables:
        lines.append("## 表格")
        lines.append("")
        for table in result.tables:
            lines.extend(_format_table(table))
            lines.append("")

    # 分页信息
    if result.pages and len(result.pages) > 1:
        lines.append("---")
        lines.append("")
        lines.append(f"> *共 {len(result.pages)} 页*")

    return "\n".join(lines)


def _format_table(table: TableContent) -> list[str]:
    """将 TableContent 格式化为 Markdown 表格。"""
    lines: list[str] = []
    if table.name:
        lines.append(f"### {table.name}")
    if not table.headers and not table.rows:
        return lines

    # 表头
    if table.headers:
        lines.append("| " + " | ".join(table.headers) + " |")
        lines.append("| " + " | ".join("---" for _ in table.headers) + " |")
    elif table.rows:
        # 无表头时用空列
        col_count = max(len(r) for r in table.rows) if table.rows else 0
        lines.append("| " + " | ".join(f"Col {i+1}" for i in range(col_count)) + " |")
        lines.append("| " + " | ".join("---" for _ in range(col_count)) + " |")

    # 数据行
    for row in table.rows:
        padded = row + [""] * (len(table.headers) - len(row)) if len(table.headers) > len(row) else row
        lines.append("| " + " | ".join(padded) + " |")

    return lines


def save_markdown(result: ParseResult, output_dir: Path = OUTPUT_DIR) -> Path:
    """将解析结果保存为 Markdown 文件。

    Args:
        result: 解析结果。
        output_dir: 输出目录。

    Returns:
        生成的 Markdown 文件路径。
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    md_content = convert_to_markdown(result)
    md_path = output_dir / f"{result.file_path.stem}{parser_config.output_markdown_ext}"
    md_path.write_text(md_content, encoding=parser_config.output_encoding)

    return md_path


def save_metadata(result: ParseResult, output_dir: Path = OUTPUT_DIR) -> Path:
    """将元数据保存为 JSON 文件。

    Args:
        result: 解析结果。
        output_dir: 输出目录。

    Returns:
        生成的 JSON 文件路径。
    """
    import json
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    meta_path = output_dir / f"{result.file_path.stem}_metadata{parser_config.output_metadata_ext}"
    with open(meta_path, "w", encoding=parser_config.output_encoding) as f:
        json.dump({
            "file_name": result.file_path.name,
            "file_format": result.file_format.value,
            "success": result.success,
            "ocr_applied": result.ocr_applied,
            "ocr_engine": result.ocr_engine,
            "processing_time_ms": result.processing_time_ms,
            "error_message": result.error_message,
            "metadata": result.metadata,
        }, f, ensure_ascii=False, indent=2)

    return meta_path
