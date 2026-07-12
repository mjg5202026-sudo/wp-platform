"""Main — CLI 入口。"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from config import OcrMode, parser_config
from src.reader import DocumentReader
from src.utils.file_utils import make_timestamped_dir
from src.utils.logger import setup_logger

app = typer.Typer(
    name="document-reader",
    help="企业级文档解析工具 —— 读取 PDF、扫描件、图片、Word、Excel。",
    add_completion=False,
)
console = Console()


@app.command()
def parse(
    input_path: Path = typer.Argument(
        ...,
        help="输入文件或目录路径",
        exists=True,
        readable=True,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="输出目录（默认 output/ 下按时间戳创建）",
        file_okay=False,
    ),
    ocr_mode: str = typer.Option(
        "auto",
        "--ocr-mode", "-O",
        help="OCR 模式: auto / force / skip",
    ),
    lang: Optional[str] = typer.Option(
        None,
        "--lang", "-l",
        help="OCR 语言（覆盖默认 ch,en）",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="输出详细日志",
    ),
) -> None:
    """解析文档并输出结构化 Markdown + 元数据。"""
    logger = setup_logger(
        name="document-reader",
        level="DEBUG" if verbose else "INFO",
    )
    logger.info("开始解析: %s", input_path)

    # 校验 OCR 模式
    try:
        mode = OcrMode(ocr_mode)
    except ValueError:
        console.print(f"[red]✗[/] 无效的 OCR 模式: {ocr_mode} (可选: auto/force/skip)")
        raise typer.Exit(1)

    output_dir = output or make_timestamped_dir(
        parser_config.OUTPUT_DIR / "cli"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    reader = DocumentReader(ocr_mode=mode)
    if lang:
        reader.set_ocr_lang(lang)

    console.print(f"[dim]输入:[/] {input_path}")
    console.print(f"[dim]输出:[/] {output_dir}")
    console.print(f"[dim]OCR:[/]  {mode.value}")
    console.print("")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=False,
    ) as progress:
        task = progress.add_task("解析文档中...", total=None)

        if input_path.is_file():
            result = reader.read_one(input_path)
            if result is None:
                console.print("[red]✗[/] 无法解析文件")
                raise typer.Exit(1)

            if result.success:
                md_path = _save_result(result, output_dir)
                progress.update(task, completed=True)
                console.print(f"\n[green]✓[/] 解析完成")
                console.print(f"  Markdown: [link=file:///{md_path}]{md_path}[/]")
                console.print(f"  字符数: {len(result.content)}")
                if result.ocr_applied:
                    console.print(f"  OCR 引擎: {result.ocr_engine}")
                console.print(f"  耗时: {result.processing_time_ms:.0f}ms")
            else:
                progress.update(task, completed=True)
                console.print(f"\n[red]✗[/] 解析失败: {result.error_message}")
                raise typer.Exit(1)

        else:
            saved = reader.process_and_save(input_path, output_dir)
            progress.update(task, completed=True)
            console.print(f"\n[green]✓[/] 批量处理完成: {len(saved)} 个文件")
            for p in saved:
                console.print(f"  [link=file:///{p}]{p}[/]")


@app.command()
def list_formats() -> None:
    """列出支持的格式。"""
    from config import EXTENSION_MAP

    console.print("[bold]支持的文件格式:[/]")
    for ext, fmt in EXTENSION_MAP.items():
        console.print(f"  {ext:8s} → {fmt.value}")


def _save_result(result, output_dir: Path) -> Path:
    """保存单个解析结果。"""
    from src.converters.markdown import save_markdown, save_metadata

    md_path = save_markdown(result, output_dir)
    save_metadata(result, output_dir)
    return md_path


def main() -> None:
    app()


if __name__ == "__main__":
    main()
