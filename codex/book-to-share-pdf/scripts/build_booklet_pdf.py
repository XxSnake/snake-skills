#!/usr/bin/env python3
"""
Build an old-paper-style Chinese reading booklet PDF from a Markdown draft.

Usage:
  python scripts/build_booklet_pdf.py draft.md -o booklet.pdf
  python scripts/build_booklet_pdf.py draft.md -o booklet.pdf --page-size A4

The parser intentionally supports a small, stable Markdown subset:
- YAML-like front matter: title, author, subtitle, book_type, date, hook
- # / ## / ### headings
- paragraphs
- unordered lists beginning with "- "
- ordered lists like "1. "
- blockquotes beginning with "> "
- horizontal rules ---

This script avoids bundling font files. It uses ReportLab's built-in CJK CID font
(STSong-Light) so Chinese text can render in common environments.
"""

from __future__ import annotations

import argparse
import html
import os
import random
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable, List, Tuple

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, A5
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    NextPageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    ListFlowable,
    ListItem,
)

PAPER = HexColor("#F3E7CF")
INK = HexColor("#2B2118")
H1 = HexColor("#5A321C")
H2 = HexColor("#6F472B")
RULE = HexColor("#C9A66B")
QUOTE_BG = HexColor("#EAD9B8")
FOOTER = HexColor("#8A735C")
MUTED = HexColor("#9A8266")

FONT_REGULAR = "STSong-Light"
FONT_BOLD = "STSong-Light"


@dataclass
class Meta:
    title: str = "未命名书籍"
    author: str = ""
    subtitle: str = "拆书分享小册"
    book_type: str = "Book-to-Share"
    date: str = ""
    hook: str = "会讲故事的读书人，把一本书重新讲给你听。"


def register_fonts() -> None:
    global FONT_REGULAR, FONT_BOLD

    skill_dir = Path(__file__).resolve().parents[1]
    windir = Path(os.environ.get("WINDIR", "C:/Windows"))
    serif_candidates = [
        skill_dir / "assets/fonts/NotoSerifSC-VF.ttf",
        windir / "Fonts/NotoSerifSC-VF.ttf",
        Path("/usr/share/fonts/truetype/noto/NotoSerifCJK-Regular.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"),
        Path("/System/Library/Fonts/Supplemental/Songti.ttc"),
    ]
    heading_candidates = [
        skill_dir / "assets/fonts/NotoSansSC-VF.ttf",
        windir / "Fonts/NotoSansSC-VF.ttf",
        Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/System/Library/Fonts/PingFang.ttc"),
    ]

    serif_path = next((path for path in serif_candidates if path.is_file()), None)
    heading_path = next((path for path in heading_candidates if path.is_file()), serif_path)
    if serif_path and heading_path:
        try:
            pdfmetrics.registerFont(TTFont("Booklet-Serif", str(serif_path)))
            pdfmetrics.registerFont(TTFont("Booklet-Bold", str(heading_path)))
            pdfmetrics.registerFontFamily(
                "Booklet-Serif",
                normal="Booklet-Serif",
                bold="Booklet-Bold",
                italic="Booklet-Serif",
                boldItalic="Booklet-Bold",
            )
            FONT_REGULAR = "Booklet-Serif"
            FONT_BOLD = "Booklet-Bold"
            return
        except Exception as exc:
            print(f"Embedded font registration failed, using CID fallback: {exc}", file=sys.stderr)

    try:
        pdfmetrics.registerFont(UnicodeCIDFont(FONT_REGULAR))
    except Exception:
        # It may already be registered.
        pass


def parse_front_matter(text: str) -> Tuple[Meta, str]:
    meta = Meta(date=str(date.today()))
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            raw = text[4:end].strip().splitlines()
            body = text[end + len("\n---") :].lstrip("\n")
            data = {}
            for line in raw:
                if ":" not in line:
                    continue
                key, value = line.split(":", 1)
                data[key.strip()] = value.strip().strip('"').strip("'")
            for field in meta.__dataclass_fields__:
                if field in data:
                    setattr(meta, field, data[field])
            return meta, body
    return meta, text


def escape(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`(.+?)`", r"<font color='#6F472B'>\1</font>", text)
    return text


def make_styles():
    base = getSampleStyleSheet()
    styles = {}
    styles["body"] = ParagraphStyle(
        "body",
        parent=base["Normal"],
        fontName=FONT_REGULAR,
        fontSize=10.6,
        leading=18.1,
        textColor=INK,
        alignment=TA_LEFT,
        spaceAfter=7,
        firstLineIndent=0,
    )
    styles["cover_kicker"] = ParagraphStyle(
        "cover_kicker",
        parent=styles["body"],
        fontSize=8.5,
        leading=12,
        textColor=MUTED,
        alignment=TA_CENTER,
        spaceAfter=8,
    )
    styles["cover_title"] = ParagraphStyle(
        "cover_title",
        parent=styles["body"],
        fontName=FONT_BOLD,
        fontSize=27,
        leading=38,
        textColor=H1,
        alignment=TA_CENTER,
        spaceAfter=10,
    )
    styles["cover_author"] = ParagraphStyle(
        "cover_author",
        parent=styles["body"],
        fontSize=11,
        leading=17,
        textColor=H2,
        alignment=TA_CENTER,
        spaceAfter=28,
    )
    styles["cover_subtitle"] = ParagraphStyle(
        "cover_subtitle",
        parent=styles["body"],
        fontSize=12,
        leading=21,
        textColor=INK,
        alignment=TA_CENTER,
        spaceAfter=34,
    )
    styles["cover_meta"] = ParagraphStyle(
        "cover_meta",
        parent=styles["body"],
        fontSize=8.8,
        leading=13,
        textColor=MUTED,
        alignment=TA_CENTER,
    )
    styles["h1"] = ParagraphStyle(
        "h1",
        parent=styles["body"],
        fontName=FONT_BOLD,
        fontSize=22,
        leading=32,
        textColor=H1,
        spaceBefore=10,
        spaceAfter=14,
        keepWithNext=True,
    )
    styles["h2"] = ParagraphStyle(
        "h2",
        parent=styles["body"],
        fontName=FONT_BOLD,
        fontSize=15,
        leading=23,
        textColor=H2,
        spaceBefore=16,
        spaceAfter=8,
        keepWithNext=True,
    )
    styles["h3"] = ParagraphStyle(
        "h3",
        parent=styles["body"],
        fontName=FONT_BOLD,
        fontSize=12.5,
        leading=19,
        textColor=H2,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True,
    )
    styles["quote"] = ParagraphStyle(
        "quote",
        parent=styles["body"],
        fontSize=10.3,
        leading=17,
        textColor=INK,
        leftIndent=0,
        rightIndent=0,
        spaceAfter=0,
    )
    styles["small"] = ParagraphStyle(
        "small",
        parent=styles["body"],
        fontSize=8.8,
        leading=14.5,
        textColor=INK,
    )
    styles["li"] = ParagraphStyle(
        "li",
        parent=styles["body"],
        fontSize=10.4,
        leading=17.2,
        leftIndent=0,
        spaceAfter=2.5,
    )
    return styles


def paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(escape(text.strip()), style)


def quote_block(lines: List[str], style: ParagraphStyle, width: float):
    content = "<br/>".join(escape(line.strip()) for line in lines if line.strip())
    p = Paragraph(content, style)
    table = Table([[p]], colWidths=[width])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), QUOTE_BG),
                ("BOX", (0, 0), (-1, -1), 0.25, HexColor("#DDC594")),
                ("LINEBEFORE", (0, 0), (0, -1), 2.0, RULE),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ]
        )
    )
    return [Spacer(1, 5), table, Spacer(1, 8)]


def list_block(items: List[str], style: ParagraphStyle, ordered: bool = False):
    if ordered:
        flow_items = [
            ListItem(Paragraph(escape(item), style), leftIndent=12, value=index)
            for index, item in enumerate(items, start=1)
        ]
    else:
        flow_items = [ListItem(Paragraph(escape(item), style), leftIndent=12) for item in items]
    return ListFlowable(
        flow_items,
        bulletType="1" if ordered else "bullet",
        leftIndent=16,
        bulletFontName=FONT_REGULAR,
        bulletFontSize=8,
        bulletColor=H2,
        start=1 if ordered else None,
    )


def parse_markdown(body: str, styles, content_width: float):
    story = []
    lines = body.splitlines()
    para: List[str] = []
    quote: List[str] = []
    bullets: List[str] = []
    ordered: List[str] = []

    def flush_para():
        nonlocal para
        if para:
            story.append(paragraph(" ".join(x.strip() for x in para), styles["body"]))
            para = []

    def flush_quote():
        nonlocal quote
        if quote:
            story.extend(quote_block(quote, styles["quote"], content_width))
            quote = []

    def flush_bullets():
        nonlocal bullets
        if bullets:
            story.append(list_block(bullets, styles["li"], ordered=False))
            story.append(Spacer(1, 5))
            bullets = []

    def flush_ordered():
        nonlocal ordered
        if ordered:
            story.append(list_block(ordered, styles["li"], ordered=True))
            story.append(Spacer(1, 5))
            ordered = []

    def flush_all():
        flush_para(); flush_quote(); flush_bullets(); flush_ordered()

    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            flush_all()
            continue

        if line.strip() == "---":
            flush_all()
            story.append(Spacer(1, 8))
            continue

        if line.startswith(">"):
            flush_para(); flush_bullets(); flush_ordered()
            quote.append(line.lstrip("> ").strip())
            continue

        m_bullet = re.match(r"^\s*[-*]\s+(.+)$", line)
        if m_bullet:
            flush_para(); flush_quote(); flush_ordered()
            bullets.append(m_bullet.group(1).strip())
            continue

        m_ordered = re.match(r"^\s*\d+[.)]\s+(.+)$", line)
        if m_ordered:
            flush_para(); flush_quote(); flush_bullets()
            ordered.append(m_ordered.group(1).strip())
            continue

        if line.startswith("# "):
            flush_all()
            story.append(Paragraph(escape(line[2:].strip()), styles["h1"]))
            story.append(Spacer(1, 2))
            continue

        if line.startswith("## "):
            flush_all()
            story.append(Paragraph(escape(line[3:].strip()), styles["h2"]))
            continue

        if line.startswith("### "):
            flush_all()
            story.append(Paragraph(escape(line[4:].strip()), styles["h3"]))
            continue

        flush_quote(); flush_bullets(); flush_ordered()
        para.append(line.strip())

    flush_all()
    return story


def draw_old_paper_background(c, doc):
    width, height = doc.pagesize
    c.saveState()
    c.setFillColor(PAPER)
    c.rect(0, 0, width, height, stroke=0, fill=1)

    # Subtle fibers and speckles; deterministic by page number.
    rnd = random.Random(1009 + doc.page)
    try:
        c.setFillAlpha(0.028)
        c.setStrokeAlpha(0.06)
    except Exception:
        pass

    for _ in range(45):
        x = rnd.uniform(0, width)
        y = rnd.uniform(0, height)
        radius = rnd.uniform(0.12, 0.45)
        shade = rnd.choice([HexColor("#7C593B"), HexColor("#B79B6C"), HexColor("#6E4B30")])
        c.setFillColor(shade)
        c.circle(x, y, radius, stroke=0, fill=1)

    # Keep texture to faint speckles only; avoid ruled-line artifacts.

    # Gentle edge darkening.
    try:
        c.setFillAlpha(0.018)
    except Exception:
        pass
    c.setFillColor(HexColor("#5A321C"))
    c.rect(0, 0, width, 5 * mm, stroke=0, fill=1)
    c.rect(0, height - 5 * mm, width, 5 * mm, stroke=0, fill=1)
    c.rect(0, 0, 4 * mm, height, stroke=0, fill=1)
    c.rect(width - 4 * mm, 0, 4 * mm, height, stroke=0, fill=1)

    c.restoreState()


def draw_footer(c, doc):
    draw_old_paper_background(c, doc)
    c.saveState()
    c.setFont(FONT_REGULAR, 8.2)
    c.setFillColor(FOOTER)
    page = str(doc.page)
    c.drawCentredString(doc.pagesize[0] / 2, 10 * mm, f"— {page} —")
    c.restoreState()


def draw_cover_page(c, doc):
    draw_old_paper_background(c, doc)


def build_pdf(input_path: Path, output_path: Path, page_size_name: str = "A5") -> None:
    register_fonts()
    text = input_path.read_text(encoding="utf-8")
    meta, body = parse_front_matter(text)
    page_size = A4 if page_size_name.upper() == "A4" else A5
    width, height = page_size

    left = right = 16 * mm
    top = bottom = 18 * mm
    content_width = width - left - right

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(output_path),
        pagesize=page_size,
        leftMargin=left,
        rightMargin=right,
        topMargin=top,
        bottomMargin=bottom,
        title=meta.title,
        author=meta.author,
    )
    frame = Frame(left, bottom, content_width, height - top - bottom, id="normal")
    doc.addPageTemplates(
        [
            PageTemplate(id="cover", frames=[frame], onPage=draw_cover_page),
            PageTemplate(id="normal", frames=[frame], onPage=draw_footer),
        ]
    )

    styles = make_styles()
    story = []
    story.append(Paragraph("BOOK-TO-SHARE READING BOOKLET", styles["cover_kicker"]))
    story.append(Spacer(1, 20 * mm))
    story.append(Paragraph(escape(meta.title), styles["cover_title"]))
    if meta.author:
        story.append(Paragraph(escape(meta.author), styles["cover_author"]))
    else:
        story.append(Spacer(1, 16))
    story.append(Paragraph(escape(meta.subtitle), styles["cover_subtitle"]))
    story.extend(quote_block([meta.hook], styles["quote"], content_width * 0.88))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph(escape(f"{meta.book_type} · {meta.date}"), styles["cover_meta"]))
    story.append(NextPageTemplate("normal"))
    story.append(PageBreak())

    story.extend(parse_markdown(body, styles, content_width))

    doc.build(story)


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a Book-to-Share old-paper PDF from Markdown.")
    parser.add_argument("input", type=Path, help="Input Markdown draft")
    parser.add_argument("-o", "--output", type=Path, default=Path("booklet.pdf"), help="Output PDF path")
    parser.add_argument("--page-size", choices=["A5", "A4"], default="A5", help="PDF page size")
    args = parser.parse_args(argv)

    if not args.input.exists():
        print(f"Input file not found: {args.input}", file=sys.stderr)
        return 2
    try:
        build_pdf(args.input, args.output, args.page_size)
    except Exception as exc:
        print(f"PDF build failed: {exc}", file=sys.stderr)
        return 1
    print(f"PDF written: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
