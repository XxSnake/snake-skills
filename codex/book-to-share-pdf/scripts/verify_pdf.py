#!/usr/bin/env python3
"""Verify a generated PDF booklet.

Checks:
- file exists and is non-empty
- PDF can be opened
- page count > 0
- text can be extracted from at least one page
- optional render smoke test using pypdfium2

Usage:
  python scripts/verify_pdf.py booklet.pdf
  python scripts/verify_pdf.py booklet.pdf --render --out-dir renders
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def verify_basic(pdf_path: Path):
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    if pdf_path.stat().st_size < 1024:
        raise ValueError(f"PDF file is unexpectedly small: {pdf_path.stat().st_size} bytes")

    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    pages = len(reader.pages)
    if pages <= 0:
        raise ValueError("PDF has no pages")

    extracted = ""
    for page in reader.pages[: min(3, pages)]:
        try:
            extracted += page.extract_text() or ""
        except Exception:
            pass
    if not extracted.strip():
        raise ValueError("Could not extract text from first pages; check whether text rendered as paths/images only")

    return {"pages": pages, "sample_text": extracted[:200]}


def render_smoke(pdf_path: Path, out_dir: Path):
    import pypdfium2 as pdfium

    out_dir.mkdir(parents=True, exist_ok=True)
    pdf = pdfium.PdfDocument(str(pdf_path))
    rendered = []
    for idx in range(min(len(pdf), 3)):
        page = pdf[idx]
        bitmap = page.render(scale=1.5)
        image = bitmap.to_pil()
        out = out_dir / f"page_{idx + 1:02d}.png"
        image.save(out)
        rendered.append(str(out))
    return rendered


def main(argv=None):
    parser = argparse.ArgumentParser(description="Verify generated PDF booklet.")
    parser.add_argument("pdf", type=Path, help="PDF to verify")
    parser.add_argument("--render", action="store_true", help="Render first pages as PNGs for visual inspection")
    parser.add_argument("--out-dir", type=Path, default=Path("_pdf_renders"), help="Render output directory")
    args = parser.parse_args(argv)

    try:
        info = verify_basic(args.pdf)
        print(f"OK: {args.pdf}")
        print(f"Pages: {info['pages']}")
        print(f"Text sample: {info['sample_text']!r}")
        if args.render:
            rendered = render_smoke(args.pdf, args.out_dir)
            print("Rendered:")
            for item in rendered:
                print(f"- {item}")
    except Exception as exc:
        print(f"VERIFY FAILED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
