# OpenCoder：AI 编码 Agent 版图

AI 编码 Agent 版图正在爆发式增长。本指南覆盖开放权重编码模型、Agent 原生 IDE、开源 Agent，以及如何根据工程工作流选择合适的工具。

## 目录

- [AI 编码版图（2026）](#landscape)
- [开放权重编码模型](#models)
- [AI 原生 IDE](#ides)
- [开源编码 Agent](#agents)
- [基准测试深入理解](#benchmarks)
- [成本对比](#costs)
- [选择指南](#selection)
- [生产架构](#production)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## AI 编码版图（2026）

编码 AI 版图分为三个清晰的层：

```
┌─────────────────────────────────────────────────────────────┐
│                    AI CODING STACK (2026)                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  LAYER 3: CODING AGENTS (Autonomous, multi-turn)           │
│  ┌──────────────┐ ┌────────────┐ ┌────────────────────┐   │
│  │  Claude Code │ │  OpenHands │ │  Cline / Aider     │   │
│  │  (Anthropic) │ │  (Open)    │ │  (Open)            │   │
│  └──────────────┘ └────────────┘ └────────────────────┘   │
│                                                             │
│  LAYER 2: AI IDEs (Completion + editing, developer-in-loop)│
│  ┌──────────────┐ ┌────────────┐ ┌────────────────────┐   │
│  │    Cursor    │ │  Windsurf  │ │  GitHub Copilot    │   │
│  └──────────────┘ └────────────┘ └────────────────────┘   │
│                                                             │
│  LAYER 1: CODING MODELS (The brains behind everything)     │
│  ┌──────────────┐ ┌────────────┐ ┌────────────────────┐   │
│  │  Opus 4.7    │ │  GPT-5.5   │ │ DeepSeek V4 Pro    │   │
│  │  Sonnet 4.6  │ │ Gemini 3.1 │ │ Qwen 3.6 Coder     │   │
│  └──────────────┘ └────────────┘ └────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 开放权重编码模型

这些模型可以自托管、微调和部署，不依赖任何 API。

### Qwen2.5-Coder（阿里巴巴）

强大的开源编码模型家族。截至 2026 年 5 月，开源编码领先者是 Qwen 3.6 Coder 和 DeepSeek V4 Pro；Qwen 2.5 Coder 仍是小型硬件自托管部署的热门选择：

| 模型 | 参数量 | 上下文 | HumanEval+ | 备注 |
|-------|------------|---------|------------|-------|
| Qwen2.5-Coder-32B-Instruct | 32B | 128K | 88.2% | 最好的开源编码模型 |
| Qwen2.5-Coder-7B-Instruct | 7B | 128K | 79.3% | 出色的小模型 |
| Qwen2.5-Coder-1.5B | 1.5B | 32K | 65.8% | 边缘/端侧使用 |

**优势：**
- 编码基准表现强，与闭源前沿模型在 SWE-bench Verified 上具有竞争力
- 支持 100 多种编程语言
- 出色的中间填充（FIM）补全能力
- Apache 2.0 协议——完全可商用

```python
# Self-hosted with vLLM
from vllm import LLM

model = LLM(
    model="Qwen/Qwen2.5-Coder-32B-Instruct",
    tensor_parallel_size=2,  # 2× A100 80GB
)
response = model.generate("def fibonacci(n: int) -> list[int]:")
```

### DeepSeek-Coder-V2（DeepSeek）

| 模型 | 参数量 | 架构 | HumanEval+ |
|-------|------------|---------|------------|
| DeepSeek-Coder-V2-Instruct | 236B（MoE） | MoE | 90.2% |
| DeepSeek-Coder-V2-Lite | 16B（MoE） | MoE | 81.1% |

**优势：**
- MoE 架构 → 每个 Token 只激活 21B 参数，效率高
- 竞赛编程能力强（CodeForces 题目）
- 开放权重，中文支持强

### StarCoder2（BigCode / Hugging Face）

| 模型 | 参数量 | 上下文 | 备注 |
|-------|------------|---------|-------|
| StarCoder2-15B | 15B | 16K | 最好的中等规模开源编码 LM |
| StarCoder2-7B | 7B | 16K | 高效，支持 80 多种语言 |
| StarCoder2-3B | 3B | 16K | 轻量、端侧 |

**优势：**
- 完全开源（BigCode OpenRAIL 协议）
- 适合 IDE 补全（延迟低）
- 对 Stack Overflow/GitHub 数据表现强

### DeepSeek-R1-Distill（用于编码）

| 模型 | 参数量 | 数学/代码 | 备注 |
|-------|------------|---------|-------|
| DeepSeek-R1-Distill-Qwen-32B | 32B | 出色 | 将推理能力蒸馏到更小模型 |
| DeepSeek-R1-Distill-Llama-8B | 8B | 良好 | 极小的推理模型 |

**使用场景**：需要在自托管规模下获得具有推理质量的代码生成时。

### 开源模型选择指南

```
Simple completions (< 100ms latency needed)?
  → StarCoder2-3B or Qwen2.5-Coder-1.5B (local, fast)

Best quality self-hosted?
  → Qwen2.5-Coder-32B-Instruct (2× A100)

Budget < 1× A100 GPU?
  → Qwen2.5-Coder-7B-Instruct (1× RTX 4090 sufficient)

Need reasoning + coding?
  → DeepSeek-R1-Distill-Qwen-32B

Competitive programming / algorithmic?
  → DeepSeek-Coder-V2 or DeepSeek-R1
```

---

## AI 原生 IDE

### Cursor

**网站：** cursor.sh | **基础：** VS Code Fork | **价格：** Pro 每月 20 美元

Cursor 是领先的 AI 原生 IDE。主要能力：

| 特性 | 描述 |
|-------------|-------------|
| **Composer** | 多文件 Agent 式编辑（相当于 Cursor 版 Claude Code） |
| **Ctrl+K** | 行内代码生成 |
| **Tab** | 预测式补全（比 Copilot 更智能） |
| **@-mentions** | 把文件、URL、文档附加到上下文 |
| **.cursorrules** | 项目级 AI 指令（类似 CLAUDE.md） |
| **模型选择** | GPT-5.5、Claude Sonnet 4.6 / Opus 4.7、Gemini 3.1 Pro、DeepSeek V4 Pro |

**最适合**：希望在熟悉的 GUI 中进行 Agent 式编辑的前端/全栈开发者。

**限制**：闭源；代码会被发送到 Cursor 服务器（提供 Privacy Mode）。

### Windsurf（Codeium）

**网站：** codeium.com/windsurf | **基础：** VS Code Fork | **价格：** 免费层 + Pro 每月 15 美元

Windsurf 通过 **Flows**（不要与 CrewAI Flows 混淆）形成差异化：

| 特性 | 描述 |
|-------------|-------------|
| **Cascade** | Windsurf 的 Agent 式编辑模式 |
| **Flows** | 确定性的 Agent 序列（Agent 与用户协同） |
| **模型选择** | 任意：GPT-5.5、Claude Sonnet 4.6 / Opus 4.7、Gemini 3.1 Pro、DeepSeek V4 |
| **免费层** | 慷慨的免费额度 |

**最适合**：希望拥有类似 Cursor 的体验，同时需要免费层和模型灵活性的团队。

### GitHub Copilot（Microsoft/OpenAI）

| 特性 | 状态（2026 年 5 月） |
|---------|---------------------|
| 补全 | ✅ 仍按安装基数保持市场领先 |
| Copilot Workspace | ✅ 多文件 Agent 式编辑（已 GA） |
| 模型 | GPT-5.5（默认）、Claude Sonnet 4.6 / Opus 4.7（可用） |
| 企业能力 | ✅ IP 保护、组织策略、关闭代码引用 |

**最适合**：已经使用 Microsoft/GitHub 生态的企业团队。

**2026 年现实**：对大多数开发者而言，Copilot 的补全质量已经被 Cursor/Windsurf 超过，但企业能力和 GitHub 集成让它在大型组织中仍然占主导。

### Google Antigravity

Antigravity 是 Google 的 Agent 式开发平台，也是 Gemini CLI 的继任者。它与其说是文本编辑器，不如说是围绕 Gemini 3 构建的**Agent 优先工作区**：

| 特性 | 详情 |
|---------|--------|
| **Agent Manager** | 专门的视图，用于启动、观察和引导多个异步编码 Agent，而不是逐个编辑文件 |
| **规划 + 产物** | Agent 在执行前和执行中生成计划及可审查产物（diff、任务列表、实时浏览器会话） |
| **内置浏览器** | Agent 可以运行并用视觉方式测试所构建的 UI |
| **模型可选** | 默认使用 Gemini 3 Pro，也支持 Anthropic Claude 和开放模型 |
| **平台** | 跨平台（macOS、Windows、Linux）；公开预览，个人免费 |

**最适合**：希望在“任务”层工作（委托目标、审查计划和结果），而非在“编辑”层工作的开发者。它与 Cursor Composer 和 Claude Code Agent 循环竞争，Google 的下注点是多 Agent 管理器 UI 和紧密的 Gemini 3 集成。

---

## 开源编码 Agent

### OpenHands（前身为 OpenDevin）

**GitHub：** github.com/All-Hands-AI/OpenHands | **协议：** MIT

领先的开源自主编码 Agent：

```bash
# Run with Docker
docker pull docker.all-hands.dev/all-hands-ai/openhands:latest
docker run -it --rm \
  -e SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime:latest \
  -e LLM_API_KEY=$ANTHROPIC_API_KEY \
  -e LLM_MODEL=claude-3-7-sonnet-20250219 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -p 3000:3000 \
  docker.all-hands.dev/all-hands-ai/openhands:latest
# Access at http://localhost:3000
```

**架构：**
```
User request
    ↓
OpenHands Controller
    ├── CodeActAgent (main strategy)
    ├── Docker Sandbox (isolated execution)
    ├── File editor (str_replace_editor)
    └── Browser (playwright for web tasks)
```

**主要特性：**
- **任意 LLM**：支持 Claude Sonnet 4.6 / Opus 4.7、GPT-5.5、Gemini 3.1 Pro、DeepSeek V4、本地 Ollama
- **Docker 沙箱**：Agent 在隔离容器中运行
- **Web UI**：类似聊天的界面，显示 Agent 的推理
- **API 访问**：用于 CI 集成的 REST API
- **SWE-bench 分数**：约 55%～60%（取决于后端模型）

### Aider

**GitHub：** github.com/paul-gauthier/aider | **协议：** Apache 2.0

终端优先、Git 原生的编码 Agent：

```bash
pip install aider-chat

# Works directly with your git repo
aider --model claude-3-7-sonnet-20250219

# Add files to context
/add src/auth.py src/models.py

# Give task
> Add JWT authentication to the User model
```

**Aider 的差异化：**
- **Git 原生**：边工作边提交修改，保持干净的 Git 历史
- **上下文地图**：维护整个代码库的地图，即使文件不在上下文中也能掌握
- **语音模式**：用语音说出任务
- **架构模式**：修改代码前先讨论设计

```bash
# SWE-bench Verified benchmarks (May 2026)
# Aider + Claude Sonnet 4.6  → ~74%
# Aider + Claude Opus 4.7    → ~87%
# Aider + GPT-5.5            → ~88%
```

### Cline（VS Code 扩展）

**GitHub：** github.com/cline/cline | **协议：** Apache 2.0

自主编码的开源 VS Code 扩展：

```
VS Code
  └── Cline Extension
        ├── Any model (Claude, GPT, Gemini, Ollama)
        ├── File system access (read/write any file)
        ├── Terminal (bash commands)
        ├── Browser (playwright)
        └── MCP servers (any MCP tool)
```

**关键差异：**
- **MCP 原生**：开箱即用的完整 MCP 支持
- **逐动作权限**：每条 Shell 命令和文件编辑都需要用户批准
- **模型灵活性**：支持任意 OpenAI 兼容 API 端点（包括本地 Ollama）
- **免费**：开源，无订阅费

**最适合**：希望免费获得类似 Cursor 的体验，同时需要完整模型灵活性的开发者。

---

## 基准测试深入理解

### SWE-bench Verified（2026 年 3 月）

Agent 软件工程的黄金标准，衡量解决真实 GitHub Issue 的能力。

| Agent / 系统 | 分数 | 模型后端 | 备注 |
|---------------|-------|-------------|-------|
| GPT-5.5（单次领先者） | 88.7% | OpenAI | 在 SWE-Bench Verified 上排名第 1（2026 年 5 月） |
| Claude Opus 4.7（Anthropic） | 87.6% | Anthropic | 在 SWE-Bench Pro 上以 64.3% 领先 |
| Claude Code | 约 87% | Claude Opus 4.7 / Sonnet 4.6 | Anthropic 官方 Agent |
| OpenHands（最佳配置） | 约 75% | Claude Sonnet 4.6 | 开源 |
| Aider | 约 74% | Claude Sonnet 4.6 / Opus 4.7 / GPT-5.5 | 开源 CLI |
| SWE-agent | 约 55% | GPT-5.5 | Princeton 研究基线 |

> [!NOTE]
> SWE-bench 分数对后端模型高度敏感。同一个 Agent 使用 claude-3-7-sonnet 时，通常比使用 GPT-4o 高 10%～15%。

### HumanEval+（开源模型）

| 模型 | HumanEval+ 分数 |
|-------|-----------------|
| Claude 3.7 Sonnet | 93.6% |
| GPT-4o | 90.2% |
| Qwen2.5-Coder-32B-Instruct | 88.2% |
| DeepSeek-Coder-V2-Instruct | 90.2% |
| StarCoder2-15B | 73.3% |

### LiveCodeBench（运行时评估，更强信号）

LiveCodeBench 使用新的竞赛编程题（不在训练数据中）：

| 模型 | LiveCodeBench 分数 |
|-------|---------------------|
| o3（high） | 68.1% |
| Claude 3.7 Sonnet | 54.2% |
| GPT-4.5 | 38.7% |
| Qwen2.5-Coder-32B | 43.2% |
| DeepSeek-R1 | 57.0% |

**启示**：LiveCodeBench 分数比 HumanEval 低得多，因为它测试新问题。o3 和 DeepSeek-R1 凭借推理能力占优。

---

## 成本对比

### 闭源 API 与开放自托管

**场景：每天 1,000 个编码任务，平均每个 5K Token**

| 方式 | 月成本 | 质量 | 延迟 |
|----------|-------------|---------|---------|
| Claude 3.7 Sonnet（API） | 约 9,000 美元 | ★★★★★ | 中 |
| GPT-4o（API） | 约 7,500 美元 | ★★★★ | 中 |
| o3-mini（API） | 约 3,300 美元 | ★★★★★（推理） | 慢 |
| Qwen2.5-Coder-32B（4×A100） | 约 4,000 美元（基础设施） | ★★★★ | 快 |
| DeepSeek-V3（Together AI） | 约 1,350 美元 | ★★★★ | 中 |

**关键洞察**：相比 Claude API，Qwen2.5-Coder-32B 自托管在每天约 500 个以上任务时具有成本竞争力。每天少于 200 个任务时，计入工程开销后，API 几乎总是更便宜。

---

## 选择指南

### 快速决策树

```
What is your primary need?

├─ IDE coding assistance (completions + chat)?
│  ├─ Microsoft ecosystem / enterprise? → GitHub Copilot
│  ├─ Want best quality? → Cursor (Pro)
│  └─ Want free + model choice? → Windsurf or Cline
│
├─ Autonomous agent for standalone coding tasks?
│  ├─ Best quality, don't mind proprietary? → Claude Code
│  ├─ Need open-source? → OpenHands
│  ├─ CLI-first, git-native? → Aider
│  └─ VS Code embedded, MCP-native? → Cline
│
├─ Self-hosted model for custom deployment?
│  ├─ Best quality? → Qwen2.5-Coder-32B
│  ├─ Need reasoning? → DeepSeek-R1-Distill-32B
│  ├─ Fast completions? → Qwen2.5-Coder-7B or StarCoder2-7B
│  └─ Edge/on-device? → Qwen2.5-Coder-1.5B or StarCoder2-3B
│
└─ CI/CD pipeline integration?
   ├─ Best results? → Claude Code SDK (headless)
   ├─ Open-source? → OpenHands REST API
   └─ Git-native? → Aider CLI in GitHub Actions
```

### 对比矩阵

| 维度 | Claude Code | Cursor | OpenHands | Aider | Cline |
|-----------|-------------|--------|-----------|-------|-------|
| 自主性 | 完整 | 中 | 完整 | 完整 | 完整 |
| 模型锁定 | Claude | 任意 | 任意 | 任意 | 任意 |
| 开源 | ❌ | ❌ | ✅ | ✅ | ✅ |
| CI/无头 | ✅ | ❌ | ✅ | ✅ | ❌ |
| GUI | CLI | 完整 IDE | Web UI | 终端 | VS Code |
| MCP | ✅ | ✅ | 部分 | ❌ | ✅ |
| Git 原生 | 部分 | 部分 | ✅ | ✅ | 部分 |
| 价格 | API 成本 | 每月 20 美元 | 免费 + API | 免费 + API | 免费 + API |

---

## 生产架构

### 企业编码 Agent 平台

下面是构建内部 AI 编码平台的一种方式：

```
┌────────────────────────────────────────────────────────────┐
│             ENTERPRISE CODING AGENT PLATFORM                │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Developer                                                 │
│     ↓ (Jira ticket / PR description)                      │
│  ┌──────────────────────────────────┐                      │
│  │        TASK INTAKE LAYER         │                      │
│  │  • Parse task from Jira/GitHub   │                      │
│  │  • Classify: simple/complex      │                      │
│  │  • Route to appropriate agent    │                      │
│  └──────────────┬───────────────────┘                      │
│                 │                                          │
│    Simple fix   │   Complex feature                        │
│        ↓        │        ↓                                 │
│  ┌──────────┐   │  ┌──────────────────┐                    │
│  │  Aider   │   │  │   Claude Code    │                    │
│  │ (cheap)  │   └→ │  SDK (headless)  │                    │
│  └────┬─────┘      └────────┬─────────┘                    │
│       │                     │                              │
│       └─────────────────────┘                              │
│                 ↓                                          │
│  ┌──────────────────────────────────┐                      │
│  │         REVIEW LAYER             │                      │
│  │  • Git diff → PR creation        │                      │
│  │  • Auto-run CI tests             │                      │
│  │  • Human review (required)       │                      │
│  └──────────────────────────────────┘                      │
│                 ↓                                          │
│         Merge to main (human approved)                     │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 生产关键决策

| 决策 | 选项 | 建议 |
|----------|---------|----------------|
| Agent 模型 | Claude 3.7、GPT-4o、开源 | 最佳结果使用 Claude 3.7 Sonnet |
| 任务接入 | 手动、Jira Webhook、GitHub 标签 | GitHub 标签触发 Actions 工作流 |
| 代码执行 | 本地、Docker、E2B | Docker（可复现、隔离） |
| 人工审查 | PR、Slack 审批、自动化 | 必须进行 PR 审查，绝不自动合并 |
| 成本控制 | 最大轮数、模型路由 | `max_turns=20`，简单任务使用 Haiku |

---

## 面试问题

### Q：如何在 Claude Code、Cursor 和 OpenHands 之间选择？

**强回答：**
取决于三个维度：

1. **界面需求**：如果开发者需要 GUI（在上下文中查看变更），使用 Cursor 或 Windsurf；如果任务是脚本化/无头的（CI 中修 Bug、生成测试），使用 Claude Code SDK 或 OpenHands。

2. **模型控制**：需要使用任意模型（或自己的微调模型）时，使用 OpenHands 或 Aider；接受仅 Anthropic、并希望获得最佳结果时，使用 Claude Code。

3. **开源要求**：企业安全团队经常要求可以审计的开源工具。OpenHands（MIT）和 Aider（Apache 2.0）是答案。

对于典型初创公司，我会建议：日常开发使用 Cursor，批量任务（根据 GitHub Issue 生成 PR）使用 Claude Code，自托管 CI 流水线使用 OpenHands。

### Q：为什么 Qwen2.5-Coder 这类开放权重编码模型对企业很重要？

**强回答：**
三个原因：

1. **数据隐私**：发送到闭源 API 的代码可能被用于训练或暴露给第三方。医疗（HIPAA）、金融（SOX）和政府团队不能让专有代码离开网络。运行在本地的 Qwen2.5-Coder-32B 可以解决这个问题。

2. **规模化成本**：每月 100 万以上的代码生成请求时，自托管比 API 价格便宜 40%～60%，补全场景尤其明显（相较 Agent 任务）。

3. **微调**：开放权重可以进行领域专门化。法律科技公司可以基于内部 DSL（领域特定语言）微调模型，而 API 不允许这样做。

Qwen2.5-Coder-32B 与 Claude 3.7 Sonnet 的质量差距确实存在，但正在缩小。对于补全和更简单的任务，开源模型通常已经“足够好”。

### Q：如何为 CI 中的 AI 编码 Agent 设计测试策略？

**强回答：**
我会使用三层评估：

**1. 功能测试**（自动化，每次运行）：
```
Agent output → Run pytest → Pass rate metric
```

**2. 真值对比**（每周）：
```
Known bug → Agent fix → Compare to expert fix
Metric: Semantic similarity of diff (not byte-exact)
```

**3. 人工评估**（抽样 5% 的 Agent PR）：
```
Senior engineer rates: Correctness, Style, Safety, 1-5 scale
```

我还会跟踪**回归率**：如果 Agent 修复引入新的失败测试，就是硬失败。Agent 应运行完整测试套件，只有在通过率提升或保持不变时才算成功。

---

## 参考资料

- Qwen2.5-Coder：https://qwenlm.github.io/blog/qwen2.5-coder/
- DeepSeek-Coder-V2：https://github.com/deepseek-ai/DeepSeek-Coder-V2
- StarCoder2：https://huggingface.co/blog/starcoder2
- OpenHands：https://github.com/All-Hands-AI/OpenHands
- Aider：https://aider.chat/
- Cline：https://github.com/cline/cline
- Cursor：https://cursor.sh/
- Windsurf：https://codeium.com/windsurf
- Google Antigravity：https://developers.googleblog.com/build-with-google-antigravity-our-new-agentic-development-platform/
- SWE-bench 排行榜：https://www.swebench.com/
- LiveCodeBench：https://livecodebench.github.io/

---

*上一篇：[Claude Code](09-claude-code.md) | 下一篇：[框架选择指南](08-framework-selection-guide.md)*
