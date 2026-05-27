# Snake Digest Codex Image2 Prompt 指南

## 统一风格

默认使用：

```text
warm-toned watercolor editorial illustration, warm yellow, ivory, sepia and soft brown palette, subtle aged paper feeling, clean composition, subject clearly readable, soft golden lighting, no text, no labels, no letters, no numbers in the image
```

## 默认尺寸

- 封面：2160x3840，竖版 9:16
- 正文：3840x2160，横版 16:9
- 如果当前 Image2 环境不支持 4K，可改用封面 1024x1536、正文 1536x1024。
- 只允许降级尺寸，不允许降级为 SVG、程序绘图、占位图或 API 路线。

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

1. 必须调用 Codex 原生 Image2 生图。
2. 不要让图片承担文字说明功能。
3. 不要生成数据图表，数据图表用 HTML 组件。
4. 不要出现文字、标签、数字。
5. 不要画真实公众人物肖像。
6. 图片必须服务于理解，不是装饰。
7. 严禁用 SVG、Mermaid、HTML/CSS、Matplotlib、Pillow、Canvas、占位图、图标拼贴、截图或程序绘图替代 Image2。
8. 如果 Image2 无法生成或无法保存到 `images/`，停止任务并报告失败，不要继续合成 PDF。
