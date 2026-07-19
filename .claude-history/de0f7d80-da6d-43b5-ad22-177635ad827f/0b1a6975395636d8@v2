"""Tests for config module."""

from __future__ import annotations

from config import (
    EXTENSION_MAP,
    IMAGE_FORMATS,
    MAX_FILE_SIZE_BYTES,
    MAX_FILE_SIZE_MB,
    FileFormat,
    OcrMode,
    ParserConfig,
    get_config,
    set_config,
)


class TestConfigValues:
    def test_file_size_limit(self) -> None:
        assert MAX_FILE_SIZE_BYTES == MAX_FILE_SIZE_MB * 1024 * 1024

    def test_extension_map_contains_all_formats(self) -> None:
        extensions = set(EXTENSION_MAP.keys())
        assert ".pdf" in extensions
        assert ".png" in extensions
        assert ".docx" in extensions
        assert ".xlsx" in extensions

    def test_image_formats(self) -> None:
        assert FileFormat.PNG in IMAGE_FORMATS
        assert FileFormat.JPG in IMAGE_FORMATS
        assert FileFormat.PDF not in IMAGE_FORMATS
        assert FileFormat.DOCX not in IMAGE_FORMATS


class TestOcrMode:
    def test_values(self) -> None:
        assert OcrMode.AUTO.value == "auto"
        assert OcrMode.FORCE.value == "force"
        assert OcrMode.SKIP.value == "skip"


class TestParserConfig:
    def test_defaults(self) -> None:
        cfg = ParserConfig()
        assert cfg.ocr_mode == OcrMode.AUTO
        assert cfg.ocr_lang == "ch,en"
        assert cfg.pdf_dpi == 300
        assert cfg.ocr_fallback_enabled is True

    def test_custom_values(self) -> None:
        cfg = ParserConfig(ocr_mode=OcrMode.FORCE, pdf_dpi=600)
        assert cfg.ocr_mode == OcrMode.FORCE
        assert cfg.pdf_dpi == 600

    def test_global_config_accessors(self) -> None:
        original = get_config()
        assert isinstance(original, ParserConfig)
        custom = ParserConfig(ocr_mode=OcrMode.SKIP)
        set_config(custom)
        assert get_config().ocr_mode == OcrMode.SKIP
        # Restore
        set_config(original)
