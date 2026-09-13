# Chain-of-Thought（CoT）

Chain-of-Thought（CoT）是鼓励 LLM 在给出最终答案前生成中间推理步骤的技术。它已经从一个简单的 Prompt 短语发展为推理模型的核心架构特征（o1、DeepSeek-R2、开启扩展思考的 Claude Opus 4.7、开启扩展思考的 GPT-5.5）。

## 目录

- [CoT 革命](#cot-revolution)
- [Zero-Shot 与程序化 CoT](#zero-vs-programmatic)
- [“思考”模型的兴起（o1、DeepSeek-R1）](#thinking-models)
- [自我纠错与验证](#self-correction)
- [CoT 失败时（过度思考）](#over-thinking)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## CoT 革命

标准 LLM 是“下一个 Token 预测器”。对于复杂数学或逻辑问题，一次前向往往不够。CoT 为模型提供了一个“草稿纸”（工作记忆），用来处理子问题。

**公式**：`Input -> Reasoning (Chain) -> Output`

---

## Zero-Shot 与程序化 CoT

| 技术 | 触发短语 | 效率 | 使用场景 |
|------|----------|------|----------|
| **Zero-Shot CoT** | “Let’s think step by step.” | 高 | 临时查询。 |
| **Few-Shot CoT** | （提供带逻辑的示例） | 稳定性更高 | 生产流水线。 |
| **程序化 CoT** | “1. 分析 X。2. 验证 Y。3. 解决 Z。” | **最适合 Agent** | 复杂多工具任务。 |

---

## “思考”模型的兴起

**OpenAI o1/GPT-5.5 扩展思考**、**DeepSeek-R2** 和 **Claude Opus 4.7** 等模型通过强化学习（RL）把 CoT“内置”进模型。

1. **系统级 CoT**：模型不只是“打印”推理，而是拥有专用的“思考窗口”。
2. **隐藏 CoT**：在许多企业版本中，推理链对用户隐藏，但系统仍可验证，以防止 Prompt 注入或“思维泄漏”。
3. **扩展规律**：这些模型遵循**推理扩展规律**——它们“思考”越久，解决难题的能力越强（给足时间，$o1$ 可以解决国际数学奥林匹克金牌级数学题）。

---

## 自我纠错与验证

生产流水线不再信任单条 Chain-of-Thought，而是叠加**自验证**。

```markdown
# Process
1. Generate Answer A via CoT.
2. Critique: "Are there any errors in the logic above?"
3. If errors: "Correct the logic and provide Answer B."
```

**细节**：现在这已经融入面向代码的**执行验证 CoT**：模型编写逻辑、运行代码，如果代码失败就自行修正。

---

## CoT 失败时（过度思考）

CoT 不是万能药。对于简单任务，它会增加：
1. **延迟**：Token 越多，响应越慢。
2. **成本**：每个“思考”Token 都需要付费。
3. **过度思考**：模型可能在没有复杂性的地方凭空制造复杂性（例如用 3 段话解释为什么 2+2=4）。

---

## 面试问题

### Q：为什么 CoT 能提升数学应用题的表现？

**强回答：**

CoT 让模型的计算复杂度与任务的逻辑复杂度相匹配。在标准的单次前向生成中，模型必须依据有限的局部信息预测最终答案 Token。使用 CoT 后，模型把问题拆成更小的自回归步骤。每一步都把上一步的输出作为上下文，让模型的注意力机制一次聚焦一个子问题（例如先加苹果，再减橙子），降低单次预测的“认知负荷”。

### Q：在延迟关键的生产环境中，如何处理 CoT？

**强回答：**

我们使用**混合推理架构**：
1. **Tier 1（快速）**：分类器识别查询是否需要深度推理。
2. **Tier 2（压缩 CoT）**：用“推理要简洁”提示模型，或者使用“知识蒸馏”，训练小模型只输出最终答案，同时受益于教师模型的 CoT 式预训练。
3. **Tier 3（流式）**：如果需要透明，就把 CoT 流式展示给用户；否则交给后台进程，这样系统可以在最终结果逐步出现时开始“预处理”。

---

## 参考资料

- Wei 等，《Chain-of-Thought Prompting Elicits Reasoning in Large Language Models》（2022）
- Wang 等，《Self-Consistency Improves Chain of Thought Reasoning in Language Models》（2023）
- OpenAI，《Learning to Reason with LLMs》（2024）

---

*下一篇：[Tree-of-Thought](04-tree-of-thought.md)*
