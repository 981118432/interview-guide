# Microsoft Agent Framework、CrewAI 与 Agent SDK 版图

过去一年，多 Agent 框架版图显著整合。微软**退役了 AutoGen**，并将其与 Semantic Kernel 合并成统一的**Microsoft Agent Framework**（RC 1.0 于 2026 年 2 月发布，目标在 2026 年第二季度 GA）。CrewAI 已成熟到 v1.13，具备企业级能力，并报告称已有超过 60% 的财富 500 强企业在使用它。同时，各大 AI 实验室都发布了自己的 Agent SDK：Anthropic 的 Claude Agent SDK、OpenAI 的 Agents SDK 和 Google 的 ADK。

## 目录

- [CrewAI：管理者视角](#crewai)
- [Microsoft Agent Framework（AutoGen 的继任者）](#microsoft-agent-framework)
- [Agent SDK 版图](#agent-sdk-landscape)
- [Swarm 与点对点通信](#swarms)
- [框架对比矩阵](#comparison)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## CrewAI：管理者视角

CrewAI 围绕**流程（Process）**这一概念构建。
- **基于角色的 Agent**：定义“研究员”“写作者”和“管理者”。
- **任务**：带有明确输出的具体目标。
- **流程编排**：顺序式、层级式或共识式（基于共识）。

### CrewAI Flows

CrewAI **Flows** 在经典 Crew 模式之上增加了**状态机层**：

```python
from crewai.flow.flow import Flow, listen, start

class ContentFlow(Flow):
    @start()
    def research_topic(self):
        # Returns research output
        return research_crew.kickoff({"topic": self.state["topic"]})
    
    @listen(research_topic)
    def write_article(self, research):
        # Triggered after research completes
        return writing_crew.kickoff({"research": research})
    
    @listen(write_article)
    def publish(self, article):
        # Final step
        return publisher.publish(article)
```

### CrewAI v1.13 亮点

CrewAI v1.13 标志着它朝企业生产就绪迈出转折性一步：

- **企业 SSO**：完整记录企业部署的单点登录能力
- **RBAC 改进**：提供完整权限参考矩阵的基于角色访问控制
- **GPT-5 兼容性**：修复 OpenAI GPT-5 和更新的 o 系列模型不再支持 `stop` 参数的问题
- **A2A 任务执行**：以结构化、确定性的方式动态委托 Agent-to-Agent 任务
- **NVIDIA NemoClaw 集成**：为安全企业部署提供基础设施级策略执行
- **RuntimeState RootModel**：统一复杂工作流的状态序列化

**使用场景**：CrewAI + Flows 最适合**业务流程自动化**（内容流水线、数据分析工作流），因为这类流程结构清晰。CrewAI 报告称，它已经支持约 20 亿次 Agent 执行。

> *已于 2026 年 5 月核验。来源：docs.crewai.com/en/changelog*

---

## Microsoft Agent Framework（AutoGen 的继任者）

### 合并：AutoGen + Semantic Kernel = Agent Framework

微软在 2025 年底退役了作为独立产品的 AutoGen，并将它与 Semantic Kernel 合并为统一的 **Microsoft Agent Framework**。候选发布版 1.0 于 2026 年 2 月发布，目标在 2026 年第二季度 GA。

**合并带来的能力：**
- **来自 AutoGen**：单 Agent 和多 Agent 对话模式的简单抽象（群聊、轮询、交接）
- **来自 Semantic Kernel**：企业级会话管理、类型安全、过滤器、遥测，以及广泛的模型/Embedding 支持

### 迁移路径

AutoGen 仍会收到 Bug 修复和安全补丁，但**新功能全部进入 Agent Framework**。微软提供了官方迁移指南。如果开始新项目，应直接使用 Agent Framework。

### 关键能力

```python
# Microsoft Agent Framework: Graph-based workflow
from agent_framework import Agent, Workflow, HandoffStep

planner = Agent("Planner", model="gpt-5.5", system_message="Decompose tasks.")
executor = Agent("Executor", model="gpt-5.5-mini", system_message="Execute sub-tasks.")

workflow = Workflow(
    steps=[
        HandoffStep(from_agent=planner, to_agent=executor),
    ],
    state_management="session",  # Built-in session persistence
)
```

**框架亮点：**
- **统一的 .NET 和 Python**：两种语言使用同一套编程模型
- **基于图的工作流**：顺序、并发、交接和群聊模式都能显式控制
- **状态管理**：面向长时间运行和人在环场景的可靠会话持久化
- **MCP 支持**：原生集成 Model Context Protocol 访问工具
- **多供应商**：支持 OpenAI、Azure OpenAI、Anthropic、Google 和本地模型

> *已于 2026 年 5 月核验。来源：learn.microsoft.com/en-us/agent-framework*

---

## Agent SDK 版图

现在每个主要 AI 实验室都有自己的 Agent 框架。以下是 2026 年 5 月的版图：

### Claude Agent SDK（Anthropic）

Claude Agent SDK（由 Claude Code SDK 更名而来）提供驱动 Claude Code 的同一套工具、Agent 循环和上下文管理能力，并以 Python 和 TypeScript 库形式提供。

- **内置工具**：读取文件、执行命令、编辑代码，Agent 无需自定义工具即可工作
- **监督器模式**：支持委托的层级 Agent 树
- **部署**：支持 AWS Bedrock、Google Vertex AI 和 Azure
- **截至 2026 年 5 月**：Python v0.1.48+，TypeScript v0.2.71+

### OpenAI Agents SDK

OpenAI 面向多 Agent 工作流的轻量框架，使用原生 Python/TypeScript 构造：

- **基于交接**：Agent 使用 `Handoff(TargetAgent)` 相互委托，无需中心监督器
- **护栏**：内置输入校验和安全检查
- **MCP 集成**：原生支持 MCP 服务器工具
- **实时 Agent**：通过 gpt-realtime-1.5 支持语音 Agent

### OpenAI AgentKit

AgentKit 是 OpenAI 构建在 Responses API 和 Agents SDK 之上的高级工具集。Agents SDK 以代码为先，而 AgentKit 面向希望少写基础设施、直接组装并发布 Agent 的团队：

- **Agent Builder**：用于组合和版本管理多 Agent 工作流（节点、分支、循环）的可视化画布，并可导出为 Agents SDK 代码。
- **ChatKit**：可嵌入、可主题化的聊天 UI，无需自己构建前端即可把 Agent 体验接入产品。
- **连接器注册表**：集中管理数据源和工具如何连接到各个 OpenAI 产品，并提供治理与访问控制。
- **评测与护栏**：内置轨迹评分、数据集和 Prompt 优化钩子，让构建到评测的循环集中在一个位置。

**何时使用**：AgentKit 适合希望获得托管式构建与发布循环、并接受运行在 OpenAI 基础设施上的团队。需要完全控制循环时降到原始 Agents SDK；需要框架中立或自托管运行时时，使用 LangGraph 或 Microsoft Agent Framework。

### OpenAI Apps SDK

Apps SDK 扩展了**模型上下文协议**，让 MCP 服务器可以在工具之外同时提供 UI。开发者定义逻辑和交互界面，应用则渲染在 ChatGPT 等客户端中。这与 MCP 规范正在标准化的“MCP Apps”（服务器渲染 UI）理念相同，它把 MCP 服务器从无头工具端点变成交互式表面。参见[工具使用与 MCP](../07-agentic-systems/03-tool-use-and-mcp.md)。

### Google Agent Development Kit（ADK）

Google 面向 Google 生态优化、但与模型无关的框架：

- **多语言**：Python、TypeScript、Java、Go（截至 2026 年 5 月均已达到 1.0+）
- **原生 A2A**：内置 Agent-to-Agent 协议支持，实现跨供应商编排
- **Vertex AI 集成**：部署到 Agent Engine Runtime 进行托管
- **基于图**：把 Agent 工作流建模成有向图

> *已于 2026 年 5 月核验。*

---

## Swarm 与点对点

两个框架以及更广泛的 SDK 版图都采用了**Swarm 模式**。
- **交接**：不使用中心监督器，而是由 Agent 将对话“交接”给最相关的专家。
- **示例**：“销售 Agent”意识到用户在问技术问题，于是把线程交接给“支持 Agent”。

---

## 框架对比矩阵

| 特性 | CrewAI | MS Agent Framework | LangGraph | Claude Agent SDK | OpenAI Agents SDK | Google ADK |
|---------|--------|-------------------|-----------|-----------------|-------------------|------------|
| **核心抽象** | Task/Process/Flow | Workflow/Agent | State/Graph | Supervisor/Tools | Handoff/Agent | Agent Graph |
| **架构** | 声明式 + 状态机 | 图工作流 | 命令式 DAG | 层级树 | Swarm 交接 | 有向图 |
| **易用性** | 高 | 中 | 低 | 中 | 高 | 中 |
| **控制力** | 低-中 | 中-高 | 高 | 中 | 低-中 | 中-高 |
| **最适合** | 业务自动化 | 企业 .NET/Python | 复杂编排 | 编码/工具 Agent | 快速多 Agent | Google Cloud AI |
| **多语言** | Python | .NET + Python | Python | Python + TS | Python + TS | Python、TS、Java、Go |
| **MCP 支持** | 是 | 是 | 通过工具 | 原生 | 是 | 是 |
| **A2A 支持** | 通过扩展 | 计划中 | 通过工具 | 不直接支持 | 不直接支持 | 原生 |

---

## 面试问题

### Q：什么时候会使用 CrewAI 而不是 LangGraph？

**强回答：**
这是**速度与精度**的选择。需要快速搭建一支 Agent 团队来执行标准流程（例如内容生成或数据分析）时，我使用 **CrewAI**，因为它开箱即用地提供“规划”和“协作”的高层抽象。需要对每次状态转换、多轮人在环触发器或不适合“角色扮演团队”比喻的复杂错误恢复逻辑进行**细粒度控制**时，我会切换到 **LangGraph**。

### Q：微软用 Agent Framework 取代了 AutoGen，这会如何影响现有 AutoGen 部署？

**强回答：**
AutoGen 仍会收到 Bug 修复和安全补丁，所以现有部署不会立即失效。但**所有新功能开发**都在 Agent Framework 中。迁移路径已有文档：AutoGen 的 `AssistantAgent` 对应 Agent Framework 的 `Agent` 类，`GroupChat` 对应新的 `Workflow` 模式，Semantic Kernel 的企业能力（会话管理、遥测、过滤器）现在也原生可用。迁移的主要收益是**统一的 .NET 和 Python 支持**以及可显式控制多 Agent 执行路径的**基于图的工作流**。新项目应直接从 Agent Framework 开始。

### Q：如何防止 Agent 之间不断对话却无法解决任务的“无限循环”？

**强回答：**
我们使用**终止条件**和**最大对话轮数**。还会实现一个“评论 Agent”，唯一职责是检测对话是否停滞。如果评论 Agent 检测到循环，就触发用户代理进行中断，或强制把群聊管理器切换到另一条推理路径。我们还监控**Token 速度**：如果一对 Agent 在 2 分钟内消耗了 100K Token 却没有进展，就自动终止会话。2026 年的 Microsoft Agent Framework 和 LangGraph 等框架提供了内置工作流超时和状态检查点，让循环检测更加系统化。

---

## 参考资料
- CrewAI：《The Multi-Agent Process Engine》（2025/2026，v1.13）
- Microsoft：《Agent Framework Overview》（2026）— learn.microsoft.com/en-us/agent-framework
- Microsoft：《AutoGen to Agent Framework Migration Guide》（2026）
- Anthropic：《Claude Agent SDK》（2026）— platform.claude.com/docs/en/agent-sdk
- OpenAI：《Agents SDK Documentation》（2026）
- [OpenAI：《Introducing AgentKit》（2025）](https://openai.com/index/introducing-agentkit/)
- [OpenAI：《Apps SDK》（2025）](https://developers.openai.com/apps-sdk)
- Google：《Agent Development Kit》（2026）— google.github.io/adk-docs
- OpenAI Swarm：《Lightweight Multi-Agent Orchestration》（2024 技术报告）

---

*下一篇：[框架选择指南](08-framework-selection-guide.md)*
