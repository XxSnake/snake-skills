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


## v3 low-color paper-unified

This version keeps the Image2-only rule and reduces large solid-color blocks in PDF layout. Use normal images by default; hero images should be rare.
