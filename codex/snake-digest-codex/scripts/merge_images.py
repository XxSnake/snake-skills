#!/usr/bin/env python3
"""Merge image placeholders into Snake Digest markdown and render PDF."""

from __future__ import annotations

import argparse
import base64
import glob
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from md_to_pdf import extract_title, md_to_html, render_pdf, resolve_output_path  # noqa: E402

PLACEHOLDER_RE = re.compile(r'<!--IMG:([A-Za-z0-9_\-]+):(.*?)(?::(normal|hero|small))?-->', re.S)


def find_image(image_dir: Path, img_id: str) -> Path | None:
    for ext in ('png', 'jpg', 'jpeg', 'webp'):
        p = image_dir / f'{img_id}.{ext}'
        if p.exists():
            return p
    for p in image_dir.iterdir():
        if p.is_file() and p.stem.lower() == img_id.lower():
            return p
    return None


def image_to_data_uri(path: Path) -> str:
    ext = path.suffix.lower()
    mime = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp'}.get(ext, 'image/png')
    return f'data:{mime};base64,' + base64.b64encode(path.read_bytes()).decode('ascii')


def merge_images_into_md(md_text: str, image_dir: Path) -> tuple[str, list[str]]:
    missing: list[str] = []
    found = 0

    def repl(match: re.Match) -> str:
        nonlocal found
        img_id = match.group(1).strip()
        caption = match.group(2).strip()
        layout = match.group(3) or 'normal'
        path = find_image(image_dir, img_id)
        if not path:
            missing.append(img_id)
            return f'<div class="article-img layout-{layout}"><div class="img-missing">[ 图片缺失：{img_id} ]</div><span class="caption">{caption}</span></div>'
        found += 1
        return f'<div class="article-img layout-{layout}"><img src="{image_to_data_uri(path)}"/><span class="caption">{caption}</span></div>'

    result = PLACEHOLDER_RE.sub(repl, md_text)
    print(f'[INFO] merged images: {found}')
    if missing:
        print('[WARN] missing images: ' + ', '.join(missing))
    return result, missing


def main() -> None:
    parser = argparse.ArgumentParser(description='Snake Digest image merge to PDF')
    parser.add_argument('input', help='article markdown with IMG placeholders')
    parser.add_argument('image_dir', help='images directory')
    parser.add_argument('output', help='output PDF path')
    parser.add_argument('--title', default=None)
    parser.add_argument('--subtitle', default='一口气搞懂一件事')
    parser.add_argument('--author', default='@潇潇蛇')
    parser.add_argument('--meta', default=None)
    parser.add_argument('--qr-image', default=None)
    parser.add_argument('--cover-image', default=None)
    parser.add_argument('--strict', action='store_true', help='fail when any image is missing')
    parser.add_argument('--engine', choices=['auto', 'browser', 'weasyprint'], default='auto')
    args = parser.parse_args()

    input_path = Path(args.input)
    image_dir = Path(args.image_dir)
    if not input_path.exists():
        raise SystemExit(f'[ERROR] missing input: {input_path}')
    if not image_dir.is_dir():
        raise SystemExit(f'[ERROR] missing image dir: {image_dir}')

    md_text = input_path.read_text(encoding='utf-8')
    merged_md, missing = merge_images_into_md(md_text, image_dir)
    if missing and args.strict:
        raise SystemExit('[ERROR] strict mode: missing images')

    actual_title = args.title or extract_title(merged_md)
    output_path = resolve_output_path(args.output, actual_title)
    html_text = md_to_html(
        merged_md,
        title=actual_title,
        subtitle=args.subtitle,
        author=args.author,
        meta_line=args.meta,
        qr_image=args.qr_image,
        cover_image=args.cover_image,
    )

    html_path = output_path.with_suffix('.html')
    html_path.write_text(html_text, encoding='utf-8')
    print(f'[OK] HTML: {html_path}')

    engine_name = render_pdf(html_path, output_path, args.engine)
    print(f'[OK] PDF: {output_path} ({output_path.stat().st_size/1024:.1f} KB)')
    print(f'[INFO] PDF engine: {engine_name}')
    if Path(args.output) != output_path:
        print(f'[INFO] generic output name replaced by title-based filename: {output_path.name}')


if __name__ == '__main__':
    main()
