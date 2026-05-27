#!/usr/bin/env python3
"""Validate Snake Digest Codex article, image plan, and generated images."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

try:
    from PIL import Image
except Exception:  # pragma: no cover
    Image = None

PLACEHOLDER_RE = re.compile(r'<!--IMG:([A-Za-z0-9_\-]+):(.*?)(?::(normal|hero|small))?-->', re.S)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def find_image(image_dir: Path, img_id: str) -> Path | None:
    for ext in ('png', 'jpg', 'jpeg', 'webp'):
        p = image_dir / f'{img_id}.{ext}'
        if p.exists():
            return p
    for p in image_dir.glob('*'):
        if p.is_file() and p.stem.lower() == img_id.lower():
            return p
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description='Validate Snake Digest Codex outputs')
    parser.add_argument('article', help='article.md')
    parser.add_argument('image_plan', help='image_plan.json')
    parser.add_argument('image_dir', help='images directory')
    parser.add_argument('--strict', action='store_true')
    args = parser.parse_args()

    article = Path(args.article)
    plan_path = Path(args.image_plan)
    image_dir = Path(args.image_dir)

    errors: list[str] = []
    warnings: list[str] = []

    if not article.exists(): errors.append(f'missing article: {article}')
    if not plan_path.exists(): errors.append(f'missing image_plan: {plan_path}')
    if not image_dir.is_dir(): errors.append(f'missing image_dir: {image_dir}')
    if errors:
        for e in errors: print('[ERROR]', e)
        raise SystemExit(1)

    text = article.read_text(encoding='utf-8')
    if not re.search(r'^#\s+\S+', text, re.M):
        errors.append('article has no H1 title')

    forbidden_article_patterns = [
        (r'<\s*svg\b', 'article contains inline SVG; Image2 images are required instead'),
        (r'```\s*mermaid', 'article contains Mermaid diagram; Image2 images are required instead'),
        (r'\.svg\b', 'article references an SVG file; Image2 raster images are required instead'),
    ]
    for pattern, message in forbidden_article_patterns:
        if re.search(pattern, text, re.I):
            errors.append(message)

    placeholders = PLACEHOLDER_RE.findall(text)
    placeholder_ids = [p[0] for p in placeholders]
    plan = load_json(plan_path)
    images = plan.get('images', [])
    plan_ids = [item.get('id') for item in images]

    if 'img_cover' not in plan_ids:
        errors.append('image_plan has no img_cover')

    for item in images:
        img_id = item.get('id')
        filename = item.get('filename')
        role = item.get('role')
        prompt = item.get('prompt_en')
        if not img_id or not filename:
            errors.append(f'bad image item: {item}')
            continue
        if role != 'cover' and img_id not in placeholder_ids:
            warnings.append(f'planned image not referenced in article: {img_id}')
        if not prompt:
            warnings.append(f'image has no prompt_en: {img_id}')
        path = image_dir / filename
        if not path.exists():
            alt = find_image(image_dir, img_id)
            if not alt:
                errors.append(f'missing image file: {filename}')
                continue
            path = alt
        if path.suffix.lower() == '.svg':
            errors.append(f'forbidden SVG image file: {path.name}; use Image2 raster output')
            continue
        if path.stat().st_size < 20_000:
            warnings.append(f'image file is very small, check it is not a placeholder or programmatic stub: {path.name}')
            if args.strict:
                errors.append(f'strict mode rejects tiny image file: {path.name}')
        if Image is not None:
            try:
                with Image.open(path) as im:
                    w, h = im.size
                if role == 'cover' and w > h:
                    warnings.append(f'cover image looks landscape: {filename} {w}x{h}')
                if role != 'cover' and h > w:
                    warnings.append(f'body image looks portrait: {filename} {w}x{h}')
            except Exception as exc:
                warnings.append(f'cannot inspect image {filename}: {exc}')

    for img_id in placeholder_ids:
        if img_id not in plan_ids:
            errors.append(f'article placeholder not in image_plan: {img_id}')
        if not find_image(image_dir, img_id):
            errors.append(f'article placeholder image missing: {img_id}')

    sources = article.parent / 'sources.md'
    if not sources.exists():
        warnings.append('sources.md missing beside article.md')
        if args.strict:
            errors.append('strict mode requires sources.md')

    if warnings:
        for w in warnings: print('[WARN]', w)
    if errors:
        for e in errors: print('[ERROR]', e)
        raise SystemExit(1)
    print('[OK] validation passed')


if __name__ == '__main__':
    main()
