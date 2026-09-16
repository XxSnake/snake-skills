# 构建与验收

只在制作或修复 PDF 时读取本文件。`<skill-dir>` 指本技能目录；`<run>` 指本次任务的工作目录。使用可用的 Python，必要时通过 `load_workspace_dependencies` 定位运行时。下面使用单行命令，避免把 Bash 续行符直接用于 PowerShell。

准备 `article.md`、`sources.md`、`image_plan.json` 及 `images/`。正文按 [设计指南](pdf_design_guide.md) 放置图片标记；生成来源和视觉要求见 [图片指南](image_prompt_guide.md)。

```text
python <skill-dir>/scripts/validate_digest.py <run>/article.md <run>/image_plan.json <run>/images --strict
python <skill-dir>/scripts/merge_images.py <run>/article.md <run>/images <run>/final.pdf --title "标题" --subtitle "副标题" --author "@潇潇蛇" --qr-image <skill-dir>/references/wechat_qr.jpg --cover-image <run>/images/img_cover.png --page-size A4 --strict --engine auto
python <skill-dir>/scripts/verify_digest_pdf.py <run>/<文章标题>.pdf --page-size A4 --render --out-dir <run>/_pdf_renders
```

作者标记和二维码采用现有默认值；用户指定署名或要求不带二维码时，按请求调整参数。A5 小册在合成与验证命令中都改用 `--page-size A5`。不同视觉风格通过 `--css-file <run>/theme.css` 覆盖默认主题。合成脚本会把 `final.pdf` 改成文章标题，并生成同名 HTML；以脚本实际输出路径为准。

严格检查拦截缺图、重复图、方向或尺寸错误、正文与计划的图片布局不一致、来源记录缺少链接等问题。自定义风格在图片计划中设置 `style_profile: "custom"`；需要多张大图时同步设置 `max_body_hero`，不要跳过严格检查。自动引擎优先使用可用的 Edge/Chrome/Chromium 或 WeasyPrint；不要打开可见的打印对话框另存，以免加入默认网址页脚。

新建 PDF 查看每一页，确认版面、常规正文字重、中文、图片、页脚和来源页正常，没有 `file:///` 本地路径。已有完整验收证据的局部修改可使用 `--pages 1,3-4` 仅重渲染受影响页，并把新渲染保存到独立目录；影响分页时检查全部页面。检查通过后交付最终 PDF；失败则修复并复验受影响内容。
