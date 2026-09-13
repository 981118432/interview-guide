# LangSmith 可观测性

2023 年，LLM 可观测性只是“记录字符串”。如今它已经发展为**完整轨迹调试**和**自动评测流水线**。LangSmith 是 LangChain 原生的方案，属于竞争激烈的“LLMOps”层；该层还包括 Langfuse（于 2026 年 1 月被 ClickHouse 收购）、LangWatch、Braintrust 和 Arize Phoenix。

## 目录

- [可观测性金字塔](#pyramid)
- [追踪与轨迹](#tracing)
- [LLM 单元测试（数据集）](#datasets)
- [自动评估器（LLM-as-Judge）](#evaluators)
- [部署管理：A/B 测试](#ab-testing)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## 可观测性金字塔

1. **顶部（价值）**：用户任务是否完成？（成功率）
2. **中部（流程）**：哪个 Agent 节点是瓶颈？（每个节点的延迟/成本）
3. **底部（原始数据）**：准确的 Prompt/Completion 对是什么？（轨迹）

---

## 追踪与轨迹

LangSmith 会自动捕获 **LangGraph** 或 **Chain** 中的每个节点。
- **元数据标注**：为每条轨迹标注 `user_id`、`model_tier` 和 `is_canary`。
- **调试器**：可以在 LangSmith UI 中“回放”轨迹，修改 Prompt 并观察响应如何变化，而不必重新运行整个应用。

---

## LLM 单元测试（数据集）

没有**数据集**就构建 LLM 应用，是“凭感觉开发”。
- **黄金数据集**：由 `(Input, Expected_Output)` 对组成的集合。
- **标准流程**：每当用户提供负面反馈，就自动把这次交互送入“纠正数据集”，供未来测试。

---

## 自动评估器

你不可能每天早上手动检查 1,000 条日志。
- **LLM-as-Judge**：使用更强的模型（Claude Opus 4.7、GPT-5.5 reasoning、DeepSeek-R2），从**语气**、**准确性**和**安全动作执行**等维度给生产模型打分。
- **自定义评估器**：检查正则表达式、JSON Schema 有效性或毒性分数的 Python 函数。

---

## A/B 测试

LangSmith 支持**实验分支**。
- 让 2% 的流量使用新的“系统 Prompt”版本。
- 实时比较**成功率**和**Token 成本**。
- 如果失败率超过阈值，自动回滚。

---

## 面试问题

### Q：为什么“轨迹归因”对 Staff 级工程师至关重要？

**强回答：**
在复杂的多 Agent 系统中，最终输出可能很糟，但错误可能在 10 步之前的“研究员”节点就发生了。没有**轨迹归因**，你只能猜应该在哪里修 Prompt。归因让我看到**推理链路**：我可以看到“研究员”没有找到正确 URL，导致“摘要器”产生幻觉。这样就能进行**定向优化**，而不是泛泛地做“Prompt 工程”。

### Q：如何证明 LangSmith 这类可观测性平台的成本合理？

**强回答：**
成本会被**开发者生产力**和**Token 效率**抵消。工程师花一天“猜测”模型为什么失败，其成本通常显著高于一个月的订阅费。此外，使用 LangSmith 找出“游荡”的 Agent（步骤过多的 Agent）后，我可以优化图，把平均步骤数从 8 步降到 5 步，直接带来 **30%～40% 的 LLM API 账单降低**。

---

## 参考资料
- LangChain 团队：《LangSmith: The Unified Evaluation Platform》（2025）
- Microsoft：《Tracing and Debugging Multi-Agent Systems》（2025）
- Weights & Biases：《Integrating LLOps into the CI/CD Pipeline》（2024/2025）

---

*下一篇：[LlamaIndex 与数据中心 AI](04-llamaindex.md)*
