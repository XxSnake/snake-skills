#!/usr/bin/env python3
"""
Validate every SKILL.md in the repo:
- must start with a YAML frontmatter block delimited by ---
- frontmatter must parse as YAML and contain non-empty `name` and `description`
- `name` should equal the parent directory name (warn, do not fail)

Exit code 1 if any hard check fails.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SCAN_DIRS = ['codex', 'claude']

errors: list[str] = []
warnings: list[str] = []
checked = 0


def parse_frontmatter(text: str) -> dict | None:
    if not text.startswith('---'):
        return None
    parts = text.split('---', 2)
    if len(parts) < 3:
        return None
    try:
        return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as e:
        raise ValueError(f'YAML parse error: {e}') from e


for scan in SCAN_DIRS:
    base = REPO_ROOT / scan
    if not base.is_dir():
        continue
    for skill_md in sorted(base.glob('*/SKILL.md')):
        checked += 1
        rel = skill_md.relative_to(REPO_ROOT)
        try:
            text = skill_md.read_text(encoding='utf-8')
        except UnicodeDecodeError as e:
            errors.append(f'{rel}: not valid UTF-8 ({e})')
            continue

        try:
            fm = parse_frontmatter(text)
        except ValueError as e:
            errors.append(f'{rel}: {e}')
            continue

        if fm is None:
            errors.append(f'{rel}: missing YAML frontmatter (--- delimited)')
            continue

        name = fm.get('name')
        desc = fm.get('description')

        if not name or not isinstance(name, str):
            errors.append(f'{rel}: missing or empty `name` in frontmatter')
        if not desc or not isinstance(desc, str):
            errors.append(f'{rel}: missing or empty `description` in frontmatter')

        expected_name = skill_md.parent.name
        if isinstance(name, str) and name != expected_name:
            warnings.append(
                f'{rel}: frontmatter name `{name}` does not match dir name `{expected_name}`'
            )

print(f'Checked {checked} SKILL.md file(s).')

for w in warnings:
    print(f'WARN: {w}')

if errors:
    print()
    for e in errors:
        print(f'ERROR: {e}')
    print(f'\n{len(errors)} error(s) found.')
    sys.exit(1)

print('OK.')
