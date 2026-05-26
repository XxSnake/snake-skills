# book-to-share-pdf

一个用于 Codex 的拆书 PDF Skill。

## 用途

当用户只提供一本书名，并要求“拆书、解构、读书分享、读书会分享、讲给别人听、写分享稿或生成 PDF”时，使用本 Skill。

它的目标不是机械总结，而是：

1. 先研究可靠资料；
2. 判断这本书适合怎么讲；
3. 做严肃拆解；
4. 转化成中文故事化分享稿；
5. 输出一份泛黄纸张风格的 PDF 小册。

## 安装位置

Codex 支持把 Skill 放在不同位置。常用方式：

```text
$HOME/.agents/skills/book-to-share-pdf/
```

或项目内：

```text
你的项目/.agents/skills/book-to-share-pdf/
```

官方文档说明：Skill 是一个包含 `SKILL.md` 的目录，可附带 `scripts/`、`references/`、`assets/`。

## 目录结构

```text
book-to-share-pdf/
├── SKILL.md
├── README.md
├── references/
│   ├── book_type_strategy.md
│   ├── research_rules.md
│   └── pdf_style_guide.md
├── assets/
│   ├── paper_texture.svg
│   └── style.css
├── scripts/
│   ├── build_booklet_pdf.py
│   └── verify_pdf.py
└── examples/
    └── sample_狂人日记.md
```

## 本地测试

```bash
cd book-to-share-pdf
python scripts/build_booklet_pdf.py examples/sample_狂人日记.md -o tests/sample_狂人日记.pdf
python scripts/verify_pdf.py tests/sample_狂人日记.pdf --render --out-dir tests/renders
```

## 依赖

PDF 生成脚本使用 Python + ReportLab。

```bash
pip install reportlab pypdf pypdfium2
```

注意：脚本不会打包字体文件。它使用 ReportLab 内置 CJK CID 字体生成中文 PDF，避免分发字体版权风险。

## 典型调用

```text
拆解《娱乐至死》，生成 PDF。
```

```text
用拆书技能拆《悉达多》，适合读书会分享。
```

```text
给我做一份《置身事内》的读书分享小册。
```
