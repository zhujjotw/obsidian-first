# Claude Code GLM Coding Plan 集成指南

> 来源：[智谱AI开放文档](https://docs.bigmodel.cn/cn/coding-plan/tool/claude)
> 创建时间：2026-02-28
> 标签： #ClaudeCode #GLM #智谱AI #开发工具

---

## 概述

Claude Code 是一个智能编码工具，可以在终端中运行，通过自然语言命令交互帮助开发者快速完成代码生成、调试、重构等任务。

**核心特性：**
- 终端中的 AI 编程助手
- 自然语言交互
- 代码生成、调试、重构
- 集成 GLM Coding Plan

---

## 前提条件

- **Node.js**：18 或更新版本
- **MacOS 用户**：推荐使用 nvm 或 Homebrew 安装 Node.js（不推荐直接安装包，可能遇到权限问题）
- **Windows 用户**：还需安装 Git for Windows

---

## 步骤一：安装 Claude Code

### 方法 1：npm 安装（推荐）

进入命令行界面，执行：

```bash
npm install -g @anthropic-ai/claude-code
```

运行如下命令，查看安装结果，若显示版本号则表示安装成功：

```bash
claude --version
```

### 方法 2：Cursor 引导安装

若您不熟悉 Node.js 且有 Cursor，可以在 Cursor 中输入命令，Cursor 会引导你完成 Claude Code 的安装：

```
Help me install Claude Code
```

> 参考：https://docs.anthropic.com/zh-CN/docs/claude-code/overview

---

## 步骤二：配置 GLM Coding Plan

配置 GLM Coding Plan 以使用智谱 AI 的 GLM 模型。

---

## 步骤三：开始使用

配置完成后，进入一个您的代码工作目录，在终端中执行 `claude` 命令即可开始使用 Claude Code。

> 若遇到「Do you want to use this API key」选择 Yes 即可

启动后选择信任 Claude Code 访问文件夹里的文件。

![Claude Code 启动界面](https://cdn.bigmodel.cn/markdown/1753631613096claude-2.png?attname=claude-2.png)

---

## 常见问题

### 如何切换使用模型

1. 手动修改配置文件 `~/.claude/settings.json`，添加或替换如下环境变量参数：

```json
{
  "env": {
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "glm-4.5-air",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "glm-4.7",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "glm-4.7"
  }
}
```

> **注**：使用 GLM-5，需要将上方的环境变量参数值手动修改为 `"glm-5"`

2. 启动一个新的命令行窗口，运行 `claude` 启动 Claude Code，在 Claude Code 中输入 `/status` 确认模型状态：

![模型状态检查](https://cdn.bigmodel.cn/markdown/1759228558734cline-2.png?attname=cline-2.png)

### 视觉和搜索 MCP 服务器

参考以下文档配置 MCP 服务器：
- [[视觉MCP服务器]]
- [[搜索MCP服务器]]
- [[网页读取MCP服务器]]

配置完成后即可在 Claude Code 中使用。

### 手工修改配置不生效

若手动修改了 `~/.claude/settings.json` 配置文件，但发现配置没有生效，参考如下排查：

1. 关闭所有 Claude Code 窗口，重新打开一个新的命令行窗口，再次运行 `claude` 启动
2. 如果问题仍然存在，可以尝试删除 `~/.claude/settings.json` 文件，然后重新配置环境变量，Claude Code 会自动生成一个新的配置文件
3. 确认配置文件的 JSON 格式是否正确，检查变量名称和不能少逗号或多逗号，可以使用在线 JSON 校验工具进行检查

### 推荐的 Claude Code 版本

建议使用最新版本的 Claude Code，您可以通过以下命令检查当前版本和升级：

> 我们在 Claude Code 2.1.42 等版本验证 OK。

```bash
# 检查当前版本
claude --version
# 输出: 2.1.42 (Claude Code)

# 升级到最新版本
claude update
```

---

## 相关链接

- [[Claude Code]] - Claude Code 主文档
- [[GLM Coding Plan]] - 智谱 AI Coding Plan
- [[Claudian]] - Obsidian 中的 Claudian 插件

---

**标签**：#开发工具 #AI #ClaudeCode #智谱AI #GLM
