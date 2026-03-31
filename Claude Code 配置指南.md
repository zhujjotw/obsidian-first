# Claude Code 配置指南

> 最后更新：2026-03-31

## 目录结构概览

### 1. Skills 目录

Skills 是 Claude Code 的扩展功能，存储在以下位置：

| 类型 | 路径 | 作用域 |
|------|------|--------|
| 个人 skills | `~/.claude/skills/<skill-name>/SKILL.md` | 所有项目可用 |
| 项目 skills | `.claude/skills/<skill-name>/SKILL.md` | 仅当前项目 |
| 插件 skills | `<plugin-root>/skills/<skill-name>/SKILL.md` | 插件启用时可用 |

**当前路径**：`/root/.claude/skills/`

### 2. 插件目录

插件存储在：
- 缓存位置：`~/.claude/plugins/cache/`
- 数据位置：`~/.claude/plugins/data/`

## Superpowers 插件

**插件路径**：
```
~/.claude/plugins/cache/claude-plugins-official/superpowers/5.0.6/
```

### 可用的 Skills

| Skill 名称 | 用途 | 调用时机 |
|------------|------|----------|
| `brainstorming` | 探索用户意图、需求和设计 | 创造性工作前 |
| `dispatching-parallel-agents` | 并行处理多个独立任务 | 面对多个独立任务时 |
| `executing-plans` | 在单独会话中执行实现计划 | 有书面计划时 |
| `finishing-a-development-branch` | 决定如何集成工作 | 实现完成后 |
| `receiving-code-review` | 处理代码审查反馈 | 收到反馈时 |
| `requesting-code-review` | 请求代码审查 | 完成任务后 |
| `subagent-driven-development` | 在当前会话执行计划 | 执行有独立任务的计划 |
| `systematic-debugging` | 系统化调试 | 遇到 bug 时 |
| `test-driven-development` | TDD 开发 | 实现功能前 |
| `using-git-worktrees` | 创建隔离的 git worktrees | 开始需要隔离的功能工作时 |
| `using-superpowers` | skills 使用指南 | 任何会话开始时 |
| `verification-before-completion` | 验证工作完成 | 声称完成前 |
| `writing-plans` | 编写实现计划 | 有规范或多步骤任务时 |
| `writing-skills` | 创建或编辑 skills | 创建新 skills 时 |

## 当前系统配置

### 环境
- 工作目录：`/mnt/c/Users/zhujiajia`
- 平台：Linux (WSL)
- Git 仓库：是
- 当前分支：master

### 个人 Skills

当前安装的个人 skills：
1. **obsidian-knowledge** - 从 Obsidian 笔记库提取知识
2. **obsidian-sync-to-github** - 同步 Obsidian 到 GitHub

## 常用命令

### Skills 相关
- `/skills` - 查看所有可用的 skills
- `/<skill-name>` - 调用特定 skill

### Git 相关
- `git status` - 查看工作树状态
- `git diff` - 查看更改
- `git log` - 查看提交历史

### 配置文件
- `~/.claude.json` - Claude Code 主配置
- `~/.gitconfig` - Git 配置

## 技巧

1. **Skill 调用顺序**：先调用 process skills（如 brainstorming），再调用 implementation skills
2. **Skill 优先级**：Enterprise > Personal > Project
3. **每个 skill 是一个目录**：必须包含 `SKILL.md` 作为入口点
4. **目录名即命令名**：`my-skill/` → `/my-skill`

## 相关资源

- [Claude Code 官方文档](https://code.claude.com/docs)
- [Claude Code Skills 文档](https://code.claude.com/docs/en/skills.md)
- [Claude Directory 文档](https://code.claude.com/docs/en/claude-directory.md)
