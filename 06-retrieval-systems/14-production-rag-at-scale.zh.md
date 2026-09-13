# 大规模生产级 RAG

生产级 RAG 已经不再是一个周末项目。它是一个分布式系统，包含检索流水线、缓存层、路由逻辑、自校正循环、多租户隔离和成本控制，并且都运行在严格的延迟 SLA 下。当 RAG 在生产环境中失败时，大约 73% 的情况根源在检索而不是生成，因此成功的企业部署会把知识源（而不是模型）当作首要投入。

## 目录

- [RAG 与长上下文](#rag-vs-long-context)
- [查询路由与分类](#query-routing)
- [RAG 的语义缓存](#semantic-caching)
- [多索引策略](#multi-index)
- [RAG 流程优化](#pipeline-optimization)
- [纠错式 RAG：自检索](#corrective-rag)
- [自适应检索](#adaptive-retrieval)
- [成本优化模式](#cost-optimization)
- [失败模式与调试](#failure-modes)
- [监控与告警](#monitoring)
- [扩展到数百万篇文档](#scaling)
- [多租户 RAG 隔离](#multi-tenant)
- [真实架构示例](#architectures)
- [系统设计面试角度](#interview)
- [参考资料](#references)

---

## RAG 与长上下文

如今每个主流前沿模型家族都支持 100 万以上 Token 的上下文窗口（Claude Opus 4.7、Claude Sonnet 4.6、GPT-5.5、Gemini 3.1 Pro、Qwen 3.6 Plus、Llama 4 Maverick），问题已经不再是“RAG 还是长上下文”，而是“什么时候各自更有优势”。

### 决策矩阵

```
                    Small Corpus           Large Corpus
                    (<100K tokens)         (>1M tokens)
                 +---------------------+---------------------+
  Static Data    |  Long Context Wins  |  RAG Required       |
  (rarely        |  - Stuff it all in  |  - Can't fit in     |
   changes)      |  - Simpler arch     |    context window   |
                 |  - No index needed  |  - Index + retrieve |
                 +---------------------+---------------------+
  Dynamic Data   |  Hybrid Approach    |  RAG Required       |
  (updates       |  - Cache context    |  - Incremental      |
   frequently)   |  - Invalidate on    |    indexing          |
                 |    change           |  - Real-time updates |
                 +---------------------+---------------------+
  Multi-User     |  RAG Preferred      |  RAG Required       |
  (per-user      |  - Personalized     |  - Tenant isolation  |
   data)         |    retrieval        |  - Access control    |
                 +---------------------+---------------------+
```

### 正面对比

| 维度 | RAG | 长上下文（100 万 Token） |
|-----------|-----|--------------------------|
| **平均查询成本** | 约 $0.0001 | 约 $0.10 |
| **平均延迟（p50）** | 约 1 秒 | 约 30～45 秒 |
| **特定事实的精确度** | 高（定向检索） | 中间位置会退化 |
| **跨文档综合** | 弱（上下文有限） | 强（能看到全部内容） |
| **语料库大小限制** | 无限 | 约 100 万 Token |
| **数据新鲜度** | 分钟级（增量索引） | 需要完整重新加载 |
| **1000 QPS 下的成本** | 约 $100/天 | 约 $100,000/天 |

### “中间丢失”问题

LLM 不会在整个上下文窗口中均匀分配注意力。与开头或结尾的信息相比，位于长上下文中间的信息准确率会下降 30% 以上。RAG 通过只把最相关的文本块放进短而聚焦的上下文，完全绕开了这一问题。

### 最佳实践：混合模式

最佳架构结合两者：先用 RAG 从大语料库中检索候选项，再将候选项加载到长上下文窗口中进行跨文档推理。

```
  User Query
      |
      v
+------------------+     +-------------------+
|  RAG Retrieval   |---->|  Long Context     |
|  (Find top 20    |     |  Synthesis        |
|   from 10M docs) |     |  (Reason across   |
+------------------+     |   20 docs deeply) |
                          +-------------------+
                                  |
                                  v
                          Final Answer with
                          Cross-Doc Citations
```

**经验法则**：如果语料库能放进上下文、能够承担延迟、也能够承担成本，就使用长上下文。否则使用 RAG。对于大多数受成本和延迟约束的生产系统，RAG 仍然是正确的默认选择。

---

## 查询路由与分类

不是每个查询都需要检索。生产系统会对输入查询进行分类，并将其路由到最合适的处理路径。

### 四路径路由器

```
                         User Query
                             |
                             v
                    +------------------+
                    |  Query Classifier |
                    |  (LLM or trained  |
                    |   classifier)     |
                    +--------+---------+
                             |
            +--------+-------+-------+--------+
            |        |               |        |
            v        v               v        v
        +------+ +--------+    +--------+ +--------+
        |Direct| |Simple  |    |Complex | |Agentic |
        | LLM  | |  RAG   |    |  RAG   | |  RAG   |
        +------+ +--------+    +--------+ +--------+
        "What    "What is      "Compare   "Analyze
        is 2+2?" our refund    Q3 vs Q4   all legal
                  policy?"     revenue    risks in
                               trends"    these 50
                                          contracts"
```

### 分类信号

| 信号 | 直接 LLM | 简单 RAG | 复杂 RAG | Agent 式 RAG |
|--------|-----------|------------|-------------|-------------|
| **需要私有数据** | 否 | 是 | 是 | 是 |
| **单跳答案** | 是 | 是 | 否 | 否 |
| **需要多个来源** | 否 | 否 | 是 | 是 |
| **需要推理链** | 否 | 否 | 可能 | 是 |
| **时间敏感数据** | 否 | 可能 | 可能 | 是 |

### 实现：轻量路由器

```python
class QueryRouter:
    """Routes queries to the optimal retrieval strategy."""

    def __init__(self, classifier_model: str = "gpt-4o-mini"):
        self.classifier = classifier_model
        self.route_counts = Counter()  # for monitoring

    async def classify(self, query: str, user_context: dict) -> str:
        # Step 1: Rule-based fast path
        if self._is_trivial(query):
            return "direct_llm"

        # Step 2: Check if query references private/org data
        if not self._needs_retrieval(query, user_context):
            return "direct_llm"

        # Step 3: LLM-based complexity classification
        complexity = await self._assess_complexity(query)

        if complexity == "simple":
            return "simple_rag"
        elif complexity == "multi_hop":
            return "complex_rag"
        else:
            return "agentic_rag"

    def _is_trivial(self, query: str) -> bool:
        """Fast regex/keyword check for trivial queries."""
        trivial_patterns = [
            r"^(what is|define|explain)\s+\w+$",
            r"^(hi|hello|thanks|bye)",
        ]
        return any(re.match(p, query.lower()) for p in trivial_patterns)

    async def _assess_complexity(self, query: str) -> str:
        """Use a small, fast model to classify complexity."""
        prompt = f"""Classify this query's retrieval complexity:
        - "simple": needs one document lookup
        - "multi_hop": needs 2-3 lookups, comparison, or synthesis
        - "agentic": needs planning, tool use, or iterative search

        Query: {query}
        Classification:"""

        result = await llm_call(self.classifier, prompt, max_tokens=10)
        return result.strip().lower()
```

### 领域专用路由

对于拥有多个知识领域的系统，应在检索前先将查询路由到正确的索引。

```python
# Rule-based domain routing
DOMAIN_RULES = {
    "revenue|sales|quota|ARR":     "financial_index",
    "policy|handbook|PTO|benefits": "hr_index",
    "API|endpoint|SDK|integration": "engineering_index",
    "compliance|GDPR|SOC2|audit":   "legal_index",
}

# Embedding-based domain routing (for ambiguous queries)
class DomainRouter:
    def __init__(self):
        self.domain_centroids = {}  # pre-computed per domain

    def route(self, query_embedding: list[float]) -> str:
        similarities = {
            domain: cosine_sim(query_embedding, centroid)
            for domain, centroid in self.domain_centroids.items()
        }
        return max(similarities, key=similarities.get)
```

---

## RAG 的语义缓存

语义缓存可以识别新查询是否与先前查询的含义基本相同，并复用缓存结果。生产系统报告称，经过良好调优的语义缓存最多可以降低 68% 的成本，并将延迟提升 65 倍。

### 三层缓存架构

```
  User Query
      |
      v
+---------------------+
| Layer 1: Exact Cache |  Hash(query) -> response
| (Redis/Memcached)    |  TTL: 1 hour
| Hit rate: ~15-25%    |  Latency: <5ms
+----------+----------+
           | miss
           v
+---------------------+
| Layer 2: Semantic    |  Embed(query) -> nearest neighbor
| Cache (Vector DB)    |  Threshold: cosine > 0.95
| Hit rate: ~20-35%    |  Latency: <50ms
+----------+----------+
           | miss
           v
+---------------------+
| Layer 3: Document    |  Cache retrieved chunks
| Cache               |  Skip re-embedding
| (saves embedding $) |  TTL: until doc changes
+----------+----------+
           | miss
           v
    Full RAG Pipeline
```

### 语义缓存实现

```python
class SemanticCache:
    """Cache RAG responses by query semantic similarity."""

    def __init__(self, vector_store, similarity_threshold: float = 0.95):
        self.vector_store = vector_store
        self.threshold = similarity_threshold
        self.response_store = {}  # query_id -> cached response

    async def get(self, query: str) -> Optional[CachedResponse]:
        # Step 1: Exact match (fast path)
        exact_key = hashlib.sha256(query.encode()).hexdigest()
        if exact_key in self.response_store:
            return self.response_store[exact_key]

        # Step 2: Semantic match
        query_embedding = await embed(query)
        results = self.vector_store.search(
            query_embedding, top_k=1
        )

        if results and results[0].score >= self.threshold:
            cached_id = results[0].metadata["response_id"]
            cached = self.response_store.get(cached_id)
            if cached and not cached.is_expired():
                return cached

        return None

    async def put(
        self, query: str, response: str,
        sources: list[str], ttl_seconds: int = 3600
    ):
        query_embedding = await embed(query)
        response_id = str(uuid4())

        # Store the embedding for future similarity lookups
        self.vector_store.upsert(
            id=response_id,
            embedding=query_embedding,
            metadata={"response_id": response_id}
        )

        # Store the actual response
        self.response_store[response_id] = CachedResponse(
            response=response,
            sources=sources,
            created_at=time.time(),
            ttl=ttl_seconds,
        )
```

### 缓存失效策略

| 策略 | 触发条件 | 用例 |
|----------|---------|----------|
| **基于 TTL** | 固定时间到期 | 通用查询、新闻 |
| **事件驱动** | 文档更新 Webhook | 知识库 |
| **版本标记** | 文档版本不匹配 | 合规关键系统 |
| **置信度门控** | 检索分数低 | 易变领域 |

**关键规则**：始终把源文档 ID 和响应一起缓存。当任何源文档更新时，让所有引用它的缓存条目失效。

```python
# Webhook-based cache invalidation
@app.post("/webhook/document-updated")
async def on_document_updated(doc_id: str):
    # Find all cache entries that used this document
    affected = cache_index.find_by_source(doc_id)
    for entry in affected:
        semantic_cache.invalidate(entry.response_id)
    logger.info(f"Invalidated {len(affected)} cache entries for doc {doc_id}")
```

---

## 多索引策略

单一的单体索引无法扩展。生产系统会按领域、租户或文档类型划分向量索引，以提升检索精度和运维隔离性。

### 索引分区模式

```
Pattern 1: Per-Domain Indexes
+--------+  +--------+  +--------+  +--------+
|  Legal |  |   HR   |  |Finance |  |  Eng   |
| Index  |  | Index  |  | Index  |  | Index  |
+--------+  +--------+  +--------+  +--------+
    |            |            |           |
    +----------- +-----+------+-----------+
                       |
                 Query Router
                       |
                  User Query


Pattern 2: Per-Tenant Indexes (Silo Model)
+----------+  +----------+  +----------+
| Tenant A |  | Tenant B |  | Tenant C |
|  Index   |  |  Index   |  |  Index   |
| (Acme)   |  | (Globex) |  | (Wayne)  |
+----------+  +----------+  +----------+


Pattern 3: Shared Index with Metadata Filtering (Pool Model)
+-------------------------------------------+
|           Shared Vector Index              |
|  +-------+  +-------+  +-------+          |
|  | doc_1 |  | doc_2 |  | doc_3 |  ...     |
|  | t:A   |  | t:B   |  | t:A   |          |
|  +-------+  +-------+  +-------+          |
|                                            |
|  WHERE tenant_id = "A"  <-- filter         |
+-------------------------------------------+
```

### 何时使用各模式

| 模式 | 隔离性 | 成本 | 运维复杂度 | 最适合 |
|---------|-----------|------|----------------------|----------|
| **按领域** | 中 | 中 | 中 | 知识领域明确不同的内部工具 |
| **按租户隔离** | 最强 | 高 | 高 | 企业 SaaS、受监管行业 |
| **共享池** | 最弱 | 低 | 低 | 中小企业 SaaS、成本敏感产品 |
| **混合桥接** | 可配置 | 中 | 高 | 企业 + 中小企业混合客户群 |

### 分层索引策略

对于超大语料库，可以使用两层索引：粗粒度的“摘要索引”负责路由，细粒度的“文本块索引”负责精确检索。

```
  Query: "What is the refund policy for enterprise plans?"
      |
      v
+--------------------+
| Summary Index      |  Contains doc-level summaries
| (10K entries)      |  Fast, broad search
+--------+-----------+
         |
         | Top 3 matching docs identified
         v
+--------------------+
| Chunk Index        |  Contains 500-token chunks
| (2M entries)       |  Precise, targeted search
| Filtered to 3 docs |
+--------+-----------+
         |
         v
   Top 5 chunks -> LLM
```

---

## RAG 流程优化

朴素的串行 RAG 流程会在每一步都增加延迟。生产流程使用并行、批处理和异步处理来满足亚秒级 SLA。

### 串行流程与优化流程

```
SEQUENTIAL (Naive):
Query -> Embed(200ms) -> Search(150ms) -> Rerank(300ms) -> Generate(800ms)
Total: ~1450ms

OPTIMIZED (Parallel + Cached):
Query ----+---> Embed(200ms) ---> Vector Search(150ms) ---+
          |                                                |--> RRF Merge -> Rerank(300ms) -> Generate(800ms)
          +---> BM25 Keyword Search(100ms) ---------------+
          |
          +---> Cache Check(5ms) -- HIT --> Return cached (5ms total)

With cache miss: ~1050ms (embedding + keyword in parallel)
With cache hit:  ~5ms
```

### 并行检索

```python
async def parallel_retrieve(
    query: str,
    query_embedding: list[float],
    indexes: list[str],
) -> list[Chunk]:
    """Run vector search, keyword search, and graph traversal in parallel."""

    tasks = [
        vector_search(query_embedding, index="main", top_k=20),
        bm25_search(query, index="main", top_k=20),
        # Optionally, graph-based retrieval for entity queries
        graph_search(query, max_hops=2, top_k=10),
    ]

    # All retrieval strategies execute concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out failures (graceful degradation)
    valid_results = [r for r in results if not isinstance(r, Exception)]

    # Merge with Reciprocal Rank Fusion
    merged = reciprocal_rank_fusion(valid_results, k=60)

    return merged[:20]  # top 20 after fusion
```

### 批量 Embedding

处理摄取任务或同时处理多个查询时，应批量调用 Embedding，以最大化 GPU 利用率。

```python
class EmbeddingBatcher:
    """Batch embedding requests to reduce per-call overhead."""

    def __init__(self, model: str, batch_size: int = 64, max_wait_ms: int = 50):
        self.model = model
        self.batch_size = batch_size
        self.max_wait = max_wait_ms / 1000
        self.queue: asyncio.Queue = asyncio.Queue()
        self._running = True

    async def embed(self, text: str) -> list[float]:
        """Submit a single text and wait for its embedding."""
        future = asyncio.Future()
        await self.queue.put((text, future))
        return await future

    async def _batch_loop(self):
        """Background loop that collects and processes batches."""
        while self._running:
            batch = []
            try:
                # Wait for at least one item
                item = await asyncio.wait_for(
                    self.queue.get(), timeout=1.0
                )
                batch.append(item)

                # Collect more items up to batch_size or max_wait
                deadline = time.time() + self.max_wait
                while len(batch) < self.batch_size and time.time() < deadline:
                    try:
                        item = await asyncio.wait_for(
                            self.queue.get(),
                            timeout=max(0, deadline - time.time())
                        )
                        batch.append(item)
                    except asyncio.TimeoutError:
                        break

                # Process the batch
                texts = [t for t, _ in batch]
                embeddings = await embed_batch(self.model, texts)

                for (_, future), emb in zip(batch, embeddings):
                    future.set_result(emb)

            except asyncio.TimeoutError:
                continue
```

### 带提前检索的流式生成

在用户打字暂停时就开始检索（通过暂停检测），并在生成 Token 时立即流式输出。

```
Timeline:
0ms     User starts typing...
300ms   Pause detected -> trigger retrieval speculatively
500ms   User submits query
        Retrieval already 200ms in -> finishes at 650ms
650ms   Reranking begins
950ms   First generation token streams to user
1800ms  Full response complete

vs. without speculation:
0ms     User submits query
200ms   Embedding
350ms   Retrieval
650ms   Reranking
1500ms  First token
2300ms  Full response complete
```

---

## 纠错式 RAG：自检索

纠错式 RAG（CRAG）在检索和生成之间增加验证层。系统会在生成响应前评估检索到的文档是否真的能够回答查询。

### CRAG 决策循环

```
  User Query
      |
      v
  Retrieve Top-K
      |
      v
+------------------+
| Relevance Grader  |  "Are these docs relevant to the query?"
| (LLM or trained   |
|  classifier)      |
+--------+---------+
         |
    +----+----+--------+
    |         |        |
    v         v        v
 CORRECT   AMBIGUOUS  WRONG
    |         |        |
    v         v        v
 Generate  Supplement  Discard &
 directly  with web    re-retrieve
           search      with reformulated
                       query
```

### 实现

```python
class CorrectiveRAG:
    """Self-correcting RAG pipeline with retrieval quality checks."""

    def __init__(self, max_corrections: int = 2):
        self.max_corrections = max_corrections

    async def answer(self, query: str) -> RAGResponse:
        attempts = 0
        current_query = query
        all_sources = []

        while attempts <= self.max_corrections:
            # Step 1: Retrieve
            chunks = await retrieve(current_query, top_k=10)

            # Step 2: Grade relevance
            grade = await self._grade_relevance(query, chunks)

            if grade.verdict == "correct":
                # High-confidence retrieval, generate directly
                return await self._generate(query, chunks, all_sources)

            elif grade.verdict == "ambiguous":
                # Supplement with additional search
                web_results = await web_search(current_query)
                chunks = self._merge_and_dedupe(chunks, web_results)
                return await self._generate(query, chunks, all_sources)

            else:  # "wrong"
                # Reformulate query and retry
                current_query = await self._reformulate(
                    original_query=query,
                    failed_query=current_query,
                    reason=grade.reason,
                )
                all_sources.extend(chunks)
                attempts += 1

        # Exhausted retries: generate best-effort with disclaimer
        return await self._generate_with_caveat(query, all_sources)

    async def _grade_relevance(
        self, query: str, chunks: list[Chunk]
    ) -> RelevanceGrade:
        """Use LLM to grade whether chunks answer the query."""
        prompt = f"""Given this query and retrieved documents, assess relevance.

Query: {query}

Documents:
{self._format_chunks(chunks)}

Respond with:
- verdict: "correct" (docs clearly answer the query)
- verdict: "ambiguous" (docs partially relevant, need supplementing)
- verdict: "wrong" (docs are irrelevant to the query)
- reason: brief explanation

JSON response:"""

        result = await llm_call(prompt, response_format="json")
        return RelevanceGrade(**json.loads(result))
```

### Self-RAG：批评 Token

Self-RAG 通过内嵌批评 Token 扩展这一模式。模型会在每一步评估自己的输出：

1. **[Retrieve]**：我应该检索吗？（是/否）
2. **[Relevant]**：检索到的信息相关吗？（是/否）
3. **[Supported]**：我的答案有证据支持吗？（完全/部分/否）
4. **[Useful]**：这个答案真的有用吗？（1～5 分）

如果任何一项检查失败，模型就回到更早的步骤重新循环。

---

## 自适应检索

不是所有查询都能从检索中获益。自适应检索会动态决定是否检索、检索多少，以及从哪些来源检索。

### 检索决策树

```
  User Query
      |
      v
  "Does this query need external knowledge?"
      |
  +---+---+
  |       |
  No      Yes
  |       |
  v       v
Direct   "How complex is the retrieval need?"
 LLM      |
answer  +-+--+---------+
        |    |         |
        v    v         v
     Single Multi    Agentic
      hop   hop      (planning
        |    |       required)
        v    v         |
     1 index 2-3       v
     top-5  indexes  Full agent
             top-10  loop
```

### 查询复杂度估算器

```python
class AdaptiveRetriever:
    """Decides retrieval strategy based on query characteristics."""

    async def retrieve(self, query: str) -> RetrievalPlan:
        # Fast heuristics first
        if self._is_general_knowledge(query):
            return RetrievalPlan(strategy="none", reason="general knowledge")

        if self._is_simple_lookup(query):
            return RetrievalPlan(
                strategy="single_hop",
                indexes=["primary"],
                top_k=5,
            )

        # LLM-based assessment for ambiguous cases
        plan = await self._plan_retrieval(query)
        return plan

    def _is_general_knowledge(self, query: str) -> bool:
        """Check if query is about widely known facts."""
        general_indicators = [
            "what is", "who is", "define", "explain the concept",
        ]
        has_org_refs = bool(re.search(
            r"(our|my|the company|internal|proprietary)", query.lower()
        ))
        is_general = any(
            query.lower().startswith(g) for g in general_indicators
        )
        return is_general and not has_org_refs

    def _is_simple_lookup(self, query: str) -> bool:
        """Check if query can be answered with a single document."""
        single_hop_patterns = [
            r"what is (the|our) .+ policy",
            r"how (do I|to) .+",
            r"where (can I|do I) find",
        ]
        return any(re.search(p, query.lower()) for p in single_hop_patterns)
```

### Token 预算感知的检索

根据可用 Token 预算和预期响应复杂度调整检索投入。

```python
def plan_retrieval_budget(query: str, max_budget_tokens: int = 4000):
    """Allocate token budget across retrieval and generation."""

    complexity = estimate_complexity(query)  # 1-5 scale

    if complexity <= 2:
        # Simple query: small context, save tokens for generation
        return {"context_tokens": 1000, "generation_tokens": 3000, "top_k": 3}
    elif complexity <= 4:
        # Medium: balanced
        return {"context_tokens": 2500, "generation_tokens": 1500, "top_k": 8}
    else:
        # Complex: heavy retrieval, concise generation
        return {"context_tokens": 3500, "generation_tokens": 500, "top_k": 15}
```

---

## 成本优化模式

在大规模场景中，RAG 成本会在 Embedding、检索、重排序和生成之间叠加。未经优化的系统可能比必要成本高出 10～50 倍。

### 一次典型 RAG 查询的成本拆分

```
Component         Cost per Query    % of Total    Optimization
-----------------------------------------------------------------
Embedding         $0.000005         ~1%           Batch + cache
Vector Search     $0.00001          ~2%           Index optimization
Reranking         $0.0001           ~15%          Skip for simple queries
LLM Generation    $0.0005-0.005     ~80%          Model tiering, caching
-----------------------------------------------------------------
Total (naive)     ~$0.001-0.006
Total (optimized) ~$0.0001-0.001    (5-10x reduction)
```

### 分层模型策略

```
                Query Complexity
                Low         Medium        High
             +----------+----------+----------+
 Generation  |  Small   |  Mid     |  Large   |
 Model       |  Model   |  Model   |  Model   |
             | (4o-mini)| (Claude  | (Claude  |
             |          |  Sonnet) |  Opus)   |
             | ~$0.0002 | ~$0.002  | ~$0.02   |
             +----------+----------+----------+

 Reranking   |  Skip    | Lightweight| Cross-  |
             |          | reranker   | encoder |
             +----------+----------+----------+
```

### 渐进式详情模式

先以最少检索回答。只有用户继续追问或置信度低时才升级。

```python
class ProgressiveRAG:
    """Start cheap, escalate only when needed."""

    async def answer(self, query: str, session: Session) -> str:
        # Level 1: Try semantic cache
        cached = await self.cache.get(query)
        if cached:
            return cached.response  # Cost: ~$0

        # Level 2: Fast retrieval + small model
        chunks = await retrieve(query, top_k=3)
        response = await generate(
            query, chunks, model="gpt-4o-mini"
        )

        # Check confidence
        if response.confidence > 0.85:
            await self.cache.put(query, response)
            return response.text  # Cost: ~$0.0003

        # Level 3: Deep retrieval + reranking + larger model
        chunks = await retrieve(query, top_k=15)
        reranked = await rerank(query, chunks, top_k=5)
        response = await generate(
            query, reranked, model="claude-sonnet-4-5"
        )

        if response.confidence > 0.7:
            await self.cache.put(query, response)
            return response.text  # Cost: ~$0.003

        # Level 4: Full agentic pipeline (expensive but thorough)
        return await self.agentic_pipeline.run(query)  # Cost: ~$0.05
```

### 成本护栏

```python
class CostGuard:
    """Prevent runaway costs in production RAG."""

    def __init__(self):
        self.daily_budget = 500.0  # $500/day
        self.per_query_limit = 0.10  # $0.10 max per query
        self.per_user_hourly = 1.0  # $1/user/hour

    async def check(self, user_id: str, estimated_cost: float) -> bool:
        daily_spent = await self.get_daily_spend()
        if daily_spent + estimated_cost > self.daily_budget:
            raise BudgetExceededError("Daily budget exhausted")

        user_spent = await self.get_user_hourly_spend(user_id)
        if user_spent + estimated_cost > self.per_user_hourly:
            raise RateLimitError("User hourly budget exceeded")

        if estimated_cost > self.per_query_limit:
            # Downgrade to cheaper strategy
            return False  # signals caller to use cheaper path

        return True
```

---

## 失败模式与调试

生产级 RAG 系统的失败概率会层层叠加。三个阶段各自有 95% 的可靠性时，整体可靠性会降到 0.95 × 0.95 × 0.95 = 0.86。理解失败模式至关重要。

### RAG 失败分类

```
+------------------------------------------------------------------+
|                    RAG Failure Modes                               |
+------------------------------------------------------------------+
|                                                                    |
|  RETRIEVAL FAILURES          GENERATION FAILURES                   |
|  +---------------------+    +-------------------------+           |
|  | Missing documents   |    | Hallucination despite   |           |
|  | (not indexed)       |    | good context            |           |
|  +---------------------+    +-------------------------+           |
|  | Wrong chunks        |    | Ignoring retrieved      |           |
|  | (low precision)     |    | context                 |           |
|  +---------------------+    +-------------------------+           |
|  | Missed chunks       |    | Over-reliance on one    |           |
|  | (low recall)        |    | source                  |           |
|  +---------------------+    +-------------------------+           |
|  | Stale embeddings    |    | Citation fabrication    |           |
|  | (drift)             |    |                         |           |
|  +---------------------+    +-------------------------+           |
|                                                                    |
|  SYSTEM FAILURES             QUALITY FAILURES                      |
|  +---------------------+    +-------------------------+           |
|  | Index unavailable   |    | Chunking artifacts      |           |
|  +---------------------+    +-------------------------+           |
|  | Embedding service   |    | Context window overflow |           |
|  | timeout             |    +-------------------------+           |
|  +---------------------+    | Answer too vague        |           |
|  | Reranker OOM        |    | (over-hedging)          |           |
|  +---------------------+    +-------------------------+           |
|                                                                    |
+------------------------------------------------------------------+
```

### 分块的 80% 规则

据估计，RAG 质量问题中约 80% 源于分块决策，而不是检索或生成。常见的分块失败包括：

- **文本块太小**：丢失上下文。“它的成本是 200 美元”——什么东西成本是 200 美元？
- **文本块太大**：相关性被稀释。一个 2000 Token 的文本块中只有 1 句话相关。
- **边界拆分**：表格或列表被拆到两个文本块中。
- **元数据缺失**：文本块没有标题、文档名或章节上下文。

### 调试清单

```
When RAG quality drops, investigate in this order:

1. RETRIEVAL QUALITY (check first -- most common root cause)
   [ ] Log the query and retrieved chunks side by side
   [ ] Compute retrieval precision@K manually for 20 failing queries
   [ ] Check if relevant documents exist in the index at all
   [ ] Compare BM25 vs vector results -- if BM25 wins, embeddings are stale

2. CHUNKING QUALITY (check second)
   [ ] Sample 50 random chunks -- do they make sense in isolation?
   [ ] Check chunk boundaries for tables, lists, code blocks
   [ ] Verify metadata (title, section, doc_id) is present

3. RERANKING QUALITY (check third)
   [ ] Compare pre-rerank vs post-rerank orderings
   [ ] Check if reranker is pushing relevant results down

4. GENERATION QUALITY (check last)
   [ ] Test with perfect context (manually curated) -- does LLM still fail?
   [ ] Check for context window overflow (truncated chunks)
   [ ] Verify system prompt is not conflicting with retrieved context
```

### Agent 式 RAG 的失败模式

Agent 式 RAG 会引入三种额外的失败模式：

1. **检索打转**：Agent 反复检索，却无法收敛到答案。追踪记录中会出现近似重复的查询和来回摆动的搜索词。修复：将检索迭代限制在 3～5 次，并跟踪每个会话中的查询唯一性。
2. **工具风暴**：Agent 在一次交互中调用过多工具。修复：设置每次查询的工具调用上限和成本上限。
3. **上下文膨胀**：Agent 累积过多检索文本块，导致上下文窗口溢出。修复：实现滑动窗口，在上下文超过阈值时丢弃最早的文本块。

---

## 监控与告警

生产级 RAG 需要在标准应用指标之外配备专门的监控。如今大约 60% 的新 RAG 部署从第一天起就包含系统化评估，这一比例相比早期 RAG“先上线、后评估”的模式大幅提升。

### RAG 监控栈

```
+--------------------------------------------------------------------+
|                    RAG Observability Layers                          |
+--------------------------------------------------------------------+
|                                                                      |
|  L1: INFRASTRUCTURE          L2: PIPELINE                           |
|  +----------------------+   +-----------------------------+         |
|  | Latency (p50/p95/p99)|   | Retrieval precision@K      |         |
|  | Error rates          |   | Retrieval recall@K         |         |
|  | Throughput (QPS)     |   | Reranker effectiveness     |         |
|  | Cache hit rate       |   | Chunk utilization rate     |         |
|  | Index size/growth    |   | Context window fill rate   |         |
|  +----------------------+   +-----------------------------+         |
|                                                                      |
|  L3: QUALITY                 L4: BUSINESS                           |
|  +----------------------+   +-----------------------------+         |
|  | Faithfulness score   |   | User satisfaction (thumbs) |         |
|  | Answer relevancy     |   | Task completion rate       |         |
|  | Hallucination rate   |   | Escalation to human rate   |         |
|  | Citation accuracy    |   | Cost per successful query  |         |
|  +----------------------+   +-----------------------------+         |
|                                                                      |
+--------------------------------------------------------------------+
```

### 关键指标与告警

| 指标 | 目标 | 告警阈值 | 操作 |
|--------|--------|-----------------|--------|
| **p95 延迟** | <2 秒 | >5 秒 | 扩展检索基础设施 |
| **缓存命中率** | >40% | <20% | 调整相似度阈值 |
| **检索 Precision@5** | >0.7 | <0.5 | 重新评估分块 |
| **忠实度** | >0.9 | <0.8 | 审计生成 Prompt |
| **幻觉率** | <5% | >10% | 收紧依据约束 Prompt |
| **空检索率** | <2% | >5% | 检查索引覆盖范围 |
| **单次查询成本** | <$0.005 | >$0.02 | 检查模型分层策略 |

### 端到端追踪日志

每个查询都应生成一个 Trace，用单一请求 ID 关联所有流水线阶段。

```python
@dataclass
class RAGTrace:
    request_id: str
    timestamp: datetime
    query: str
    route: str                    # "simple_rag", "complex_rag", etc.
    cache_hit: bool
    retrieval_latency_ms: float
    chunks_retrieved: int
    chunks_after_rerank: int
    rerank_latency_ms: float
    generation_model: str
    generation_latency_ms: float
    total_latency_ms: float
    input_tokens: int
    output_tokens: int
    estimated_cost: float
    faithfulness_score: float     # 0-1, computed async
    user_feedback: Optional[str]  # thumbs up/down

    def to_dict(self) -> dict:
        return asdict(self)
```

### 自动化质量抽样

对生产查询样本运行离线评估，在用户察觉之前发现质量漂移。

```python
async def nightly_quality_check(sample_size: int = 200):
    """Sample production queries and evaluate RAG quality."""
    traces = await get_recent_traces(limit=sample_size)

    scores = []
    for trace in traces:
        # Re-run the query with evaluation
        eval_result = await evaluate_rag_response(
            query=trace.query,
            response=trace.response,
            retrieved_chunks=trace.chunks,
            metrics=["faithfulness", "relevancy", "context_precision"],
        )
        scores.append(eval_result)

    avg_faithfulness = mean([s.faithfulness for s in scores])
    avg_relevancy = mean([s.relevancy for s in scores])

    if avg_faithfulness < 0.85:
        alert("RAG faithfulness degraded", severity="high")
    if avg_relevancy < 0.70:
        alert("RAG relevancy degraded", severity="medium")

    publish_metrics("rag.nightly.faithfulness", avg_faithfulness)
    publish_metrics("rag.nightly.relevancy", avg_relevancy)
```

---

## 扩展到数百万篇文档

从数千篇扩展到数百万篇文档，会在索引吞吐、检索延迟和索引管理方面引入新的挑战。

### 扩展维度

```
Documents:   1K  -->  100K  -->  1M  -->  100M
             |        |         |         |
Chunks:      10K      1M        10M       1B
             |        |         |         |
Index Size:  50MB     5GB       50GB      5TB
             |        |         |         |
Strategy:    Single   Single    Sharded   Distributed
             Node     Node +    Index     Cluster +
                      Replicas             Tiered
```

### 大规模摄取流水线

```
  Document Sources
  (S3, DBs, APIs, File Shares)
         |
         v
+-------------------+
| Ingestion Queue   |  (Kafka / SQS)
| - Deduplication   |
| - Priority queue  |
+--------+----------+
         |
    +----+----+----+----+
    |    |    |    |    |     Parallel workers
    v    v    v    v    v
  +--+ +--+ +--+ +--+ +--+
  |W1| |W2| |W3| |W4| |W5|  Parse + Chunk + Embed
  +--+ +--+ +--+ +--+ +--+
    |    |    |    |    |
    +----+----+----+----+
         |
         v
+-------------------+
| Vector DB Cluster |
| (Sharded by       |
|  doc_type or      |
|  tenant_id)       |
+-------------------+
```

### 分片策略

| 策略 | 工作方式 | 优点 | 缺点 |
|----------|-------------|------|------|
| **基于哈希** | shard = hash(doc_id) % N | 分布均匀 | 需要跨分片查询 |
| **基于范围** | 按日期范围分片 | 时间查询快 | 分片大小不均 |
| **基于领域** | 按文档类型分片 | 无需跨分片查询 | 领域负载不均衡 |
| **基于租户** | 按 tenant_id 分片 | 完全隔离 | 会产生很多小分片 |

### 索引维护

当文档达到数百万篇时，索引维护会成为关键的运维问题。

```python
class IndexMaintenanceScheduler:
    """Scheduled tasks for index health at scale."""

    async def run_daily(self):
        # 1. Detect and re-embed stale documents
        stale_docs = await find_docs_with_old_embeddings(
            older_than_days=90,
            embedding_model_version="v2"  # current is v3
        )
        if stale_docs:
            await enqueue_reembedding(stale_docs)

        # 2. Remove orphaned vectors (doc deleted but vector remains)
        orphans = await find_orphaned_vectors()
        if orphans:
            await delete_vectors(orphans)

        # 3. Compact and optimize indexes
        for shard in await list_shards():
            if shard.fragmentation_pct > 20:
                await compact_shard(shard.id)

        # 4. Verify index health
        for shard in await list_shards():
            health = await check_shard_health(shard.id)
            if not health.ok:
                alert(f"Shard {shard.id} unhealthy: {health.reason}")
```

### 用于检索的读副本

分离读写路径，避免摄取流程降低查询延迟。

```
  Ingestion Pipeline              Query Pipeline
        |                              |
        v                              v
  +-----------+     Replication   +-----------+
  |  Primary  | ----------------> |  Replica  |
  |  (Write)  |                   |  (Read)   |
  +-----------+                   +-----------+
                                  |  Replica  |
                                  |  (Read)   |
                                  +-----------+
                                  |  Replica  |
                                  |  (Read)   |
                                  +-----------+
```

---

## 多租户 RAG 隔离

多租户 RAG 是 SaaS 产品中最常见的生产模式。隔离做错就意味着租户之间发生数据泄露，这是严重的安全故障。

### 三种隔离模型

```
SILO MODEL (Strongest Isolation)
+----------+  +----------+  +----------+
| Tenant A |  | Tenant B |  | Tenant C |
| +------+ |  | +------+ |  | +------+ |
| |Index | |  | |Index | |  | |Index | |
| +------+ |  | +------+ |  | +------+ |
| |Cache | |  | |Cache | |  | |Cache | |
| +------+ |  | +------+ |  | +------+ |
+----------+  +----------+  +----------+
Cost: $$$$    Best for: Enterprise, Regulated Industries


POOL MODEL (Cost-Efficient)
+-------------------------------------------+
|              Shared Index                  |
|  [A] [B] [A] [C] [B] [A] [C] [B] [C]    |
|                                            |
|  Every query includes:                     |
|  WHERE tenant_id = ? (MANDATORY)           |
+-------------------------------------------+
Cost: $       Best for: SMB SaaS


BRIDGE MODEL (Hybrid)
+----------+  +----------------------------+
| Tenant A |  |     Shared Pool            |
| (Enterprise) | [B] [C] [D] [E] [F] [G]  |
| +------+ |  |                            |
| |Dedicated|  | WHERE tenant_id = ?       |
| |Index | |  +----------------------------+
| +------+ |
+----------+
Cost: $$      Best for: Mixed customer base
```

### 安全：纵深防御

```python
class TenantIsolatedRetriever:
    """Enforces tenant isolation at every retrieval layer."""

    async def retrieve(
        self, query: str, tenant_id: str, user_id: str
    ) -> list[Chunk]:
        # Layer 1: Tenant ID is MANDATORY in every query
        if not tenant_id:
            raise SecurityError("tenant_id required for retrieval")

        # Layer 2: Validate user belongs to tenant
        if not await self.authz.user_in_tenant(user_id, tenant_id):
            raise AuthorizationError("User not in tenant")

        # Layer 3: Apply tenant filter at the database level
        chunks = await self.vector_db.search(
            query_embedding=await embed(query),
            filter={"tenant_id": {"$eq": tenant_id}},  # ALWAYS filtered
            top_k=10,
        )

        # Layer 4: Post-retrieval verification
        for chunk in chunks:
            assert chunk.metadata["tenant_id"] == tenant_id, \
                f"Cross-tenant leak detected: {chunk.id}"

        # Layer 5: Audit log
        await self.audit_log.record(
            action="retrieve",
            tenant_id=tenant_id,
            user_id=user_id,
            chunk_ids=[c.id for c in chunks],
        )

        return chunks
```

### 租户感知的摄取

租户上下文必须注入流水线的每个阶段，从摄取一直传递到生成。

```
Document Upload (Tenant A)
        |
        v
  +---------------------+
  | Validate Ownership  |  Does this doc belong to Tenant A?
  +---------------------+
        |
        v
  +---------------------+
  | Chunk + Embed       |  Attach tenant_id to every chunk
  +---------------------+
        |
        v
  +---------------------+
  | Index with Metadata |  {"tenant_id": "A", "doc_id": "...", ...}
  +---------------------+
        |
        v
  +---------------------+
  | Invalidate Cache    |  Clear Tenant A's cache entries
  +---------------------+             for affected documents
```

### 防止邻居噪声

在共享池模型中，一个租户的高负载可能拖慢所有租户。

```python
class TenantRateLimiter:
    """Per-tenant rate limiting and resource quotas."""

    def __init__(self):
        self.tenant_limits = {
            "free":       {"qps": 5,   "daily_queries": 500},
            "pro":        {"qps": 50,  "daily_queries": 10_000},
            "enterprise": {"qps": 200, "daily_queries": 100_000},
        }

    async def check(self, tenant_id: str, tier: str) -> bool:
        limits = self.tenant_limits[tier]

        current_qps = await self.redis.get(f"qps:{tenant_id}")
        if current_qps and int(current_qps) >= limits["qps"]:
            raise RateLimitError(f"QPS limit ({limits['qps']}) exceeded")

        daily_count = await self.redis.get(f"daily:{tenant_id}")
        if daily_count and int(daily_count) >= limits["daily_queries"]:
            raise RateLimitError("Daily query limit exceeded")

        # Increment counters
        pipe = self.redis.pipeline()
        pipe.incr(f"qps:{tenant_id}")
        pipe.expire(f"qps:{tenant_id}", 1)  # 1-second window
        pipe.incr(f"daily:{tenant_id}")
        pipe.expire(f"daily:{tenant_id}", 86400)
        await pipe.execute()

        return True
```

---

## 真实架构示例

### 示例 1：客服 RAG

```
+------------------------------------------------------------------+
|                   Customer Support RAG System                     |
+------------------------------------------------------------------+
|                                                                    |
|  Customer Query                                                    |
|       |                                                            |
|       v                                                            |
|  +------------+    +---------+    +------------------+             |
|  | Query      |--->| Semantic|--->| Intent           |             |
|  | Normalizer |    | Cache   |    | Classifier       |             |
|  +------------+    +---------+    +--------+---------+             |
|                     (hit->skip)            |                       |
|                                   +--------+---------+             |
|                                   |                  |             |
|                                   v                  v             |
|                             +-----------+    +-------------+      |
|                             | Knowledge |    | Order/Acct  |      |
|                             | Base RAG  |    | Database    |      |
|                             | (articles,|    | (SQL lookup)|      |
|                             |  FAQs)    |    +-------------+      |
|                             +-----------+           |              |
|                                   |                 |              |
|                                   +--------+--------+              |
|                                            |                       |
|                                            v                       |
|                                   +------------------+             |
|                                   | Response Gen     |             |
|                                   | (with citations  |             |
|                                   |  + confidence)   |             |
|                                   +--------+---------+             |
|                                            |                       |
|                                   +--------+---------+             |
|                                   |                  |             |
|                                   v                  v             |
|                            confidence > 0.8    confidence < 0.8   |
|                            Auto-respond        Route to human      |
|                                                                    |
+------------------------------------------------------------------+

Scale: 50K articles, 2M customer interactions/month
Latency SLA: p95 < 3s
Cache hit rate: ~45%
Auto-resolution rate: ~60%
```

### 示例 2：企业知识平台

```
+------------------------------------------------------------------+
|              Enterprise Multi-Tenant Knowledge Platform            |
+------------------------------------------------------------------+
|                                                                    |
|  +------------------+                                              |
|  | Auth + Tenant    |                                              |
|  | Resolution       |                                              |
|  +--------+---------+                                              |
|           |                                                        |
|           v                                                        |
|  +------------------+                                              |
|  | Query Router     |                                              |
|  +--+----+----+-----+                                              |
|     |    |    |                                                     |
|     v    v    v                                                     |
|  +----+ +----+ +--------+                                          |
|  |Docs| |Wiki| |Tickets |  Per-domain indexes                     |
|  |Idx | |Idx | |Idx     |  (all tenant-filtered)                   |
|  +----+ +----+ +--------+                                          |
|     |    |    |                                                     |
|     +----+----+                                                     |
|          |                                                          |
|          v                                                          |
|  +------------------+                                              |
|  | Cross-Encoder    |                                              |
|  | Reranker         |                                              |
|  +--------+---------+                                              |
|           |                                                        |
|           v                                                        |
|  +------------------+     +-------------------+                    |
|  | Tiered LLM       |<--->| Permission Filter |                    |
|  | Generation        |     | (doc-level ACLs)  |                    |
|  +------------------+     +-------------------+                    |
|           |                                                        |
|           v                                                        |
|  +------------------+                                              |
|  | Response + Audit |                                              |
|  | Trail            |                                              |
|  +------------------+                                              |
|                                                                    |
+------------------------------------------------------------------+

Scale: 200 tenants, 10M documents total, 500K queries/day
Isolation: Bridge model (5 enterprise silos + shared pool)
Ingestion: Async via Kafka, ~50K docs/day
```

### 示例 3：法律文档分析

```
  User: "Summarize indemnification clauses across all vendor contracts"
      |
      v
  +---------------------+
  | Agentic RAG Planner |
  +---------------------+
      |
      | Plan: 1. Find all vendor contracts
      |        2. Extract indemnification clauses
      |        3. Synthesize comparison
      |
      v
  +---------------------+    +-------------------+
  | Step 1: Metadata    |--->| Filter: doc_type  |
  | Search              |    | = "vendor_contract"|
  +---------------------+    +-------------------+
      |                            |
      | 47 contracts found         |
      v                            v
  +---------------------+    +-------------------+
  | Step 2: Section     |--->| Filter: section   |
  | Retrieval           |    | = "indemnification"|
  +---------------------+    +-------------------+
      |                            |
      | 43 relevant sections       |
      v                            |
  +---------------------+         |
  | Step 3: Long Context|<--------+
  | Synthesis           |
  | (load 43 sections   |
  |  into 1M context)   |
  +---------------------+
      |
      v
  Comparative summary with
  per-contract citations
```

---

## 系统设计面试角度

### Q：设计一个跨 500 个租户、每秒服务 10,000 个查询、p99 延迟为 2 秒的 RAG 系统。

**参考答案：**

我会将系统设计为四层。

**第一层：路由与缓存。** 查询路由器将每个输入查询分类为直接 LLM、简单 RAG 或复杂 RAG。三层缓存（精确匹配、语义缓存、文档缓存）处理约 40%～50% 的流量，因此真正进入检索流水线的只有 5000～6000 QPS。

**第二层：检索。** 我会使用桥接隔离模型——前 20 个企业租户使用专用索引（隔离模式），其余 480 个租户共享一个带强制 tenant_id 过滤的池化索引。检索并行运行混合搜索（向量 + BM25），再用互惠秩融合合并结果。向量数据库集群按租户层级分片，并通过副本提升读取吞吐。

**第三层：生成。** 分层模型策略将简单查询路由到小模型，将复杂查询路由到大模型。在保证困难查询质量的同时保持较低平均成本。按租户限流可以防止邻居噪声。

**第四层：可观测性。** 每个查询都会产生包含延迟拆分、检索分数和成本的 Trace。每晚抽样 500 个查询，评估忠实度和相关性。当 p95 延迟超过 3 秒，或忠实度低于 0.85 时触发告警。

**成本估算**：在 10K QPS、缓存命中率 50%、小模型/大模型比例 70/30 的假设下，每日生成成本约为 2000～5000 美元，基础设施成本约为 500～1000 美元。

### Q：如果 RAG 系统检索到了不相关文档，但 LLM 仍然生成了听起来合理的答案，该如何处理？

**参考答案：**

这是最危险的 RAG 失败模式，因为它会基于真实但不相关的文档生成听起来很自信的幻觉。我会从三个位置处理：

首先，在检索阶段增加相关性评估器——使用分类器（或 LLM 调用）对每个检索文本块相对于查询的相关性进行评分。如果所有文本块都低于阈值，系统应该转向 Web 搜索（纠错式 RAG 模式），或者返回“我没有足够信息”，而不是根据弱上下文生成答案。

其次，在生成阶段使用受约束的 Prompt，要求模型在证据不足时明确说明。输出中包含置信度分数，并将低置信度答案路由给人工审核。

第三，在监控阶段跟踪检索分数与用户反馈之间的相关性。如果检索分数很高的查询仍然收到差评，根因可能是重排序器或分块策略。记录完整 Trace（查询、检索文本块、生成答案、用户反馈），以便调试具体失败案例。

### Q：你的 RAG 系统在查询量没有增加的情况下，成本在过去一个月翻了三倍。你会如何诊断和修复？

**参考答案：**

我会按以下顺序调查：

首先检查**缓存命中率**。如果命中率下降，说明更多查询进入了完整流水线。常见原因包括：语义缓存阈值发生变化、数据更新后缓存失效过于激进，或查询分布变化导致无法匹配缓存查询。

其次检查**模型路由分布**。如果查询分类器把更多查询路由到了昂贵的大模型，仅此一项就可能让成本翻三倍。检查查询复杂度是否发生变化，或者分类器行为是否发生漂移。

第三检查 Agent 式 RAG 路径中的**检索打转**。如果纠错式 RAG 循环重试次数增加（可能是 Embedding 过时或检索质量退化导致），每个查询都会产生多次检索和生成调用。Trace 日志会显示每个查询的平均迭代次数。

第四检查**Embedding 流水线**。如果文档被不必要地重复生成 Embedding（重复摄取、没有去重），Embedding 成本就会飙升。

修复方案取决于根因，但常见措施包括：调优语义缓存阈值、为每次查询设置成本上限以强制切换到更便宜的兜底路径、修复 Embedding 过时问题以减少纠错检索循环，以及在摄取流水线中增加去重。

---

## 参考资料

- Asai 等。《Self-RAG: Learning to Retrieve, Generate, and Critique》（2024）
- Yan 等。《Corrective Retrieval Augmented Generation (CRAG)》（2024）
- Shi 等。《RAGRouter: Learning to Route Queries to Multiple RAL Models》（2025）
- Redis。《RAG at Scale: How to Build Production AI Systems in 2026》
- Anthropic。《1M Token Context Window General Availability》（2026 年 3 月）
- RAGAS Framework。《Context Precision, Recall, Faithfulness, and Relevancy Metrics》
- AWS。《Multi-Tenant RAG with Amazon Bedrock Knowledge Bases》（2025）
- Microsoft。《Design a Secure Multitenant RAG Inferencing Solution》（2025）

---

*下一篇：[面向 AI 的数据工程](15-data-engineering-for-ai.md)*
