# Snake Digest Codex 工作流清单

1. 建立 outputs/<slug>/ 工作目录。
2. 联网研究并写 sources.md。
3. 写 article.md。
4. 插入图片占位符。
5. 写 image_plan.json。
6. 必须使用 Codex 原生 Image2 逐张生成图片并保存到 images/；不得使用 SVG、Mermaid、程序绘图、占位图或 API 备用路线。
7. 运行 validate_digest.py --strict；如发现缺图、SVG/占位图痕迹或图片文件不存在，停止修复。
8. 运行 merge_images.py 生成 final.pdf。
9. 检查 final.html 和 final.pdf。
10. 向用户交付路径与文件清单。
