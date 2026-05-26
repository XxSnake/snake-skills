#!/usr/bin/env python3
"""
Snake Digest 图片合成脚本
用法: python merge_images.py article.md image_folder/ output.pdf [--title "标题"] [--subtitle "副标题"]

功能：
1. 读取文章MD（含占位符 <!--IMG:img_01:图片说明--> ）
2. 从 image_folder/ 中查找对应的图片文件（img_01.png/jpg/webp）
3. 将图片以base64编码嵌入HTML
4. 调用 md_to_pdf 的排版逻辑生成最终PDF

依赖: pip install weasyprint markdown --break-system-packages
"""

import sys
import os
import re
import argparse
import base64
import glob

# 导入同目录下的 md_to_pdf 模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from md_to_pdf import md_to_html


def find_image(image_dir, img_id):
    """在目录中查找匹配的图片文件，支持多种格式"""
    for ext in ['png', 'jpg', 'jpeg', 'webp']:
        pattern = os.path.join(image_dir, f"{img_id}.{ext}")
        matches = glob.glob(pattern)
        if matches:
            return matches[0]
    # 也尝试不区分大小写
    for f in os.listdir(image_dir):
        name_no_ext = os.path.splitext(f)[0]
        if name_no_ext.lower() == img_id.lower():
            return os.path.join(image_dir, f)
    return None


def image_to_base64(filepath):
    """将图片文件转为base64 data URI"""
    ext = os.path.splitext(filepath)[1].lower()
    mime_map = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.webp': 'image/webp',
    }
    mime = mime_map.get(ext, 'image/png')
    with open(filepath, 'rb') as f:
        data = base64.b64encode(f.read()).decode('utf-8')
    return f"data:{mime};base64,{data}"


def merge_images_into_md(md_text, image_dir):
    """替换MD中的图片占位符为实际图片"""

    # 匹配占位符格式: <!--IMG:img_01:图片说明文字-->
    pattern = r'<!--IMG:(\w+):(.*?)-->'

    found = 0
    missing = []

    def replacer(match):
        nonlocal found
        img_id = match.group(1)
        caption = match.group(2).strip()

        filepath = find_image(image_dir, img_id)
        if filepath:
            found += 1
            data_uri = image_to_base64(filepath)
            return (
                f'<div class="article-img">'
                f'<img src="{data_uri}" />'
                f'<span class="caption">{caption}</span>'
                f'</div>'
            )
        else:
            missing.append(img_id)
            # 保留占位符文字，不会因为缺图而报错
            return (
                f'<div class="article-img">'
                f'<div class="img-missing">[ 图片缺失：{img_id} ]</div>'
                f'<span class="caption">{caption}</span>'
                f'</div>'
            )

    result = re.sub(pattern, replacer, md_text)

    print(f"[INFO] 找到 {found} 张图片")
    if missing:
        print(f"[WARN] 以下图片未找到: {', '.join(missing)}")

    return result


def main():
    parser = argparse.ArgumentParser(description="Snake Digest 图片合成 → PDF")
    parser.add_argument("input", help="文章 Markdown 文件路径")
    parser.add_argument("image_dir", help="图片文件夹路径")
    parser.add_argument("output", help="输出 PDF 文件路径")
    parser.add_argument("--title", default=None, help="文章标题")
    parser.add_argument("--subtitle", default="一口气搞懂", help="副标题")
    parser.add_argument("--author", default="Snake", help="作者名")
    parser.add_argument("--qr", default=None, help="封面二维码链接")
    parser.add_argument("--qr-image", default=None, help="封面二维码图片文件路径")
    parser.add_argument("--cover-image", default=None, help="封面主题图片文件路径")
    args = parser.parse_args()

    # 检查输入
    if not os.path.isfile(args.input):
        print(f"[ERROR] 找不到文件: {args.input}")
        sys.exit(1)
    if not os.path.isdir(args.image_dir):
        print(f"[ERROR] 找不到图片目录: {args.image_dir}")
        sys.exit(1)

    # 读取MD
    with open(args.input, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # 合成图片
    md_merged = merge_images_into_md(md_text, args.image_dir)

    # 提取元信息
    meta_line = ""
    for line in md_text.split("\n"):
        stripped = line.strip().lstrip(">").strip()
        if "领域" in stripped or "类型" in stripped or "日期" in stripped:
            meta_line = stripped
            break

    # 生成HTML
    html = md_to_html(
        md_merged,
        title=args.title or "Snake Digest",
        subtitle=args.subtitle,
        meta_line=meta_line,
        author=args.author,
        qr_data=args.qr,
        qr_image=args.qr_image,
        cover_image=args.cover_image
    )

    # 保存HTML
    html_path = args.output.replace('.pdf', '.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"[OK] HTML 已生成: {html_path}")

    # 生成PDF
    from weasyprint import HTML
    HTML(string=html).write_pdf(args.output)
    size_kb = os.path.getsize(args.output) / 1024
    print(f"[OK] PDF 已生成: {args.output} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
