# LangGraph 编排

LangGraph 已成为构建有状态多 Agent 系统的**事实标准**。它在 2025 年底达到 v1.0，并在 2026 年初凭借企业对图运行时的采用，在 GitHub Star 数上超过 CrewAI。与简单链不同，LangGraph 支持**循环**、**状态持久化**和**人在环**干预。

## 目录

- [图的理念](#philosophy)
- [循环与无环工作流](#cyclic)
- [LangGraph 中的状态管理](#state)
- [持久化与检查点](#persistence)
- [多 Agent 编排模式](#multi-agent)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## 图的理念

2023 年，Agent 是“黑盒”。
如今，Agent 是**图**。
一个图由以下部分组成：
- **节点**：Python 函数（LLM、工具或数据处理逻辑）。
- **边**：节点之间的路径。
- **条件边**：根据**状态**决定路径的逻辑。

---

## 循环与无环

标准 LangChain 是**无环的**（顺序执行）。
LangGraph 是**有环的**。
- **循环的力量**：Agent 可以尝试调用工具，看到错误后**循环回到**“思考”节点再次尝试。这是 **ReAct** 模式的基础。

---

## 状态管理

**状态 Schema** 是图的“思维”。
```python
class GraphState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    plan: list[str]
    is_secure: bool
```
**细节**：使用带有 `add_messages` 的 `Annotated`，可以让图向历史中**追加**内容，而不是覆盖历史，从而保留完整的推理轨迹。

---

## 持久化与检查点

当前 LangGraph 使用**基于 Thread 的持久化**。
- **概念**：每个会话都有一个 `thread_id`。
- **收益**：如果用户两天后回来，Agent 仍能记住自己在多步骤工作流中执行到的确切位置。
- **时间旅行**：开发者可以从某个过去的状态重新“运行”特定 Thread，以调试故障。

---

## 多 Agent 模式

| 模式 | 描述 | 案例 |
|---------|-------------|------------|
| **监督器** | 一个“管理器”指挥专门的工作 Agent。 | 研究团队 |
| **点对点**| Agent 直接把任务交接给彼此。 | 客服 |
| **层级式**| 图中嵌套图（嵌套图）。 | 企业工程 |

---

## 面试问题

### Q：为什么使用 LangGraph，而不是 OpenAI 的“Assistant API”？

**强回答：**
**控制力和可移植性**。Assistant API 是黑盒：你看不到准确的 Prompt，也无法控制逻辑门。LangGraph 是**白盒框架**。我可以使用任意模型（OpenAI、Claude、Llama 3.3），精确控制工具调用时机，并在步骤之间注入自定义校验逻辑。更重要的是，LangGraph 是**开源的**，可以在本地或本地部署环境运行，这对许多企业的安全要求至关重要。

### Q：如何处理包含 20 多个节点的图中的“状态过载”？

**强回答：**
我们使用**状态收窄**。不把完整全局状态传给每个节点，而是为子图定义专门的子状态。我们还使用 **Trim Runnable**，在消息历史进入 LLM 前对其剪枝，确保不浪费 Token，同时让“事实”保留在持久化层中。

---

## 参考资料
- LangChain 团队：《LangGraph: Multi-Agent Workflows at Scale》（2025）
- Anthropic：《Building Resilient Agents with State Machines》（2025）
- OpenSource AI：《Cycles and the Future of Agency》（2024 技术报告）

---

*下一篇：[LangSmith 可观测性](03-langsmith-observability.md)*
