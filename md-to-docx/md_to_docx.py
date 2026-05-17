#!/usr/bin/env python3
"""
Конвертация Markdown (.md) в Word (.docx) с оформлением по требованиям ВКР.

Использование:
    python md_to_docx.py document.md
    python md_to_docx.py document.md -o report.docx
    python md_to_docx.py document.md --toc
    python md_to_docx.py document.md --no-preprocess
    python md_to_docx.py document.md --engine html
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

from md_preprocess import preprocess_markdown

PACKAGE_DIR = Path(__file__).resolve().parent
DEFAULT_REFERENCE = PACKAGE_DIR / "assets" / "reference.docx"
DEFAULT_LUA_FILTER = PACKAGE_DIR / "filters" / "vkr_docx.lua"


def ensure_reference_docx(path: Path) -> Path:
    if path.is_file():
        return path
    from build_reference_docx import build_reference_docx

    build_reference_docx(path)
    return path


def convert_pandoc(
    source: Path,
    destination: Path,
    *,
    reference_doc: Path,
    lua_filter: Path | None,
    use_toc: bool,
) -> None:
    import pypandoc

    extra_args = [
        "--standalone",
        f"--reference-doc={reference_doc}",
        "-f",
        "markdown+smart",
    ]
    if lua_filter and lua_filter.is_file():
        extra_args.append(f"--lua-filter={lua_filter}")
    if use_toc:
        extra_args.extend(["--toc", "--toc-depth=3"])

    pypandoc.convert_file(
        str(source),
        to="docx",
        outputfile=str(destination),
        format="markdown",
        extra_args=extra_args,
    )


def convert_html(source: Path, destination: Path) -> None:
    """Запасной вариант без Pandoc (без стилей ВКР)."""
    import markdown
    from docx import Document
    from htmldocx import HtmlToDocx

    text = source.read_text(encoding="utf-8")
    html = markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "toc", "nl2br", "sane_lists"],
    )
    document = Document()
    HtmlToDocx().add_html_to_document(html, document)
    document.save(str(destination))


ENGINES = {
    "pandoc": "pandoc",
    "html": "html",
}


def default_output_path(source: Path) -> Path:
    return source.with_suffix(".docx")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Преобразовать Markdown в Word (.docx) с оформлением ВКР.",
    )
    parser.add_argument("input", type=Path, help="Исходный .md файл")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Выходной .docx (по умолчанию: то же имя, расширение .docx)",
    )
    parser.add_argument(
        "--engine",
        choices=sorted(ENGINES),
        default="pandoc",
        help="pandoc (рекомендуется) или html (запасной)",
    )
    parser.add_argument(
        "--reference-doc",
        type=Path,
        default=DEFAULT_REFERENCE,
        help="Шаблон Word со стилями (по умолчанию: assets/reference.docx)",
    )
    parser.add_argument(
        "--lua-filter",
        type=Path,
        default=DEFAULT_LUA_FILTER,
        help="Lua-фильтр Pandoc (по умолчанию: filters/vkr_docx.lua)",
    )
    parser.add_argument(
        "--toc",
        action="store_true",
        help="Сгенерировать оглавление Word (вместо HYPERLINK из экспорта)",
    )
    parser.add_argument(
        "--no-preprocess",
        action="store_true",
        help="Не очищать MD от артефактов Word и не преобразовывать **заголовки**",
    )
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Сохранить предобработанный .md рядом с выходным файлом",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    source = args.input.expanduser().resolve()
    if not source.is_file():
        print(f"Ошибка: файл не найден: {source}", file=sys.stderr)
        return 1

    destination = (args.output or default_output_path(source)).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)

    work_source = source
    temp_md: Path | None = None

    if not args.no_preprocess:
        raw = source.read_text(encoding="utf-8")
        cleaned, stats = preprocess_markdown(raw, strip_word_toc=not args.toc)
        if args.keep_temp:
            temp_md = destination.with_suffix(".preprocessed.md")
            temp_md.write_text(cleaned, encoding="utf-8")
            work_source = temp_md
        else:
            tmp = tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".md",
                encoding="utf-8",
                delete=False,
            )
            tmp.write(cleaned)
            tmp.close()
            temp_md = Path(tmp.name)
            work_source = temp_md
        print(
            f"Предобработка: заголовков {stats.headings_promoted}, "
            f"удалено строк TOC/HYPERLINK {stats.hyperlinks_removed}, "
            f"подписей {stats.captions_marked}",
            file=sys.stderr,
        )

    try:
        if args.engine == "pandoc":
            reference = ensure_reference_docx(
                args.reference_doc.expanduser().resolve(),
            )
            convert_pandoc(
                work_source,
                destination,
                reference_doc=reference,
                lua_filter=args.lua_filter.expanduser().resolve(),
                use_toc=args.toc,
            )
        else:
            convert_html(work_source, destination)
    except Exception as exc:
        print(f"Ошибка конвертации: {exc}", file=sys.stderr)
        if args.engine == "pandoc":
            print(
                "Подсказка: pip install -r requirements.txt\n"
                "  или: python build_reference_docx.py",
                file=sys.stderr,
            )
        return 1
    finally:
        if temp_md and not args.keep_temp:
            temp_md.unlink(missing_ok=True)

    print(f"Готово: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
