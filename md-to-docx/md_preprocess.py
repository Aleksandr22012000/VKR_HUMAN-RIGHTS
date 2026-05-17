"""
Предобработка Markdown перед конвертацией в DOCX (в т.ч. файлы после экспорта из Word).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Разделы оглавления Word с HYPERLINK — заменяем на автогенерацию Pandoc (--toc).
_TOC_HYPERLINK = re.compile(
    r"^\s*(?:>\s*)?(?:HYPERLINK|PAGEREF|TOC\\).*$",
    re.IGNORECASE,
)
_TOC_FIELD = re.compile(r"^TOC\s+\\", re.IGNORECASE)

# Заголовки **...**
_BOLD_LINE = re.compile(r"^\*\*(.+)\*\*\s*$")

_STRUCTURAL_TITLES = frozenset(
    {
        "ВВЕДЕНИЕ",
        "ЗАКЛЮЧЕНИЕ",
        "ОГЛАВЛЕНИЕ",
        "СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ",
        "СПИСОК СОКРАЩЕНИЙ",
        "СПИСОК РЕКОМЕНДУЕМОЙ ЛИТЕРАТУРЫ",
    }
)

_NUM_HEADING = re.compile(
    r"^(\d+(?:\.\d+)*)\.?\s+(.+)$",
)
_APPENDIX = re.compile(r"^Приложение\s+([А-ЯЁ])\s*$", re.IGNORECASE)
_CHAPTER = re.compile(r"^Глава\s+(\d+)\.\s*(.*)$", re.IGNORECASE)
_TABLE_CAPTION = re.compile(
    r"^Таблица\s+(\d+(?:\.\d+)?)\s*(?:---|—)\s*(.+)$",
    re.IGNORECASE,
)
_FIGURE_CAPTION = re.compile(
    r"^Рисунок\s+(\d+(?:\.\d+)?)\s*(?:---|—)\s*(.+)$",
    re.IGNORECASE,
)

# Артефакты Pandoc/Word
_SPAN_UNDERLINE = re.compile(r"\{[.]underline\}", re.IGNORECASE)
_STRAY_BACKSLASH = re.compile(r"\\([\\*_\-])")
_WORD_SOFT_BREAK = re.compile(r"\\\s*$")


@dataclass
class PreprocessStats:
    hyperlinks_removed: int = 0
    headings_promoted: int = 0
    captions_marked: int = 0


def _heading_level(number: str) -> int:
    depth = number.count(".") + 1
    return min(depth, 4)


def _classify_bold_title(inner: str) -> tuple[int, str] | None:
    """Вернуть (уровень, класс pandoc) или None."""
    upper = inner.strip().upper()
    if upper in _STRUCTURAL_TITLES or upper.startswith("СПИСОК "):
        return 1, "structural"

    appendix = _APPENDIX.match(inner.strip())
    if appendix:
        return 1, "appendix"

    chapter = _CHAPTER.match(inner.strip())
    if chapter:
        title = inner.strip()
        return 1, "chapter"

    num = _NUM_HEADING.match(inner.strip())
    if num:
        level = _heading_level(num.group(1))
        return level, ""

    # Полностью прописные короткие строки — разделы методички
    if inner == upper and len(inner) < 160 and re.search(r"[А-ЯЁ]", inner):
        if re.match(r"^\d+\.\s", inner):
            return 1, ""
        if re.match(r"^\d+\.\d+", inner):
            return 2, ""

    # Подзаголовки списка литературы и разделов
    if re.match(
        r"^(Нормативные|Основная|Периодические|другие|Список|Перечень|Краткая)",
        inner,
        re.IGNORECASE,
    ):
        return 2, ""

    return None


def _to_heading(line: str, level: int, css_class: str) -> str:
    inner = _BOLD_LINE.match(line).group(1).strip()  # type: ignore[union-attr]
    hashes = "#" * level
    if css_class:
        return f"{hashes} {inner} {{.{css_class}}}"
    return f"{hashes} {inner}"


def _normalize_line(line: str) -> str:
    line = _SPAN_UNDERLINE.sub("", line)
    line = _STRAY_BACKSLASH.sub(r"\1", line)
    line = _WORD_SOFT_BREAK.sub("", line)
    # Тире Word: --- между словами → em dash (оставляем дефисы в номерах)
    line = re.sub(r"(?<=\s)---(?=\s)", "—", line)
    return line


def _is_toc_region(started: bool, line: str) -> bool:
    if _BOLD_LINE.match(line):
        inner = _BOLD_LINE.match(line).group(1).strip().upper()  # type: ignore[union-attr]
        if inner == "ОГЛАВЛЕНИЕ":
            return True
        if started and inner == "ВВЕДЕНИЕ":
            return False
    return started


def _join_split_bold_lines(lines: list[str]) -> list[str]:
    """Склеить заголовки вида **\\ + 7. TITLE** или **5. TITLE\\nпродолжение**."""
    joined: list[str] = []
    buffer: str | None = None

    def flush() -> None:
        nonlocal buffer
        if buffer is not None:
            joined.append(buffer)
            buffer = None

    for line in lines:
        stripped = line.strip()
        if stripped in ("**\\**", "**\\", "**"):
            continue

        if buffer is None:
            if stripped.startswith("**") and not stripped.endswith("**"):
                buffer = stripped
                continue
            joined.append(line)
            continue

        buffer = f"{buffer} {stripped}".strip()
        if buffer.endswith("**"):
            joined.append(buffer)
            buffer = None

    flush()
    return joined


def preprocess_markdown(text: str, *, strip_word_toc: bool = True) -> tuple[str, PreprocessStats]:
    """
    Очистить MD от артефактов Word и преобразовать **заголовки** в # синтаксис.
    """
    stats = PreprocessStats()
    out: list[str] = []
    in_word_toc = False
    skip_blank_run = 0

    for raw in _join_split_bold_lines(text.splitlines()):
        line = _normalize_line(raw)

        if strip_word_toc:
            if _BOLD_LINE.match(line):
                inner = _BOLD_LINE.match(line).group(1).strip().upper()  # type: ignore[union-attr]
                if inner == "ОГЛАВЛЕНИЕ":
                    in_word_toc = True
                elif in_word_toc and inner == "ВВЕДЕНИЕ":
                    in_word_toc = False

            if in_word_toc and (
                _TOC_HYPERLINK.match(line)
                or _TOC_FIELD.match(line)
                or re.search(r"\.{5,}", line)
                or re.match(r"^\s*\d+\s*$", line)
            ):
                stats.hyperlinks_removed += 1
                continue

        if _TOC_HYPERLINK.match(line) or _TOC_FIELD.match(line):
            stats.hyperlinks_removed += 1
            continue

        # Пустые **\** или ** **
        if line in ("**\\**", "** **", "**"):
            continue

        bold = _BOLD_LINE.match(line)
        if bold:
            classified = _classify_bold_title(bold.group(1))
            if classified:
                level, css_class = classified
                out.append(_to_heading(line, level, css_class))
                stats.headings_promoted += 1
                skip_blank_run = 0
                continue

        table_cap = _TABLE_CAPTION.match(line.strip())
        if table_cap:
            num, title = table_cap.groups()
            out.append(f"**Таблица {num} — {title.strip()}** {{.table-caption}}")
            stats.captions_marked += 1
            skip_blank_run = 0
            continue

        figure_cap = _FIGURE_CAPTION.match(line.strip())
        if figure_cap:
            num, title = figure_cap.groups()
            out.append(f"**Рисунок {num} — {title.strip()}** {{.figure-caption}}")
            stats.captions_marked += 1
            skip_blank_run = 0
            continue

        if not line.strip():
            skip_blank_run += 1
            if skip_blank_run <= 2:
                out.append("")
            continue

        skip_blank_run = 0
        out.append(line)

    result = "\n".join(out).strip() + "\n"
    return result, stats
