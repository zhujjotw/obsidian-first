# Claude Code Skills 注册指南

## 问题排查过程

### 问题现象
```
/obsidian-knowledge
Error: Unknown skill: obsidian-knowledge
```

### 解决方案

#### 1. 正确的目录结构

**错误方式**：
```
.claude/skills/obsidian-knowledge.md          # 单文件，不会被识别
.claude/skills/obsidian-knowledge/skill.md    # 目录 + skill.md，不会被识别
```

**正确方式**：
```
.claude/skills/.agents/skills/obsidian-knowledge/SKILL.md
```

#### 2. SKILL.md 文件格式

必须以 YAML frontmatter 开头：

```markdown
---
name: obsidian-knowledge
description: |
  技能描述，支持多行
---

# 技能内容

...
```

#### 3. 权限配置

在 `.claude/settings.local.json` 中添加权限：

```json
{
  "permissions": {
    "allow": [
      "Skill(obsidian-knowledge)"
    ]
  }
}
```

#### 4. 重启 Session

**重要**：修改后必须重启 session 才能生效！

---

## 完整的 Skill 注册步骤

### Step 1: 创建 Skill 目录

```bash
mkdir -p /root/.claude/skills/.agents/skills/my-skill
```

### Step 2: 创建 SKILL.md

```markdown
---
name: my-skill
description: |
  我的自定义技能描述
---

# 技能内容

这里写技能的具体指令...
```

### Step 3: 添加权限

编辑 `/root/.claude/skills/.claude/settings.local.json`：

```json
{
  "permissions": {
    "allow": [
      "Skill(my-skill)"
    ]
  }
}
```

### Step 4: 重启 Session

退出并重新进入 Claude Code

### Step 5: 验证

```
/my-skill
```

---

## 目录结构总览

```
.claude/skills/
├── .agents/
│   └── skills/
│       ├── obsidian-knowledge/
│       │   └── SKILL.md
│       └── my-skill/
│           └── SKILL.md
├── .claude/
│   └── settings.local.json
├── gstack/              # 第三方技能库
└── obsidian-sync -> ... # 符号链接
```

---

## 注意事项

1. **SKILL.md 必须大写**
2. **frontmatter 的 `---` 分隔符必须存在**
3. **name 字段必须与目录名一致**
4. **修改后必须重启 session**
5. **权限配置是必须的**

---

## 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| Unknown skill | 目录结构不对 | 使用 `.agents/skills/<name>/SKILL.md` |
| Unknown skill | 没有配置权限 | 添加到 `settings.local.json` |
| Unknown skill | 没有重启 session | 重启 session |
| 技能不生效 | frontmatter 格式错误 | 检查 `---` 包裹的 YAML |
