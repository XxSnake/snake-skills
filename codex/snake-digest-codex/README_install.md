# snake-digest-codex 安装说明

建议放到：

```text
D:\repos\snake-skills\codex\snake-digest-codex\
```

安装依赖：

```bash
cd D:\repos\snake-skills\codex\snake-digest-codex
pip install -r requirements.txt
```

可选：软链接到 Codex skills。优先使用当前 Codex 文档推荐的用户级目录：

```powershell
New-Item -ItemType Directory -Force "$HOME\.agents\skills"
New-Item -ItemType SymbolicLink `
  -Path "$HOME\.agents\skills\snake-digest-codex" `
  -Target "D:\repos\snake-skills\codex\snake-digest-codex"
```

最推荐流程：让 Codex 读取 `SKILL.md`，按主题自动完成研究、写作、Image2 生图和 PDF 生成。

硬性要求：图片必须由 Codex 原生 Image2 生成并保存为本地图片。不得使用 SVG、Mermaid、程序绘图、占位图或 API 备用路线。


## v4 title-filename and footer fix

This version keeps the Image2-only rule, uses @潇潇蛇 as the PDF footer-left text, and automatically renames generic final/draft outputs to the article title.


注意：正式 PDF 请用 `scripts/merge_images.py` 或 `scripts/md_to_pdf.py` 生成。不要用浏览器打开 HTML 后打印成 PDF，否则可能出现 `file:///...` 页脚和白边。
