# 2026 年工具使用与计算机 Agent 版图

本页与英文原文逐段对应，保留标题层级、列表、表格、代码、公式、链接和面试问答。

AI Agent 与外部世界交互的方式发生了巨大变化。2024 年的“工具使用”通常是模型输出由后端执行的 JSON 函数调用；如今已经出现能够克隆仓库、运行 Shell 命令、通过截图控制桌面并在 WhatsApp 上发消息的完整自主 Agent，它们通过 MCP 等标准协议编排。本章梳理这些工具的版图、架构和区分它们的设计决策。

## 目录

- [生态概览](#ecosystem-overview)
- [类别分类](#category-taxonomy)
- [OpenClaw：走红的个人 AI Agent](#openclaw)
- [OpenHands：自主开发者 Agent](#openhands)
- [Open Interpreter：本地代码执行](#open-interpreter)
- [Claude Computer Use：基于视觉的自动化](#claude-computer-use)
- [Claude Code：终端 Agent](#claude-code)
- [IDE Agent：Cursor、Windsurf、Cline](#ide-agents)
- [对比矩阵](#comparison-matrix)
- [市场趋势与采用情况（2026）](#market-trends)
- [系统设计面试角度](#interview-angle)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## 生态概览

2026 年的工具使用生态已经围绕四类架构模式集中发展，每类模式分别针对不同程度的自主性、安全性和集成深度优化：

```
+-----------------------------------------------------------------------+
|                     2026 Tool-Use Ecosystem                           |
+-----------------------------------------------------------------------+
|                                                                       |
|  +-------------------+  +-------------------+  +-------------------+  |
|  |  LOCAL AGENTS     |  |  CLOUD AGENTS     |  |  IDE AGENTS       |  |
|  |                   |  |                   |  |                   |  |
|  |  OpenClaw         |  |  Claude Code      |  |  Cursor           |  |
|  |  Open Interpreter |  |  OpenAI Codex     |  |  Windsurf         |  |
|  |  OpenHands (local)|  |  OpenHands Cloud  |  |  Cline            |  |
|  |  LM Studio Agent  |  |  Google Jules     |  |  GitHub Copilot   |  |
|  +-------------------+  +-------------------+  +-------------------+  |
|                                                                       |
|  +-------------------+  +-------------------+  +-------------------+  |
|  |  COMPUTER-USE     |  |  MCP SERVERS      |  |  MESSAGING AGENTS |  |
|  |                   |  |                   |  |                   |  |
|  |  Claude Computer  |  |  10,000+ servers  |  |  OpenClaw (multi) |  |
|  |  Use API          |  |  97M monthly SDK  |  |  Custom bots      |  |
|  |  Open Interpreter |  |  downloads        |  |  via MCP bridges  |  |
|  |  (Computer API)   |  |                   |  |                   |  |
|  +-------------------+  +-------------------+  +-------------------+  |
+-----------------------------------------------------------------------+
```

2026 年的关键洞察是：这些类别正在融合。Claude Code 是在本地运行的云端 Agent；OpenClaw 是连接云端 LLM 的本地 Agent；Cursor 是带云端 Background Agent 的 IDE Agent。边界正在模糊，真正重要的是底层的**架构模式**（下一章会介绍）。

---

## 类别分类

### 1. 本地 Agent（自托管、用户控制）

运行在用户自有硬件上的 Agent。LLM 调用可以发往云端，但 Agent 进程、记忆和工具执行都在本地。

**关键属性：**
- 完整访问用户机器上的文件系统
- 记忆本地持久化（SQLite、JSON、Markdown）
- 用户拥有全部数据，不受供应商锁定
- 安全责任完全由操作员承担

**示例：**OpenClaw、Open Interpreter、本地部署的 OpenHands

### 2. 云端 Agent（供应商托管、API 驱动）

运行在供应商托管云环境中的 Agent。代码在 Sandbox VM 或容器中执行。

**关键属性：**
- Sandbox 执行（Docker、Firecracker VM、E2B）
- 无法访问本地文件系统（在克隆的仓库上工作）
- 供应商负责扩展、安全和基础设施
- 按使用量或订阅计费

**示例：**Claude Code（云模式）、OpenAI Codex、Google Jules、OpenHands Cloud

### 3. IDE Agent（编辑器集成、感知上下文）

直接嵌入代码编辑器的 Agent。它们深入理解项目结构、打开的文件和编辑器状态。

**关键属性：**
- 与编辑器 UI 紧密集成（行内 Diff、Tab 补全）
- 通过嵌入或 AST 解析建立代码库索引
- 在分支上异步工作的后台 Agent
- 针对开发者工作流优化，而非通用自动化

**示例：**Cursor（Agent Mode + Background Agent）、Windsurf（Cascade）、Cline、GitHub Copilot、Google Antigravity（以 Gemini 3 Agent 为核心、带多 Agent 管理视图的工作区，是 Gemini CLI 的后继者）

### 4. 计算机使用 Agent（基于视觉、驱动 GUI）

像人类一样通过查看截图和点击来操作软件的 Agent。

**关键属性：**
- 模型查看截图并决定鼠标/键盘动作
- 可操作任意应用（不需要 API）
- 延迟更高（每步截图—动作循环需要 1～3 秒）
- 为保证安全需要 Sandbox 环境（VM + VNC）

**示例：**Claude Computer Use API、Open Interpreter Computer API

---

## OpenClaw：走红的个人 AI Agent

### 它是什么

OpenClaw 是奥地利开发者 Peter Steinberger 创建的自托管开源个人 AI 助手。它最初于 2025 年 11 月以“Clawdbot”发布，2026 年 1 月改名为 OpenClaw。不到 5 个月 GitHub Star 从 0 增长到 34.6 万，并于 2026 年 3 月 3 日超过 React，成为 GitHub Star 数最多的软件项目。

**数据概览（2026 年 5 月）：**
- 超过 346,000 个 GitHub Star
- 320 万活跃用户
- 超过 500,000 个运行实例
- ClawHub 上超过 44,000 个社区 Skill
- 项目网站每月 3800 万访客
- 集成超过 24 个消息平台

### 工作方式

OpenClaw 的架构有六个核心组件：

```
+-------------------------------------------------------------------+
|                      OpenClaw Architecture                        |
+-------------------------------------------------------------------+
|                                                                   |
|  +-----------+     +-----------+     +----------+                 |
|  |  Gateway  |---->|  LLM      |---->| PI Agent |                 |
|  |           |     |  (Brain)  |     | (Exec)   |                 |
|  +-----------+     +-----------+     +----------+                 |
|       ^                  |                |                       |
|       |                  v                v                       |
|  +-----------+     +-----------+     +----------+                 |
|  | Channels  |     | SOUL.md   |     | Skills   |                 |
|  | (24+)     |     | (Identity)|     | (44K+)   |                 |
|  +-----------+     +-----------+     +----------+                 |
|                          |                                        |
|                          v                                        |
|                    +-----------+                                  |
|                    | Memories  |                                  |
|                    | (Persist) |                                  |
|                    +-----------+                                  |
+-------------------------------------------------------------------+
```

**1. Gateway**：消息进出层。连接 WhatsApp（通过 Baileys）、Telegram、Discord、Slack、Signal、iMessage、Microsoft Teams、Matrix 等 16 多个平台；支持私信和通过提及激活的群组对话。

**2. LLM（大脑）**：设计上与模型无关。支持 GPT-4o、Claude、Gemini、DeepSeek 或通过 Ollama 使用本地模型。用户选择模型，架构不关心具体供应商。

**3. PI Agent（Process Interactor）**：允许 LLM 在主机系统上创建、编辑、运行和删除文件的小型 Runtime。LLM 生成代码，PI Agent 保存并执行它，这就是 Agent 的“手”。

**4. SOUL.md（身份层）**：定义 Agent 个性、沟通风格、价值观和行为防护栏的普通 Markdown 文件。会话开始时加载并注入系统 Prompt。每个 Agent 实例先读取 SOUL.md，也就是“读出自己的存在”。

**5. Skill（插件系统）**：为 Agent 提供新能力的扩展。ClawHub 上有超过 44,000 个社区 Skill。Skill 遵循 AgentSkills 规范，可以打包、放在工作区本地或全局安装。

**6. Memories（持久上下文）**：本地存储的长期记忆。Agent 跨对话逐渐建立关于用户的上下文，与 SOUL.md 结合后，让每个 Agent 在所有消息平台上保持一致个性。

### 工作区文件

| 文件 | 用途 |
|------|---------|
| `SOUL.md` | Agent 个性、语气、价值观、防护栏 |
| `AGENTS.md` | 运维指令、工具配置 |
| `HEARTBEAT.md` | 定时自主动作（类似 Cron） |
| `Memories/` | 跨对话持久上下文 |

### 安全问题

OpenClaw 的快速增长超过了安全实践的成熟速度。截至 2026 年 5 月，超过 135,000 个实例暴露在公网，其中许多使用默认配置。ClawHub Skill 市场的安全监管很少：Skill 以 Markdown 为主、可选 TypeScript，创建和安装容易，也容易被滥用。这是任何将 OpenClaw 部署到生产环境的人都必须考虑的关键设计问题。

---

## OpenHands：自主开发者 Agent

### 它是什么

OpenHands（原名 OpenDevin）是开源自主 AI 软件工程师。它采用 MIT 许可证，可以修改代码、执行命令、浏览网页并与 API 交互。与只建议代码片段的工具不同，OpenHands 会克隆仓库、运行终端命令、执行测试，并在 Sandbox Docker 容器中调试错误。

### 架构：事件流 + Sandbox 运行时

```
+-------------------------------------------------------------------+
|                     OpenHands Architecture                        |
+-------------------------------------------------------------------+
|                                                                   |
|  +------------------+                                             |
|  |   User / API     |                                             |
|  +--------+---------+                                             |
|           |                                                       |
|           v                                                       |
|  +--------+---------+     +------------------+                    |
|  |  Agent Controller |<--->|  Event Stream    |                   |
|  |  (CodeAct 1.0)   |     |  Hub             |                   |
|  +--------+---------+     +--------+---------+                    |
|           |                        |                              |
|           v                        v                              |
|  +--------+---------+     +--------+---------+                    |
|  |  Action Dispatch  |     |  Observation     |                   |
|  |                   |     |  Collector       |                   |
|  |  - CmdRunAction   |     |                  |                   |
|  |  - FileWriteAction|     |  - CmdOutput     |                   |
|  |  - BrowseURLAction|     |  - FileContent   |                   |
|  |  - CodeAction     |     |  - BrowserState  |                   |
|  +--------+---------+     +------------------+                    |
|           |                                                       |
|           v                                                       |
|  +--------+--------------------------------------------------+    |
|  |              Docker Sandbox (Per Session)                 |    |
|  |                                                           |    |
|  |  +----------+  +----------+  +----------+                |    |
|  |  | Terminal  |  |  Python  |  | Browser  |                |    |
|  |  | (bash)   |  | (stateful)|  | (BrowserGym)             |    |
|  |  +----------+  +----------+  +----------+                |    |
|  +-----------------------------------------------------------+    |
+-------------------------------------------------------------------+
```

**关键架构决策：**
- **事件流架构**：所有 Agent—环境交互都以类型化事件流经中央 Hub。Agent 分析对话状态并产生 Action，Sandbox 产生 Observation。
- **每会话 Docker 容器**：每个会话拥有独立隔离、具备完整操作系统能力的容器，容器与主机隔离。
- **CodeAct 1.0**：默认 Agent 模板，将 LLM 推理嵌入统一编码控制平面，并维护会话级项目上下文。
- **BrowserGym 集成**：Agent 可通过声明式原语（DOM 操作、导航）执行浏览器自动化。
- **SDK 可组合**：OpenHands SDK 是 Python 库，可以用代码定义 Agent、本地运行，或在云端扩展到数千个。

**近期更新（v1.6.0，2026 年 3 月）：**
- 支持 Kubernetes 编排 Agent 会话
- 提供多步任务拆解的 Planning Mode Beta
- 188 名以上贡献者贡献超过 2100 次

---

## Open Interpreter：本地代码执行

### 它是什么

Open Interpreter 是一个提供 ChatGPT 式终端界面的本地代码执行 Agent。它不会只展示代码让你手动运行，而是请求许可后直接在你的机器上执行，并完整访问本地文件。

### 架构

```
+-------------------------------------------------------------------+
|                  Open Interpreter Architecture                    |
+-------------------------------------------------------------------+
|                                                                   |
|  +------------------+                                             |
|  |  Terminal UI      |                                            |
|  |  (ChatGPT-like)  |                                            |
|  +--------+---------+                                             |
|           |                                                       |
|           v                                                       |
|  +--------+---------+     +------------------+                    |
|  |  Core Engine      |<--->|  LLM Provider   |                   |
|  |                   |     |  (100+ models)  |                    |
|  |  - NL to Code     |     |  GPT, Claude,   |                   |
|  |  - Permission     |     |  Ollama, LM     |                   |
|  |    Gate            |     |  Studio, etc.   |                   |
|  +--------+---------+     +------------------+                    |
|           |                                                       |
|           v                                                       |
|  +--------+---------+                                             |
|  |  Code Executor    |                                            |
|  |                   |                                            |
|  |  - Python         |                                            |
|  |  - JavaScript     |                                            |
|  |  - Shell/Bash     |                                            |
|  |  - AppleScript    |                                            |
|  +--------+---------+                                             |
|           |                                                       |
|           v                                                       |
|  +--------+---------+                                             |
|  |  Computer API     |                                            |
|  |  (GUI Control)    |                                            |
|  |                   |                                            |
|  |  - Screen capture |                                            |
|  |  - Mouse/Keyboard |                                            |
|  |  - Icon detection |                                            |
|  +-------------------+                                            |
+-------------------------------------------------------------------+
```

**关键属性：**
- **模型灵活性**：支持 100 多个 LLM。要获得最大能力可使用 GPT-4o 或 Claude；重视隐私时也可通过 Ollama 和 LM Studio 完全离线运行。
- **权限闸门**：每次代码执行都需要用户批准（可信工作流可关闭）。
- **Computer API**：除代码执行外，Open Interpreter 还能查看屏幕、识别 UI 元素并控制鼠标键盘，使其从代码解释器升级为计算机自动化 Agent。
- **默认无 Sandbox**：直接运行在主机上。这是为最大能力做出的刻意选择，但意味着错误的 LLM 输出可能损坏系统；Docker Sandbox 是可选项。

### 何时使用 Open Interpreter

最适合需要通过对话界面操作本地机器的数据分析、文件处理和系统管理任务。不适合生产部署或不可信环境。

---

## Claude Computer Use：基于视觉的自动化

### 它是什么

Claude Computer Use 是 Anthropic API 的一项功能，允许 Claude 通过截图、鼠标移动、键盘输入和应用交互控制桌面。它于 2024 年 10 月以 Beta 形式推出，之后快速发展。截至 2026 年 5 月，Sonnet 4.6 在 OSWorld-Verified 上达到 72.5%，高于发布时的 14.9%；Opus 4.7 则在 Agent 编码基准上进一步提升（SWE-bench Pro 为 64.3%）。

### 视觉—动作循环

```
+-------------------------------------------------------------------+
|              Claude Computer Use: Vision-Action Loop               |
+-------------------------------------------------------------------+
|                                                                   |
|  Step 1: OBSERVE          Step 2: REASON          Step 3: ACT    |
|  +----------------+       +----------------+      +------------+ |
|  |  Take          |       |  Analyze       |      |  Execute   | |
|  |  Screenshot    |------>|  Screenshot    |----->|  Action    | |
|  |  (base64 PNG)  |       |  + Task Goal   |      |  (click,   | |
|  |                |       |  + History      |      |  type,     | |
|  +----------------+       +----------------+      |  scroll)   | |
|                                                    +------+-----+ |
|                                                           |       |
|          +------------------------------------------------+       |
|          |                                                        |
|          v                                                        |
|  +-------+--------+                                               |
|  |  Wait + Take   |                                               |
|  |  New Screenshot|-------> (Loop back to Step 1)                 |
|  +----------------+                                               |
|                                                                   |
+-------------------------------------------------------------------+
```

### 可用工具

| 工具 | 能力 | 说明 |
|------|------------|-------|
| `computer` | 鼠标、键盘、截图 | 完整桌面 GUI 控制 |
| `bash` | 运行 Shell 命令 | 跨轮次持久会话 |
| `text_editor` | 读取/写入/编辑文件 | 支持 view、create、str_replace |

### 2026 年增强

- **Zoom Action**：点击前以高分辨率检查小型 UI 元素，降低密集界面的误点击率。
- **可在 Claude Cowork 和 Claude Code 中使用**：面向 Pro 和 Max 用户的研究预览版，破坏性动作前必须人工确认。
- **Sandbox 最佳实践**：始终在 Sandbox VM（Docker + VNC 或 E2B 云环境）中运行，绝不让计算机使用 Agent 访问无 Sandbox 的主机。

### 性能趋势

| 日期 | OSWorld 分数 | 关键里程碑 |
|------|---------------|---------------|
| 2024 年 10 月 | 14.9% | Beta 发布（Claude 3.5 Sonnet） |
| 2025 年中 | 约 40% | Claude 3.7 改进 |
| 2026 年第一季度 | 72.5% | Sonnet 4.6、Zoom Action |

---

## Claude Code：终端 Agent

### 它是什么

Claude Code 是 Anthropic 驻留在终端中的 Agent 编码工具。它读取代码库、编辑文件、运行命令并集成开发工具。产品于 2025 年 5 月公开发布，截至 2026 年 2 月 ARR 超过 25 亿美元。

### 架构

Claude Code 是一个 TypeScript 终端 Agent，循环执行三个阶段：

```
+-------------------------------------------------------------------+
|                   Claude Code Agent Loop                          |
+-------------------------------------------------------------------+
|                                                                   |
|  +------------------+                                             |
|  |  1. GATHER       |  Read files, grep codebase, glob search,   |
|  |     CONTEXT      |  check git status, analyze structure        |
|  +--------+---------+                                             |
|           |                                                       |
|           v                                                       |
|  +--------+---------+                                             |
|  |  2. TAKE         |  Edit files, run bash, write new files,     |
|  |     ACTION       |  create commits, spawn subagents            |
|  +--------+---------+                                             |
|           |                                                       |
|           v                                                       |
|  +--------+---------+                                             |
|  |  3. VERIFY       |  Run tests, check build, review diffs,     |
|  |     RESULTS      |  validate output                            |
|  +--------+---------+                                             |
|           |                                                       |
|           +--------> (Loop back to Step 1 if not done)            |
|                                                                   |
+-------------------------------------------------------------------+

Built-in Tools: bash, read, write, edit, glob, grep, browser,
                subagent, notebook, web_search, web_fetch
```

**关键架构属性：**
- 一个拥有丰富工具集的 Agent 循环
- 通过斜杠命令和 CLAUDE.md 按需加载 Skill
- 为长会话提供上下文压缩（100 万以上 Token 上下文）
- 创建子 Agent 处理并行工作流
- 使用 Worktree 隔离并行分支执行
- 权限治理（工具允许/拒绝规则）
- 带依赖图的任务系统
- 用于自定义自动化的 Hooks（提交前后、文件变更）

---

## IDE Agent：Cursor、Windsurf、Cline

### Cursor

Cursor 是深度集成 AI 的 VS Code 分支。2.0 版本（2026 年初）引入：
- **Agent Mode**：使用 20 倍规模的强化学习进行多文件编辑
- **Background Agents**：在云 VM 中克隆仓库，自主工作，完成后打开 PR
- **Mission Control**：管理并行 Agent 工作流的仪表盘
- **市场表现**：年化收入 20 亿美元，超过 200 万用户、100 万付费客户，已被一半《财富》500 强采用

### Windsurf

Windsurf（原名 Codeium，2025 年 7 月被 Cognition 以 2.5 亿美元收购）提供：
- **Cascade**：分析项目结构、协调跨文件变更并从错误中自恢复的多步 AI Agent
- **专有模型**：SWE-1.5（比 Sonnet 4.5 快 13 倍）和 Fast Context
- **Codemaps**：AI 驱动的可视化代码导航
- **跨 IDE 插件**：支持 40 多个 IDE（JetBrains、Vim、NeoVim、XCode）

### Cline

Cline 是一个作为完整 Agent 工作而非自动补全工具的 VS Code 扩展。它分步执行、评估结果、修复自身错误并继续运行。它比 Cursor 或 Windsurf 更自主，但打磨程度较低。

### IDE Agent 架构比较

```
+-------------------------------------------------------------------+
|                 IDE Agent Architecture Patterns                   |
+-------------------------------------------------------------------+
|                                                                   |
|  Cursor:                                                          |
|  [Editor] --> [Agent Mode] --> [Multi-file RL] --> [Apply Diffs]  |
|                    |                                               |
|                    +--> [Background Agent] --> [Cloud VM] --> [PR] |
|                                                                   |
|  Windsurf:                                                        |
|  [Editor] --> [Cascade Agent] --> [RAG Codebase] --> [Apply Edits]|
|                    |                                               |
|                    +--> [SWE-1.5 Model] --> [Fast Context]        |
|                                                                   |
|  Cline:                                                           |
|  [Editor] --> [Agent Loop] --> [Evaluate] --> [Self-Fix] --> [Act]|
|                    |                                               |
|                    +--> [Any LLM Provider] --> [Tool Calls]       |
+-------------------------------------------------------------------+
```

---

## 对比矩阵

| 特性 | OpenClaw | OpenHands | Open Interpreter | Claude Computer Use | Claude Code | Cursor |
|---------|----------|-----------|-----------------|-------------------|-------------|--------|
| **类型** | 本地 Agent | 开发 Agent | 本地代码执行 | 视觉自动化 | 终端 Agent | IDE Agent |
| **许可证** | AGPL-3.0 | MIT | AGPL-3.0 | 专有 API | 专有 | 专有 |
| **GitHub Star** | 346K | 51K+ | 58K+ | 不适用（API） | 42K+ | 不适用 |
| **Sandbox** | 否（主机） | 是（Docker） | 否（主机） | 需要 VM | 可配置 | 是（Background Agent） |
| **LLM 支持** | 任意（与模型无关） | 任意 | 100+ 模型 | 仅 Claude | 仅 Claude | 多模型 |
| **GUI 控制** | 否 | 是（BrowserGym） | 是（Computer API） | 是（原生） | 通过计算机使用 | 否 |
| **代码执行** | 是（PI Agent） | 是（容器） | 是（本地） | 是（bash 工具） | 是（bash） | 是（终端） |
| **消息** | 24+ 平台 | Web UI / API | 终端 | API | 终端 / IDE | 编辑器 |
| **记忆** | 持久（本地） | 基于会话 | 基于会话 | 按对话 | 会话 + CLAUDE.md | 按项目 |
| **MCP 支持** | 社区 Skill | 有限 | 否 | 通过 Claude | 原生 | 正在增长 |
| **最适合** | 个人助手 | 自主开发 | 数据分析 | GUI 自动化 | 专业开发 | IDE 工作流 |
| **风险级别** | 高（无 Sandbox） | 低（Sandbox） | 高（无 Sandbox） | 中（需要 VM） | 中 | 低 |

---

## 市场趋势与采用情况（2026）

### 数据

- **MCP 生态**：超过 1 万个活跃 Server，SDK 月下载量 9700 万。
- **Gartner 预测**：到 2026 年底，40% 的企业应用会集成 AI Agent（2025 年初不足 5%）。
- **OpenClaw**：历史上达到 30 万 GitHub Star 最快的项目（不到 5 个月）。
- **Claude Code**：截至 2026 年 2 月 ARR 达 25 亿美元，是达到 10 亿美元最快的企业软件产品。
- **Cursor**：年化收入 20 亿美元，覆盖半数《财富》500 强企业。

### 关键趋势

**1. Agent 类型融合**：本地、云端和 IDE Agent 的边界正在消失。Claude Code 在本地运行但使用云模型，Cursor Background Agent 在云端运行，OpenClaw 可以连接任意 LLM。行业正走向能在任意环境运行的通用 Agent 架构。

**2. MCP 成为通用工具层**：MCP 已成为工具集成标准，被 Anthropic、OpenAI、Google 及数百家工具供应商采用。2026 年路线图聚焦企业能力：身份传递、工具预算、结构化错误语义和审计轨迹。

**3. Sandbox 不再可选**：OpenClaw 安全危机（13.5 万个实例暴露）推动行业转向默认 Sandbox 架构。新 Agent 应开箱即用地提供隔离。

**4. 成本优化成为一等关注点**：计划与执行模式（强模型负责计划，便宜模型负责执行）可降低 90% 成本，这是 Agent 领域对应云成本优化的模式。

**5. 后台与异步 Agent**：Cursor Background Agent 和 Claude Code 的子 Agent 创建，代表行业从同步交互式 Agent 转向完成后通知用户的自主异步工作者。

---

## 系统设计面试角度

在系统设计面试中被问到工具使用 Agent 时，重点讨论以下维度：

**1. 安全模型**：执行是否在 Sandbox 中？凭证如何管理？如果 LLM 生成恶意代码怎么办？（可比较 OpenClaw 的 AGPL 许可和非 Sandbox 执行与 OpenHands 的 Docker 隔离。）

**2. 状态管理**：Agent 如何在工具调用之间保持上下文？会话型（OpenHands）、持久记忆型（OpenClaw）还是基于文件（Claude Code 的 CLAUDE.md）？

**3. 工具发现**：静态清单（旧方式）、通过 MCP 动态发现，还是 Skill 市场（OpenClaw ClawHub）？

**4. 延迟预算**：函数调用每次 50～200ms，而基于视觉的自动化每次截图—动作循环需要 1～3 秒，这如何影响 UX？

**5. 故障处理**：工具调用失败怎么办？重试、回退还是转人工？放弃前允许多少次重试？

---

## 面试问题

### Q：团队要构建内部 AI 助手，应基于 OpenClaw、OpenHands，还是使用 Claude Code + MCP 自研？

**强回答：**
取决于用例和安全要求。OpenClaw 针对带消息集成的个人助手优化；如果目标是拥有持久人格的 Slack/Teams Bot，它很合适，但非 Sandbox 执行和 AGPL 许可会带来企业顾虑。OpenHands 更适合自主开发任务，其 Docker Sandbox 和 MIT 许可更友好。自定义内部工具需要最大控制力时，Claude Code 加 MCP Server 最合适：可以精确定义可用工具，在自有基础设施运行，并利用 MCP 的标准化发现与认证。决策树是：消息优先选 OpenClaw，开发自动化选 OpenHands，自定义企业工具选 MCP + 自有 Agent 循环。

### Q：如何设计一个让非技术用户用 AI 自动化桌面任务的系统？

**强回答：**
我会使用基于视觉的计算机使用模式（Claude Computer Use 或类似方案）。关键决策包括：(1) 始终运行在 Sandbox VM 中，避免 Agent 损坏用户真实机器；(2) 任何破坏性动作前都加入人在回路确认，如删除文件、提交表单、购买；(3) 使用 Zoom Action 模式减少密集 UI 中的误点击；(4) 设置 Token 和成本上限，防止无限循环；(5) 记录所有动作形成审计轨迹。主要权衡是延迟，每次截图—动作需要 1～3 秒，但它不需要 API 就能操作任意应用。对有 API 的应用，可结合计算机使用和函数调用提高速度。

### 问：为什么 OpenClaw 比历史上任何开源项目增长都快？这说明市场什么趋势？

**强回答：**
有三个因素。(1) **零摩擦入驻**：OpenClaw 连接人们已经使用的消息平台（WhatsApp、Telegram），用户不必学习新界面。(2) **SOUL.md 个性化**：赋予 Agent 自定义个性会产生情感连接和传播性，人们愿意分享自己的 Agent。(3) **与模型无关的架构**：用户不被锁定到单一 LLM 供应商，成本更低、灵活性更高。市场信号是，Agent 的“接口”比底层模型更重要；人们希望 Agent 在自己所在的地方出现（消息应用，而不是 Web UI）。反面教训是，快速增长却不投入安全会造成 13.5 万个实例暴露这样的危机，这是所有开源 Agent 项目的警示。

### 问：比较 AI Agent 的 Sandbox 执行与无 Sandbox 执行，分别何时选择？

**强回答：**
Sandbox（Docker/VM）：用于不可信代码执行、多租户系统或任何生产部署。OpenHands 做得很好，每个会话都有自己的 Docker 容器，代价是配置复杂度和性能开销。无 Sandbox（访问主机）：只用于用户正在观察的单用户可信环境。Open Interpreter 和 OpenClaw 为获得最大能力采用这种方式，风险是错误的 LLM 输出可能损坏主机。2026 年共识是默认使用 Sandbox，并为高级用户提供逃生口。面试中要强调，Sandbox 边界是安全决策，不只是便利性决策。

---

## 参考资料

- OpenClaw GitHub 仓库与文档（2025～2026）
- OpenHands 文档与 SDK 参考（2025～2026）
- Open Interpreter GitHub 仓库（2024～2026）
- Anthropic：《Computer Use Tool 文档》（2024～2026）
- Anthropic：《Claude Code 概览》（2025～2026）
- MCP 规范 2025-11-25 与 2026 路线图
- Gartner：《AI Agent 采用预测》（2025～2026）
- Cursor、Windsurf 和 Cline 官方文档（2025～2026）

---

*下一篇：[工具使用 Agent 的架构模式](02-architecture-patterns.md)*
