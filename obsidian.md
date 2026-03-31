# Obsidian

## Skills
### 写入笔记（WSL）
- 目标路径：使用 WSL 路径 `/mnt/c/Users/zhujiajia/Documents/obsidian/first/`。
- 写入方式：在终端用 `cat <<'EOF' > file.md` 直接创建/覆盖。
- 校验方式：用 `rg --files <vault>` 确认文件存在。
- 适用场景：快速生成或更新 Markdown 笔记。

