"""
Document Reader Skill — 全局配置。

所有硬编码参数统一放在此文件，业务代码中不允许出现魔数、魔字符串。
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Final


# ── 项目路径 ──────────────────────────────────────────────────────────────

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent
OUTPUT_DIR: Final[Path] = PROJECT_ROOT / "output"
LOGS_DIR: Final[Path] = PROJECT_ROOT / "logs"
INPUT_DIR: Final[Path] = PROJECT_ROOT / "input"
EXAMPLES_DIR: Final[Path] = PROJECT_ROOT / "examples"


# ── 日志配置 ──────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class LogConfig:
    """日志配置。"""
    level: str = "INFO"
    format: str = "{asctime} | {levelname:<7} | {name:<20} | {message}"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    max_bytes: int = 10 * 1024 * 1024  # 10 MB
    backup_count: int = 7
    encoding: str = "utf-8"


# ── 文件格式 ──────────────────────────────────────────────────────────────

class FileFormat(str, Enum):
    """支持的文件格式枚举。"""
    PDF = "pdf"
    PNG = "png"
    JPG = "jpg"
    JPEG = "jpeg"
    TIFF = "tiff"
    BMP = "bmp"
    DOCX = "docx"
    XLSX = "xlsx"
    UNKNOWN = "unknown"


# ── OCR 模式 ──────────────────────────────────────────────────────────────

class OcrMode(str, Enum):
    """OCR 工作模式。"""
    AUTO = "auto"      # 自动判断是否需要 OCR
    FORCE = "force"    # 强制 OCR（忽略文字层）
    SKIP = "skip"      # 跳过 OCR（仅提取已有文字）


# ── 解析器配置 ────────────────────────────────────────────────────────────

@dataclass
class ParserConfig:
    """各格式解析器的行为配置。"""
    # PDF
    pdf_dpi: int = 300
    pdf_page_limit: int | None = None  # None = 无限制

    # OCR
    ocr_mode: OcrMode = OcrMode.AUTO
    ocr_lang: str = "ch,en"           # PaddleOCR 语言
    ocr_confidence_threshold: float = 0.5
    ocr_fallback_enabled: bool = True  # PaddleOCR 失败 → Tesseract

    # Tesseract（降级方案）
    tesseract_cmd: str = "tesseract"
    tesseract_lang: str = "chi_sim+eng"

    # Image
    image_max_size: tuple[int, int] = (4096, 4096)

    # Excel
    excel_sheet_limit: int | None = None
    excel_include_hidden: bool = False

    # Word
    docx_extract_headers: bool = True
    docx_extract_footers: bool = True
    docx_extract_images: bool = False

    # Output
    output_markdown_ext: str = ".md"
    output_metadata_ext: str = ".json"
    output_encoding: str = "utf-8"


# ── 文件大小限制 ──────────────────────────────────────────────────────────

MAX_FILE_SIZE_MB: Final[int] = 200
MAX_FILE_SIZE_BYTES: Final[int] = MAX_FILE_SIZE_MB * 1024 * 1024


# ── 支持的文件扩展名映射 ───────────────────────────────────────────────────

EXTENSION_MAP: Final[dict[str, FileFormat]] = {
    ".pdf": FileFormat.PDF,
    ".png": FileFormat.PNG,
    ".jpg": FileFormat.JPG,
    ".jpeg": FileFormat.JPEG,
    ".tiff": FileFormat.TIFF,
    ".tif": FileFormat.TIFF,
    ".bmp": FileFormat.BMP,
    ".docx": FileFormat.DOCX,
    ".xlsx": FileFormat.XLSX,
}

# 需要 OCR 的图片格式
IMAGE_FORMATS: Final[set[FileFormat]] = {
    FileFormat.PNG,
    FileFormat.JPG,
    FileFormat.JPEG,
    FileFormat.TIFF,
    FileFormat.BMP,
}


# ── 实例化默认配置 ────────────────────────────────────────────────────────

parser_config: ParserConfig = ParserConfig()
log_config: LogConfig = LogConfig()


def get_config() -> ParserConfig:
    """获取当前解析器配置（支持外部覆盖）。"""
    return parser_config


def set_config(cfg: ParserConfig) -> None:
    """外部设置解析器配置。"""
    global parser_config
    parser_config = cfg


# ── 环境变量覆盖（可选） ────────────────────────────────────────────────────

def _env_path(key: str, default: Path) -> Path:
    val = os.environ.get(f"DOCREADER_{key}")
    return Path(val) if val else default


OUTPUT_DIR = _env_path("OUTPUT_DIR", OUTPUT_DIR)
LOGS_DIR = _env_path("LOGS_DIR", LOGS_DIR)
INPUT_DIR = _env_path("INPUT_DIR", INPUT_DIR)
