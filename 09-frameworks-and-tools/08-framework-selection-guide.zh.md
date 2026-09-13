# 框架选择指南

过去一年，AI 框架版图已经显著整合。现在每个主要 AI 实验室都提供 Agent SDK，微软把 AutoGen 和 Semantic Kernel 合并成统一的 Agent Framework，互操作协议（MCP、A2A）也已经成为基本配置。本指南提供一套**决策矩阵**，根据生产要求、团队经验和系统规模选择技术栈。

## 目录

- [框架版图](#landscape)
- [决策矩阵](#matrix)
- [自建、购买还是使用框架](#build-vs-buy)
- [应避免的反模式](#anti-patterns)
- [Staff 级建议](#recommendation)
- [面试问题](#interview-questions)

---

## 框架版图

### 编排与 Agent 框架

| 框架 | 层级 | 主要价值 | 关键弱点 |
|-----------|------|---------------|--------------|
| **LangGraph** | L1（核心） | 精确的状态控制、基于图 | 复杂度高、学习曲线陡 |
| **DSPy** | L1（核心） | 可靠性与优化 | 前期成本（训练） |
| **LlamaIndex**| L2（数据） | 高级检索（RAG） | 逻辑灵活性 |
| **CrewAI** | L3（应用） | 业务流程速度、企业 RBAC | 隐藏故障 |
| **MS Agent Framework** | L1（企业） | 统一 .NET + Python，替代 AutoGen + SK | RC 状态（2026 年第二季度 GA） |

### Agent SDK（实验室专属）

| 框架 | 层级 | 主要价值 | 关键弱点 |
|-----------|------|---------------|--------------|
| **Claude Agent SDK** | L1（Agent） | 内置工具、生产级 Agent 循环 | 需要 Anthropic API |
| **OpenAI Agents SDK** | L1（Agent） | 轻量交接、护栏 | 以 OpenAI 为中心 |
| **Google ADK** | L1（Agent） | 多语言、原生 A2A + Google Cloud | 偏向 Google 生态 |

### 编码 Agent

| 框架 | 层级 | 主要价值 | 关键弱点 |
|-----------|------|---------------|--------------|
| **Claude Code** | L1（编码） | 自主 CLI 编码 Agent | 需要 Anthropic API |
| **Cursor / Windsurf** | L2（IDE） | 紧密的 IDE + Agent 集成 | 基础设施闭源 |
| **OpenHands** | L2（编码） | 开源自主 Agent | 需要自行托管 |

> **2026 年 4 月提示**：Semantic Kernel 已不再作为独立框架列出，而是合并进 Microsoft Agent Framework。现有 SK 用户应规划迁移。

---

## 决策矩阵

**使用以下逻辑选择技术栈：**

### 核心编排
1. **纯 RAG 应用？** → **LlamaIndex**。
2. **需要长时间运行的状态/人在环？** → **LangGraph**。
3. **高可靠性（99%+）和跨模型可移植性很关键？** → **DSPy**。
4. **C#/.NET 企业团队？** → **Microsoft Agent Framework**（替代 Semantic Kernel + AutoGen）。
5. **为业务用户构建高层自动化？** → **CrewAI + Flows**。

### Agent SDK（根据主要模型供应商选择）
6. **基于 Claude/Anthropic API 构建 Agent？** → **Claude Agent SDK**（Python/TS，内置文件/代码/命令工具）。
7. **基于 OpenAI API 构建 Agent？** → **OpenAI Agents SDK**（轻量交接、护栏、MCP 支持）。
8. **基于 Google Cloud/Gemini 构建 Agent？** → **Google ADK**（原生 A2A、Vertex AI 部署、多语言）。
9. **需要跨供应商 Agent 通信？** → 在上述任一框架之上使用 **A2A 协议**。

### 编码 Agent
10. **进行文件系统级别的自主编码任务？** → **Claude Code**（CLI）或 **Cline**（VS Code）。
11. **需要支持任意 LLM 的开源编码 Agent？** → **OpenHands**（Docker）。
12. **想要最好的 IDE + AI 体验？** → **Cursor**（闭源）或 **Windsurf**（Codeium）。

---

## 自建、购买还是使用框架

作为 Staff 工程师，必须抵制**框架膨胀**。

- **使用框架**：当它解决了**非平凡的计算机科学问题**（例如状态持久化、贝叶斯 Prompt 优化、向量-图关联）。
- **自建（薄封装）**：只是简单调用 LLM 时。对于单轮 Agent，框架增加的延迟、更新变化和调试开销不值得。

---

## 应避免的反模式

1. **框架隧道**：强行把复杂逻辑流程塞进不支持它的框架（例如用纯 RAG 库构建编码 Agent）。
2. **金锤**：仅仅因为 LangChain 流行就使用它，而一个 50 行的 Python 脚本会更快、更便宜。
3. **忽视可观测性**：不配备 LLOps 层（LangSmith/Phoenix）就部署任何框架。

---

## Staff 级建议

对于现代生产级 Agent 系统：
- **编排**：用 LangGraph 管理状态和循环；.NET 团队使用 Microsoft Agent Framework。
- **Agent SDK**：匹配模型供应商——Claude Agent SDK（Anthropic）、Agents SDK（OpenAI）、ADK（Google）。它们都支持通过 MCP 访问工具。
- **优化**：使用 DSPy 为不同模型层级编译 Prompt。
- **检索**：使用 LlamaIndex 实现多阶段 RAG。
- **可观测性**：使用 LangSmith 进行追踪和评测。
- **跨供应商 Agent**：使用 A2A 协议实现组织边界之间的 Agent-to-Agent 协调。
- **自主编码**：文件级编辑任务使用 Claude Code（CLI）或 Cline（VS Code）。
- **开源编码 Agent**：使用 OpenHands 进行自托管或接入 CI 流水线。

**2026 年洞察**：
1. Agent 编码工具（Claude Code、Cursor、OpenHands）不是编排框架的替代品，而是一个**新类别**：它们运行在文件系统层，位于 LLM API 之上、应用逻辑之下。
2. 协议层已经成熟：**MCP 用于 Agent-to-Tool**，**A2A 用于 Agent-to-Agent**，它们正在成为基础设施标准，而不是可选附加项。架构应该同时支持两者。
3. 每个实验室都发布自己的 Agent SDK，会带来**供应商锁定风险**。可以使用跨 SDK 通用的 MCP 访问工具，以及供应商中立的 A2A 进行 Agent 协调来缓解。

> *更新于 2026 年 5 月。*

---

## 面试问题

### Q：为什么我们看到从“Prompt”转向 DSPy 这类“编程”的趋势？

**强回答：**
**工业化**。Prompt 工程像“炼金术”：不一致，也无法扩展。通过 DSPy 等框架编程 LLM，可以把 AI 当作一门**软件工程学科**。我们可以应用 CI/CD、单元测试（指标）和自动优化，把 AI 从“不确定的魔法”变成大型分布式系统中**可预测的组件**，而这是任何关键生产环境的要求。

### Q：如果要构建同时支持 OpenAI、Anthropic 和本地 Llama 模型的系统，你会如何架构？

**强回答：**
我会用 **DSPy** 做 Prompt 层，用 **LangGraph** 做编排层。DSPy 的 **Signature** 可以把任务定义与模型的具体行为解耦。然后使用统一模型网关（如 LiteLLM 或内部代理）处理不同的 API 格式。工具访问使用 **MCP**：它与模型无关，所以无论当前使用哪个 LLM 后端，相同的 MCP 服务器都能工作。如果需要跨团队 Agent 协调，就在边界层使用 **A2A**。这样从 GPT-4o 切换到 Claude Sonnet 4 时，不必重写 50 个 Prompt，只需重新编译或更新配置。

### Q：每个 AI 实验室都发布自己的 Agent SDK 时，如何避免供应商锁定？

**强回答：**
关键是**分离编排层与模型层**。核心工作流使用与框架无关的编排器，如 LangGraph，或使用自定义薄封装。模型专属 SDK 适合原型阶段或已经确定单一供应商的场景；对于生产级多供应商系统，应把模型交互放在抽象层之后（LiteLLM 网关或 DSPy Signature）。工具访问使用 **MCP** 提供可移植性，同一个 MCP 服务器可以服务任意 SDK；Agent 协调用 **A2A** 提供供应商中立的通信。实际规则是：在叶节点（单个 Agent 实现）使用实验室专属 SDK，但让编排图保持与供应商无关。

---

## 参考资料
- Google Cloud：《Enterprise Generative AI Reference Architecture》（2025）
- Gartner：《Magic Quadrant for AI Application Frameworks》（2025）
- Gartner：《Predicts 2026: 40% of Enterprise Apps to Feature AI Agents》（2025）
- Thoughtworks：《Technology Radar: The Rise of Agentic Frameworks》（2024/2025 年 11 月）
- Microsoft：《Agent Framework Overview》（2026）
- Anthropic：《Claude Agent SDK》（2026）
- Google：《Agent Development Kit》（2026）
- OpenAI：《Agents SDK》（2026）

---

*下一篇：[应对框架变动](12-navigating-framework-churn.md)*
