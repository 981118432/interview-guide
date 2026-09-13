# Prompt Engineering 基础

Prompt Engineering 是设计输入以引导 LLM 行为的过程。它已经从“试错”发展为一种有纪律的架构实践，DSPy 等框架甚至把它视为编译问题，而不只是写作练习。

## 目录

- [核心理念（意图 + 约束）](#core-philosophy)
- [指令层级](#instruction-hierarchy)
- [角色 Prompt](#role-prompting)
- [指令清晰度与分隔符](#clarity)
- [Zero-Shot 与 Few-Shot 效率](#zero-vs-few)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## 核心理念：意图 + 约束

有效的 Prompt，关键是最大化**意图披露**，同时最小化**输出方差**。

1. **意图**：模型具体应该做什么。
2. **约束**：模型具体应该*避免*什么（安全、语气、格式）。

**原则**：“Prompting 就是用自然语言编程。”要像对待代码一样对待 Prompt（版本控制、单元测试）。

---

## 指令层级

生产系统使用分层的消息结构：

| 角色 | 职责 | 细节 |
|------|------|------|
| **System** | 高层规则、人格、安全。 | 对前沿模型最有粘性（H-rank）。 |
| **Developer** | 技术覆盖规则（例如格式）。 | 面向“无主见”模型的新角色。 |
| **User** | 具体的动态查询。 | 容易受到注入，必须隔离。 |
| **Assistant** | 之前轮次的历史。 | “近因偏差”的来源。 |

---

## 角色 Prompt

分配人格不再只是说“你是一名教师”，而是一个**能力锚点**。

- **弱**：“你是一名程序员。”
- **强**：“你是一家一线科技公司的 Staff 软件工程师，专长是高并发 Rust 系统。你优先考虑内存安全和零成本抽象。”

**为什么有效**：它把模型的注意力集中到训练数据中与该高层专业能力相关的子集，减少无关幻觉。

---

## 指令清晰度与分隔符

当前的前沿模型能够处理巨大的上下文。分隔符帮助模型区分指令和数据。

```markdown
# Instructions
Analyze the following text for PII.

# Data to Analyze
--- START OF USER DATA ---
$USER_INPUT_HERE
--- END OF USER DATA ---

# Output Schema
{ "pii_found": boolean, "types": [] }
```

**可使用的分隔符**：XML 标签（`<context>`、`</context>`）、Markdown 标题（`#`）或三引号（`"""`）。

---

## Zero-Shot 与 Few-Shot 效率

| 方面 | Zero-Shot | Few-Shot |
|------|-----------|----------|
| **延迟** | 最低（Prompt 短） | 更高（包含示例 Token） |
| **准确率** | 不稳定 | 高（格式稳定） |
| **使用场景** | 简单聊天、摘要 | 特定格式、细微逻辑 |

**策略**：如果模型是“前沿推理”模型（Claude Opus 4.7、开启扩展思考的 GPT-5.5、DeepSeek-R2），使用 **Zero-Shot + 清晰的 Chain-of-Thought**。如果是小模型（8B），使用 **Few-Shot** 为其提供锚定。

---

## 面试问题

### Q：为什么在现代 LLM 中，系统 Prompt 比用户 Prompt 权重更高？

**强回答：**

系统 Prompt 通常通过模型的架构训练（RLHF）获得更高优先级，在某些架构中还可能被注入特殊的“仅指令”嵌入空间。从设计角度看，系统 Prompt 定义了交互的“宪法”。如果用户 Prompt 与系统 Prompt 冲突（例如要求制作炸弹），一个对齐良好的模型会被训练为优先遵守系统的“安全约束”，而不是用户的“任务意图”。

### Q：什么是“逐步思考” Prompt 优化？

**强回答：**

2022 年，“一步一步思考”是触发 Chain-of-Thought（CoT）的魔法短语。现代做法是**程序化 CoT**。不使用模糊短语，而是给出明确的推理里程碑：“1. 识别核心问题。2. 列出约束。3. 提出 3 个方案。4. 选择最佳方案并说明理由。”这为模型的内部注意力提供了“确定性路径”，让生产 Agent 的输出可靠得多。

---

## 参考资料

- OpenAI，《Prompt Engineering Guide》（2024-2025）
- Anthropic，《Claude Prompt Engineering Documentation》（2024）
- Google DeepMind，《The Power of Prompting》（2023）

---

*下一篇：[Few-Shot 与上下文学习](02-few-shot-and-icl.md)*
