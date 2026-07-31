#!/usr/bin/env python3
"""Verify a generated PDF booklet.

Checks:
- file exists and is non-empty
- PDF can be opened and every page contains extractable text
- page size is A5 or A4 portrait
- at least one font is embedded
- a sources section is present
- optional full-document rendering using pypdfium2

Usage:
  python scripts/verify_pdf.py booklet.pdf
  python scripts/verify_pdf.py booklet.pdf --render --out-dir renders
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def dereference(value):
    return value.get_object() if hasattr(value, "get_object") else value


def embedded_font_names(reader) -> set[str]:
    embedded: set[str] = set()
    for page in reader.pages:
        resources = dereference(page.get("/Resources")) or {}
        fonts = dereference(resources.get("/Font")) or {}
        for font_ref in fonts.values():
            font = dereference(font_ref) or {}
            candidates = [font]
            for descendant_ref in font.get("/DescendantFonts", []):
                candidates.append(dereference(descendant_ref) or {})
            for candidate in candidates:
                descriptor = dereference(candidate.get("/FontDescriptor"))
                if descriptor and any(key in descriptor for key in ("/FontFile", "/FontFile2", "/FontFile3")):
                    embedded.add(str(candidate.get("/BaseFont") or font.get("/BaseFont") or "unknown"))
    return embedded


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

    extracted_pages = []
    blank_pages = []
    allowed_sizes = ((419.53, 595.28), (595.28, 841.89))
    for index, page in enumerate(reader.pages, start=1):
        try:
            page_text = page.extract_text() or ""
        except Exception as exc:
            raise ValueError(f"Could not extract text from page {index}: {exc}") from exc
        extracted_pages.append(page_text)
        if not page_text.strip():
            blank_pages.append(index)

        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        if not any(abs(width - expected_w) <= 3 and abs(height - expected_h) <= 3 for expected_w, expected_h in allowed_sizes):
            raise ValueError(f"Unexpected page size on page {index}: {width:.1f} x {height:.1f} pt")

    if blank_pages:
        raise ValueError("Pages without extractable text: " + ", ".join(map(str, blank_pages)))

    extracted = "\n".join(extracted_pages)
    if "资料来源" not in extracted:
        raise ValueError("The PDF does not contain a visible 资料来源 section")

    fonts = embedded_font_names(reader)
    if not fonts:
        raise ValueError("No embedded font found; Chinese text may change or disappear on another device")

    return {"pages": pages, "sample_text": extracted[:200], "embedded_fonts": sorted(fonts)}


def render_smoke(pdf_path: Path, out_dir: Path):
    import pypdfium2 as pdfium

    out_dir.mkdir(parents=True, exist_ok=True)
    for stale in out_dir.glob("page_*.png"):
        stale.unlink()
    pdf = pdfium.PdfDocument(str(pdf_path))
    rendered = []
    for idx in range(len(pdf)):
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
    parser.add_argument("--render", action="store_true", help="Render every page as PNGs for visual inspection")
    parser.add_argument("--out-dir", type=Path, default=Path("_pdf_renders"), help="Render output directory")
    args = parser.parse_args(argv)

    try:
        info = verify_basic(args.pdf)
        print(f"OK: {args.pdf}")
        print(f"Pages: {info['pages']}")
        print("Embedded fonts: " + ", ".join(info["embedded_fonts"]))
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
