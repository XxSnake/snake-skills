#!/usr/bin/env python3
"""Verify and optionally render every page of a Snake Digest PDF."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


GENERIC_NAMES = {'final', 'draft', 'output'}


def verify_pdf(pdf_path: Path) -> dict:
    if not pdf_path.exists():
        raise FileNotFoundError(f'PDF not found: {pdf_path}')
    if pdf_path.stat().st_size < 10_000:
        raise ValueError(f'PDF is unexpectedly small: {pdf_path.stat().st_size} bytes')
    if pdf_path.stem.lower() in GENERIC_NAMES:
        raise ValueError('final PDF must use the article title instead of a generic filename')

    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    page_count = len(reader.pages)
    if page_count <= 0:
        raise ValueError('PDF has no pages')

    text_parts: list[str] = []
    page_sizes: list[tuple[float, float]] = []
    blank_pages: list[int] = []
    for index, page in enumerate(reader.pages, start=1):
        page_sizes.append((float(page.mediabox.width), float(page.mediabox.height)))
        try:
            page_text = page.extract_text() or ''
        except Exception:
            page_text = ''
        text_parts.append(page_text)
        if not re.sub(r'\s+', '', page_text):
            blank_pages.append(index)
    full_text = '\n'.join(text_parts)

    if blank_pages:
        raise ValueError('pages without extractable text: ' + ', '.join(map(str, blank_pages)))
    if len(re.sub(r'\s+', '', full_text)) < 80:
        raise ValueError('PDF text extraction is nearly empty; check fonts and rendering')
    if re.search(r'file:///|https?://localhost', full_text, re.I):
        raise ValueError('PDF contains a local file address in its visible text')
    if '资料来源' not in full_text:
        raise ValueError('PDF has no visible sources section')

    expected_a4 = (595.3, 841.9)
    for index, (width, height) in enumerate(page_sizes, start=1):
        if abs(width - expected_a4[0]) > 4 or abs(height - expected_a4[1]) > 4:
            raise ValueError(f'page {index} is not A4 portrait: {width:.1f}x{height:.1f} pt')

    return {
        'pages': page_count,
        'characters': len(re.sub(r'\s+', '', full_text)),
    }


def render_all_pages(pdf_path: Path, out_dir: Path, dpi: int = 120) -> list[Path]:
    import pypdfium2 as pdfium

    out_dir.mkdir(parents=True, exist_ok=True)
    for stale in out_dir.glob('page_*.png'):
        stale.unlink()

    pdf = pdfium.PdfDocument(str(pdf_path))
    rendered: list[Path] = []
    scale = dpi / 72
    for index in range(len(pdf)):
        page = pdf[index]
        bitmap = page.render(scale=scale)
        image = bitmap.to_pil()
        output = out_dir / f'page_{index + 1:03d}.png'
        image.save(output)
        rendered.append(output)
    if len(rendered) != len(pdf):
        raise ValueError('not every PDF page was rendered')
    return rendered


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Verify and render a Snake Digest PDF')
    parser.add_argument('pdf', type=Path)
    parser.add_argument('--render', action='store_true', help='render every page to PNG')
    parser.add_argument('--out-dir', type=Path, default=Path('_pdf_renders'))
    parser.add_argument('--dpi', type=int, default=120)
    args = parser.parse_args(argv)

    try:
        info = verify_pdf(args.pdf)
        print(f"[OK] PDF: {args.pdf}")
        print(f"[OK] pages: {info['pages']}")
        print(f"[OK] extracted characters: {info['characters']}")
        if args.render:
            rendered = render_all_pages(args.pdf, args.out_dir, args.dpi)
            print(f'[OK] rendered all {len(rendered)} page(s) to: {args.out_dir}')
    except Exception as exc:
        print(f'[ERROR] PDF verification failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
