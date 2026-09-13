# 状态管理模式

AI 系统中的状态管理已经从简单的“会话”转向**有状态的 Agent 图**。管理 Agent“思维”的流转和持久化，与 LLM 本身同样重要；这也是 LangGraph 成为 LangChain 构建 Agent 的默认控制流运行时的主要原因之一。

## 目录

- [状态对象](#state-object)
- [状态机与 DAG 编排](#orchestration)
- [检查点与恢复](#checkpointing)
- [并行状态与 Fork/Join](#parallel)
- [时间旅行（重写状态）](#time-travel)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## 状态对象

“状态”是 Agent 会话的**唯一事实来源**。
```python
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    plan: list[str]
    current_task: str
    tool_results: dict[str, Any]
    user_context: dict[str, Any]
    iteration_count: int
```
**最佳实践**：状态应该**严格类型化**，并且在可能的情况下采用**只追加**的方式，防止长执行循环中发生数据丢失。

---

## 状态机（LangGraph）

行业已经趋于使用**循环图**（状态机）。
- **节点**：接收状态并返回更新的函数。
- **边**：根据状态值决定下一个节点的条件逻辑（例如 `if state['error'] -> goto 'recovery_node'`）。

---

## 检查点与恢复

在生产环境中，Agent 可能运行数分钟或数小时。
- **持久化层**：每次状态更新都保存到数据库（Postgres/Redis）。
- **韧性**：如果服务器崩溃，编排器会取回最后一个 `checkpoint_id`，并从原来停下的位置精确恢复。
- **用户体验**：这使**异步 Agent**成为可能：用户先收到“我正在处理”的消息，10 分钟后在状态变为“完成”时收到通知。

---

## 并行状态（Fork/Join）

对于复杂任务，我们会**Fork 状态**。
1. **扇出**：把状态发送给 3 个子 Agent（例如研究员 A、B、C）。
2. **扇入（Join）**：一个“管理器”Agent 接收三者的输出，并将它们合并回主状态对象。

---

## 时间旅行（重写状态）

正如 HITL 章节所述，状态管理支持**人工干预**。
- 开发者可以浏览会话历史，找到某个“错误轮次”，在特定时间戳编辑状态对象，并从该点**重新运行**图。

---

## 面试问题

### Q：为什么用基于“图”的状态机（LangGraph），而不是 Agent 的简单“While 循环”？

**强回答：**
While 循环是**不透明且脆弱的**。逻辑难以可视化，错误处理也会变成嵌套的 if 语句。基于图的方式则**可观测且模块化**。你可以把完整流程可视化（例如 Mermaid 图），单独对节点进行单元测试，并且只需增加新的边，就能简单实现“回溯”或“并行执行”等复杂功能。由于框架负责在节点之间保存和加载状态，它也让**状态持久化**变得很简单。

### Q：如何防止长时间运行的 Agent 会话出现“状态膨胀”？

**强回答：**
我们使用**状态剪枝**和**消息摘要**。子任务完成后，不再让整个 `tool_results` 字典贯穿整张图，而是及时裁剪。对于 `messages` 列表，我们使用专门的“摘要节点”，每 10 轮运行一次，把历史压缩成简洁的上下文块，确保不会达到 Token 上限，同时保持状态对象响应迅速。

---

## 参考资料
- LangChain：《LangGraph: Multi-Agent Workflows》（2024/2025）
- Temporal.io：《Stateful AI Agents at Scale》（2025）
- AWS Bedrock：《Managing Long-Running Agent Sessions》（2025）

---

*下一篇：[第 09 节：框架与工具](../09-frameworks-and-tools/01-langchain-deep-dive.md)*
