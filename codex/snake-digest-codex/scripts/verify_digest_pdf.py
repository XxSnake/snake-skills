#!/usr/bin/env python3
"""Verify and optionally render every page of a Snake Digest PDF."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


GENERIC_NAMES = {'final', 'draft', 'output'}
PAGE_SIZES = {
    'A4': (595.3, 841.9),
    'A5': (419.5, 595.3),
}


def verify_pdf(pdf_path: Path, page_size: str = 'A4') -> dict:
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

    expected_size = PAGE_SIZES[page_size.upper()]
    for index, (width, height) in enumerate(page_sizes, start=1):
        if abs(width - expected_size[0]) > 4 or abs(height - expected_size[1]) > 4:
            raise ValueError(f'page {index} is not {page_size.upper()} portrait: {width:.1f}x{height:.1f} pt')

    return {
        'pages': page_count,
        'characters': len(re.sub(r'\s+', '', full_text)),
    }


def parse_pages(value: str | None, page_count: int) -> list[int]:
    if not value:
        return list(range(1, page_count + 1))
    selected: set[int] = set()
    for part in value.split(','):
        bounds = part.strip().split('-', 1)
        start = int(bounds[0])
        end = int(bounds[1]) if len(bounds) == 2 else start
        if start < 1 or end < start or end > page_count:
            raise ValueError(f'invalid page selection: {part}')
        selected.update(range(start, end + 1))
    return sorted(selected)


def render_all_pages(pdf_path: Path, out_dir: Path, dpi: int = 120, pages: str | None = None) -> list[Path]:
    import pypdfium2 as pdfium

    out_dir.mkdir(parents=True, exist_ok=True)
    pdf = pdfium.PdfDocument(str(pdf_path))
    selected = parse_pages(pages, len(pdf))
    if pages is None:
        for stale in out_dir.glob('page_*.png'):
            stale.unlink()
    rendered: list[Path] = []
    scale = dpi / 72
    try:
        for page_number in selected:
            page = pdf[page_number - 1]
            bitmap = page.render(scale=scale)
            image = bitmap.to_pil()
            output = out_dir / f'page_{page_number:03d}.png'
            image.save(output)
            rendered.append(output)
            bitmap.close()
            page.close()
    finally:
        pdf.close()
    if len(rendered) != len(selected):
        raise ValueError('not every selected PDF page was rendered')
    return rendered


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Verify and render a Snake Digest PDF')
    parser.add_argument('pdf', type=Path)
    parser.add_argument('--render', action='store_true', help='render every page to PNG')
    parser.add_argument('--out-dir', type=Path, default=Path('_pdf_renders'))
    parser.add_argument('--dpi', type=int, default=120)
    parser.add_argument('--page-size', choices=['A4', 'A5'], default='A4')
    parser.add_argument('--pages', help='render selected pages, for example 1,3-5; preserves other rendered pages')
    args = parser.parse_args(argv)

    try:
        info = verify_pdf(args.pdf, args.page_size)
        print(f"[OK] PDF: {args.pdf}")
        print(f"[OK] pages: {info['pages']}")
        print(f"[OK] extracted characters: {info['characters']}")
        if args.render:
            rendered = render_all_pages(args.pdf, args.out_dir, args.dpi, args.pages)
            scope = 'selected' if args.pages else 'all'
            print(f'[OK] rendered {scope} {len(rendered)} page(s) to: {args.out_dir}')
    except Exception as exc:
        print(f'[ERROR] PDF verification failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
