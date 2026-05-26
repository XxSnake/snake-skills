# Claude Code Skills

本目录用于存放 [Claude Code](https://claude.com/claude-code) 可用的 skills。

目前为空，后续添加的 skill 会按以下结构组织：

```
<skill-name>/
└── SKILL.md       # frontmatter 必须包含 name 和 description
```

Claude Code 的 skill 默认搜索路径是 `~/.claude/skills/`，本仓库的 `install.ps1` 会把这里的每个子目录软链接过去。

## 与 Codex skill 的差异

- Claude Code skill 由用户输入 `/<skill-name>` 显式触发，或被 agent 在判定 description 匹配时自动触发。
- Codex skill 的触发机制略有不同，且支持 `$skill-reference` 这种 skill 间互相调用的写法。
- 同一个能力同时给两边用时，建议各自维护一份 SKILL.md，共享底层 references 目录（用 symlink 或 git submodule）。
