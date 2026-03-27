# Onyx 项目分析

> [!info] 项目地址
> GitHub: [onyx-dot-app/onyx](https://github.com/onyx-dot-app/onyx)
> 官网: [onyx.app](https://www.onyx.app)
> 文档: [docs.onyx.app](https://docs.onyx.app)

## 项目概述

**Onyx** 是一个功能丰富的、可自托管的 AI Chat UI 平台，前身为 **Danswer**，后更名为 Onyx。它兼容所有主流 LLM（OpenAI、Anthropic、Gemini 等）和自托管模型（Ollama、vLLM 等），支持完全离线/气隙环境运行。

核心定位：**企业级 AI 知识检索 + 对话平台**，适合从个人用户到大型企业的各类团队。

## 社区数据

| 指标           | 数据                                              |
| ------------ | ----------------------------------------------- |
| GitHub Stars | ~18.4k                                          |
| Forks        | ~2.5k                                           |
| Watchers     | 112                                             |
| 最新版本         | v3.0.5                                          |
| 融资           | $10M 种子轮（Khosla Ventures + First Round Capital） |
| 许可证          | MIT（社区版）/ 企业版另计                                 |
| 孵化器          | Y Combinator W24                                |

## 技术栈

| 层级       | 技术                              |
| -------- | ------------------------------- |
| **后端**   | Python (FastAPI)                |
| **前端**   | React                           |
| **搜索引擎** | Vespa（高性能开源搜索引擎）                |
| **向量检索** | 混合搜索（Hybrid Search）+ 知识图谱       |
| **数据库**  | PostgreSQL（用户/元数据）、Vespa（文档索引）  |
| **部署**   | Docker / Kubernetes / Terraform |
| **云平台**  | 支持 AWS EKS、Azure VMs 等          |

## 核心功能

### 1. RAG（检索增强生成）
- 业界领先的**混合搜索 + 知识图谱**
- 支持数千万级别文档的索引和检索
- 自定义索引和检索策略
- 文档权限控制（镜像外部应用的用户访问权限）

### 2. Connectors（连接器）
- 支持超过 **40+** 数据源的连接器
- 包括：Google Drive、Slack、Confluence、Notion、Jira、GitHub、SharePoint、Web 爬取等
- 自动拉取知识、元数据和访问信息

### 3. Custom Agents（自定义智能体）
- 为 AI Agent 配置独立的指令、知识和动作
- 支持 MCP（Model Context Protocol）扩展能力
- Actions 系统：让 AI Agent 与外部系统交互

### 4. Web Search（网络搜索）
- 支持 Google PSE、Exa、Serper 搜索引擎
- 内置爬虫 + Firecrawl 集成
- **Deep Research**：多步骤智能体搜索，提供深度研究能力

### 5. Code Interpreter（代码解释器）
- 在线执行代码分析数据
- 渲染图表和创建文件

### 6. Image Generation（图片生成）
- 根据用户提示生成图片

### 7. 企业级安全
- SSO 支持（OIDC / SAML / OAuth2）
- RBAC 角色权限控制
- 凭证加密
- 多种用户角色（基础用户、策展人、管理员）

### 8. 协作功能
- 对话分享
- 反馈收集
- 用户管理
- 使用分析

## 架构概览

```
用户请求 → React 前端 → FastAPI 后端
                              ├── LLM 调用层（多模型适配）
                              ├── RAG 检索层（Vespa + 知识图谱）
                              ├── Connector 层（40+ 数据源）
                              ├── Agent 层（自定义智能体）
                              └── 存储（PostgreSQL + Vespa）
```

## 快速部署

```bash
curl -fsSL https://raw.githubusercontent.com/onyx-dot-app/onyx/main/deployment/docker_compose/install.sh > install.sh && chmod +x install.sh && ./install.sh
```

## 适用场景

| 场景      | 说明                                              |
| ------- | ----------------------------------------------- |
| 企业内部知识库 | 连接 Confluence/Notion/SharePoint，让员工通过 AI 查询公司知识 |
| 客服支持系统  | 基于 FAQ + 文档构建智能客服                               |
| 研发团队助手  | 连接 Jira/GitHub，辅助代码审查和问题追踪                      |
| 合规与法务   | 大规模文档检索与分析                                      |
| 个人知识管理  | 自托管私有 AI 助手，保护数据隐私                              |

## 版本对比

| | 社区版 (CE) | 企业版 (EE) |
|--|------------|------------|
| 许可证 | MIT | 商业许可 |
| 核心功能 | 完整 | 完整 + 企业增强 |
| 适用规模 | 小团队 | 大型组织 |
| 价格 | 免费 | 付费 |

## 优势与局限

### 优势
- 开源且 MIT 协议，可自由部署和修改
- 功能全面（RAG + Agent + 搜索 + 协作）
- 支持完全离线/气隙环境
- 连接器生态丰富（40+）
- 活跃的社区和持续的更新维护
- 顶级 VC 支持，项目可持续性强

### 局限
- 企业版功能需要付费
- 自托管需要一定运维能力
- 大规模文档索引对硬件要求较高

## 相关链接

- [GitHub 仓库](https://github.com/onyx-dot-app/onyx)
- [官方文档](https://docs.onyx.app)
- [Discord 社区](https://discord.gg/TDJ59cGV2X)
- [Onyx Cloud（免费试用）](https://cloud.onyx.app/signup)
- [Roadmap](https://github.com/orgs/onyx-dot-app/projects/2)

---
*分析日期：2026-03-27*
