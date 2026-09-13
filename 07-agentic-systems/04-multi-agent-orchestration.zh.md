# 多 Agent 编排

复杂系统很少只包含一个 Agent，而是由一组专门 Agent 组成。编排已经从“盲目管理器”发展到**层级 Supervisor**、**动态 Swarm**和由 A2A 等互操作协议支持的**跨供应商 Agent 网络**。Gartner 预计，到 2026 年底，40% 的企业应用会包含面向特定任务的 AI Agent，而 2025 年初这一比例还不到 5%。

## 目录

- [为什么需要多 Agent？](#why)
- [Supervisor 模式](#supervisor)
- [Pipeline 模式](#pipeline)
- [Swarm 与点对点（P2P）](#swarms)
- [基于图的编排（2026 年主流模式）](#graph-orchestration)
- [通过 A2A 进行跨供应商 Agent 编排](#cross-vendor)
- [2026 年多 Agent 框架版图](#framework-landscape)
- [Agent 团队中的状态管理](#state)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## 为什么需要多 Agent？

一个拥有 50 个工具的单 Agent 会承受**认知负荷**。
1. **专业化**：“代码 Agent”可以使用针对 Python 优化的模型，而“搜索 Agent”使用针对 RAG 优化的模型。
2. **并行性**：多个 Agent 可以同时处理互不依赖的子任务。
3. **解耦评测**：可以把“写作 Agent”和“研究 Agent”分开评测。

---

## Supervisor 模式（层级式）

截至 2026 年最常见的企业模式。

- **Supervisor**：高推理模型（Claude Opus 4.7、GPT-5.5 reasoning、Gemini 3.1 Pro Deep Think），负责分解用户 Prompt 并委派给 Worker。
- **Worker**：快速、成本高效的模型（Claude Haiku 4.5、Gemini 3.1 Flash、GPT-5.5-mini），负责执行工作。
- **Reviewer**：独立 Agent，把汇总后的输出与 Supervisor 的原始计划进行核验。

**架构**：截至 2026 年，LangGraph 仍是实现这类有状态层级循环的主流框架。Claude Agent SDK、Google ADK 和 Microsoft Agent Framework 都原生支持该模式。

---

## Swarm（OpenAI 模式）

**Swarm** 在 2024 年末开始流行，重点是“交接”。

- 一个 Agent 把对话“交接”给另一个 Agent。
- **核心概念**：`Handoff(TargetAgent)`。
- **收益**：没有中心“管理器”瓶颈，对话可以自然地在专门实体之间流转。

---

## 基于图的编排（2026 年主流模式）

2026 年的架构势头已经明确转向**基于图的编排**：Agent 工作流被建模为带类型状态的有向图。

### 图模式为何胜出

- **显式控制流**：节点是 Agent 或函数，边定义转换，包括条件分支和循环。
- **可视化**：团队可以把工作流作为图检查和调试。
- **状态感知**：带类型的状态对象在图中传递，支持检查点和恢复。

### 框架支持

| 框架 | 图模型 | 关键差异 |
|------|--------|----------|
| **LangGraph**（24k stars） | 带类型状态的命令式 DAG | 最成熟，社区最广 |
| **Google ADK**（17k stars） | 内置 A2A 的 Agent 图 | 原生集成 Google Cloud |
| **Microsoft Agent Framework** | 工作流图（顺序、并发、交接） | 统一 .NET + Python，企业治理 |
| **Claude Agent SDK** | 基于 Supervisor 的层级树 | 内置工具（bash、编辑器），生产就绪 |

### Paperclip 模式（规模化层级 Agent）

2026 年一个值得注意的发展是 **Paperclip**（2026 年 3 月发布后 3 周内达到 44,900 个 GitHub stars）。它采用层级模型：CEO Agent 接收顶层目标，进行分解，然后委派给会派生和协调 Worker Agent 的 Manager Agent。这个模式展示了深层层级多 Agent 树如何处理复杂的真实任务。

> *已于 2026 年 5 月验证。*

---

## 通过 A2A 进行跨供应商 Agent 编排

**Agent-to-Agent（A2A）协议**（见[工具使用与 MCP](03-tool-use-and-mcp.md#a2a)）支持新的多 Agent 模式：**跨供应商编排**。在 A2A 之前，多 Agent 系统要求所有 Agent 共享同一框架和运行时。现在可以：

1. **Agent 发现**：编排器通过 **Agent Card**（描述能力的 JSON 元数据）找到专门 Agent。
2. **任务委派**：编排器通过 HTTP/SSE 向远程 Agent 发送结构化任务。
3. **异步进度**：远程 Agent 将状态更新流式返回，编排器可以并行委派给其他 Agent。
4. **结果收集**：返回最终产物并整合到编排器状态中。

**生产示例**：一个采购系统中，编排器（LangGraph）通过 A2A 委派合规检查给专门 Agent（Google ADK），把库存查询交给 MCP 连接的工具，把合同生成交给 CrewAI 团队；它们分别通过 A2A 和 MCP 通信。

> *已于 2026 年 5 月验证。来源：a2a-protocol.org*

---

## 2026 年多 Agent 框架版图

如今每个主要 AI 实验室都提供 Agent 框架。2026 年 5 月的多 Agent 编排版图如下：

| 框架 | 供应商 | 多 Agent 模型 | 状态 |
|------|--------|---------------|------|
| **LangGraph** | LangChain | 基于图，最灵活 | 生产（126k stars） |
| **Claude Agent SDK** | Anthropic | 带内置工具的 Supervisor 树 | GA（Python + TypeScript） |
| **Google ADK** | Google | 基于图，原生支持 A2A | GA（Python、TS、Java、Go） |
| **Microsoft Agent Framework** | Microsoft | 工作流 + 群聊模式 | RC 1.0（2026 年 2 月），2026 年第二季度 GA |
| **OpenAI Agents SDK** | OpenAI | 带 Guardrail 的基于交接的 Swarm | GA（Python + TypeScript） |
| **CrewAI** | CrewAI Inc. | 基于角色、带 Flow 的团队 | v1.13（60%+ 财富 500 强） |
| **Smolagents** | HuggingFace | 轻量、开源 | 活跃开发 |

**关键趋势**：没有一个框架能在四种多 Agent 模式（Supervisor、Swarm、Pipeline、Debate）上都做到最好。团队越来越多地组合框架，例如用 LangGraph 做复杂编排，用 CrewAI 做面向业务用户的自动化。

> *已于 2026 年 5 月验证。*

---

## 状态管理

多 Agent 系统最大的挑战是**共享黑板**。

1. **局部状态**：只对特定 Agent 可见的上下文。
2. **全局状态**：对所有 Agent 可见的共享记忆（例如最终草稿）。
3. **写冲突**：两个 Agent 同时尝试修改相同的全局状态。
   - **最佳实践**：使用**事务性交接**。只有“拥有”锁的 Agent 才能写入全局状态。

---

## 点对点（P2P）辩论

对于高准确率任务（例如法律或医疗），使用**Agent 辩论**。
- **Agent A**：提出答案。
- **Agent B**：尝试找出 Agent A 答案中的漏洞。
- **Agent A**：根据 B 的批评完善答案。
- **结果**：收敛到比任何单个 Agent 都更高质量的结果。

---

## 面试问题

### Q：Supervisor 多 Agent 架构的主要失败模式是什么？

**强回答：**

主要失败模式是**分解失败**。如果 Supervisor Agent 把任务拆成逻辑不一致或存在隐藏依赖的子任务，Worker 可能会正确回答“错误的问题”。标准修复方式是**迭代式规划**：执行前，Supervisor 必须从 Worker 获得“子任务可行性确认”。另一个失败是**上下文稀释**：全局状态被 Worker 日志撑得过大，Supervisor 失去“全局视角”。

### Q：如何在“链序列”和“多 Agent 图”之间选择？

**强回答：**

任务线性且确定时，我使用**链序列**（例如 Extract -> Translate -> Summarize）。任务**非线性**或需要**条件循环**时，我使用**多 Agent 图**（如 LangGraph）。例如，“Translate”步骤可能失败，需要回到“Extract”获取更多上下文；静态链会中断，而图可以通过路由回早期节点进行自我纠错。

### Q：什么时候使用 A2A 进行多 Agent 编排，而不是把所有 Agent 放在一个框架中？

**强回答：**

当团队拥有所有 Agent、共享同一个运行时且 Agent 调用之间的低延迟很关键时，我会把 Agent 保留在单一框架中。当跨越**组织或供应商边界**时引入 A2A，例如编排器需要委派给另一团队维护的合规 Agent，或接入第三方专门 Agent（如法律审查服务）。A2A 增加 HTTP 开销，但提供**供应商中立**、**独立扩展**以及通过 Agent Card 进行**能力发现**。经验法则是：同团队、同框架；不同团队或供应商，使用 A2A。

---

## 参考资料

- Wu 等，《AutoGPT: An Autonomous GPT-4 Experiment》（历史/2025 更新）
- Li 等，《Camel: Communicative Agents for 'Mind' Exploration》（2023/2025）
- OpenAI，《Swarms Framework》（2024/2025）
- Google，《Agent2Agent Protocol》（2025/2026）
- Gartner，《Predicts 2026: AI Agent Market》（2025）
- Andrew Ng，《Agentic Design Patterns》（2025/2026）

---

*下一篇：[Agent 记忆与状态](05-agent-memory-and-state.md)*
