"""Document Reader — 核心编排器，统筹解析流程。"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from config import OcrMode, parser_config
from src.converters.markdown import save_markdown, save_metadata
from src.detectors.ocr_needed import is_ocr_needed
from src.metadata.extractor import extract_basic_metadata
from src.parsers.base import BaseParser, ParseResult
from src.parsers.excel_parser import ExcelParser
from src.parsers.image_parser import ImageParser
from src.parsers.pdf_parser import PdfParser
from src.parsers.word_parser import WordParser
from src.utils.file_utils import collect_input_files, detect_format, validate_file
from src.utils.logger import get_logger


class DocumentReader:
    """文档读取器 — 统一入口。

    自动检测文件格式，选择合适的解析器，
    判断是否需要 OCR，输出结构化结果。
    """

    def __init__(self, ocr_mode: OcrMode = OcrMode.AUTO) -> None:
        self.ocr_mode = ocr_mode
        self.logger = get_logger("document-reader")
        self._parsers: list[BaseParser] = self._init_parsers()

    def _init_parsers(self) -> list[BaseParser]:
        return [
            PdfParser(),
            ImageParser(),
            WordParser(),
            ExcelParser(),
        ]

    def set_ocr_lang(self, lang: str) -> None:
        """设置 OCR 语言（对所有支持 OCR 的解析器生效）。"""
        for parser in self._parsers:
            if hasattr(parser, "_ocr") and hasattr(parser._ocr, "lang"):
                parser._ocr.lang = lang

    def read(self, input_path: Path, **kwargs) -> list[ParseResult]:
        """读取并解析文档。

        Args:
            input_path: 文件或目录路径。
            **kwargs: 传递给解析器的额外参数。

        Returns:
            解析结果列表。
        """
        files = collect_input_files(input_path)
        if not files:
            self.logger.warning("没有找到可解析的文件: %s", input_path)
            return []

        results: list[ParseResult] = []
        for file_path in files:
            validation_error = validate_file(file_path)
            if validation_error:
                self.logger.error("文件验证失败: %s — %s", file_path.name, validation_error)
                continue

            result = self._parse_single(file_path, **kwargs)
            results.append(result)

            if result.success:
                self.logger.info(
                    "✓ %s (%s, %.0fms)",
                    file_path.name,
                    result.file_format.value,
                    result.processing_time_ms,
                )
            else:
                self.logger.error("✗ %s — %s", file_path.name, result.error_message)

        return results

    def read_one(self, file_path: Path) -> Optional[ParseResult]:
        """读取并解析单个文件。"""
        results = self.read(file_path)
        return results[0] if results else None

    def _parse_single(self, file_path: Path, **kwargs) -> ParseResult:
        """解析单个文件。"""
        ocr_needed = is_ocr_needed(file_path, self.ocr_mode)
        parser, use_ocr = self._resolve_parser(file_path, ocr_needed)

        if parser is None:
            fmt = detect_format(file_path)
            return ParseResult(
                file_path=file_path,
                file_format=fmt,
                content="",
                success=False,
                error_message=f"没有找到合适的解析器: {fmt.value}",
            )

        # 执行解析 — 向支持 OCR 参数的解析器传递标记
        extra_kwargs = dict(kwargs)
        if use_ocr:
            extra_kwargs["ocr"] = True

        result = parser.parse(file_path, **extra_kwargs)

        # 补充基础元数据
        meta = extract_basic_metadata(file_path)
        result.metadata = {**meta, **result.metadata}

        return result

    def _resolve_parser(self, file_path: Path, ocr_needed: bool) -> tuple[Optional[BaseParser], bool]:
        """解析器选择逻辑。

        Args:
            file_path: 文件路径。
            ocr_needed: 是否需要 OCR。

        Returns:
            (parser, should_use_ocr): 解析器实例和是否启用 OCR。
        """
        for parser in self._parsers:
            if parser.can_handle(file_path):
                if ocr_needed and isinstance(parser, PdfParser):
                    return parser, True
                return parser, False
        return None, False

    def process_and_save(
        self,
        input_path: Path,
        output_dir: Optional[Path] = None,
    ) -> list[Path]:
        """解析文档并保存输出。

        Args:
            input_path: 输入文件或目录。
            output_dir: 输出目录（默认自动创建）。

        Returns:
            生成的输出文件路径列表。
        """
        from src.utils.file_utils import make_timestamped_dir

        output_dir = output_dir or make_timestamped_dir(parser_config.OUTPUT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)

        results = self.read(input_path)
        saved_files: list[Path] = []

        for result in results:
            if result.success:
                md_path = save_markdown(result, output_dir)
                meta_path = save_metadata(result, output_dir)
                saved_files.extend([md_path, meta_path])
                self.logger.info("已保存: %s, %s", md_path.name, meta_path.name)

        return saved_files
