"""Tests for logger utility."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

import pytest

from src.utils.logger import get_logger, setup_logger


class TestSetupLogger:
    def test_returns_logger(self) -> None:
        logger = setup_logger("test-logger", level="DEBUG")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test-logger"
        assert logger.level == logging.DEBUG

    def test_creates_log_file(self, tmp_path: Path) -> None:
        log_file = tmp_path / "test.log"
        logger = setup_logger("file-test", log_file=log_file)
        logger.info("hello world")
        assert log_file.exists()
        content = log_file.read_text("utf-8")
        assert "hello world" in content

    def test_does_not_duplicate_handlers(self) -> None:
        logger = setup_logger("no-dupe")
        handler_count = len(logger.handlers)
        logger = setup_logger("no-dupe")
        assert len(logger.handlers) == handler_count

    def test_get_logger_creates_if_missing(self) -> None:
        name = "fresh-logger"
        # Ensure it doesn't exist
        if name in logging.root.manager.loggerDict:
            del logging.root.manager.loggerDict[name]
        logger = get_logger(name)
        assert logger.handlers


class TestLoggerLevels:
    @pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING", "ERROR"])
    def test_level_set_correctly(self, level: str) -> None:
        logger = setup_logger(f"level-{level}", level=level)
        assert logger.level == getattr(logging, level)
