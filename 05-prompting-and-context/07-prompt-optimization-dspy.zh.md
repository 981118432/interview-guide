# Prompt 优化（DSPy）

Prompt 已经从“手工调参”时代进入“程序化”时代。**DSPy（Declarative Self-improving Language Programs，声明式自改进语言程序）**是构建稳健 LLM 流水线的事实标准，它通过算法自动优化 Prompt。3.x 系列（DSPy 3.1.3 于 2026 年 2 月 5 日发布，之后到 2026 年 5 月持续发布小版本）加强了与原生推理模型的集成，并提供更清晰的异步运行时。

## 目录

- [DSPy 理念：编程与 Prompt](#philosophy)
- [Signature 与 Module](#signatures-modules)
- [Teleprompter（优化器）](#optimizers)
- [“Prompt 即权重”类比](#prompt-as-weight)
- [指标驱动优化](#metrics)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## DSPy 理念：编程与 Prompt

在传统 Prompt 中，更换模型（例如从 GPT-5.5 换到 Claude Sonnet 4.6 或 Llama 4）需要重写全部 Prompt。
**DSPy 把逻辑与格式分离。**

- **逻辑**：由 **Module** 定义（例如 ChainOfThought、ReAct）。
- **优化**：系统自动为特定模型找到最好的 Prompt 和示例，让它完成这段逻辑。

---

## Signature 与 Module

不再编写 Prompt，而是定义一个 **Signature**：输入是什么，输出应该是什么。

```python
# Signature pattern
class MultiHopQA(dspy.Signature):
    """Answer questions that require multiple context retrievals."""
    context = dspy.InputField()
    question = dspy.InputField()
    answer = dspy.OutputField(desc="A concise 1-sentence answer")

# Logic is handled by a Module
qa_system = dspy.ChainOfThought(MultiHopQA)
```

---

## Teleprompter（优化器）

Teleprompter 是反复迭代程序以提升准确率的算法。
1. **BootstrapFewShot**：自动为 Prompt 找到高质量示例。
2. **MIPROv2**：尝试不同指令措辞，并选择能最大化得分的贝叶斯优化器。它仍然是 3.x 系列的旗舰优化器。

**重要性**：你不再需要猜“Be helpful”还是“Think carefully”更好，优化器会用数据证明答案。

---

## “Prompt 即权重”类比

在 DSPy 中，Prompt 就像神经网络中的权重。你不会把权重“硬编码”进去，而是训练它们。
- 如果更换模型，只需**重新编译**（重新训练）程序。优化器会找到新模型更容易理解的新 Few-Shot 示例。

---

## 指标驱动优化

优化需要一个 **Metric**（返回分数的函数）。
- **Exact Match**：`prediction.answer == target.answer`
- **LLM-as-Judge**：使用更大的模型（Claude Opus 4.7、GPT-5.5 reasoning）评估小模型（Llama 4 8B、Claude Haiku 4.5）的输出。

---

## 面试问题

### Q：DSPy 如何解决 Prompt Engineering 的“脆弱性”？

**强回答：**

DSPy 把“格式”和“锚定”的复杂性从人转移到编译器中。手写 Prompt，实际上是在把特定时间点、特定模型的行为“硬编码”进去（时间点调优）。如果模型更新或更换，Prompt 就会失效。DSPy 把 Prompt 当作可学习参数。通过定义清晰的 **Signature** 和 **Metric**，我们让系统通过数千次模拟迭代“搜索”最有效的 Prompt，使最终系统更能适应模型变化。

### Q：DSPy 中的“Teleprompter”是什么？

**强回答：**

Teleprompter 是程序化优化器。它接收一个 DSPy 程序（可能是由多个 Module 组成的复杂链）和一小组训练示例，然后把它们“编译”为优化版本。它会生成潜在的“思考模式”和示例，根据 Metric 测试它们，再选择最有效的组合。简而言之，Teleprompter 就是 Prompt Engineering 世界里的“梯度下降”。

---

## 参考资料

- Khattab 等，《DSPy: Compiling Declarative Language Models》（2023/2024）
- Stanford NLP，《DSPy Documentation and Tutorials》（2025）

---

*下一篇：[Prompt 注入与防御](08-prompt-injection-defense.md)*
