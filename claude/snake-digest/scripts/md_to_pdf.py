#!/usr/bin/env python3
"""
Snake Digest 科普长文 Markdown → PDF 转换脚本 (WeasyPrint版)
用法: python md_to_pdf.py input.md output.pdf [--title "文章标题"] [--subtitle "一口气搞懂XXX"]

依赖: pip install weasyprint markdown --break-system-packages
"""

import sys
import os
import re
import argparse
import markdown

# ── CSS 样式 —— 杂志风格 + 可视化元素 ──
CSS_TEMPLATE = r"""
@page {
    size: A4;
    margin: 28mm 24mm 22mm 24mm;
    background: #faf6ee;

    @top-center {
        content: "HEADER_TEXT";
        font-family: "Droid Sans Fallback", "Georgia", serif;
        font-size: 7.5pt;
        color: #b8a88a;
        letter-spacing: 1.5pt;
        border-bottom: 0.3pt solid #d6c9a8;
        padding-bottom: 3mm;
    }

    @bottom-right {
        content: counter(page);
        font-family: "Droid Sans Fallback", "Georgia", serif;
        font-size: 8pt;
        color: #b8a88a;
    }

    @bottom-left {
        content: "@潇潇蛇";
        font-family: "Droid Sans Fallback", "Georgia", serif;
        font-size: 7pt;
        color: #c4b494;
        letter-spacing: 2pt;
    }
}

@page :first {
    margin: 0;
    @top-center { content: none; }
    @bottom-right { content: none; }
    @bottom-left { content: none; }
}

body {
    font-family: "Droid Sans Fallback", "Georgia", "Songti SC", serif;
    font-size: 10.5pt;
    line-height: 1.9;
    color: #3a3228;
    text-align: justify;
    background: #faf6ee;
    margin: 0;
}

/* ══════ 封面 ══════ */
.cover {
    page-break-after: always;
    position: relative;
    width: 210mm;
    height: 297mm; /* full A4 — 满版出血 */
    background: #faf6ee;
    overflow: hidden;
}
/* 有封面图时：全铺背景 */
.cover.has-image {
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}
/* 底部渐变遮罩：从透明到深色 */
.cover .overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 24mm 24mm 22mm 24mm;
    background: linear-gradient(to bottom, rgba(40,32,24,0), rgba(40,32,24,0.75) 35%, rgba(40,32,24,0.88));
    text-align: center;
}
/* 无封面图时居中布局 */
.cover.no-image {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
}
.cover.no-image .overlay {
    position: static;
    background: none;
    padding: 0;
}
/* 封面标题 - 有图时白色 */
.cover.has-image h1 {
    font-size: 28pt;
    color: #ffffff;
    margin-bottom: 4mm;
    font-weight: 700;
    letter-spacing: 2pt;
    border: none;
    page-break-before: avoid;
    line-height: 1.3;
    text-shadow: 0 1pt 3pt rgba(0,0,0,0.4);
}
.cover.has-image .subtitle {
    font-size: 12pt;
    color: rgba(255,255,255,0.85);
    margin-bottom: 6mm;
    font-style: italic;
    letter-spacing: 0.5pt;
}
.cover.has-image .brand {
    font-size: 12pt;
    color: rgba(255,255,255,0.9);
    letter-spacing: 3pt;
    margin-top: 5mm;
}
.cover.has-image .cover-qr img {
    border: 1.5pt solid rgba(255,255,255,0.5);
    border-radius: 2pt;
}
.cover.has-image .cover-qr .qr-hint {
    color: rgba(255,255,255,0.7);
}
/* 无封面图时保留原色 */
.cover.no-image h1 {
    font-size: 30pt;
    color: #3a3228;
    margin-bottom: 5mm;
    font-weight: 700;
    letter-spacing: 2pt;
    border: none;
    page-break-before: avoid;
    line-height: 1.3;
}
.cover.no-image .subtitle {
    font-size: 12pt;
    color: #8a7d6b;
    margin-bottom: 12mm;
    font-style: italic;
    letter-spacing: 0.5pt;
}
.cover.no-image .top-rule {
    width: 30%;
    margin: 0 auto 12mm auto;
    border: none;
    border-top: 0.8pt solid #8a7d6b;
}
.cover.no-image .divider-ornament {
    font-size: 14pt;
    color: #c4b494;
    margin: 8mm 0;
    letter-spacing: 6pt;
}
.cover.no-image .brand {
    font-size: 13pt;
    color: #8a7d6b;
    letter-spacing: 3pt;
    margin-top: 15mm;
}
.cover-qr {
    margin-top: 5mm;
    text-align: center;
}
.cover-qr img {
    width: 24mm;
    height: 24mm;
    border-radius: 2pt;
}
.cover-qr .qr-hint {
    display: block;
    font-size: 7.5pt;
    color: #b8a88a;
    margin-top: 1.5mm;
}

/* ══════ 一级标题 ══════ */
h1 {
    font-size: 18pt;
    color: #3a3228;
    margin-top: 14mm;
    margin-bottom: 8mm;
    padding-bottom: 4mm;
    border-bottom: 0.8pt solid #c4b494;
    page-break-before: always;
    font-weight: 700;
    letter-spacing: 1pt;
}

/* ══════ 二级标题 ══════ */
h2 {
    font-size: 13pt;
    color: #5c4e3c;
    margin-top: 10mm;
    margin-bottom: 5mm;
    font-weight: 700;
    padding-left: 4mm;
    border-left: 3pt solid #c4b494;
}

/* ══════ 三级标题 ══════ */
h3 {
    font-size: 11pt;
    color: #6b5d4a;
    margin-top: 7mm;
    margin-bottom: 3mm;
    font-weight: 700;
}

h4 {
    font-size: 10.5pt;
    color: #7a6c58;
    margin-top: 5mm;
    margin-bottom: 2mm;
    font-weight: 700;
    font-style: italic;
}

/* ══════ 段落 ══════ */
p {
    margin-top: 1.8mm;
    margin-bottom: 1.8mm;
    orphans: 3;
    widows: 3;
}

/* ══════ 引用块 ══════ */
blockquote {
    margin: 6mm 8mm;
    padding: 5mm 5mm 5mm 12mm;
    background: #f3ede0;
    border-left: 2.5pt solid #8a7d6b;
    color: #5c4e3c;
    font-size: 10pt;
    font-style: italic;
}
blockquote p {
    margin: 1mm 0;
    font-style: italic;
}

/* ══════ 粗体 ══════ */
strong, b {
    font-weight: 700;
    color: #2e2720;
}

/* ══════ 行内代码 ══════ */
code {
    font-family: "Courier New", Courier, monospace;
    background: #f0e8d8;
    color: #6b4c2a;
    padding: 0.5mm 2mm;
    border-radius: 2pt;
    font-size: 9.5pt;
}

/* ══════ 表格 ══════ */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 5mm 0;
    font-size: 9.5pt;
}
thead th {
    background: #5c4e3c;
    color: #faf6ee;
    padding: 3mm;
    text-align: left;
    font-weight: 700;
    letter-spacing: 0.5pt;
}
tbody td {
    padding: 2.5mm 3mm;
    border-bottom: 0.4pt solid #d6c9a8;
    color: #3a3228;
}
tbody tr:nth-child(even) {
    background: #f3ede0;
}

/* ══════ 分隔线 ══════ */
hr {
    border: none;
    text-align: center;
    margin: 6mm 0;
}
hr::after {
    content: "\00B7  \00B7  \00B7";
    color: #c4b494;
    font-size: 12pt;
    letter-spacing: 4pt;
}

/* ══════ 列表 ══════ */
ul, ol {
    margin: 2mm 0;
    padding-left: 8mm;
}
li {
    margin-bottom: 1.2mm;
}

/* ══════ 链接 ══════ */
a {
    color: #6b4c2a;
    text-decoration: none;
    border-bottom: 0.3pt dotted #b8a88a;
}


/* ╔═══════════════════════════════════════════╗
   ║         可视化组件样式                      ║
   ╚═══════════════════════════════════════════╝ */

/* ── 划重点框：一句话总结核心概念 ── */
.key-point {
    margin: 6mm 0;
    padding: 5mm 6mm;
    background: #f3ede0;
    border: 1pt solid #d6c9a8;
    border-radius: 3pt;
    text-align: center;
    page-break-inside: avoid;
}
.key-point .label {
    font-size: 7.5pt;
    color: #b8a88a;
    letter-spacing: 3pt;
    text-transform: uppercase;
    margin-bottom: 2mm;
    display: block;
}
.key-point .content {
    font-size: 11.5pt;
    color: #3a3228;
    font-weight: 700;
    line-height: 1.6;
}

/* ── 大数字：关键统计数据突出展示 ── */
.big-number {
    margin: 6mm auto;
    text-align: center;
    page-break-inside: avoid;
}
.big-number .number {
    font-size: 32pt;
    font-weight: 700;
    color: #5c4e3c;
    line-height: 1.1;
    display: block;
}
.big-number .unit {
    font-size: 14pt;
    color: #8a7d6b;
    font-weight: 400;
}
.big-number .desc {
    font-size: 9pt;
    color: #8a7d6b;
    margin-top: 1.5mm;
    display: block;
}

/* ── 数字卡片行：并排展示多个关键数字 ── */
.number-row {
    display: flex;
    justify-content: space-around;
    margin: 6mm 0;
    page-break-inside: avoid;
}
.number-row .number-card {
    text-align: center;
    flex: 1;
    padding: 4mm 3mm;
    border-right: 0.5pt solid #d6c9a8;
}
.number-row .number-card:last-child {
    border-right: none;
}
.number-row .val {
    font-size: 22pt;
    font-weight: 700;
    color: #5c4e3c;
    display: block;
    line-height: 1.2;
}
.number-row .lbl {
    font-size: 8.5pt;
    color: #8a7d6b;
    display: block;
    margin-top: 1mm;
}

/* ── 类比框：左边日常场景，右边专业概念 ── */
.analogy-box {
    margin: 6mm 0;
    display: flex;
    gap: 0;
    border: 1pt solid #d6c9a8;
    border-radius: 3pt;
    overflow: hidden;
    page-break-inside: avoid;
}
.analogy-box .daily {
    flex: 1;
    padding: 4mm 5mm;
    background: #f7f2e8;
}
.analogy-box .pro {
    flex: 1;
    padding: 4mm 5mm;
    background: #ede7d8;
}
.analogy-box .side-label {
    font-size: 7.5pt;
    color: #b8a88a;
    letter-spacing: 2pt;
    text-transform: uppercase;
    margin-bottom: 2mm;
    display: block;
    text-align: center;
}
.analogy-box .side-content {
    font-size: 9.5pt;
    color: #3a3228;
    line-height: 1.65;
    text-align: left;
}
.analogy-box .arrow {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 2mm;
    font-size: 16pt;
    color: #c4b494;
    background: #f0eadb;
}

/* ── 对比卡片：A vs B ── */
.vs-box {
    margin: 6mm 0;
    display: flex;
    gap: 0;
    page-break-inside: avoid;
}
.vs-box .vs-card {
    flex: 1;
    padding: 4mm 5mm;
    border: 1pt solid #d6c9a8;
}
.vs-box .vs-card:first-child {
    border-radius: 3pt 0 0 3pt;
    background: #f7f2e8;
    border-right: none;
}
.vs-box .vs-card:last-child {
    border-radius: 0 3pt 3pt 0;
    background: #ede7d8;
}
.vs-box .vs-title {
    font-size: 11pt;
    font-weight: 700;
    color: #5c4e3c;
    text-align: center;
    margin-bottom: 3mm;
    padding-bottom: 2mm;
    border-bottom: 0.5pt solid #d6c9a8;
    display: block;
}
.vs-box .vs-content {
    font-size: 9.5pt;
    color: #3a3228;
    line-height: 1.65;
}

/* ── 时间线 ── */
.timeline {
    margin: 6mm 0 6mm 6mm;
    padding-left: 8mm;
    border-left: 2pt solid #d6c9a8;
    page-break-inside: avoid;
}
.timeline .event {
    position: relative;
    margin-bottom: 4mm;
    padding-left: 4mm;
}
.timeline .event::before {
    content: "";
    position: absolute;
    left: -10.5mm;
    top: 2mm;
    width: 3mm;
    height: 3mm;
    background: #8a7d6b;
    border-radius: 50%;
}
.timeline .event .year {
    font-size: 9pt;
    font-weight: 700;
    color: #8a7d6b;
    display: block;
}
.timeline .event .what {
    font-size: 10pt;
    color: #3a3228;
    display: block;
    line-height: 1.5;
}

/* ── 流程图（横排步骤条） ── */
.flow-steps {
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 6mm 0;
    page-break-inside: avoid;
}
.flow-steps .step {
    text-align: center;
    flex: 1;
    padding: 3mm 2mm;
    background: #f3ede0;
    border: 1pt solid #d6c9a8;
    border-radius: 3pt;
    font-size: 9pt;
    color: #3a3228;
    line-height: 1.4;
}
.flow-steps .step .step-num {
    font-size: 14pt;
    font-weight: 700;
    color: #5c4e3c;
    display: block;
    margin-bottom: 1mm;
}
.flow-steps .flow-arrow {
    padding: 0 2mm;
    font-size: 14pt;
    color: #c4b494;
}

/* ── 知识卡片：小贴士/背景知识 ── */
.info-card {
    margin: 5mm 0;
    padding: 4mm 5mm 4mm 5mm;
    background: #f7f2e8;
    border: 0.5pt solid #d6c9a8;
    border-radius: 3pt;
    font-size: 9.5pt;
    color: #5c4e3c;
    line-height: 1.65;
    page-break-inside: avoid;
}
.info-card .info-label {
    font-size: 7.5pt;
    color: #b8a88a;
    letter-spacing: 2pt;
    text-transform: uppercase;
    margin-bottom: 2mm;
    display: block;
}

/* ── SVG容器：自定义图表/图形 ── */
.diagram {
    margin: 6mm auto;
    text-align: center;
    page-break-inside: avoid;
}
.diagram svg {
    max-width: 100%;
}
.diagram .caption {
    font-size: 8.5pt;
    color: #8a7d6b;
    font-style: italic;
    margin-top: 2mm;
    display: block;
}

/* ── 文章插图 ── */
.article-img {
    margin: 6mm 0;
    text-align: center;
    page-break-inside: avoid;
}
.article-img img {
    max-width: 92%;
    border-radius: 3pt;
    border: 0.5pt solid #d6c9a8;
}
.article-img .caption {
    font-size: 8.5pt;
    color: #8a7d6b;
    font-style: italic;
    margin-top: 2mm;
    display: block;
}
.article-img .img-placeholder {
    padding: 15mm 10mm;
    background: #f3ede0;
    border: 1pt dashed #c4b494;
    border-radius: 3pt;
    color: #b8a88a;
    font-style: italic;
    font-size: 10pt;
}
.article-img .img-missing {
    padding: 10mm 10mm;
    background: #f9f0e0;
    border: 1pt dashed #d4a574;
    border-radius: 3pt;
    color: #c4935a;
    font-style: italic;
    font-size: 9pt;
}
"""


def md_to_html(md_text, title="Snake Digest", subtitle="一口气搞懂",
               meta_line="", author="Snake", qr_data=None, qr_image=None,
               cover_image=None):
    """将 Markdown 转为带封面的 HTML"""

    html_body = markdown.markdown(
        md_text,
        extensions=['tables', 'fenced_code', 'nl2br', 'md_in_html'],
        output_format='html5'
    )

    # 移除正文中的第一个 h1（用在封面上）
    first_h1_match = re.search(r'<h1>(.*?)</h1>', html_body)
    if first_h1_match:
        extracted_title = first_h1_match.group(1)
        if not title or title == "Snake Digest":
            title = extracted_title
        html_body = html_body.replace(first_h1_match.group(0), '', 1)

    css = CSS_TEMPLATE.replace("HEADER_TEXT", title)

    # 生成/嵌入二维码
    qr_html = ""
    if qr_image:
        # 直接嵌入用户提供的二维码图片
        import base64 as b64mod
        ext = os.path.splitext(qr_image)[1].lower()
        mime_map = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp'}
        mime = mime_map.get(ext, 'image/jpeg')
        with open(qr_image, 'rb') as qf:
            qr_b64 = b64mod.b64encode(qf.read()).decode('utf-8')
        qr_html = f'<div class="cover-qr"><img src="data:{mime};base64,{qr_b64}" /><span class="qr-hint">微信扫码添加好友</span></div>'
    elif qr_data:
        try:
            import qrcode
            import io, base64
            qr = qrcode.QRCode(version=1, box_size=6, border=2,
                               error_correction=qrcode.constants.ERROR_CORRECT_M)
            qr.add_data(qr_data)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="#5c4e3c", back_color="#faf6ee")
            buf = io.BytesIO()
            qr_img.save(buf, format='PNG')
            qr_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            qr_html = f'<div class="cover-qr"><img src="data:image/png;base64,{qr_b64}" /><span class="qr-hint">扫码关注</span></div>'
        except ImportError:
            qr_html = ""

    # 封面图片
    cover_img_b64 = None
    if cover_image and os.path.isfile(cover_image):
        import base64 as b64mod2
        ext = os.path.splitext(cover_image)[1].lower()
        mime_map = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp'}
        mime = mime_map.get(ext, 'image/jpeg')
        with open(cover_image, 'rb') as cf:
            cover_img_b64 = f"data:{mime};base64,{b64mod2.b64encode(cf.read()).decode('utf-8')}"

    if cover_img_b64:
        cover_html = f"""
    <div class="cover has-image" style="background-image: url('{cover_img_b64}');">
        <div class="overlay">
            <h1>{title}</h1>
            <div class="subtitle">{subtitle}</div>
            <div class="brand">@潇潇蛇</div>
            {qr_html}
        </div>
    </div>
        """
    else:
        cover_html = f"""
    <div class="cover no-image">
        <div class="overlay">
            <hr class="top-rule">
            <h1>{title}</h1>
            <div class="subtitle">{subtitle}</div>
            {"<div class='author'>" + meta_line + "</div>" if meta_line else ""}
            <div class="divider-ornament">◆</div>
            <div class="brand">@潇潇蛇</div>
            {qr_html}
        </div>
    </div>
        """

    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <style>{css}</style>
</head>
<body>
{cover_html}
{html_body}
</body>
</html>"""

    return full_html


def main():
    parser = argparse.ArgumentParser(description="Snake Digest Markdown → PDF")
    parser.add_argument("input", help="输入的 Markdown 文件路径")
    parser.add_argument("output", help="输出的 PDF 文件路径")
    parser.add_argument("--title", default=None, help="文章标题")
    parser.add_argument("--subtitle", default="一口气搞懂", help="副标题")
    parser.add_argument("--author", default="Snake", help="作者名")
    parser.add_argument("--qr", default=None, help="封面二维码链接（如小红书主页URL）")
    parser.add_argument("--qr-image", default=None, help="封面二维码图片文件路径")
    parser.add_argument("--cover-image", default=None, help="封面主题图片文件路径")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        md_text = f.read()

    meta_line = ""
    for line in md_text.split("\n"):
        stripped = line.strip().lstrip(">").strip()
        if "领域" in stripped or "类型" in stripped or "日期" in stripped:
            meta_line = stripped
            break

    html = md_to_html(
        md_text,
        title=args.title or "Snake Digest",
        subtitle=args.subtitle,
        meta_line=meta_line,
        author=args.author,
        qr_data=args.qr,
        qr_image=args.qr_image,
        cover_image=args.cover_image
    )

    html_path = args.output.replace('.pdf', '.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"[OK] HTML 已生成: {html_path}")

    from weasyprint import HTML
    HTML(string=html).write_pdf(args.output)
    size_kb = os.path.getsize(args.output) / 1024
    print(f"[OK] PDF 已生成: {args.output} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
