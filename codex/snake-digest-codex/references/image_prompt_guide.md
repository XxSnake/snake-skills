# Snake Digest Codex 图片生成指南

## 统一风格

默认使用：

```text
warm-toned watercolor editorial illustration, muted low-saturation warm yellow, ivory, sepia and soft brown palette, subtle aged paper feeling, clean composition, subject clearly readable, soft golden lighting, no large saturated color blocks, no neon blue/green/red/purple areas, no text, no labels, no letters, no numbers in the image
```


## 配色约束：避免大面积异色

即使主题里有零食、商品包装、城市灯光，也必须把颜色压进同一套纸感调色盘：

- 主色：米白、旧纸黄、浅赭、棕褐、柔和金色。
- 可出现少量商品色，但必须低饱和、被水彩纸感稀释。
- 避免大面积纯蓝、纯绿、正红、紫色、霓虹色、高饱和包装墙。
- 不要让图片像电商海报、货架广告、PPT 插画。
- 正文图默认使用 `normal` 布局；`hero` 只用于开篇或重大转折，一篇最多 1 张。

推荐在每个 prompt 末尾追加：

```text
muted palette, low saturation, colors harmonized with aged ivory paper, no large saturated color blocks, no neon colors, no commercial poster look
```

## 默认尺寸

- 封面：2160x3840，竖版 9:16
- 正文：3840x2160，横版 16:9
- 如果当前内置图片工具不支持 4K，可改用封面 1024x1536、正文 1536x1024。
- 只允许降低尺寸，不允许用 SVG、程序绘图、占位图或二维码代替。

## Prompt 类型

### 类比场景图

把一个专业概念转成日常场景。

示例：

```text
warm-toned watercolor editorial illustration, a small bubble tea shop owner shaking hands with a pearl supplier across a wooden counter, both looking relieved because they agreed on a future price, cozy shop interior, soft golden lighting, no text, no labels, no letters, no numbers in the image
```

### 机制隐喻图

不要做带文字的流程图，用具象隐喻表现机制。

示例：

```text
warm-toned watercolor editorial illustration, a chain of simple scenes connected by flowing ribbons: a farmer in a wheat field, a trading hall silhouette, and a bakery storefront, showing risk moving through the supply chain, editorial composition, no text, no labels, no letters, no numbers in the image
```

### 历史故事图

强调时代、地点、情绪，但不要画真实人物肖像。

### 对比概念图

可以用左右分屏，但不要出现文字。比如左边盾牌挡雨，右边冲浪者乘浪。

## 硬性规则

1. 必须使用 ChatGPT 内置图像模型生图：遵循 `imagegen` 技能，并调用 Codex 内置 `image_gen` 工具。
2. 不要让图片承担文字说明功能。
3. 不要生成数据图表，数据图表用 HTML 组件。
4. 不要出现文字、标签、数字。
5. 不要画真实公众人物肖像。
6. 图片必须服务于理解，不是装饰。
7. 最终只接受 PNG、JPG、JPEG 或 WebP 位图。严禁生成或使用 SVG，也不得把 SVG 转成位图；同样不能用 Mermaid、HTML/CSS、Matplotlib、Pillow、Canvas、占位图、图标拼贴、二维码、截图或程序绘图替代模型生成的插画。
8. 每个不同画面单独调用一次内置工具。生成后先检查，再从 `$CODEX_HOME/generated_images/` 复制或移动到项目 `images/` 目录，并使用计划中的稳定文件名。
9. 不得静默切换到其他图像模型或需要 API 密钥的路线。ChatGPT 内置图像模型不可用时停止合成；只有用户明确同意时才按 `imagegen` 技能的备用流程继续。
