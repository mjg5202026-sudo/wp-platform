"""OCR Necessity Detector — 判断文档是否需要 OCR。"""

from __future__ import annotations

from pathlib import Path

from config import FileFormat, IMAGE_FORMATS, OcrMode, parser_config
from src.utils.file_utils import detect_format


def is_ocr_needed(file_path: Path, ocr_mode: OcrMode = OcrMode.AUTO) -> bool:
    """判断指定文件是否需要 OCR。

    Args:
        file_path: 文件路径。
        ocr_mode: OCR 模式。

    Returns:
        是否需要 OCR。
    """
    if ocr_mode == OcrMode.FORCE:
        return True
    if ocr_mode == OcrMode.SKIP:
        return False

    fmt = detect_format(file_path)

    # 图片格式始终需要 OCR
    if fmt in IMAGE_FORMATS:
        return True

    # PDF — 检查是否有文字层
    if fmt == FileFormat.PDF:
        return _pdf_has_no_text_layer(file_path)

    # Word / Excel 不需要 OCR
    return False


def _pdf_has_no_text_layer(file_path: Path) -> bool:
    """检查 PDF 是否缺少可选文字层（即是否为纯扫描件）。"""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        return True  # 没有 PyMuPDF 时保守处理

    try:
        doc = fitz.open(file_path)
        total_text = ""
        limit = min(len(doc), parser_config.pdf_page_limit or len(doc))
        for page_num in range(limit):
            page = doc[page_num]
            total_text += page.get_text().strip()
        doc.close()
        return len(total_text) < 50  # 少于 50 个字符视为无文字层
    except Exception:
        return True  # 出错时保守处理：尝试 OCR
