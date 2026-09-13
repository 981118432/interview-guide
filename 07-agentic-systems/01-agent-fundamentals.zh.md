# Agent 基础

Agent 是由 LLM 驱动的系统，它从“聊天”走向“自主解决问题”。这个定义已经从简单的 ReAct 循环转向使用内置“System 2”思考的**闭环推理系统**（Claude Opus 4.7 扩展思考、GPT-5.5 推理、DeepSeek-R2、Gemini 3.1 Pro Deep Think）。

## 目录

- [Agent 公式](#formula)
- [System 1（LLM）与 System 2（推理模型）](#systems)
- [自主性等级（自主谱系）](#levels)
- [核心组件](#components)
- [Agent 生命周期](#lifecycle)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## Agent 公式

现代 Agent 能力通常可以描述为：
`Agent = Reasoning Model + Tool Use + Persistent Memory + Environment Feedback`

**细节**：2023 年的 Agent 是聊天模型外面的“包装器”。如今 Agent 越来越**一体化**。前沿模型（Claude Opus 4.7、具备推理能力的 GPT-5.5、DeepSeek-R2）已经把“思考”过程融入预训练，使 Agent 循环更稳定，也不容易“停滞”。

---

## System 1 与 System 2 思考

设计 Agent 时必须选择正确的“思考模式”：

| 模式 | 认知类型 | 类比 | 当前技术栈 |
|------|----------|------|------------|
| **System 1** | 快速、直觉、反应式 | 反射 | Claude Haiku 4.5/Sonnet 4.6/GPT-5.5-mini/Gemini 3.1 Flash |
| **System 2** | 缓慢、逻辑、规划 | 深思熟虑 | Claude Opus 4.7/GPT-5.5 reasoning/DeepSeek-R2/Gemini 3.1 Pro Deep Think |

**设计模式**：System 1 模型用于“快速 UI”和“路由”；System 2 模型用于“决策门”和“复杂规划”。

---

## 自主性等级

不是所有自主系统都是“Agent”。我们按**自主性等级**对它们分类：

1. **L0：脚本化链**：固定顺序（例如标准 LangChain）。
2. **L1：工具增强**：模型选择工具，但不做规划。
3. **L2：ReAct Agent**：简单的“思考 -> 行动 -> 观察”循环。
4. **L3：自主规划器**：把目标拆成子任务图。
5. **L4：环境 Agent**：在后台运行，只在必要时介入。

---

## 核心组件

### 1. 推理模型（执行者）

Agent 的 CPU，决定“成功路径”。

### 2. 工具（四肢）

让 Agent 能够影响现实世界的接口（API、浏览器、数据库）。
> [!Note]
> **Model Context Protocol（MCP）** 现在已经成为工具互操作的行业标准，Anthropic、OpenAI、Google、Microsoft 和 AWS 都在采用。2025 年 12 月，治理工作转移到 Linux Foundation 的 Agentic AI Foundation。

### 3. 记忆（经验）

- **短期记忆**：上下文窗口（KV Cache）。
- **长期记忆**：向量数据库或持久化状态（例如 Mem0）。

---

## Agent 生命周期

1. **接收**：接收用户目标。
2. **分解**：把目标拆成子步骤。
3. **执行**：调用工具并处理结果。
4. **反思**：评估观察结果是否让 Agent 更接近目标。
5. **完成**：为用户综合出最终证明。

---

## 面试问题

### Q：为什么“推理模型”（例如 Claude Opus 4.7 或开启扩展思考的 GPT-5.5）比标准 LLM 更适合 Agent？

**强回答：**

标准 LLM（System 1）通过模式匹配预测**下一个 Token**。工具调用出错时，它经常会幻觉式地修复，而不是承认失败。推理模型在推理时使用 **Chain-of-Thought（CoT）**，会在输出响应前经历多个隐藏轮次的“思考”。对 Agent 来说，这意味着更高的**路径可靠性**：模型不容易陷入无限循环，也不容易重复执行同一个失败动作，因为它已经在内部模拟过失败。

### Q：如何防止长时间任务中的“Agent 漂移”？

**强回答：**

Agent 漂移发生在子步骤把 Agent 带离原始目标太远、导致它失去上下文时。标准解决方案是**目标锚定**：把“原始目标”作为固定的系统消息，并使用**次级观察模型**（更小、更便宜的模型）将每个 Agent 动作与原始目标进行比较打分。如果分数低于阈值，就强制 Agent 从根目标重新规划。

---

## 参考资料

- Kahneman，D.，《Thinking, Fast and Slow》（应用于 AI，2025）
- OpenAI，《Learning to Reason with LLMs》（2024）
- DeepSeek，《R1: Cold-Start Data for Reasoning》（2025）

---

*下一篇：[推理循环：ReAct 及其后续](02-reasoning-loops-react-and-beyond.md)*
