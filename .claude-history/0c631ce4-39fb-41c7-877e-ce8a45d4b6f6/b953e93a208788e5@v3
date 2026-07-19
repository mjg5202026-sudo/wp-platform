"""File utilities — 文件操作工具。"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from config import EXTENSION_MAP, FileFormat, MAX_FILE_SIZE_BYTES


def detect_format(file_path: Path) -> FileFormat:
    """
    根据扩展名检测文件格式。

    Args:
        file_path: 文件路径。

    Returns:
        FileFormat 枚举值。无法识别时返回 UNKNOWN。
    """
    ext = file_path.suffix.lower()
    return EXTENSION_MAP.get(ext, FileFormat.UNKNOWN)


def is_supported(file_path: Path) -> bool:
    """检查文件是否为支持的格式。"""
    return detect_format(file_path) != FileFormat.UNKNOWN


def validate_file(file_path: Path) -> Optional[str]:
    """
    验证文件是否可用。

    Args:
        file_path: 文件路径。

    Returns:
        如果验证失败，返回错误消息字符串；否则返回 None。
    """
    if not file_path.exists():
        return f"文件不存在: {file_path}"
    if not file_path.is_file():
        return f"路径不是文件: {file_path}"
    if file_path.stat().st_size == 0:
        return f"文件为空: {file_path}"
    if file_path.stat().st_size > MAX_FILE_SIZE_BYTES:
        size_mb = file_path.stat().st_size / (1024 * 1024)
        return f"文件超过大小限制 ({size_mb:.1f} MB > {MAX_FILE_SIZE_BYTES / 1024 / 1024:.0f} MB): {file_path}"
    if not is_supported(file_path):
        return f"不支持的文件格式: {file_path.suffix}"
    return None


def collect_input_files(input_path: Path) -> list[Path]:
    """
    收集所有待处理的输入文件。

    Args:
        input_path: 文件或目录路径。

    Returns:
        支持的文件路径列表。
    """
    if input_path.is_file():
        return [input_path] if is_supported(input_path) else []

    if input_path.is_dir():
        seen: set[Path] = set()
        files: list[Path] = []
        for ext in EXTENSION_MAP:
            for p in input_path.glob(f"*{ext}"):
                resolved = p.resolve()
                if resolved not in seen:
                    seen.add(resolved)
                    files.append(p)
        return sorted(files)

    return []


def make_timestamped_dir(base_dir: Path) -> Path:
    """在 base_dir 下按时间戳创建目录。"""
    from datetime import datetime

    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = base_dir / ts
    path.mkdir(parents=True, exist_ok=True)
    return path


def format_bytes(size: int) -> str:
    """格式化文件大小为可读字符串。"""
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    else:
        return f"{size / (1024 * 1024):.1f} MB"
