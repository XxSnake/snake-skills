# Snake Digest Codex 工作流清单

1. 建立 outputs/<slug>/ 工作目录。
2. 联网研究并写 sources.md。
3. 写 article.md。
4. 插入图片占位符。
5. 写 image_plan.json。
6. 必须使用 ChatGPT 内置图像模型：遵循 `imagegen` 技能并调用内置 `image_gen` 逐张生成；只保留 PNG、JPG、JPEG 或 WebP 位图，拒绝 SVG；检查后把选定图片放入项目 images/，使用计划中的文件名。
7. 运行 `validate_digest.py --strict`；缺图、重复图、方向错误、尺寸过小、计划不一致或来源笔记未完成时停止修复。
8. 运行 `merge_images.py --strict --engine auto` 生成 PDF；通用文件名会自动改成文章标题。
9. 运行 `verify_digest_pdf.py --render`，确认全部页面都成功转成图片。
10. 实际查看每一页；页脚左侧应显示 @潇潇蛇，不应显示 file:/// 路径。
11. 只把最终 PDF 作为主要交付物，其他文件在用户需要时提供。


禁止通过可见的浏览器打印界面手动另存；脚本的无界面浏览器引擎已经关闭默认页眉页脚。
