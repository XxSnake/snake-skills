#!/usr/bin/env python3
"""Create a standard output workspace for one Snake Digest topic."""

from __future__ import annotations

import argparse
import re
import shutil
from datetime import date
from pathlib import Path

try:
    from slugify import slugify
except Exception:
    slugify = None


def safe_slug(text: str) -> str:
    if slugify:
        s = slugify(text, max_length=60, allow_unicode=False)
    else:
        s = re.sub(r'[^A-Za-z0-9\u4e00-\u9fff]+', '-', text).strip('-').lower()[:60]
    return s or 'snake-digest'


def main() -> None:
    parser = argparse.ArgumentParser(description='Initialize Snake Digest output workspace')
    parser.add_argument('topic')
    parser.add_argument('--root', default='outputs')
    parser.add_argument('--slug', default=None)
    args = parser.parse_args()

    skill_dir = Path(__file__).resolve().parents[1]
    slug = args.slug or safe_slug(args.topic)
    out = Path(args.root) / slug
    (out / 'images').mkdir(parents=True, exist_ok=True)

    templates = skill_dir / 'templates'
    article = templates / 'article_template.md'
    sources = templates / 'source_notes_template.md'
    image_plan = templates / 'image_plan_template.json'

    if article.exists() and not (out / 'article.md').exists():
        txt = article.read_text(encoding='utf-8').replace('文章标题', args.topic).replace('YYYY-MM-DD', str(date.today()))
        (out / 'article.md').write_text(txt, encoding='utf-8')
    if sources.exists() and not (out / 'sources.md').exists():
        shutil.copy(sources, out / 'sources.md')
    if image_plan.exists() and not (out / 'image_plan.json').exists():
        txt = image_plan.read_text(encoding='utf-8').replace('文章标题', args.topic).replace('article-slug', slug)
        (out / 'image_plan.json').write_text(txt, encoding='utf-8')

    print(f'[OK] workspace: {out}')
    print(f'[NEXT] edit {out / "article.md"}, {out / "sources.md"}, {out / "image_plan.json"}')


if __name__ == '__main__':
    main()
