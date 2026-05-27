---
name: snake-digest-codex
description: |
  Snake Digest Codex —— 一口气搞懂一件事，并在 Codex 内完成研究、写作、Image2 配图、精美 PDF 排版与最终交付。
  当用户想把一个复杂概念、行业、现象、技术、历史事件或商业问题，从零讲透，并输出一份可分享的图文 PDF 小册子时使用。
  触发词包括但不限于：帮我搞懂、一口气了解、讲透、做成PDF、生成图文PDF、snake-digest、snake-digest-codex、用小Lin方式讲讲、讲到我能听懂。
---

# Snake Digest Codex

版本：v3 · Image2-only · 低色块纸感统一版

> 核心目标：把一个复杂主题，从资料研究、叙事科普、Image2 配图到精美 PDF，完整产出成一份可分享的小册子。

本 Skill 是 `snake-digest` 的 Codex 版。它不再采用“Claude 写图像任务 → 用户去 ChatGPT 生图 → 再回传”的手工流程，而是默认在 Codex 里完成闭环：

```text
明确主题 → 联网研究 → 写科普长文 → 规划插图 → 调用 Image2 生图并落盘 → 合成精美 PDF → 交付最终文件夹
```

## 0. 工作边界与优先级

### 默认产物

每次完整执行后，输出一个主题文件夹：

```text
outputs/<slug>/
├─ article.md              # 最终文章 Markdown
├─ sources.md              # 资料来源与关键事实记录
├─ image_plan.json         # 图片规划与 prompt
├─ images/
│  ├─ img_cover.png
│  ├─ img_01.png
│  ├─ img_02.png
│  └─ ...
├─ final.html
└─ final.pdf
```

### 唯一生图路线：Codex 原生 Image2（硬性要求）

本 Skill 的配图**必须**通过 Codex 原生 Image2 / 图像生成能力完成。没有备用路线。

硬性规则：

1. 必须逐张调用 Image2 生成 `image_plan.json` 中的所有图片。
2. 每张图必须保存到 `outputs/<slug>/images/`。
3. 文件名必须严格匹配 `img_cover.png`、`img_01.png`、`img_02.png`……。
4. 生成结果必须是实际图片文件，优先 PNG。
5. 严禁用 SVG、HTML/CSS、Mermaid、Canvas、Matplotlib、Pillow 程序绘图、占位图、纯色块、图标拼贴、截图或任何“假装成图片”的替代物。
6. 严禁使用 OpenAI API、`OPENAI_API_KEY` 或任何 `generate_images_api.py` 式备用脚本。
7. 如果当前 Codex 环境不能调用 Image2、不能把 Image2 结果保存为本地图片，必须停止并向用户说明：`Image2 未成功调用，无法继续生成最终 PDF`。
8. 不允许在缺图、假图、SVG 图的情况下继续合成最终 PDF。

判断标准：最终 `images/` 目录里的封面图和正文图，必须是 Image2 生成的真实视觉插画，而不是程序生成的矢量示意图。


### PDF 视觉硬约束：低色块、纸感统一

本 Skill 的 PDF 目标不是“彩色信息图”，而是“泛黄纸张上的轻杂志小册子”。

硬性规则：

1. 组件背景必须克制，优先半透明纸色、细边框、留白，不要出现大面积实色块。
2. `key-point`、`number-row`、`flow-steps`、`vs-box`、`info-card` 只能作为点缀，不能连续堆满一页。
3. 正文不要出现大段代码块、JSON、命令行或图片计划；这些内容放进 `sources.md` 或附属文件，不进入最终 PDF 正文。
4. `hero` 图片只在开篇强钩子或重大转折处使用，默认正文图片用 `normal`；一篇文章最多 1 张正文 `hero` 图。
5. Image2 prompt 必须强调低饱和、暖黄、米白、棕褐、旧纸感；即使画面中有商品包装，也要把颜色压低，不要大面积蓝、绿、红、紫、霓虹色。
6. 如果某页视觉上出现大面积异色块，优先减少组件实色背景和 `hero` 图片面积，而不是改正文内容。

### 质量优先级

1. 准确性优先于故事性。
2. 理解性优先于专业堆砌。
3. PDF 视觉完成度优先于“普通 Markdown 转 PDF”。
4. 图片必须服务于理解，不能只是装饰。
5. 不确定信息必须标注，不许编造。

---

## 1. 环境准备

首次使用时，在 skill 目录或项目根目录执行：

```bash
pip install -r requirements.txt
```

如果 WeasyPrint 在 Windows 上报系统依赖错误，先不要乱改代码，优先检查 WeasyPrint 官方依赖、GTK/Pango/Cairo 环境，或改用 WSL2 执行。

建议目录：

```text
D:\repos\snake-skills\codex\snake-digest-codex\
```

可通过 symlink 安装到：

```text
~/.agents/skills/snake-digest-codex
```

---

## 2. 主题确认

用户给出主题后，如果已经足够明确，不追问，直接开始。例如：

```text
帮我一口气搞懂一瓶可乐卖2块3怎么还能赚钱
```

只在以下情况追问：

- 主题本身不完整，无法判断对象。
- 用户明确要求特定受众、篇幅、风格或用途，但信息缺失。
- 涉及高风险领域，需要确认边界，例如医疗、法律、投资建议。

默认假设读者是聪明但零基础的人。

---

## 3. 联网研究

必须联网搜索，不能只靠模型记忆。资料不够时继续补搜。

### 研究维度

按主题灵活选择：

- 基本定义和核心机制
- 起源故事
- 发展脉络
- 关键数据
- 经典案例
- 争议和批评
- 跟普通人的关系
- 最新状态或政策变化

### 资料质量排序

```text
官方 / 原始文件 > 权威机构 > 主流媒体 > 专业媒体 > 个人博客 / 聚合内容
```

### sources.md 要求

必须建立 `sources.md`，记录：

- 来源标题
- URL
- 发布/更新日期，如能查到
- 支撑了文章里的哪一个事实
- 可信度备注

不要把来源只堆到 PDF 最后。写作过程中要用它约束事实。

---

## 4. 叙事模型选择

从四种模型中选一个主模型，可以少量混用，但骨架要清楚。

### A. 时间线叙事

适合讲一个国家、公司、行业或事件的来龙去脉。

结构：

```text
钩子 → 起源 → 发展 → 转折 → 失控 / 高潮 → 现状 → 归因 → 未来
```

### B. 概念递进

适合讲一个概念、机制或技术。

结构：

```text
钩子 → 日常类比 → 正式概念 → 运作机制 → 真实案例 → 本质框架 → 跟我有什么关系
```

### C. 多角度扫描

适合讲宏观全景、多区域、多角色、多维度问题。

结构：

```text
全景判断 → 分区块讲清楚 → 区块之间的关联 → 关键变量 → 后续观察
```

### D. 问题链

适合回答“为什么”。

结构：

```text
现象 → 第一层为什么 → 第二层为什么 → 第三层为什么 → 根因 → 推演
```

---

## 5. 写作原则

### 零知识假设

读者不是笨，而是从没接触过这个领域。每个专业术语第一次出现时，必须先翻译再使用。

固定节奏：

```text
日常场景 → 白话解释 → 正式术语 → 回到真实世界验证
```

### 类比原则

优先使用日常场景：奶茶店、菜市场、租房、打游戏、网购、点外卖、排队、打麻将、存钱罐、小卖部、施工现场等。

不要用另一个同样复杂的专业领域做类比。

### 钩子开头

开篇 3-5 句话必须抓住读者。可以用：

- 震撼数据
- 荒谬反差
- 真实场景
- 直接追问

禁止：

```text
今天我们来聊聊……
在当今社会……
随着技术发展……
XX 是一个重要概念……
```

### 章节标题

标题要像朋友聊天时说的话，不要像论文目录。

推荐：

```text
所以钱到底去哪了？
转折来了
等等，还有更离谱的
那代价是什么？
说了这么多，跟我有什么关系？
```

禁止：

```text
第一章：概述
3.2 影响因素分析
小结
```

### 语言禁区

避免高频 AI 套话：

```text
首先、其次、最后、综上所述、值得注意的是、不难发现、众所周知、赋能、抓手、打造闭环、具有重要意义
```

谨慎使用并尽量减少：

```text
说白了、意味着什么、本质上、换句话说、不可否认
```

---

## 6. 可视化组件

PDF 支持以下 HTML 组件。写入 Markdown 即可被 `md_to_pdf.py` 渲染。

### key-point

```html
<div class="key-point">
  <span class="label">划重点</span>
  <span class="content">期货的本质是一份关于未来价格的约定。</span>
</div>
```

### big-number

```html
<div class="big-number">
  <span class="number">170<span class="unit">万%</span></span>
  <span class="desc">某一年极端通胀率</span>
</div>
```

### number-row

```html
<div class="number-row">
  <div class="number-card"><span class="val">260万</span><span class="lbl">高点</span></div>
  <div class="number-card"><span class="val">40万</span><span class="lbl">低点</span></div>
  <div class="number-card"><span class="val">-85%</span><span class="lbl">降幅</span></div>
</div>
```

### analogy-box

```html
<div class="analogy-box">
  <div class="daily"><span class="side-label">生活场景</span><span class="side-content">你提前跟房东锁定一年房租。</span></div>
  <div class="arrow">→</div>
  <div class="pro"><span class="side-label">专业概念</span><span class="side-content">这就是远期合约的雏形。</span></div>
</div>
```

### vs-box

```html
<div class="vs-box">
  <div class="vs-card"><span class="vs-title">A</span><span class="vs-content">解释 A。</span></div>
  <div class="vs-card"><span class="vs-title">B</span><span class="vs-content">解释 B。</span></div>
</div>
```

### timeline

```html
<div class="timeline">
  <div class="event"><span class="year">1848</span><span class="what">一个关键节点。</span></div>
  <div class="event"><span class="year">1972</span><span class="what">另一个关键节点。</span></div>
</div>
```

### flow-steps

```html
<div class="flow-steps">
  <div class="step"><span class="step-num">①</span>第一步</div>
  <span class="flow-arrow">→</span>
  <div class="step"><span class="step-num">②</span>第二步</div>
</div>
```

### info-card

```html
<div class="info-card">
  <span class="info-label">小知识</span>
  这里补充一个不打断主线的背景。
</div>
```

---

说明：本 Skill 不再提供 `diagram` / SVG 组件。凡是需要“图”的地方，必须进入第 7 节图片规划，并通过第 8 节的 Image2 工作流生成真实图片。

---

## 7. 图片规划

Codex 版默认必须配图，不再等用户二次触发。

### 图片数量

默认：

```text
1 张封面图 + 3-6 张正文图
```

短主题可用 3 张正文图，复杂主题用 5-6 张。不要为了凑数量生成装饰图。

### 图片类型

优先选择：

- 类比场景图
- 历史故事图
- 机制隐喻图
- 对比概念图
- 全景氛围封面图

不要生成：

- 数据图表，数据图表用 HTML 组件做
- 带文字、字母、数字、标签的图片
- 真实公众人物肖像
- 跟理解无关的装饰图
- SVG / 矢量示意图 / Mermaid 图 / 程序绘图 / 占位图

重要：如果某个位置需要图片，就必须在 `image_plan.json` 中登记，并用 Image2 生成真实图片文件。不能用 HTML 或 SVG 临时代替。

### 图片占位符格式

在 `article.md` 中插入：

```html
<!--IMG:img_01:图片说明文字:normal-->
<!--IMG:img_02:图片说明文字:hero-->
<!--IMG:img_03:图片说明文字:small-->
```

布局可选：

```text
normal：正文普通插图
hero：大幅重点插图
small：小图，适合轻提示
```

### image_plan.json 字段

必须生成 `image_plan.json`。结构参考 `templates/image_plan_template.json`。

每张图至少包含：

```json
{
  "id": "img_01",
  "filename": "img_01.png",
  "role": "body",
  "layout": "normal",
  "size": "3840x2160",
  "insert_after_heading": "章节标题",
  "caption": "图片说明",
  "prompt_zh": "中文画面说明",
  "prompt_en": "English prompt for Image2"
}
```

封面图：

```json
{
  "id": "img_cover",
  "filename": "img_cover.png",
  "role": "cover",
  "layout": "cover",
  "size": "2160x3840"
}
```

### Image2 Prompt 风格

默认风格：

```text
warm-toned watercolor editorial illustration, muted low-saturation warm yellow, ivory, sepia and soft brown palette, subtle aged paper feeling, clean composition, subject clearly readable, no large saturated color blocks, no neon blue/green/red/purple areas, no text, no labels, no letters, no numbers in the image
```

正文图默认横版 16:9，优先 4K：

```text
3840x2160
```

封面图默认竖版 9:16，优先 4K：

```text
2160x3840
```

如果生成失败、等待过久或当前 Codex 图像工具不支持 4K，则降级：

```text
正文图：1536x1024
封面图：1024x1536
```

---

## 8. Codex 原生 Image2 工作流（必须执行）

执行顺序：

1. 读取 `image_plan.json`。
2. 按顺序调用 Image2 生成 `img_cover`、`img_01`、`img_02`……。
3. 使用每项的 `prompt_en` 作为实际生图 prompt；必要时参考 `prompt_zh` 理解意图。
4. 每生成一张，立即保存到：

```text
outputs/<slug>/images/<filename>
```

5. 严格检查文件名，不得保存为随机名。
6. 不要让用户手动下载、手动上传。
7. 不得用 SVG、Mermaid、HTML/CSS、脚本绘图或占位图替代 Image2。
8. 不得调用 API 生图脚本，也不得要求用户提供 API Key。
9. 如果 Image2 调用失败，停止；不要生成最终 PDF。
10. 图片完成后运行：

```bash
python scripts/validate_digest.py outputs/<slug>/article.md outputs/<slug>/image_plan.json outputs/<slug>/images --strict
```

校验通过后再合成 PDF。

---

## 9. PDF 生成

有图最终 PDF：

```bash
python scripts/merge_images.py outputs/<slug>/article.md outputs/<slug>/images outputs/<slug>/final.pdf \
  --title "标题" \
  --subtitle "一口气搞懂XXX" \
  --author "Snake" \
  --qr-image references/wechat_qr.jpg \
  --cover-image outputs/<slug>/images/img_cover.png
```

无图调试 PDF：

```bash
python scripts/md_to_pdf.py outputs/<slug>/article.md outputs/<slug>/draft.pdf --title "标题" --subtitle "一口气搞懂XXX"
```

最终交付前必须同时存在：

```text
final.pdf
final.html
article.md
sources.md
image_plan.json
images/img_cover.png
```

---

## 10. PDF 设计要求

目标不是普通文档，而是“轻杂志 / 纸质读物 / 泛黄书页”的阅读体验。

必须做到：

- 封面满版，有主题图、标题、副标题、Snake Digest 标识
- 正文米白泛黄纸张感，不要纯白
- 章节标题有仪式感，但不能浮夸
- 每 2-3 个章节至少出现一个视觉组件或插图
- 图片说明要克制，像杂志 caption
- 页眉页脚要轻，不抢正文
- 最后一节必须有“资料来源与延伸阅读”或在 PDF 后附 sources

不要做到：

- 花里胡哨的模板感
- 图片过多挤压阅读
- 大面积黑底导致打印困难
- 用乱码文字图当信息图

更详细的排版原则见 `references/pdf_design_guide.md`。

---

## 11. 质检清单

交付前运行：

```bash
python scripts/validate_digest.py outputs/<slug>/article.md outputs/<slug>/image_plan.json outputs/<slug>/images --strict
```

必须确认：

- Markdown 有标题
- 所有 `<!--IMG:...-->` 占位符都有对应图片
- `image_plan.json` 中所有正文图都在文章中被引用
- 封面图存在
- 图片尺寸和角色基本匹配
- PDF 已生成
- sources.md 存在

发现问题，先修复，不要解释一堆然后交付半成品。

---

## 12. 交付方式

向用户汇报时，不要复制整篇文章到聊天里。只说明：

```text
已完成：final.pdf、article.md、sources.md、image_plan.json、images/
```

并给出本地路径。若用户要求，再展示摘要、目录或某一节内容。
