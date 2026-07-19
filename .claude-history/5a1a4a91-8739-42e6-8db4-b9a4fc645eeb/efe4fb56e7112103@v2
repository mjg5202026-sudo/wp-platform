"""Initial tests — 验证基础工具函数。"""

from __future__ import annotations

from pathlib import Path

import pytest

from config import FileFormat
from src.utils.file_utils import (
    collect_input_files,
    detect_format,
    is_supported,
    validate_file,
)


class TestDetectFormat:
    def test_pdf(self) -> None:
        assert detect_format(Path("test.pdf")) == FileFormat.PDF
        assert detect_format(Path("test.PDF")) == FileFormat.PDF

    def test_png(self) -> None:
        assert detect_format(Path("image.png")) == FileFormat.PNG

    def test_jpg(self) -> None:
        assert detect_format(Path("photo.jpg")) == FileFormat.JPG
        assert detect_format(Path("photo.jpeg")) == FileFormat.JPEG

    def test_docx(self) -> None:
        assert detect_format(Path("report.docx")) == FileFormat.DOCX

    def test_xlsx(self) -> None:
        assert detect_format(Path("data.xlsx")) == FileFormat.XLSX

    def test_unknown(self) -> None:
        assert detect_format(Path("file.txt")) == FileFormat.UNKNOWN
        assert detect_format(Path("file")) == FileFormat.UNKNOWN


class TestIsSupported:
    def test_supported(self) -> None:
        assert is_supported(Path("test.pdf")) is True
        assert is_supported(Path("test.docx")) is True
        assert is_supported(Path("test.xlsx")) is True

    def test_unsupported(self) -> None:
        assert is_supported(Path("test.txt")) is False
        assert is_supported(Path("test")) is False


class TestValidateFile:
    def test_file_not_found(self) -> None:
        error = validate_file(Path("nonexistent.pdf"))
        assert error is not None
        assert "不存在" in error

    def test_not_a_file(self, tmp_path: Path) -> None:
        error = validate_file(tmp_path)
        assert error is not None
        assert "不是文件" in error

    def test_empty_file(self, tmp_path: Path) -> None:
        f = tmp_path / "empty.pdf"
        f.write_text("")
        error = validate_file(f)
        assert error is not None
        assert "为空" in error

    def test_valid_file(self, tmp_path: Path) -> None:
        f = tmp_path / "test.pdf"
        f.write_text("not a real pdf, but file exists and non-empty")
        error = validate_file(f)
        assert error is None

    def test_unsupported_format(self, tmp_path: Path) -> None:
        f = tmp_path / "test.txt"
        f.write_text("hello")
        error = validate_file(f)
        assert error is not None
        assert "不支持" in error


class TestCollectInputFiles:
    def test_single_file(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.pdf"
        f.write_text("content")
        files = collect_input_files(f)
        assert files == [f]

    def test_unsupported_file(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.txt"
        f.write_text("content")
        files = collect_input_files(f)
        assert files == []

    def test_directory(self, tmp_path: Path) -> None:
        (tmp_path / "a.pdf").write_text("1")
        (tmp_path / "b.png").write_text("2")
        (tmp_path / "c.txt").write_text("3")
        files = collect_input_files(tmp_path)
        assert len(files) == 2
        assert all(f.suffix.lower() in (".pdf", ".png") for f in files)

    def test_directory_no_matches(self, tmp_path: Path) -> None:
        (tmp_path / "a.txt").write_text("1")
        files = collect_input_files(tmp_path)
        assert files == []
