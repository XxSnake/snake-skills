# Codex Skills

本目录下每个子目录是一个 [Codex](https://github.com/openai/codex) 可用的 skill。

## 目录约定

每个 skill 至少要有：

```
<skill-name>/
└── SKILL.md       # frontmatter 必须包含 name 和 description
```

可选：

```
<skill-name>/
├── SKILL.md
├── README.md      # 人类可读的介绍（中文/英文均可）
├── CHANGELOG.md   # 迭代记录
├── VERSION        # 单行版本号
├── references/    # 长引用资料（按需 load）
├── scripts/       # 该 skill 用到的脚本
├── assets/        # 静态资源
├── examples/      # 示例输出
└── agents/        # 该 skill 嵌套调用的 sub-agent 定义
```

## SKILL.md frontmatter 最小要求

```yaml
---
name: my-skill-name           # 与目录名一致
description: 一句话讲清楚这个 skill 做什么 + 什么时候触发
---
```

可选字段：`version`（语义化版本）、`metadata`（自定义结构）。

## 安装

见仓库根目录 [README](../README.md#安装到本地)。
