#!/usr/bin/env python3
"""
Snake Digest Codex Markdown → HTML/PDF

Usage:
  python scripts/md_to_pdf.py article.md final.pdf --title "标题" --subtitle "一口气搞懂XXX"
"""

from __future__ import annotations

import argparse
import base64
import html
import os
import re
from datetime import date
from pathlib import Path

import markdown

CSS_TEMPLATE = r'''
@page {
  size: A4;
  margin: 26mm 22mm 22mm 22mm;
  background: #f8f1e4;
  @top-center {
    content: "HEADER_TEXT";
    font-family: "Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", "SimSun", serif;
    font-size: 7.4pt;
    color: #aa9776;
    letter-spacing: 1.4pt;
    border-bottom: .35pt solid #dccdad;
    padding-bottom: 3mm;
  }
  @bottom-left {
    content: "SNAKE DIGEST";
    font-family: "Georgia", "Noto Serif CJK SC", serif;
    font-size: 7pt;
    color: #b9a98a;
    letter-spacing: 2pt;
  }
  @bottom-right {
    content: counter(page);
    font-family: "Georgia", "Noto Serif CJK SC", serif;
    font-size: 8pt;
    color: #b9a98a;
  }
}

@page :first {
  margin: 0;
  @top-center { content: none; }
  @bottom-left { content: none; }
  @bottom-right { content: none; }
}

* { box-sizing: border-box; }

html, body {
  margin: 0;
  padding: 0;
}

body {
  font-family: "Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", "SimSun", serif;
  font-size: 10.6pt;
  line-height: 1.92;
  color: #3d3428;
  background:
    radial-gradient(circle at 18% 12%, rgba(255,255,255,.50) 0, rgba(255,255,255,0) 32%),
    radial-gradient(circle at 82% 88%, rgba(210,185,135,.16) 0, rgba(210,185,135,0) 35%),
    linear-gradient(90deg, rgba(98,76,42,.025), rgba(255,255,255,0) 8%, rgba(98,76,42,.02) 100%),
    #f8f1e4;
  text-align: justify;
}

a { color: #7d5f2f; text-decoration: none; border-bottom: .3pt solid #d2be94; }

.cover {
  page-break-after: always;
  width: 210mm;
  height: 297mm;
  position: relative;
  overflow: hidden;
  background: #e9dcc4;
}
.cover.has-image {
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}
.cover.no-image {
  background:
    radial-gradient(circle at 50% 42%, rgba(255,255,255,.45), rgba(255,255,255,0) 40%),
    linear-gradient(135deg, #f5ebd8, #dfceb0);
}
.cover::after {
  content: "";
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 50% 30%, rgba(255,255,255,.08), rgba(0,0,0,0) 40%),
    linear-gradient(to bottom, rgba(25,19,13,.05), rgba(25,19,13,.35));
}
.cover-panel {
  position: absolute;
  z-index: 2;
  left: 19mm;
  right: 19mm;
  bottom: 22mm;
  padding: 13mm 12mm 11mm 12mm;
  background: rgba(45,34,23,.72);
  border: .45pt solid rgba(255,255,255,.28);
  border-radius: 2mm;
  color: #fff8ea;
}
.cover.no-image .cover-panel {
  background: rgba(255,250,239,.72);
  color: #382d21;
  border-color: rgba(113,87,49,.22);
}
.series {
  font-family: "Georgia", serif;
  font-size: 9pt;
  letter-spacing: 3.2pt;
  color: rgba(255,248,230,.78);
  margin-bottom: 5mm;
}
.cover.no-image .series { color: #9a805b; }
.cover h1 {
  margin: 0 0 5mm 0;
  padding: 0;
  border: 0;
  font-size: 29pt;
  line-height: 1.22;
  letter-spacing: .6pt;
  color: inherit;
  page-break-before: avoid;
}
.cover .subtitle {
  font-size: 12.2pt;
  color: rgba(255,248,230,.82);
  margin-bottom: 7mm;
}
.cover.no-image .subtitle { color: #6e5b40; }
.cover-meta {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 6mm;
  border-top: .4pt solid rgba(255,255,255,.24);
  padding-top: 5mm;
  font-size: 8.2pt;
  letter-spacing: .8pt;
  color: rgba(255,248,230,.72);
}
.cover.no-image .cover-meta { border-top-color: rgba(113,87,49,.22); color: #7d6848; }
.cover-qr img { width: 22mm; height: 22mm; border-radius: 1.8mm; border: .6pt solid rgba(255,255,255,.45); }
.cover-qr span { display: block; margin-top: 1mm; font-size: 6.8pt; text-align: center; }

.content-wrap {
  padding: 0;
}

h1 {
  page-break-before: always;
  margin: 8mm 0 8mm 0;
  padding-bottom: 4mm;
  border-bottom: .8pt solid #cdbb96;
  font-size: 19pt;
  line-height: 1.35;
  color: #382f24;
}

h2 {
  margin: 12mm 0 5.5mm 0;
  padding: 0 0 0 4mm;
  border-left: 3pt solid #bd9d64;
  font-size: 14pt;
  line-height: 1.45;
  color: #574632;
  page-break-after: avoid;
}

h2::after {
  content: "";
  display: block;
  width: 24mm;
  border-bottom: .35pt solid #d9c8a4;
  margin-top: 2.8mm;
}

h3 {
  margin: 8mm 0 3.5mm 0;
  font-size: 11.6pt;
  color: #69573e;
  page-break-after: avoid;
}

p { margin: 0 0 4mm 0; }
strong { color: #2d251d; font-weight: 700; }
em { color: #755f3d; }
blockquote {
  margin: 6mm 0;
  padding: 4mm 5mm;
  border-left: 3pt solid #d2b274;
  background: rgba(255,255,255,.38);
  color: #5b4a35;
  border-radius: 1.8mm;
}

ul, ol { margin-top: 2mm; margin-bottom: 5mm; padding-left: 7mm; }
li { margin-bottom: 1.5mm; }

table {
  width: 100%;
  border-collapse: collapse;
  margin: 7mm 0;
  font-size: 9.3pt;
  background: rgba(255,255,255,.38);
  border-radius: 2mm;
  overflow: hidden;
}
th { background: #e4d2ad; color: #473722; font-weight: 700; }
th, td { border: .45pt solid #d6c39e; padding: 2.8mm 3mm; vertical-align: top; }

code {
  font-family: "Consolas", "Menlo", monospace;
  background: rgba(120,90,40,.10);
  border-radius: 1mm;
  padding: .3mm 1mm;
  font-size: 9pt;
}
pre {
  background: rgba(63,48,31,.88);
  color: #fff6df;
  padding: 4mm;
  border-radius: 2mm;
  white-space: pre-wrap;
  font-size: 8.4pt;
  margin: 6mm 0;
}
pre code { background: transparent; color: inherit; padding: 0; }

.key-point, .info-card, .big-number, .analogy-box, .vs-box, .number-row, .timeline, .flow-steps, .article-img {
  page-break-inside: avoid;
}

.key-point {
  margin: 7mm 0;
  padding: 4.5mm 5mm;
  background: linear-gradient(135deg, #efe1bf, #f9f1df);
  border: .55pt solid #d2b77e;
  border-radius: 3mm;
}
.key-point .label, .info-label {
  display: inline-block;
  font-size: 8pt;
  letter-spacing: 1.2pt;
  color: #8a6b35;
  margin-right: 2mm;
  font-weight: 700;
}
.key-point .content { font-size: 11.2pt; font-weight: 700; color: #3d2d18; }

.big-number {
  margin: 8mm auto;
  padding: 7mm 5mm;
  text-align: center;
  border-top: .7pt solid #cdb27a;
  border-bottom: .7pt solid #cdb27a;
  background: rgba(255,255,255,.26);
}
.big-number .number { display: block; font-family: Georgia, serif; font-size: 34pt; line-height: 1; color: #8a5b20; }
.big-number .unit { font-size: 15pt; margin-left: 1mm; }
.big-number .desc { display: block; margin-top: 2.5mm; font-size: 9.5pt; color: #715c3d; letter-spacing: .6pt; }

.number-row { display: flex; gap: 3mm; margin: 7mm 0; }
.number-card { flex: 1; padding: 4mm 3mm; text-align: center; background: #f0dfbd; border: .5pt solid #d6be8c; border-radius: 2.2mm; }
.number-card .val { display:block; font-family: Georgia, serif; font-size: 18pt; color: #7d531e; font-weight: 700; }
.number-card .lbl { display:block; margin-top: 1.5mm; font-size: 8.2pt; color: #69553b; }

.analogy-box { display: flex; align-items: stretch; gap: 3mm; margin: 8mm 0; }
.analogy-box .daily, .analogy-box .pro { flex: 1; padding: 4mm; border-radius: 2.3mm; background: rgba(255,255,255,.42); border: .5pt solid #dcc79f; }
.analogy-box .pro { background: rgba(233,211,169,.42); }
.analogy-box .arrow { width: 8mm; text-align: center; align-self: center; font-size: 17pt; color: #a27b3e; }
.side-label { display:block; font-size: 7.6pt; color: #967443; letter-spacing: 1pt; margin-bottom: 2mm; font-weight: 700; }
.side-content { display:block; font-size: 9.5pt; line-height: 1.7; }

.vs-box { display: flex; gap: 4mm; margin: 7mm 0; }
.vs-card { flex: 1; padding: 4.5mm; border-radius: 2.4mm; border: .55pt solid #d6bd8a; background: rgba(255,255,255,.38); }
.vs-title { display:block; font-weight: 700; font-size: 11.4pt; color: #6f4c1d; margin-bottom: 2mm; }
.vs-content { font-size: 9.5pt; line-height: 1.75; }

.timeline { margin: 7mm 0; border-left: 2pt solid #c4a15d; padding-left: 4mm; }
.timeline .event { margin: 0 0 4mm 0; position: relative; }
.timeline .event::before { content: ""; position: absolute; left: -5.4mm; top: 2.5mm; width: 3mm; height: 3mm; border-radius: 50%; background: #9d7637; }
.timeline .year { display:inline-block; min-width: 16mm; font-family: Georgia, serif; color: #8a5b20; font-weight: 700; }
.timeline .what { color: #4b3c2a; }

.flow-steps { display: flex; align-items: stretch; gap: 2mm; margin: 7mm 0; }
.flow-steps .step { flex: 1; padding: 3.5mm 2.5mm; background: #efe0bf; border: .5pt solid #d2ba85; border-radius: 2mm; text-align: center; font-size: 8.7pt; line-height: 1.5; }
.step-num { display:block; font-size: 13pt; color: #8a5b20; margin-bottom: 1mm; }
.flow-arrow { align-self: center; color: #a27b3e; }

.info-card { margin: 6mm 0; padding: 4mm 4.5mm; background: rgba(255,255,255,.40); border: .5pt dashed #cdb27a; border-radius: 2.2mm; color: #5a4934; }
.caption, .article-img .caption { display:block; text-align:center; margin-top: 2mm; font-size: 8pt; color: #8a7a60; line-height: 1.5; }

.article-img { margin: 8mm auto; text-align: center; }
.article-img img { display:block; margin:0 auto; border-radius: 2.4mm; border: .6pt solid rgba(120,90,40,.18); box-shadow: 0 2mm 6mm rgba(65,45,20,.16); }
.article-img.layout-normal img { width: 92%; }
.article-img.layout-hero { margin: 10mm -5mm; }
.article-img.layout-hero img { width: 100%; }
.article-img.layout-small img { width: 66%; }
.img-missing { padding: 14mm; background: rgba(150,60,40,.08); border: .7pt dashed #b77; color: #9b4636; border-radius: 2mm; }

.sources-note { page-break-before: always; }
hr { border: 0; border-top: .5pt solid #d2c09a; margin: 8mm 0; }
'''


def read_file(path: str | os.PathLike) -> str:
    return Path(path).read_text(encoding='utf-8')


def file_to_data_uri(path: str | os.PathLike | None) -> str | None:
    if not path:
        return None
    p = Path(path)
    if not p.exists():
        return None
    ext = p.suffix.lower()
    mime = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp'}.get(ext, 'image/png')
    data = base64.b64encode(p.read_bytes()).decode('ascii')
    return f'data:{mime};base64,{data}'


def extract_title(md_text: str, fallback: str = 'Snake Digest') -> str:
    m = re.search(r'^#\s+(.+?)\s*$', md_text, flags=re.M)
    return m.group(1).strip() if m else fallback


def strip_first_h1(md_text: str, title: str) -> str:
    lines = md_text.splitlines()
    if lines and lines[0].startswith('# '):
        first = lines[0][2:].strip()
        if first == title:
            return '\n'.join(lines[1:]).lstrip()
    return md_text


def extract_meta(md_text: str) -> str:
    for line in md_text.splitlines()[:12]:
        clean = line.strip().lstrip('>').strip()
        if any(k in clean for k in ('主题分类', '领域', '类型', '版本日期', '日期')):
            return re.sub(r'\s{2,}', ' · ', clean)
    return str(date.today())


def md_body_to_html(md_text: str) -> str:
    return markdown.markdown(
        md_text,
        extensions=['extra', 'tables', 'fenced_code', 'attr_list', 'sane_lists'],
        output_format='html5',
    )


def build_cover(title: str, subtitle: str, author: str, meta_line: str, cover_image: str | None, qr_image: str | None) -> str:
    cover_uri = file_to_data_uri(cover_image)
    qr_uri = file_to_data_uri(qr_image)
    cls = 'has-image' if cover_uri else 'no-image'
    bg = f' style="background-image: url({cover_uri});"' if cover_uri else ''
    qr_html = ''
    if qr_uri:
        qr_html = f'<div class="cover-qr"><img src="{qr_uri}"/><span>扫码关注</span></div>'
    return f'''
<section class="cover {cls}"{bg}>
  <div class="cover-panel">
    <div class="series">SNAKE DIGEST</div>
    <h1>{html.escape(title)}</h1>
    <div class="subtitle">{html.escape(subtitle)}</div>
    <div class="cover-meta">
      <div>{html.escape(meta_line)}<br/>{html.escape(author)}</div>
      {qr_html}
    </div>
  </div>
</section>
'''


def md_to_html(md_text: str, title: str | None = None, subtitle: str = '一口气搞懂一件事', author: str = 'Snake', meta_line: str | None = None, qr_image: str | None = None, cover_image: str | None = None) -> str:
    actual_title = title or extract_title(md_text)
    actual_meta = meta_line or extract_meta(md_text)
    body_md = strip_first_h1(md_text, actual_title)
    body_html = md_body_to_html(body_md)
    css = CSS_TEMPLATE.replace('HEADER_TEXT', html.escape(f'SNAKE DIGEST · {actual_title}'))
    cover = build_cover(actual_title, subtitle, author, actual_meta, cover_image, qr_image)
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<title>{html.escape(actual_title)}</title>
<style>{css}</style>
</head>
<body>
{cover}
<main class="content-wrap">
{body_html}
</main>
</body>
</html>
'''


def main() -> None:
    parser = argparse.ArgumentParser(description='Snake Digest Codex Markdown to PDF')
    parser.add_argument('input', help='input markdown')
    parser.add_argument('output', help='output PDF')
    parser.add_argument('--title', default=None)
    parser.add_argument('--subtitle', default='一口气搞懂一件事')
    parser.add_argument('--author', default='Snake')
    parser.add_argument('--meta', default=None)
    parser.add_argument('--qr-image', default=None)
    parser.add_argument('--cover-image', default=None)
    parser.add_argument('--html-out', default=None, help='optional HTML output path')
    args = parser.parse_args()

    md_text = read_file(args.input)
    html_text = md_to_html(md_text, args.title, args.subtitle, args.author, args.meta, args.qr_image, args.cover_image)

    html_path = Path(args.html_out) if args.html_out else Path(args.output).with_suffix('.html')
    html_path.write_text(html_text, encoding='utf-8')
    print(f'[OK] HTML: {html_path}')

    from weasyprint import HTML
    HTML(string=html_text, base_url=str(Path(args.input).resolve().parent)).write_pdf(args.output)
    print(f'[OK] PDF: {args.output} ({Path(args.output).stat().st_size/1024:.1f} KB)')


if __name__ == '__main__':
    main()
