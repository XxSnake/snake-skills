#!/usr/bin/env python3
"""Validate Snake Digest Codex article, image plan, and generated images."""

from __future__ import annotations

import argparse
import hashlib
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
        (r'<\s*svg\b', 'article contains inline SVG; ChatGPT-generated raster images are required'),
        (r'```\s*mermaid', 'article contains Mermaid diagram; ChatGPT-generated raster images are required'),
        (r'\.svg\b', 'article references an SVG file; only ChatGPT-generated PNG/JPG/WebP images are allowed'),
    ]
    for pattern, message in forbidden_article_patterns:
        if re.search(pattern, text, re.I):
            errors.append(message)

    if re.search(r'^```', text, re.M):
        warnings.append('article contains fenced code block; it may create a large visual block in PDF. Move code/JSON/commands to sources.md unless essential.')
        if args.strict:
            errors.append('strict mode rejects fenced code blocks in final article.md')

    placeholders = PLACEHOLDER_RE.findall(text)
    placeholder_ids = [p[0] for p in placeholders]
    plan = load_json(plan_path)
    generation_mode = plan.get('generation_mode')
    if generation_mode != 'chatgpt-image-model-raster-only':
        warnings.append('image_plan does not declare ChatGPT raster-only generation mode')
        if args.strict:
            errors.append('strict mode requires generation_mode=chatgpt-image-model-raster-only')
    images = plan.get('images', [])
    if not isinstance(images, list) or not images:
        errors.append('image_plan has no usable images list')
        images = []
    plan_ids = [item.get('id') for item in images]
    duplicate_plan_ids = sorted({img_id for img_id in plan_ids if img_id and plan_ids.count(img_id) > 1})
    if duplicate_plan_ids:
        errors.append('duplicate image ids in image_plan: ' + ', '.join(duplicate_plan_ids))

    duplicate_placeholder_ids = sorted({img_id for img_id in placeholder_ids if placeholder_ids.count(img_id) > 1})
    if duplicate_placeholder_ids:
        warnings.append('article reuses image placeholders: ' + ', '.join(duplicate_placeholder_ids))
        if args.strict:
            errors.append('strict mode requires each planned body image to appear once')

    body_hero_count = sum(1 for item in images if item.get('role') != 'cover' and item.get('layout') == 'hero')
    if body_hero_count > 1:
        warnings.append(f'image_plan has {body_hero_count} body hero images; use normal layout by default to preserve paper-like visual consistency')
        if args.strict:
            errors.append('strict mode allows at most 1 body hero image')

    if 'img_cover' not in plan_ids:
        errors.append('image_plan has no img_cover')

    if Image is None and args.strict:
        errors.append('strict mode requires Pillow to inspect raster image dimensions')

    style_text = str(plan.get('style') or '')
    seen_hashes: dict[str, str] = {}

    for item in images:
        img_id = item.get('id')
        filename = item.get('filename')
        role = item.get('role')
        prompt = item.get('prompt_en')
        if not img_id or not filename:
            errors.append(f'bad image item: {item}')
            continue
        if role not in {'cover', 'body'}:
            errors.append(f'invalid image role for {img_id}: {role!r}')
        layout = item.get('layout')
        if role == 'cover' and layout != 'cover':
            errors.append(f'cover image must use cover layout: {img_id}')
        if role != 'cover' and layout not in {'normal', 'hero', 'small'}:
            errors.append(f'invalid body image layout for {img_id}: {layout!r}')
        if role != 'cover' and img_id not in placeholder_ids:
            warnings.append(f'planned image not referenced in article: {img_id}')
            if args.strict:
                errors.append(f'strict mode rejects unreferenced planned image: {img_id}')
        if not prompt:
            warnings.append(f'image has no prompt_en: {img_id}')
            if args.strict:
                errors.append(f'strict mode requires prompt_en: {img_id}')
        combined_style = f'{style_text} {prompt or ""}'.lower()
        if not any(term in combined_style for term in ('muted', 'low-saturation', 'low saturation', 'sepia', 'aged paper')):
            warnings.append(f'image prompt lacks the muted aged-paper style: {img_id}')
            if args.strict:
                errors.append(f'strict mode requires the shared muted paper style: {img_id}')
        path = image_dir / filename
        if not path.exists():
            alt = find_image(image_dir, img_id)
            if not alt:
                errors.append(f'missing image file: {filename}')
                continue
            if args.strict:
                errors.append(f'strict mode requires exact planned filename: {filename}')
            path = alt
        if path.suffix.lower() not in {'.png', '.jpg', '.jpeg', '.webp'}:
            errors.append(f'forbidden non-raster image file: {path.name}')
            continue
        if path.stat().st_size < 20_000:
            warnings.append(f'image file is very small, inspect it for placeholder content: {path.name}')
            if args.strict:
                errors.append(f'strict mode rejects tiny image file: {path.name}')

        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest in seen_hashes:
            other_id = seen_hashes[digest]
            warnings.append(f'duplicate image content: {other_id} and {img_id}')
            if args.strict:
                errors.append(f'strict mode rejects duplicate image content: {other_id} and {img_id}')
        else:
            seen_hashes[digest] = img_id

        if Image is not None:
            try:
                with Image.open(path) as im:
                    w, h = im.size
                    im.verify()
                if min(w, h) < 800:
                    warnings.append(f'image resolution is too small for final PDF: {filename} {w}x{h}')
                    if args.strict:
                        errors.append(f'strict mode requires both image edges to be at least 800 px: {filename}')
                if role == 'cover' and h / max(w, 1) < 1.2:
                    warnings.append(f'cover image is not sufficiently portrait: {filename} {w}x{h}')
                    if args.strict:
                        errors.append(f'strict mode requires a portrait cover image: {filename}')
                if role != 'cover' and w / max(h, 1) < 1.2:
                    warnings.append(f'body image is not sufficiently landscape: {filename} {w}x{h}')
                    if args.strict:
                        errors.append(f'strict mode requires a landscape body image: {filename}')
            except Exception as exc:
                warnings.append(f'cannot inspect image {filename}: {exc}')
                if args.strict:
                    errors.append(f'strict mode requires a readable raster image: {filename}')

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
    else:
        source_text = sources.read_text(encoding='utf-8').strip()
        empty_template_fields = sum(
            bool(re.search(pattern, source_text, re.M))
            for pattern in (
                r'^- 标题：\s*$',
                r'^- URL：\s*$',
                r'^- 支撑事实：\s*$',
            )
        )
        if len(source_text) < 120 or empty_template_fields >= 2:
            warnings.append('sources.md still looks empty or template-only')
            if args.strict:
                errors.append('strict mode requires completed source notes')

    if not re.search(r'^#{1,3}\s+.*资料来源', text, re.M):
        warnings.append('article has no sources or further-reading section')
        if args.strict:
            errors.append('strict mode requires a sources section in article.md')

    if warnings:
        for w in warnings: print('[WARN]', w)
    if errors:
        for e in errors: print('[ERROR]', e)
        raise SystemExit(1)
    print('[OK] validation passed')


if __name__ == '__main__':
    main()
