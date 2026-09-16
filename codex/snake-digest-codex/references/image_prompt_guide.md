# Snake Digest Codex 图片生成指南

此文件描述默认纸感风格；用户指定其他风格时服从请求。`image_plan.json` 用 `style_profile` 区分 `warm-paper` 与自定义风格，用 `max_body_hero` 记录本册允许的大图数量，每张图可用 `orientation` 指定 `portrait`、`landscape`、`square` 或 `any`。严格检查验证这些显式选择，不把默认审美误当成用户不可覆盖的硬规则。

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

## 尺寸与封面安全区

- 封面：优先选择最接近最终页面比例的竖图；内置工具只支持固定比例时可用 1024x1536。
- 正文：3840x2160，横版 16:9
- 如果当前内置图片工具不支持 4K，可用正文 1536x1024。
- 只允许降低尺寸，不允许用 SVG、程序绘图、占位图或二维码代替。

封面使用 `background-size: cover`，可能裁去边缘。把关键主体放在中央约 80% 安全区；下部约 35% 保持安静，给标题面板留出空间。生成后必须按最终纸张比例查看裁切结果，不能只看原图。

同册插画除了共享色调，还应共享笔触、材质、细节密度和反复出现的主体设计。需要保持同一人物、场景或物件时，复用已选图作为生成参考；不要只靠重复一段风格词声称一致。

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
7. 最终插画只接受 PNG、JPG、JPEG 或 WebP 位图。严禁用 SVG、Mermaid、HTML/CSS、Matplotlib、Pillow、Canvas、占位图、图标拼贴、二维码或截图冒充生成式插画。准确图表和文字关系可按正文需要使用 HTML 组件，不受这条插画来源规则限制。
8. 每个不同画面单独调用一次内置工具。生成后先检查，再从工具实际返回路径复制到项目 `images/` 目录，使用计划中的稳定文件名；不要假定生成目录或提前删除原图。
9. 不得静默切换到其他图像模型或需要 API 密钥的路线。ChatGPT 内置图像模型不可用时停止合成；只有用户明确同意时才按 `imagegen` 技能的备用流程继续。
