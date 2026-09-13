# Agentic RAG

Agentic RAG 从“线性流水线”转向**“推理循环”**。它不只检索一次，而是由 Agent 决定*何时*检索、*检索什么*来解决查询。主流生产模式包括 Self-RAG（模型输出反思 Token）、Corrective RAG（带纠正路由的检索评估器）、Adaptive RAG（分类器选择流水线深度）、在文档上运行 ReAct，以及多跳查询分解。LangGraph 是有状态循环中最常见的控制流运行时；LlamaIndex Workflows 常用于单流水线、检索密集型变体。

## 目录

- [线性 RAG 与 Agentic RAG](#comparison)
- [Self-RAG（自我反思）](#self-rag)
- [Corrective RAG（CRAG）](#crag)
- [多跳推理循环](#multi-hop)
- [Agent 过滤与计划修订](#planning)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## 线性 RAG 与 Agentic RAG

| 模型 | 线性 RAG | Agentic RAG |
|------|----------|-------------|
| **结构** | 预先确定的顺序 | 动态循环 |
| **自我纠错** | 无 | 高（可以重新检索） |
| **查询复杂度** | 简单（一步） | 困难（多步） |
| **延迟** | 低（固定） | 可变（多轮） |

**原则**：当查询需要“综合证明”，而不只是“匹配文档”时，使用 Agentic RAG。要为此做预算：3～4 次迭代的循环通常需要端到端 8～12 秒，因此如果用户体验需要低于 3 秒的响应，就把简单查询路由到快速路径（Adaptive RAG）。

---

## Self-RAG（自我反思）

**Self-RAG** 在 2024/2025 年得到推广，它使用“批评 Token”评价自己的工作。

1. **检索**：模型拉取 Top-K 块。
2. **评估**：信息相关吗？（CRITIC：`Relevant`）
3. **生成**：答案有依据吗？（CRITIC：`Supported`）
4. **迭代**：如果答案没有依据，模型会**自动**触发更宽范围的搜索。

---

## Corrective RAG（CRAG）

CRAG 在检索和生成之间增加一层“可靠性层”。

- **逻辑**：
  - 如果检索结果**正确**：直接生成。
  - 如果检索结果**有歧义**：使用 Web Search 工具补充。
  - 如果检索结果**错误**：丢弃上下文，使用外部搜索或兜底逻辑。

---

## 多跳推理循环

对于“收购 Figma 的公司的 CEO 是谁？”这类问题，系统必须：
1. **第 1 跳**：搜索“谁收购了 Figma？”（结果：Adobe）。
2. **第 2 跳**：搜索“Adobe 的 CEO 是谁？”（结果：Shantanu Narayen）。

**Agent 模式**：Agent 维护一个“状态对象”，每次检索后更新“子目标”，直到链条完成。

---

## Agent 过滤与计划修订

现代 Agent 使用**子步骤计划**。
- Agent 不进行一次大检索，而是先写出计划：“我会先在内部数据库检查 X，然后查看 Y 的公共 API。”
- **计划修订**：如果第 1 步失败，Agent 会**重写**第 2 步。

---

## 面试问题

### Q：Agentic RAG 中的“推理-检索平衡”是什么？

**强回答：**

Agent 循环中的每一次“推理轮次”都会增加 Token 成本和用户延迟。生产工程师的目标是找到“检索阈值”。我们使用**Token 预算**，最多允许 Agent 进行 3～5 个“轮次”，之后强制给出最终答案。我们也使用**推测检索**：让 Agent 预测接下来会采取的 2 个步骤，并同时为两步检索，从而减少往返延迟。

### Q：为什么 Agentic RAG 往往质量更高，却“可靠性”（确定性）更低？

**强回答：**

Agentic RAG 是非确定性的，因为模型每一步都在“决定”路径。用户查询的轻微变化，可能让 Agent 选择不同工具或搜索策略，导致不同的答案格式。标准缓解方式是使用**受约束的 Agent 框架**（如 LangGraph 或 DSPy）：即使路径之间的选择仍是随机的，也严格定义“可能路径图”。

---

## 参考资料

- Asai 等，《Self-RAG: Learning to Retrieve, Generate, and Critique》（2024/2025）
- Yan 等，《Corrective Retrieval Augmented Generation（CRAG）》（2024）
- LangChain，《Agentic RAG with LangGraph》（2025）

---

*下一篇：[高级检索模式](09-advanced-retrieval-patterns.md)*
