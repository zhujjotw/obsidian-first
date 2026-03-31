# Claude Code Skills 注册机制

## 1. 发现机制

Claude Code 通过**目录扫描**自动发现 skills：

```
扫描优先级：
1. Enterprise scope (企业级)
2. ~/.claude/skills/          (个人全局)
3. .claude/skills/             (项目级)
4. <plugin>/skills/            (插件级，带命名空间)
```

### 嵌套发现

在 monorepo 中，编辑 `packages/frontend/src/app.tsx` 时会自动发现 `packages/frontend/.claude/skills/`

---

## 2. 可调用结构

### 最小结构

```
skill-name/
└── SKILL.md    # 必须大写，不是 skill.md
```

### SKILL.md 格式

```markdown
---
name: skill-name              # 可选，默认用目录名
description: 何时使用此技能   # 重要！Claude 靠此知道何时调用
---

技能指令内容...
```

### 可选 Frontmatter 字段

| 字段 | 作用 |
|------|------|
| `disable-model-invocation: true` | 只允许用户手动调用 |
| `user-invocable: false` | 只允许 Claude 调用（背景知识） |
| `allowed-tools: Read, Grep` | 限制工具访问 |
| `context: fork` | 在子 agent 中运行 |
| `agent: Explore` | 指定子 agent 类型 |
| `paths: "src/**/*.ts"` | 仅对匹配文件激活 |
| `argument-hint: "[filename]"` | 自动完成提示 |

---

## 3. Symlink vs 目录

| 类型 | 状态 |
|------|------|
| 目录 + SKILL.md | ✅ 完全支持 |
| Symlink | ⚠️ 官方未完全支持 (社区需求中) |

**注意**：`.claude/rules/` 明确支持 symlinks，但 skills 目录尚未正式支持。

---

## 4. Skill Tool 内部流程

```
1. 扫描 .claude/skills/
2. 注册为工具（名称 + 描述）
3. 用户调用时才加载完整内容
4. 参数替换：$ARGUMENTS, $1, ${CLAUDE_SKILL_DIR}
```

### 字符串替换

| 变量 | 含义 |
|------|------|
| `$ARGUMENTS` | 所有传入参数 |
| `$1`, `$2`, ... | 特定位置参数 |
| `${CLAUDE_SESSION_ID}` | 当前会话 ID |
| `${CLAUDE_SKILL_DIR}` | SKILL.md 所在目录 |

---

## 5. .agents/skills vs .claude/skills

| 目录 | 用途 |
|------|------|
| `.agents/skills/` | 跨平台标准 (Agent Skills Standard) |
| `.claude/skills/` | Claude Code 专用 |

### .agents/skills/

```
.agents/skills/
├── obsidian-knowledge/
│   └── SKILL.md
└── my-skill/
    └── SKILL.md
```

**目的**：
- 跨 agent 共享（Claude Code, Cursor, Aider, Codex CLI 等）
- 标准化位置，多个 AI 编码工具识别
- 可移植性

### .claude/skills/

```
.claude/skills/
├── my-skill/
│   └── SKILL.md
└── another-skill/
    └── SKILL.md
```

**目的**：
- Claude Code 专用
- 支持 monorepo 嵌套发现
- 集成 Claude Code 权限系统

---

## 6. 我的目录结构解析

```
~/.claude/skills/
├── gstack/                    # gstack 技能集目录
│   ├── ship                   # 可执行脚本
│   ├── review
│   └── ...
├── obsidian-knowledge/        # SKILL.md 格式
│   └── SKILL.md
├── .agents/skills/            # Agent 标准目录
│   └── obsidian-knowledge/
│       └── SKILL.md
└── obsidian-sync -> ...       # 符号链接
```

### 为什么 ship、review 可调用？

因为它们是 **gstack 的可执行脚本**，不是 SKILL.md 格式的 skill。

### 为什么 obsidian-sync-to-github.md 不可调用？

因为它只是文档，缺少：
1. 独立目录结构
2. SKILL.md 文件名
3. YAML frontmatter

### 如何让 obsidian-sync 成为可调用 skill？

```bash
mkdir ~/.claude/skills/obsidian-sync
mv obsidian-sync-to-github.md ~/.claude/skills/obsidian-sync/SKILL.md
```

然后添加 frontmatter：

```markdown
---
name: obsidian-sync
description: 同步 Obsidian 笔记到 GitHub
---

（原有内容）
```

---

## 7. 参考资料

- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills)
- [Agent Skills Open Standard](https://agentskills.io/home)
- [GitHub Issue: Symlinks support](https://github.com/anthropics/claude-code/issues/37590)
