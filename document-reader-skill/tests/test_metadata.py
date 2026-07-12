"""Tests for metadata extractor."""

from __future__ import annotations

from pathlib import Path

from src.metadata.extractor import extract_basic_metadata


class TestExtractBasicMetadata:
    def test_returns_required_keys(self, tmp_path: Path) -> None:
        f = tmp_path / "test.pdf"
        f.write_text("content")
        meta = extract_basic_metadata(f)

        assert meta["file_name"] == "test.pdf"
        assert meta["file_extension"] == ".pdf"
        assert meta["file_format"] == "pdf"
        assert meta["file_size_bytes"] == 7
        assert "created_at" in meta
        assert "modified_at" in meta

    def test_file_size_display(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.pdf"
        f.write_text("A" * 2048)
        meta = extract_basic_metadata(f)
        assert "KB" in meta["file_size_display"]
