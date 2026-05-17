#!/usr/bin/env python3
"""Создать reference.docx со стилями по методическим требованиям ВКР (раздел 6.4)."""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Mm, Pt


def _set_font(style, name: str = "Times New Roman", size_pt: int = 14) -> None:
    style.font.name = name
    style.font.size = Pt(size_pt)
    rfonts = style.element.rPr.rFonts if style.element.rPr is not None else None
    if rfonts is None:
        rpr = style.element.get_or_add_rPr()
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:ascii"), name)
    rfonts.set(qn("w:hAnsi"), name)
    rfonts.set(qn("w:cs"), name)
    rfonts.set(qn("w:eastAsia"), name)


def _paragraph_format(
    style,
    *,
    align=WD_ALIGN_PARAGRAPH.JUSTIFY,
    indent_mm: float = 12.5,
    line_spacing: float = 1.5,
    space_before_pt: float = 0,
    space_after_pt: float = 0,
) -> None:
    pf = style.paragraph_format
    pf.alignment = align
    pf.first_line_indent = Mm(indent_mm)
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    pf.line_spacing = line_spacing
    pf.space_before = Pt(space_before_pt)
    pf.space_after = Pt(space_after_pt)


def _add_custom_style(doc: Document, name: str, base: str = "Normal") -> None:
    if name in [s.name for s in doc.styles]:
        return
    style = doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
    style.base_style = doc.styles[base]
    return style


def build_reference_docx(path: Path) -> Path:
    doc = Document()
    for section in doc.sections:
        section.page_height = Mm(297)
        section.page_width = Mm(210)
        section.left_margin = Mm(30)
        section.right_margin = Mm(10)
        section.top_margin = Mm(20)
        section.bottom_margin = Mm(20)

    normal = doc.styles["Normal"]
    _set_font(normal, size_pt=14)
    _paragraph_format(normal)

    for level, size, indent, align in (
        (1, 14, 0, WD_ALIGN_PARAGRAPH.LEFT),
        (2, 14, 12.5, WD_ALIGN_PARAGRAPH.LEFT),
        (3, 14, 12.5, WD_ALIGN_PARAGRAPH.LEFT),
        (4, 14, 12.5, WD_ALIGN_PARAGRAPH.LEFT),
    ):
        h = doc.styles[f"Heading {level}"]
        _set_font(h, size_pt=size)
        _paragraph_format(
            h,
            align=align,
            indent_mm=indent,
            line_spacing=1.5,
            space_before_pt=12 if level == 1 else 6,
            space_after_pt=6,
        )
        h.paragraph_format.keep_with_next = True

    structural = _add_custom_style(doc, "Structural")
    _set_font(structural, size_pt=14)
    _paragraph_format(
        structural,
        align=WD_ALIGN_PARAGRAPH.CENTER,
        indent_mm=0,
        space_before_pt=12,
        space_after_pt=12,
    )

    for name, align, size in (
        ("Table Caption", WD_ALIGN_PARAGRAPH.LEFT, 12),
        ("Figure Caption", WD_ALIGN_PARAGRAPH.CENTER, 12),
    ):
        cap = _add_custom_style(doc, name)
        _set_font(cap, size_pt=size)
        _paragraph_format(cap, align=align, indent_mm=0, line_spacing=1.0)

    if "Footnote Text" in [s.name for s in doc.styles]:
        fn = doc.styles["Footnote Text"]
        _set_font(fn, size_pt=10)
        _paragraph_format(fn, line_spacing=1.0)

    doc.add_paragraph("Образец основного текста.", style="Normal")
    doc.add_paragraph("Раздел 1. Пример заголовка", style="Heading 1")
    doc.add_paragraph("1.1. Пример подраздела", style="Heading 2")

    path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(path))
    return path


def main() -> None:
    out = Path(__file__).resolve().parent / "assets" / "reference.docx"
    build_reference_docx(out)
    print(f"Создан: {out}")


if __name__ == "__main__":
    main()
