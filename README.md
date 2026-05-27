# snake-skills

我个人在使用和维护的 AI agent skills，按运行时（runtime）分目录管理。

## 仓库结构

```
snake-skills/
├── codex/          # Codex (OpenAI) 用的 skills
├── claude/         # Claude Code 用的 skills
├── scripts/        # 安装与维护脚本
└── .github/        # CI 校验
```

每个 skill 是一个独立目录，内含 `SKILL.md`（必含 `name` / `description` frontmatter）以及该 skill 自己的资源（references、scripts、assets 等）。

## Skills

### Codex

| Skill | 说明 |
|---|---|
| [book-to-share-pdf](codex/book-to-share-pdf/) | 给一本书生成中文故事化拆书 PDF（泛黄纸张风格），用于读书分享/读书会。 |
| [snake-digest-codex](codex/snake-digest-codex/) | 一口气搞懂一件事：在 Codex 内完成研究、写作、Image2 配图、精美 PDF 排版与交付的完整闭环。snake-digest 的 Codex 版。 |
### Claude Code

| Skill | 说明 |
|---|---|
| [snake-digest](claude/snake-digest/) | 一口气搞懂一件事：把陌生概念/行业/技术写成叙事驱动的科普长文，最终导出排版精美的 PDF。灵感来自"小Lin说"。 |

## 安装到本地

仓库 clone 下来之后，运行 PowerShell 脚本，把每个 skill 软链接到 Codex / Claude Code 的默认搜索路径：

```powershell
# 需要管理员权限，或开启 Windows 开发者模式（让普通用户可以创建 symlink）
pwsh -File scripts/install.ps1
```

脚本会：

1. 检测 `~/.codex/skills/` 和 `~/.claude/skills/` 是否存在，缺则创建。
2. 把 `codex/<name>/` 和 `claude/<name>/` 用符号链接的方式映射进去。
3. 如果目标位置已经有同名目录且不是 symlink，会先备份为 `<name>.bak-<timestamp>`，再建链接。

之后在本仓库里改任何文件，agent 端立刻看到最新版本，不需要再同步。

## 迭代与版本

- 每个 skill 自己维护 `CHANGELOG.md`（如果需要）。
- 重大变更或对外发布版本时，在 SKILL.md frontmatter 里加 `version: x.y.z`。
- 主分支由 GitHub Actions 自动校验所有 SKILL.md 的 frontmatter，缺 `name` 或 `description` 的 PR 会被拒。

## 贡献 / 反馈

这是个人仓库。欢迎 issue 提建议，PR 仅在涉及明显修复（拼写、链接、明显 bug）时考虑接受。

## License

[MIT](LICENSE)
