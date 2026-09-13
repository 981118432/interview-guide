# 重排序策略

重排序是检索的第二阶段：使用高精度模型，对一小组候选项（Top 50～100）重新评分。它连接了“高效搜索”和“完美依据”：第一阶段检索优化召回率，重排序优化精确率。目前生产环境中占主导地位的三种重排序器是 BGE-Reranker-v2-m3、Cohere Rerank 3 和 Voyage rerank-2；选择由成本模型、延迟尾部、语言覆盖范围以及是否需要自托管权重决定。

## 目录

- [为什么需要重排序](#why-reranking)
- [重排序架构](#reranking-architectures)
- [重排序模型](#reranking-models)
- [实现模式](#implementation-patterns)
- [什么时候重排序](#when-to-rerank)
- [基于 LLM 的重排序](#llm-based-reranking)
- [SLM 蒸馏](#slm-distillation)
- [生产考量](#production-considerations)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## 为什么需要重排序

### 质量差距

| 阶段 | 模型 | 速度 | 质量 |
|-------|-------|---------|---------|
| Embedding 检索 | 双编码器 | 快（毫秒级） | 良好 |
| 重排序 | 交叉编码器 | 慢（10～100ms） | 更好 |

**差距产生的原因：**
- 双编码器分别对查询和文档生成 Embedding
- 交叉编码器联合处理查询和文档
- 联合处理可以捕获双编码器遗漏的交互

### 示例

```
Query: "How to configure CUDA memory"

Document 1: "Configure GPU memory using CUDA_VISIBLE_DEVICES..."
Document 2: "Memory management in CUDA applications..."
Document 3: "Configure RAM allocation for machine learning..."

Bi-encoder scores (cosine similarity):
- Doc 1: 0.72
- Doc 2: 0.75  <-- Ranked first (wrong)
- Doc 3: 0.71

Cross-encoder scores (relevance):
- Doc 1: 0.91  <-- Ranked first (correct)
- Doc 2: 0.67
- Doc 3: 0.42
```

交叉编码器可以看出，查询中的“CUDA memory”与文档 1 中的“GPU memory...CUDA”相关。

---

## 重排序架构

### 双编码器与交叉编码器

**双编码器（第一阶段）：**
```
Query --> Encoder --> Query Embedding -+
                                      +-> Similarity
Document --> Encoder --> Doc Embedding +
```
- 每篇文档 O(1)（Embedding 已预计算）
- 看不到查询与文档之间的交互

**交叉编码器（重排序）：**
```
[Query, Document] --> Encoder --> Relevance Score
```
- 每个查询 O(n)（处理每个候选项）
- 能看到完整的查询—文档上下文
- 使用**注意力机制**比较查询中的具体词语如何改变文档中词语的含义（延迟交互）

### 两阶段流水线

生产级检索使用两阶段漏斗：

```
+----------------------------------------------------------------+
|  STAGE 1: Retrieval (Bi-Encoder)                                |
|                                                                 |
|  Query --> Embed --> Top-K candidates (K=100)                   |
|  Scale: Search 1 Billion docs. Cost: Low (ms).                 |
+----------------------------+-----------------------------------+
                             |
                             v
+----------------------------------------------------------------+
|  STAGE 2: Reranking (Cross-Encoder)                             |
|                                                                 |
|  For each candidate:                                            |
|    score = reranker([query, candidate])                         |
|  Scale: Search Top 100 docs. Cost: High (10-100ms).            |
|                                                                 |
|  Return Top-N by reranker score (N=5-10)                        |
+----------------------------------------------------------------+
```

### 多阶段流水线

对于超大语料库：

```
Stage 1: Sparse (BM25)      -> Top 1000
Stage 2: Dense (Bi-encoder) -> Top 100
Stage 3: Cross-encoder      -> Top 10
```

每个阶段都以速度换取准确率。

---

## 重排序模型

### 交叉编码器模型

| 模型 | 规模 | 语言 | 质量 |
|-------|------|-----------|---------|
| ms-marco-MiniLM-L-6 | 2200 万 | 英语 | 良好 |
| bge-reranker-base | 2.78 亿 | 英语 | 很好 |
| **bge-reranker-v2-m3** | 5.68 亿 | 多语言 | 优秀 |
| Cohere Rerank v3 | API | 多语言 | 优秀 |
| Jina Reranker v2 | 多种 | 多语言（8000+ Token） | 很好 |

**“中间丢失”的修复**：重排序器经过训练，会无论信息在文本块中的什么位置都优先考虑相关信息，确保“中间”数据在发送给最终 LLM 前得到正确评分。

### 使用交叉编码器

```python
from sentence_transformers import CrossEncoder

# Load model
reranker = CrossEncoder('BAAI/bge-reranker-base')

def rerank(query: str, documents: list[str], top_k: int = 5) -> list[tuple[str, float]]:
    # Create pairs
    pairs = [[query, doc] for doc in documents]

    # Score all pairs
    scores = reranker.predict(pairs)

    # Sort by score
    scored_docs = sorted(
        zip(documents, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return scored_docs[:top_k]
```

### Cohere Rerank

```python
import cohere

co = cohere.Client(api_key="...")

def cohere_rerank(
    query: str,
    documents: list[str],
    top_k: int = 5
) -> list[dict]:
    response = co.rerank(
        model="rerank-english-v3.0",
        query=query,
        documents=documents,
        top_n=top_k,
        return_documents=True
    )

    return [
        {
            "text": result.document.text,
            "score": result.relevance_score,
            "index": result.index
        }
        for result in response.results
    ]
```

### 模型选择指南

| 用例 | 推荐模型 | 说明 |
|----------|-------------------|-------|
| 英语、自托管 | bge-reranker-base | 平衡良好 |
| 多语言 | bge-reranker-v2-m3 | 最佳开源方案 |
| 低延迟 | MiniLM-L-6 | 快 4 倍 |
| 最高质量 | Cohere Rerank v3 | API，规模化成本高 |
| 大 Batch | Jina Reranker | 吞吐良好 |
| 长查询（8000+） | Jina Reranker v2 | 能处理长上下文 |

---

## 实现模式

### 模式 1：基本重排序

```python
class RerankedRetriever:
    def __init__(
        self,
        vector_db,
        embedding_model,
        reranker,
        retrieval_k: int = 50,
        rerank_k: int = 5
    ):
        self.vector_db = vector_db
        self.embedding_model = embedding_model
        self.reranker = reranker
        self.retrieval_k = retrieval_k
        self.rerank_k = rerank_k

    def search(self, query: str) -> list[Document]:
        # Stage 1: Retrieve candidates
        query_embedding = self.embedding_model.encode(query)
        candidates = self.vector_db.search(
            query_embedding,
            top_k=self.retrieval_k
        )

        # Stage 2: Rerank
        pairs = [[query, c.text] for c in candidates]
        scores = self.reranker.predict(pairs)

        # Combine and sort
        for candidate, score in zip(candidates, scores):
            candidate.rerank_score = score

        reranked = sorted(candidates, key=lambda x: x.rerank_score, reverse=True)
        return reranked[:self.rerank_k]
```

### 模式 2：批量重排序

```python
def batch_rerank(
    queries: list[str],
    candidates_per_query: list[list[str]],
    reranker,
    batch_size: int = 32
) -> list[list[tuple[str, float]]]:
    # Flatten all pairs
    all_pairs = []
    pair_mapping = []  # (query_idx, doc_idx)

    for q_idx, (query, candidates) in enumerate(zip(queries, candidates_per_query)):
        for d_idx, doc in enumerate(candidates):
            all_pairs.append([query, doc])
            pair_mapping.append((q_idx, d_idx))

    # Batch score
    all_scores = []
    for i in range(0, len(all_pairs), batch_size):
        batch = all_pairs[i:i + batch_size]
        scores = reranker.predict(batch)
        all_scores.extend(scores)

    # Reconstruct per-query results
    results = [[] for _ in queries]
    for (q_idx, d_idx), score in zip(pair_mapping, all_scores):
        results[q_idx].append((candidates_per_query[q_idx][d_idx], score))

    # Sort each query's results
    for i in range(len(results)):
        results[i].sort(key=lambda x: x[1], reverse=True)

    return results
```

### 模式 3：异步重排序

```python
import asyncio

class AsyncReranker:
    def __init__(self, reranker, max_concurrent: int = 5):
        self.reranker = reranker
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def rerank_async(
        self,
        query: str,
        documents: list[str]
    ) -> list[tuple[str, float]]:
        async with self.semaphore:
            # Run reranking in thread pool
            loop = asyncio.get_event_loop()
            scores = await loop.run_in_executor(
                None,
                lambda: self.reranker.predict([[query, doc] for doc in documents])
            )
            return sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
```

---

## 什么时候重排序

### 成本收益分析

| 因素 | 不重排序 | 重排序 |
|--------|-------------------|----------------|
| 延迟 | 50～100ms | 150～300ms |
| 质量（NDCG） | 0.65 | 0.78 |
| 复杂度 | 简单 | 中等 |
| 成本 | 基线 | +API 成本或 +计算资源 |

### 决策框架

**始终重排序：**
- 质量至关重要（面向客户、高风险）
- 检索候选项的分数接近
- 查询复杂或包含多个部分
- 预算允许增加延迟

**跳过重排序：**
- 延迟预算非常紧（总计小于 100ms）
- 检索候选项的排名明显
- 简单查询（单词查找）
- 大规模场景对成本敏感

### 推理时间权衡

| 阶段 | 检索（K） | 重排（N） | 延迟 | 质量 |
|-------|---------------|------------|---------|---------|
| **朴素** | 5 | 0 | 50ms | 低 |
| **标准** | 50 | 5 | 150ms | 高 |
| **企业级** | 200 | 20 | 500ms | 最高 |

**关键规则**：如果预算为 200ms，应花 50ms 检索、150ms 重排序。重排 Top 50 的投入产出比远高于从向量数据库中检索更多文本块。

### 最佳候选数量

重排序前应该检索多少候选项：

```python
def optimize_candidate_count(test_set, retriever, reranker):
    """Find optimal retrieval_k for reranking."""
    results = {}

    for retrieval_k in [10, 20, 50, 100, 200]:
        ndcg_scores = []
        latencies = []

        for query, relevant_docs in test_set:
            start = time.time()

            # Retrieve
            candidates = retriever.search(query, top_k=retrieval_k)

            # Rerank to top 5
            reranked = reranker.rerank(query, candidates, top_k=5)

            latency = time.time() - start
            latencies.append(latency)

            ndcg = compute_ndcg(reranked, relevant_docs)
            ndcg_scores.append(ndcg)

        results[retrieval_k] = {
            "ndcg": mean(ndcg_scores),
            "latency_p99": percentile(latencies, 99)
        }

    return results

# Typical findings:
# K=20:  NDCG 0.72, latency 120ms
# K=50:  NDCG 0.76, latency 180ms  <-- Often sweet spot
# K=100: NDCG 0.77, latency 280ms  <-- Diminishing returns
```

---

## 基于 LLM 的重排序

### 将 LLM 用作重排序器

LLM 可以评估相关性，但成本很高：

```python
def llm_rerank(
    query: str,
    documents: list[str],
    model: str = "gpt-4o-mini"
) -> list[tuple[str, float]]:
    prompt = f"""Rate the relevance of each document to the query.
Query: {query}

Documents:
{format_documents(documents)}

For each document, output a relevance score from 0-10.
Format: DOC_NUM: SCORE
"""

    response = llm.generate(prompt)
    scores = parse_scores(response)

    return sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
```

**优点：**
- 可以处理复杂的相关性判断
- 理解细微差别和上下文
- 无需维护独立模型

**缺点：**
- 规模化成本高（是交叉编码器的 10～100 倍）
- 更慢（1～3 秒，而不是 100ms）
- 非确定性

### LLM 的列表式与逐点式重排序

**逐点式**：独立评估每篇文档
```
For document: [doc text]
Query: [query]
Rate relevance 0-10: _
```

**列表式**：一起排序所有文档
```
Query: [query]
Rank these documents by relevance:
A: [doc1]
B: [doc2]
C: [doc3]
Output order: _
```

**列表式通常更好**，因为 LLM 能直接比较文档。前沿模型（如 o1-mini 或 Sonnet 3.7）在这方面非常强，但会增加 1～2 秒延迟。它只用于法律、医疗等高风险企业搜索。

### 多文档的滑动窗口

```python
def sliding_window_rerank(
    query: str,
    documents: list[str],
    window_size: int = 10,
    step: int = 5
) -> list[str]:
    """Rerank many documents with LLM using sliding window."""
    ranked = list(range(len(documents)))

    for start in range(0, len(documents), step):
        window = ranked[start:start + window_size]

        # LLM ranks this window
        window_docs = [documents[i] for i in window]
        window_order = llm_listwise_rank(query, window_docs)

        # Update rankings
        for new_pos, old_idx in enumerate(window_order):
            ranked[start + new_pos] = window[old_idx]

    return [documents[i] for i in ranked]
```

---

## SLM 蒸馏

为解决基于 LLM 重排序的延迟问题，现在会使用**蒸馏的小型语言模型（SLM）**。

- **过程**：使用一个大模型（例如 GPT-5.2）为 100 万个文档对重排序，再用这些标签“蒸馏”出一个仅有 0.1B 参数的小模型。
- **结果**：以标准 CPU 查询的延迟（小于 10ms）获得大模型 95% 的重排序质量。
- **生产模式**：通常使用交叉编码器，在低置信度重排序分数时再使用 LLM 兜底。

---

## 生产考量

### 延迟优化

```python
class OptimizedReranker:
    def __init__(self, model_name: str, device: str = "cuda"):
        self.model = CrossEncoder(model_name, device=device)
        # Enable optimizations
        self.model.model.half()  # FP16

    def rerank(self, query: str, documents: list[str]) -> list[tuple[str, float]]:
        with torch.inference_mode():
            pairs = [[query, doc] for doc in documents]
            scores = self.model.predict(
                pairs,
                batch_size=32,
                show_progress_bar=False
            )
        return sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
```

**优化技术：**
- FP16 推理：加速 2 倍
- 批处理：摊销开销
- ONNX 导出：加速 1.5～2 倍
- TensorRT：加速 2～3 倍（NVIDIA）
- 模型蒸馏：以质量换取 4 倍加速

### 缓存重排序结果

```python
class CachedReranker:
    def __init__(self, reranker, cache_ttl: int = 3600):
        self.reranker = reranker
        self.cache = TTLCache(maxsize=10000, ttl=cache_ttl)

    def rerank(self, query: str, documents: list[str]) -> list[tuple[str, float]]:
        # Cache key includes query and doc hashes
        key = self._make_key(query, documents)

        if key in self.cache:
            return self.cache[key]

        result = self.reranker.rerank(query, documents)
        self.cache[key] = result
        return result

    def _make_key(self, query: str, documents: list[str]) -> str:
        doc_hash = hashlib.sha256(
            "".join(sorted(documents)).encode()
        ).hexdigest()[:16]
        query_hash = hashlib.sha256(query.encode()).hexdigest()[:16]
        return f"{query_hash}:{doc_hash}"
```

### 兜底策略

```python
def rerank_with_fallback(
    query: str,
    candidates: list[Document],
    primary_reranker,
    timeout: float = 2.0
) -> list[Document]:
    try:
        # Try reranking with timeout
        result = timeout_call(
            primary_reranker.rerank,
            args=(query, candidates),
            timeout=timeout
        )
        return result
    except TimeoutError:
        # Fallback: return original order
        logger.warning("Reranker timeout, using original order")
        return candidates
    except Exception as e:
        logger.error(f"Reranker error: {e}")
        return candidates
```

---

## 面试问题

### Q：为什么交叉编码器从根本上比双编码器更准确？

**参考答案：**
双编码器在还不知道查询之前，就为文档创建了一个静态的单向量表示，因此丢失了文本不同部分之间的具体关系。交叉编码器将查询和文档作为一个输入对，并使用**注意力机制**对二者进行比较。它能看到查询中的具体词语如何改变文档中词语的含义（延迟交互），因此比两个固定向量之间简单的数学相似度产生更细致的相关性评分。

**实践中**：第一阶段检索使用双编码器（速度），重排序使用交叉编码器（质量），从而兼得两者优点。

### Q：如何决定重排序多少候选项？

**参考答案：**
这是质量与延迟之间的权衡：

**影响因素：**
- 重排序器每篇文档的延迟
- 总延迟预算
- 质量提升曲线（通常存在收益递减）
- 第一阶段检索质量

**过程：**
1. 压测重排序器每篇文档的延迟
2. 计算延迟预算内允许的最大候选数
3. 测试不同 K 值下的质量
4. 找到质量与延迟的拐点

**典型发现：**
- K=20～50 通常最优
- 超过 K=100 后质量收益很小
- 根据第一阶段检索质量调整

如果重排序预算是 200ms、每篇文档需要 4ms，我会重排约 50 个候选项。

### Q：什么时候会使用基于 LLM 的重排序？

**参考答案：**
以下情况适合使用 LLM 重排序：

1. **复杂相关性判断**：查询需要理解细微差异、上下文或多跳推理
2. **低流量**：没有理由训练/托管交叉编码器
3. **要求最高质量**：法律、医疗、安全关键场景
4. **流水线已经使用 LLM**：边际成本更低

**注意事项：**
- 规模化成本高（是交叉编码器的 10～100 倍）
- 更慢（1～3 秒，而不是 100ms）
- 非确定性
- 可能需要仔细设计 Prompt

**生产模式**：通常使用交叉编码器，在低置信度重排序分数时由 LLM 兜底。

### Q：如何处理超长查询（例如一整段话）的重排序？

**参考答案：**
长查询会造成交叉编码器的“Token 预算”问题，因为交叉编码器通常有 512 或 1024 Token 的限制。常见修复方案是**滑动窗口重排序**或**查询摘要**。也可以使用能处理 8000+ Token 的专用模型（例如 **Jina-Reranker-v2**）。另一种常见方式是先用快速短上下文模型进行“第一轮重排”，再用高上下文 LLM 对 Top 5 候选项进行“第二轮重排”。

---

## 参考资料

- Nogueira and Cho。《Passage Re-ranking with BERT》（2019）
- Nogueira 等。《Multi-Stage Document Ranking with BERT》（2019/2025 更新）
- BAAI BGE Reranker: https://huggingface.co/BAAI/bge-reranker-base
- Cohere Rerank: https://docs.cohere.com/docs/rerank
- Sun 等。《Is ChatGPT Good at Search? Investigating Large Language Models as Re-Ranking Agents》（2023）

---

*上一篇：[混合搜索](05-hybrid-search.md) | 下一篇：[GraphRAG](07-graph-rag.md)*
