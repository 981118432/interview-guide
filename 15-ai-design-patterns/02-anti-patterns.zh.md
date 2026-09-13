# AI 反模式

本页与英文原文逐段对应，保留标题层级、列表、表格、代码、公式、链接和面试问答。

知道哪些事情不该做，与掌握最佳实践同样重要。本章整理 AI 系统设计中的常见错误。

## 目录

- [架构反模式](#architecture-anti-patterns)
- [RAG 反模式](#rag-anti-patterns)
- [Agent 反模式](#agent-anti-patterns)
- [Prompt 反模式](#prompting-anti-patterns)
- [评测反模式](#evaluation-anti-patterns)
- [生产反模式](#production-anti-patterns)
- [面试问题](#interview-questions)

---

## 架构反模式

### 上帝 Prompt

**问题：**试图处理所有事情的单一超大 Prompt。

```python
# ANTI-PATTERN: God Prompt
SYSTEM_PROMPT = """
You are a helpful assistant. You can:
1. Answer questions about our products
2. Help with technical support
3. Process refunds
4. Schedule appointments
5. Translate languages
6. Write code
7. Analyze data
8. Generate reports
... [continues for 5000 tokens]
"""
```

**失败原因：**
- 上下文被指令消耗，而不是用于用户内容。
- 模型难以处理相互冲突的指令。
- 不可能针对所有情况优化。
- 一次更新会影响所有场景。

**解决方案：**
```python
# PATTERN: Specialized components
class QueryRouter:
    async def route(self, query: str) -> str:
        intent = await self.classify_intent(query)
        handler = self.handlers[intent]
        return await handler.process(query)
```

---

### 单供应商依赖

**问题：**整个系统依赖单一 LLM 供应商。

```python
# ANTI-PATTERN: Single provider
async def generate(prompt: str) -> str:
    return await openai.chat.completions.create(...)
```

**失败原因：**
- 供应商宕机等于整个系统失败。
- 限流会影响全部流量。
- 没有议价空间。
- 被锁定在一个模型家族中。

**解决方案：**
```python
# PATTERN: Multi-provider with failover
class LLMClient:
    def __init__(self):
        self.providers = [OpenAI(), Anthropic(), Google()]
    
    async def generate(self, prompt: str) -> str:
        for provider in self.providers:
            try:
                return await provider.generate(prompt)
            except ProviderError:
                continue
        raise AllProvidersFailedError()
```

---

### 过早微调

**问题：**还没有穷尽简单方案就开始微调。

**失败原因：**
- 成本高且耗时。
- 需要高质量训练数据（通常并不具备）。
- 难以更新和维护。
- 很多时候并无必要。

**决策流程：**
```
Try prompting first
    ↓ (not working)
Try few-shot examples
    ↓ (not working)
Try RAG for knowledge
    ↓ (not working)
Consider fine-tuning (with 500+ examples)
```

---

## RAG 反模式

### 检索一切

**问题：**不考虑相关性，检索过多文档。

```python
# ANTI-PATTERN: Retrieve everything
results = vector_db.search(query, top_k=50)
context = "\n".join([r.text for r in results])
```

**失败原因：**
- 噪声淹没有效信号。
- 超出上下文限制。
- 在无关内容上浪费 Token。
- 产生“中间丢失”效应。

**解决方案：**
```python
# PATTERN: Quality over quantity
results = vector_db.search(query, top_k=20)
reranked = await reranker.rerank(query, results)
context = "\n".join([r.text for r in reranked[:5] if r.score > 0.7])
```

---

### 没有切块策略

**问题：**文档切块随意，或完全不切块。

```python
# ANTI-PATTERN: Fixed-size blind chunking
chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
```

**失败原因：**
- 在句子或段落中间截断。
- 丢失语义连贯性。
- 将相关信息分开。
- 检索质量差。

**解决方案：**
```python
# PATTERN: Semantic-aware chunking
chunks = semantic_chunker.chunk(
    text,
    chunk_size=500,
    overlap=100,
    respect_boundaries=["paragraph", "section"]
)
```

---

### 忽略元数据

**问题：**把所有文档当作地位相同的纯文本。

```python
# ANTI-PATTERN: Ignore metadata
embedding = embed(document.text)
vector_db.insert(embedding, {"text": document.text})
```

**失败原因：**
- 无法按日期、来源和类型过滤。
- 无法按文档实施访问控制。
- 无法区分新旧内容权重。
- 丢失有价值的上下文。

**解决方案：**
```python
# PATTERN: Rich metadata
vector_db.insert(embedding, {
    "text": document.text,
    "source": document.source,
    "date": document.date,
    "access_level": document.access_level,
    "document_type": document.type,
    "section": document.section
})

# Filter query
results = vector_db.search(
    query,
    filter={"date": {"$gte": "2024-01-01"}, "access_level": user.level}
)
```

---

## Agent 反模式

### 无限循环风险

**问题：**Agent 没有终止条件。

```python
# ANTI-PATTERN: No limits
while not done:
    action = await agent.decide_action()
    result = await execute(action)
    done = agent.check_done(result)
```

**失败原因：**
- Agent 可能无限循环。
- 成本螺旋式失控。
- 永远无法返回用户结果。
- 耗尽资源。

**解决方案：**
```python
# PATTERN: Multiple termination conditions
MAX_STEPS = 20
MAX_COST = 10.0
MAX_TIME = 300  # seconds

for step in range(MAX_STEPS):
    if cost_tracker.total > MAX_COST:
        return "Cost limit reached"
    if time.time() - start > MAX_TIME:
        return "Time limit reached"
    
    action = await agent.decide_action()
    result = await execute(action)
    
    if agent.check_done(result):
        return result
    
return "Step limit reached"
```

---

### 不安全的工具访问

**问题：**赋予 Agent 不受限制的工具访问权限。

```python
# ANTI-PATTERN: Full access
tools = [
    delete_file,
    execute_shell_command,
    send_email,
    database_query  # unrestricted!
]
```

**失败原因：**
- Agent 可以删除关键文件。
- 可以外传数据。
- 可以执行恶意命令。
- 没有审计轨迹。

**解决方案：**
```python
# PATTERN: Scoped, validated tools
tools = [
    ScopedFileTool(allowed_dirs=["/tmp/agent"]),
    RestrictedShellTool(allowed_commands=["ls", "cat"]),
    EmailTool(requires_confirmation=True),
    ReadOnlyDatabaseTool(allowed_tables=["products"])
]
```

---

### 没有记忆的 Agent

**问题：**Agent 每一轮都从头开始。

```python
# ANTI-PATTERN: Stateless agent
async def handle_message(message: str) -> str:
    return await agent.run(message)  # No context
```

**失败原因：**
- 无法完成多轮任务。
- 重复同样的错误。
- 无法从经验中学习。
- 用户体验差。

**解决方案：**
```python
# PATTERN: Persistent memory
async def handle_message(session_id: str, message: str) -> str:
    memory = await memory_store.get(session_id)
    response = await agent.run(message, memory=memory)
    await memory_store.update(session_id, memory)
    return response
```

---

## Prompt 反模式

### 模糊指令

**问题：**Prompt 含义模糊，却期望模型表现出特定行为。

```python
# ANTI-PATTERN: Vague
prompt = "Help the user with their request."
```

**失败原因：**
- “帮助”没有明确定义。
- 没有指定格式。
- 没有边界。
- 行为不一致。

**解决方案：**
```python
# PATTERN: Specific and structured
prompt = """
You are a customer support agent for TechCorp.

Your role:
- Answer questions about our products
- Help troubleshoot issues
- Escalate to human when unsure

Response format:
1. Acknowledge the issue
2. Provide a solution or ask clarifying questions
3. Offer next steps

Do NOT:
- Make promises about refunds (escalate instead)
- Provide legal or medical advice
- Share internal company information
"""
```

---

### 没有输出格式

**问题：**不指定格式，却期望结构化输出。

```python
# ANTI-PATTERN: Hope for structure
prompt = "Extract the person's name, date, and location from this text."
response = await llm.generate(prompt)
# Response: "The person is John, he was there on March 5th in NYC"
# Now try to parse that...
```

**解决方案：**
```python
# PATTERN: Explicit format
prompt = """
Extract information and return as JSON:
{
    "name": "string",
    "date": "YYYY-MM-DD",
    "location": "string"
}

Text: ...
"""
# Or use structured output APIs
response = await llm.generate(prompt, response_format={"type": "json_object"})
```

---

## 评测反模式

### 凭感觉评测

**问题：**把“我觉得看起来不错”当作评测方法。

```python
# ANTI-PATTERN: Manual spot-checking
for i in range(5):
    response = await generate(test_prompts[i])
    print(response)  # Developer looks at it
# "Looks good, ship it!"
```

**失败原因：**
- 不可复现。
- 挑选有利样例。
- 没有基线比较。
- 遗漏边界案例。

**解决方案：**
```python
# PATTERN: Systematic evaluation
eval_dataset = load_eval_set()  # 100+ examples
results = []

for example in eval_dataset:
    response = await generate(example["input"])
    score = await evaluate(response, example["expected"])
    results.append(score)

metrics = {
    "accuracy": sum(results) / len(results),
    "failures": [e for e, r in zip(eval_dataset, results) if r < 0.5]
}
```

---

### Training on Test Set

**问题：**使用评测数据做开发决策。

```python
# ANTI-PATTERN: Overfitting to eval
for iteration in range(100):
    accuracy = evaluate_on_test_set()  # Same set every time
    tweak_prompt_based_on_failures(test_set)  # Optimizing for test set
```

**失败原因：**
- 对特定样例过拟合。
- 真实世界表现不同。
- 无法真正衡量泛化能力。

**解决方案：**
```python
# PATTERN: Proper data splits
dev_set = load_dev_set()      # For iteration
test_set = load_test_set()    # Final evaluation only

# Iterate on dev set
for iteration in range(100):
    accuracy = evaluate(dev_set)
    improve_based_on(dev_set)

# Final evaluation on untouched test set
final_accuracy = evaluate(test_set)
```

---

## Production Anti-Patterns

### No Rate Limiting

**问题：**每个用户可以无限调用 LLM。

```python
# ANTI-PATTERN: Open access
@app.route("/generate")
async def generate():
    return await llm.generate(request.prompt)  # No limits!
```

**失败原因：**
- 单个用户就能耗尽预算。
- 存在拒绝服务风险。
- 成本不可预期。
- 没有公平使用机制。

**解决方案：**
```python
# PATTERN: Rate limiting
@app.route("/generate")
@rate_limit(requests_per_minute=10, requests_per_day=100)
@cost_limit(max_cost_per_day=1.0)
async def generate():
    return await llm.generate(request.prompt)
```

---

### No Caching

**问题：**每个相同请求都重新调用 LLM。

```python
# ANTI-PATTERN: No cache
async def answer_faq(question: str) -> str:
    return await llm.generate(question)  # Same FAQ, same cost every time
```

**失败原因：**
- 为相同查询浪费资金。
- 增加不必要的延迟。
- 同一个问题得到不一致的答案。

**解决方案：**
```python
# PATTERN: Semantic caching
async def answer_faq(question: str) -> str:
    cached = await cache.get_similar(question, threshold=0.95)
    if cached:
        return cached.response
    
    response = await llm.generate(question)
    await cache.set(question, response)
    return response
```

---

## 面试问题

### Q：你在 LLM 应用中看到的最大反模式是什么？

**强回答：**

“危害最大的是‘上帝 Prompt’反模式：用一个超大 Prompt 处理所有场景。

**它常见的原因：**从一个 Prompt 开始、随着需求增加指令，看起来更简单。

**失败原因：**
- 上下文被指令消耗，而不是用于用户内容。
- 相互冲突的指令会混淆模型。
- 无法针对不同用例优化。
- 变更会产生不可预测的副作用。

**修复方式：**将请求路由到专用处理器。每个处理器都有针对单一任务优化的聚焦 Prompt。路由器可以很简单（基于关键词），也可以更智能（复杂场景使用 LLM）。

这不仅适用于 Prompt。一般原则是：把复杂性拆分到专业组件中，而不是把所有东西塞进一个巨型单体。”

### Q：如何避免 Agent 成本失控？

**强回答：**

“在不同层级设置多种限制：

**单请求限制：**
- 最大步数（例如 20）。
- 最大 Token 数（例如 5 万）。
- 最大时间（例如 5 分钟）。

**单会话限制：**
- 每日 Token 预算。
- 每日成本上限。

**单用户限制：**
- 限流（每分钟/小时/天请求数）。
- 成本归因与上限。

**监控：**
- 实时成本跟踪。
- 异常告警（单请求 > 1 美元）。
- 成本激增时熔断。

**架构：**
- 从便宜模型级联到昂贵模型。
- 缓存常见操作。
- 批处理相似请求。

关键是预设 Agent 会试图永远运行，在每一层加入硬停止条件。没有适当限制时，Agent 几分钟就可能产生 1000 美元账单。”

---

*Previous: [Design Patterns](01-design-patterns.md)*
