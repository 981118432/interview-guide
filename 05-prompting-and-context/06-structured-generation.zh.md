# 结构化生成

结构化生成是强制 LLM 以机器可读格式（JSON、YAML、CSV）输出，并达到 100% 可靠性的过程。这项实践已经从“基于 Prompt 的请求”转向“引擎级约束”。

## 目录

- [JSON Mode 革命](#json-mode)
- [函数调用与工具使用](#function-calling)
- [约束解码（CFG 与正则）](#constrained-decoding)
- [多阶段抽取模式](#multi-stage)
- [校验与格式错误](#validation)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## JSON Mode 革命

过去，获得 JSON 往往要苦苦要求“只返回 JSON，不要其他文本”。
**标准方式**：使用原生 `response_format: { type: "json_schema" }`（OpenAI/Gemini），或使用工具输出 Schema（Anthropic）。

- **收益**：100% 的语法有效性。模型实际上无法输出不是合法 JSON 的字符串。
- **幕后机制**：服务引擎在每一步都对词表进行掩码，确保下一步只能选择合法 JSON 字符（例如 `{`、`"`、`:`、`[`）。

---

## 函数调用与工具使用

函数调用是一种结构化生成：LLM“选择”一个函数并填充它的参数。

```json
// Example Tool Call
{
  "name": "get_stock_price",
  "arguments": { "symbol": "AAPL", "interval": "1d" }
}
```

**细节**：**并行函数调用**现在已经成为标准。模型可以决定同时调用 5 个不同工具（例如同时查询账户余额、信用评分和贷款利率），再聚合结果。

---

## 约束解码（CFG 与正则）

对于自托管模型（Llama-cpp、通过 Outlines 使用的 vLLM），我们使用**上下文无关文法（CFG）**或**正则表达式**。

```python
# Outlines Pattern
model = outlines.models.transformers("meta-llama/Llama-4-8B")
generator = outlines.generate.regex(model, r"(\d{3})-\d{3}-\d{4}")
# Result: The model can ONLY output telephone numbers.
```

---

## 多阶段抽取模式

对于复杂的数据抽取（例如从医疗记录中提取 50 个字段），不要一次完成。
- **阶段 1（文本到文本）**：用自然语言抽取一套“杂乱但完整”的事实。
- **阶段 2（文本到 JSON）**：使用更小、更便宜的模型，把这些自然语言事实转换成严格的 JSON Schema。
- **收益**：减少“高压下的幻觉”——当被迫同时进行推理并遵守严格语法时，大模型反而容易出错。

---

## 校验与格式错误

即使使用“JSON Mode”，JSON 内部的**逻辑**也可能错误（例如缺少字段，或日期格式错误）。

**恢复模式：**
1. 使用 **Pydantic/Zod** 校验输出。
2. 如果失败，把**Traceback**发回模型：“错误：字段 `age` 必须是整数，但得到的是 `twenty`。请修复并重新生成。”
3. 大多数模型第一次重试就能修正错误。

---

## 面试问题

### Q：为什么“JSON Mode”比基于 Prompt 的 JSON 请求更可靠？

**强回答：**

基于 Prompt 的请求依赖模型“愿意”遵守指令；“JSON Mode”（或约束解码）依赖服务引擎“无法”做其他事情。通过在推理层应用“Logit Bias”或“Grammar Mask”，引擎把下一个 Token 的选择限制为符合 Schema 的合法 Token。这会消除“开场白”（例如“好的，以下是你的 JSON……”），也保证不会因为高温度或随机性得到格式错误的字符串。

### Q：一次让 LLM 输出太多结构化字段有什么风险？

**强回答：**

这涉及**Schema 复杂度**与**信息完整性**的权衡。随着 Schema 变大（例如 20 个以上的层级字段），模型的注意力会被用于维护 JSON 结构（括号、Key、引号），而不是核验数据准确性。这经常导致“遗漏型幻觉”：模型跳过字段，或用占位数据填充。缓解方式是使用“Chain-of-Density”抽取，或把抽取拆成多个并行子任务。

---

## 参考资料

- OpenAI，《Structured Outputs Documentation》（2024 年 8 月更新）
- Outlines Project，《Context-Free Grammar Guided Generation》（2024）
- Willard 等，《Efficient Guided Generation for LLMs》（2023）

---

*下一篇：[Prompt 优化（DSPy）](07-prompt-optimization-dspy.md)*
