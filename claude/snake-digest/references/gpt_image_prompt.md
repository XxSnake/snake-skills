# Snake Digest 图片生成指令模板

> 本文件是给 Claude 写图片任务文件时参考的模板。Claude 在输出 `_图片任务.md` 时，应按照这个模板的格式来组织内容，让用户可以直接复制粘贴给 ChatGPT 使用。

## 输出格式

图片任务文件 `[主题名]_图片任务.md` 的结构如下：

```markdown
# 图片生成任务：[文章标题]

请按以下清单逐张生成图片。

## 统一风格要求

- 风格：暖色调水彩/淡彩插画风格（warm-toned watercolor editorial illustration）
- 色调：偏暖黄、米白、棕褐，与泛黄纸张的阅读背景协调
- 构图：简洁清晰，主体突出，不要有文字/字母/数字出现在画面中
- 用途：嵌入PDF科普长文，配合正文辅助理解概念
- 比例：横版 16:9

## 图片清单

### 第1张：img_01.png

**插入位置**：「[章节名]」章节，[简述上下文]

**画面描述**：
[详细的画面描述，用中英双语写prompt。中文帮用户理解画的是什么，英文是给image-2用的实际prompt]

**英文Prompt**：
[完整的英文prompt，包含风格要求]

---

### 第2张：img_02.png

...（以此类推）
```

## Prompt写作规范

### 图片类型及对应prompt策略

**场景图**（把类比场景画出来）：
- 描述具体的人物、环境、动作
- 强调日常感和生活气息
- 示例："A warm watercolor illustration of a small bubble tea shop owner shaking hands with a supplier across a wooden counter, warm golden lighting, cozy atmosphere, no text"

**机制示意图**（解释流程或关系）：
- 用视觉隐喻而非抽象图表
- 示例："A warm-toned watercolor diagram showing three connected scenes: a farmer in a wheat field, an arrow pointing to a trading floor building, another arrow to a bakery, representing the futures market supply chain, no text no labels"

**历史场景图**（给故事配画面）：
- 描述时代感、地点特征、氛围
- 示例："A moody watercolor illustration of the London financial district in 1992, dark storm clouds over old stone buildings, traders rushing on the street, warm sepia tones, editorial style, no text"

**对比/概念图**（视觉化抽象概念）：
- 用具象物体隐喻抽象概念
- 示例："A split watercolor illustration: left side shows a shield protecting a small shop from rain (hedging), right side shows a surfer riding a big wave (speculation), warm tones, no text"

### 硬性规则

1. 每张prompt末尾都加 `no text, no labels, no letters, no numbers in the image`
2. 每张prompt开头都加风格锚定词 `warm-toned watercolor editorial illustration`
3. 中文描述和英文prompt都要写，中文让用户看懂画的是什么，英文给模型用
4. 文件名统一用 `img_01.png`、`img_02.png` 递增编号，封面图用 `img_cover.png`
5. 一篇文章通常 3-6 张正文图 + 1 张封面图
6. 正文图比例：横版 16:9；封面图比例：竖版 9:16（封面要铺满A4竖版页面）

### 不要生成的图片类型

- 纯装饰性的配图（跟理解无关的）
- 数据图表（这个用HTML组件做，不用图片）
- 包含文字/标签的图（image-2生成的文字通常是乱码）
- 真实人物肖像（涉及版权和隐私）
