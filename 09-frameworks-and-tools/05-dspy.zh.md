# DSPy：编程语言模型

**DSPy** 已成为高可靠 AI 系统的行业参考。它代表了从“Prompt 工程”（反复试错）到**Prompt 编译**（自动优化）的范式转变，基准测试持续显示，相比人工调优的 Prompt，质量可以提升 10%～40%。

## 目录

- [编程范式](#paradigm)
- [Signature：描述任务](#signatures)
- [优化器与 MIPROv2](#optimizers)
- [断言与约束](#assertions)
- [管理模型漂移](#model-drift)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## 编程范式

DSPy 把 LLM 应用看作一个**神经网络**。
- **模块**：可复用的逻辑块（例如 `ChainOfThought`）。
- **Signature**：描述模块行为的声明式规范（输入 -> 输出）。
- **优化器**：根据指标寻找模块最佳“权重”（Prompt）的过程。

---

## Signature：描述任务

你不再编写 100 行 Prompt，而是编写一个**Signature**：
```python
class ResearchAssistant(dspy.Signature):
    """Answer the question by synthesizing the provided web context."""
    context = dspy.InputField(desc="Scraped web content")
    question = dspy.InputField()
    answer = dspy.OutputField(desc="A technical summary with citations")
```
**关键细节**：Signature 与**模型无关**。你可以把它编译到 Claude Opus 4.7、Claude Sonnet 4.6、GPT-5.5、Gemini 3.1 Pro 或 Llama 4 8B，而无需修改任何一行代码。

---

## 优化器与 MIPROv2

**MIPROv2（多阶段指令提议优化器）**是 DSPy 的旗舰优化器。
1. **指令提议**：“辅助模型”为该任务提出 10～20 种不同的系统 Prompt 写法。
2. **贝叶斯优化**：DSPy 在小型训练集上运行这些 Prompt，并使用指标给它们评分。
3. **选择**：挑选使指标（例如事实性分数）最大化的 Prompt。

---

## 断言与约束

DSPy 支持**硬断言和软断言**。
- `dspy.Suggest(...)`：如果模型未通过检查（例如“答案必须少于 50 个词”），DSPy 会自动带着失败原因重新提示模型，让它自行修正。
- `dspy.Assert(...)`：如果违反硬约束（例如“不能包含 PII”），执行会停止并进入恢复状态。

---

## 管理模型漂移

当 OpenAI 或 Anthropic 发布权重更新时，人工编写的 Prompt 往往会失效。
- **2025 年的解决方案**：使用 DSPy 时，只需**重新编译**。优化器会为更新后的模型架构找到新的“最优” Token，无需人工劳动即可保持一致性。

---

## 面试问题

### Q：为什么说 DSPy 是“反 Prompt 工程”？

**强回答：**
因为它用**优化循环**替代了**人工反复试错循环**。在 Prompt 工程中，人是优化器；在 DSPy 中，人是**教师**。你定义*目标*（Signature）和*评估方式*（Metric），并提供少量*示例*。然后框架使用数学优化（如贝叶斯搜索）寻找统计表现最好的 Token。这让系统相比一套硬编码字符串更具**可移植性**和**可扩展性**。

### Q：在生产环境使用 DSPy 最大的缺点是什么？

**强回答：**
**编译延迟和成本**。编译复杂的 DSPy 流水线，可能需要运行 100～500 次 LLM 调用来测试不同的 Prompt 变体，这会产生显著的前期成本。不过对 Staff 级工程师来说，这是一个**权衡**：用更多开发/编译时间换取**可保证的可靠性**和更低的**运行时失败率**。另一个挑战是学习曲线：它要求你像 ML 研究人员一样思考，而不是像传统开发者一样思考。

---

## 参考资料
- Khattab 等：《DSPy: Compiling Declarative Language Model Calls》（2024/2025）
- Stanford NLP：《The MIPROv2 Technical Report》（2025）
- Databricks：《Productionizing Programmed Prompts》（2025）

---

*下一篇：[Semantic Kernel：企业 AI](06-semantic-kernel.md)*
