# AI 设计模式

本页与英文原文逐段对应，保留标题层级、列表、表格、代码、公式、链接和面试问答。

本章整理构建 AI 系统时常见的模式，类似于软件工程中的设计模式。每个模式都说明适用场景、实现建议和权衡。

## 目录

- [RAG 模式](#rag-patterns)
- [Agent 模式](#agent-patterns)
- [优化模式](#optimization-patterns)
- [可靠性模式](#reliability-patterns)
- [成本模式](#cost-patterns)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## RAG 模式

### 模式：朴素 RAG

最简单的 RAG 实现：

```
Query → Embed → Search → Top K → Stuff into prompt → Generate
```

**适用场景：**
- MVP 和原型开发。
- 简单问答。
- 检索质量已经足够时。

**局限：**
- 没有重排序。
- 没有查询增强。
- 可能检索到不相关分块。

---

### 模式：高级 RAG

包含多个阶段的增强流水线：

```
Query → Rewrite → Embed → Hybrid Search → Rerank → Filter → Generate
```

```python
class AdvancedRAG:
    async def query(self, user_query: str) -> str:
        # Step 1: Query rewriting
        enhanced_query = await self.rewrite_query(user_query)
        
        # Step 2: Hybrid retrieval
        semantic_results = await self.vector_search(enhanced_query, top_k=50)
        keyword_results = await self.bm25_search(enhanced_query, top_k=50)
        
        # Step 3: Fusion
        combined = self.reciprocal_rank_fusion(semantic_results, keyword_results)
        
        # Step 4: Reranking
        reranked = await self.rerank(enhanced_query, combined[:20])
        
        # Step 5: Generation with top results
        context = self.format_context(reranked[:5])
        return await self.generate(user_query, context)
```

**适用场景：**
- 生产系统。
- 对准确性要求高时。
- 文档集合复杂时。

---

### 模式：父子检索

检索小分块，但返回更大的父分块：

```
Document
    └── Parent chunk (2000 tokens)
            ├── Child chunk (200 tokens) ← Retrieve on this
            ├── Child chunk (200 tokens)
            └── Child chunk (200 tokens)
```

```python
class ParentChildRetriever:
    def __init__(self, vector_store):
        self.vector_store = vector_store
    
    async def retrieve(self, query: str, top_k: int = 5) -> list[str]:
        # Search on child chunks (more precise)
        child_results = await self.vector_store.search(
            query, 
            collection="child_chunks",
            top_k=top_k * 3
        )
        
        # Get unique parent chunks
        parent_ids = set(r.metadata["parent_id"] for r in child_results)
        
        # Return parent chunks (more context)
        parents = await self.get_parents(list(parent_ids)[:top_k])
        return parents
```

**适用场景：**
- 需要精确检索时。
- 生成阶段需要更多上下文时。
- 文档结构具有层次性时。

---

### 模式：Self-RAG

由模型决定何时检索以及检索什么：

```python
class SelfRAG:
    async def generate(self, query: str) -> str:
        # Step 1: Decide if retrieval is needed
        needs_retrieval = await self.assess_retrieval_need(query)
        
        if needs_retrieval:
            # Step 2: Retrieve
            context = await self.retrieve(query)
            
            # Step 3: Assess relevance
            relevant_context = await self.filter_relevant(query, context)
            
            # Step 4: Generate with context
            response = await self.generate_with_context(query, relevant_context)
            
            # Step 5: Self-critique
            is_supported = await self.check_support(response, relevant_context)
            if not is_supported:
                response = await self.regenerate(query, relevant_context)
        else:
            response = await self.generate_without_context(query)
        
        return response
```

**适用场景：**
- 参数知识与检索知识混合。
- 希望模型有选择地检索。
- 研究和实验。

---

### 模式：纠错 RAG（CRAG）

评估并修正检索质量：

```python
class CorrectiveRAG:
    async def query(self, user_query: str) -> str:
        # Initial retrieval
        docs = await self.retrieve(user_query)
        
        # Grade each document
        graded = []
        for doc in docs:
            grade = await self.grade_relevance(user_query, doc)
            graded.append((doc, grade))
        
        # Categorize results
        relevant = [d for d, g in graded if g == "relevant"]
        ambiguous = [d for d, g in graded if g == "ambiguous"]
        
        if len(relevant) >= 3:
            # Enough relevant docs
            context = relevant
        elif len(relevant) + len(ambiguous) >= 2:
            # Refine ambiguous docs
            refined = await self.refine_search(user_query, ambiguous)
            context = relevant + refined
        else:
            # Web search fallback
            web_results = await self.web_search(user_query)
            context = relevant + web_results
        
        return await self.generate(user_query, context)
```

**适用场景：**
- 文档语料库不可靠。
- 需要高准确率。
- 能够为质量检查承担额外延迟。

---

## Agent 模式

### 模式：ReAct

交替进行推理与行动：

```
Thought → Action → Observation → Thought → Action → Observation → Answer
```

实现方式请参阅 [Agent 架构](../07-agentic-systems/01-agent-fundamentals.md)。

**适用场景：**
- 通用 Agent。
- 需要可解释的决策过程。
- 中等复杂度任务。

---

### 模式：计划与执行

先创建计划，再执行各个步骤：

```python
class PlanAndExecuteAgent:
    async def run(self, task: str) -> str:
        # Step 1: Create plan
        plan = await self.create_plan(task)
        
        # Step 2: Execute each step
        results = []
        for step in plan.steps:
            result = await self.execute_step(step, results)
            results.append(result)
            
            # Re-plan if needed
            if result.needs_replanning:
                plan = await self.replan(task, results)
        
        # Step 3: Synthesize final answer
        return await self.synthesize(task, results)
    
    async def create_plan(self, task: str) -> Plan:
        prompt = f"""
        Create a step-by-step plan to accomplish this task: {task}
        
        Return as JSON:
        {{
            "steps": [
                {{"id": 1, "description": "...", "tool": "..."}},
                ...
            ]
        }}
        """
        return await self.llm.generate(prompt)
```

**适用场景：**
- 复杂的多步任务。
- 需要查看计划。
- 任务适合拆解。

---

### 模式：批评器/验证器

一个 Agent 生成结果，另一个进行批评：

```python
class CriticPattern:
    async def generate_with_critique(self, task: str, max_iterations: int = 3) -> str:
        response = await self.generator.generate(task)
        
        for i in range(max_iterations):
            # Critique the response
            critique = await self.critic.evaluate(task, response)
            
            if critique.is_acceptable:
                break
            
            # Regenerate with feedback
            response = await self.generator.regenerate(
                task, 
                previous=response, 
                feedback=critique.feedback
            )
        
        return response
```

**适用场景：**
- 质量至关重要。
- 能够承担额外延迟。
- 任务有明确成功标准。

---

### 模式：分层 Agent

管理者将任务委派给专业工作 Agent：

```python
class ManagerAgent:
    def __init__(self):
        self.workers = {
            "research": ResearchAgent(),
            "coding": CodingAgent(),
            "writing": WritingAgent()
        }
    
    async def run(self, task: str) -> str:
        # Decompose task
        subtasks = await self.decompose(task)
        
        # Assign to workers
        results = {}
        for subtask in subtasks:
            worker = self.workers[subtask.worker_type]
            results[subtask.id] = await worker.execute(subtask)
        
        # Synthesize results
        return await self.synthesize(task, results)
```

**适用场景：**
- 跨多个领域的复杂任务。
- 不同子任务需要不同工具。
- 存在并行化机会。

---

## 优化模式

### 模式：模型级联

将请求路由到满足要求的最低成本模型：

```python
class ModelCascade:
    def __init__(self):
        self.models = [
            ("gpt-4o-mini", 0.15),     # Cheapest
            ("gpt-4o", 2.50),           # Mid-tier
            ("claude-3.5-sonnet", 3.00) # Most capable
        ]
    
    async def generate(self, query: str) -> str:
        # Classify complexity
        complexity = await self.classify_complexity(query)
        
        if complexity == "simple":
            return await self.call_model("gpt-4o-mini", query)
        elif complexity == "medium":
            return await self.call_model("gpt-4o", query)
        else:
            return await self.call_model("claude-3.5-sonnet", query)
```

**适用场景：**
- 查询量很高。
- 查询复杂度差异大。
- 成本优化优先。

---

### 模式：推测执行

用小模型生成草稿，再用大模型验证：

```python
class SpeculativeExecution:
    async def generate(self, prompt: str, n_tokens: int = 5) -> str:
        output = []
        
        while len(output) < max_tokens:
            # Draft with small model
            draft = await self.draft_model.generate(
                prompt + "".join(output),
                n_tokens=n_tokens
            )
            
            # Verify with large model
            verified = await self.target_model.verify(
                prompt + "".join(output),
                draft
            )
            
            # Accept verified tokens
            output.extend(verified.accepted_tokens)
            
            if verified.is_complete:
                break
        
        return "".join(output)
```

**适用场景：**
- 对延迟敏感的应用。
- 有对齐良好的草稿模型。
- 生成模式可预测。

---

### 模式：缓存层

多级缓存策略：

```python
class CachingLLM:
    def __init__(self):
        self.exact_cache = ExactMatchCache()
        self.semantic_cache = SemanticCache(threshold=0.95)
    
    async def generate(self, query: str) -> str:
        # Level 1: Exact match
        cached = await self.exact_cache.get(query)
        if cached:
            return cached
        
        # Level 2: Semantic similarity
        similar = await self.semantic_cache.get_similar(query)
        if similar:
            return similar
        
        # Cache miss: Generate
        response = await self.llm.generate(query)
        
        # Store in caches
        await self.exact_cache.set(query, response)
        await self.semantic_cache.set(query, response)
        
        return response
```

**适用场景：**
- 反复出现相似查询。
- 成本降低优先。
- 可以容忍一定陈旧性。

---

## 可靠性模式

### 模式：重试与回退

```python
class RetryWithFallback:
    async def generate(self, query: str) -> str:
        providers = [
            ("openai", "gpt-4o"),
            ("anthropic", "claude-3.5-sonnet"),
            ("google", "gemini-1.5-pro")
        ]
        
        for provider, model in providers:
            try:
                return await self.call(provider, model, query)
            except RateLimitError:
                continue
            except ServiceError:
                continue
        
        # All providers failed
        raise AllProvidersUnavailable()
```

---

### 模式：熔断器

```python
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, reset_timeout: int = 60):
        self.failures = 0
        self.state = "closed"
        self.last_failure = None
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
    
    async def call(self, func, *args):
        if self.state == "open":
            if time.time() - self.last_failure > self.reset_timeout:
                self.state = "half-open"
            else:
                raise CircuitOpenError()
        
        try:
            result = await func(*args)
            self.failures = 0
            self.state = "closed"
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure = time.time()
            if self.failures >= self.failure_threshold:
                self.state = "open"
            raise
```

---

### 模式：舱壁

隔离组件之间的故障：

```python
class BulkheadExecutor:
    def __init__(self, max_concurrent: int = 10):
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def execute(self, func, *args):
        async with self.semaphore:
            return await func(*args)

# Separate bulkheads for different operations
rag_bulkhead = BulkheadExecutor(max_concurrent=20)
agent_bulkhead = BulkheadExecutor(max_concurrent=5)
```

---

## 成本模式

### 模式：Token 预算

```python
class TokenBudget:
    def __init__(self, max_input: int, max_output: int):
        self.max_input = max_input
        self.max_output = max_output
    
    def constrain_input(self, messages: list[dict]) -> list[dict]:
        total_tokens = 0
        constrained = []
        
        for msg in reversed(messages):
            tokens = count_tokens(msg["content"])
            if total_tokens + tokens > self.max_input:
                break
            constrained.insert(0, msg)
            total_tokens += tokens
        
        return constrained
```

---

### 模式：成本跟踪装饰器

```python
def track_cost(model: str):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_tokens = get_token_count()
            result = await func(*args, **kwargs)
            end_tokens = get_token_count()
            
            cost = calculate_cost(model, end_tokens - start_tokens)
            metrics.record("llm_cost", cost, tags={"model": model})
            
            return result
        return wrapper
    return decorator

@track_cost("gpt-4o")
async def generate_response(query: str):
    return await llm.generate(query)
```

---

## 面试问题

### Q：描述三种 RAG 模式，并说明各自的适用场景。

**强回答：**

“我会介绍朴素 RAG、高级 RAG 和父子检索。

**朴素 RAG** 最简单：对查询做嵌入、搜索向量、将 Top K 结果填入 Prompt 并生成。我会在 MVP 或检索质量已经足够好时使用它。它实现快，但没有重排序和查询增强。

**高级 RAG** 增加多个阶段：查询改写、混合搜索（语义 + 关键词）、重排序和过滤。生产中对准确性有要求时我会使用它；为了 10～15% 的精确率提升，额外 100～200ms 的重排序延迟通常值得。

**父子检索**对小分块做嵌入以实现精确匹配，但返回更大的父分块作为上下文。当文档有结构、同时需要检索精度和生成上下文时，我会使用它。

具体模式取决于准确性要求、延迟预算和文档特征。我通常先用朴素 RAG 建立基线，再迭代到高级 RAG。”

### Q：生产 LLM 系统会采用哪些可靠性模式？

**强回答：**

“我会实现多层可靠性机制：

对临时故障使用**指数退避重试**。LLM API 经常遇到限流和临时错误。

使用**多供应商回退**：如果 OpenAI 出现问题，就自动路由到 Anthropic 或 Google。这要求抽象 LLM 接口。

使用**熔断器**停止持续冲击故障服务。连续失败 N 次后打开熔断，立即路由到回退服务，为主服务恢复留出时间。

所有供应商都失败时进行**优雅降级**：返回缓存回答、展示回退消息或排队稍后处理，而不是直接报错。

使用**舱壁隔离**避免一个组件的失败级联。Agent 工作负载与 RAG 工作负载使用独立线程池。

每一层都设置**超时**。LLM 调用可能挂起，因此要设置积极的超时时间并优雅处理。

关键是预设故障一定会发生并围绕故障设计，而不是寄希望于故障永远不会发生。”

---

## 参考资料

- Gao et al. "Retrieval-Augmented Generation for Large Language Models: A Survey" (2024)
- Yao et al. "ReAct: Synergizing Reasoning and Acting in Language Models" (2023)
- Microsoft Patterns for AI: https://learn.microsoft.com/azure/architecture/patterns/

---

*下一篇：[需要避免的反模式](02-anti-patterns.md)*
