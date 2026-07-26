# 小红书自动发布助手 / Xiaohongshu Autopost

这是一个 Codex 技能：根据一个选题，协助制作并发布中文小红书图文笔记。

This is a Codex skill that helps turn a topic into a Chinese Xiaohongshu image-and-text post and publish it.

## 能做什么 / What it does

- 用第一人称写中文笔记，并保持自然、有观点、不营销的表达。
- 根据主题生成原创配图，并自动决定图片数量和封面风格。
- 自动补充少量相关话题，不添加地点。
- 在已登录的小红书账号中完成图文发布，并核验结果。
- 遇到政治、疑似违规或无法可靠判断的内容时停止发布并提醒用户。

- Writes Chinese posts in a natural first-person voice with a thoughtful, non-promotional tone.
- Generates original images and chooses an appropriate number of images and cover style.
- Adds a small set of relevant topics and leaves location blank.
- Publishes image-and-text posts through an already signed-in Xiaohongshu account and verifies the result.
- Stops and alerts the user for political, potentially non-compliant, or uncertain content.

## 使用方法 / Usage

在 Codex 中提供一个选题即可，例如：

Provide a topic in Codex, for example:

> 根据这个选题制作并发布一篇小红书图文笔记：我第一次授权 Codex 协助发布笔记

使用前，请在 Codex 浏览器中登录小红书。

Before use, sign in to Xiaohongshu in the Codex browser.

## 发布规则 / Publishing rules

- 常规内容通过审核后可以直接发布。
- 最终发布前需要用户确认。
- 如果小红书页面的发布按钮无法自动操作，用户可以手动点击发布；技能会继续核验发布结果。
- 不会绕过验证码、登录验证或平台限制。

- Regular content may be published after review.
- The user confirms immediately before final publication.
- If Xiaohongshu's publish button cannot be operated automatically, the user can click it manually; the skill then verifies the result.
- The skill never bypasses CAPTCHA, login verification, or platform restrictions.

## 目录结构 / Structure

- `SKILL.md`：技能规则和完整流程 / workflow and rules
- `agents/openai.yaml`：Codex 入口配置 / Codex entry configuration
