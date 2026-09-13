# 混合搜索

混合搜索结合稠密（语义）检索与稀疏（关键词）检索，同时获得两者的优点。它是生产级 RAG 的基线：Elasticsearch 的 `rrf` 检索器、OpenSearch 混合搜索、Weaviate、Qdrant 和 Azure AI Search 都开箱即用地提供原生混合流水线。

## 目录

- [为什么需要混合搜索](#why-hybrid-search)
- [稠密检索与稀疏检索](#dense-vs-sparse-retrieval)
- [混合搜索架构](#hybrid-search-architectures)
- [融合方法](#fusion-methods)
- [学习型稀疏 Embedding（SPLADE）](#learned-sparse-embeddings-splade)
- [实现模式](#implementation-patterns)
- [调优与优化](#tuning-and-optimization)
- [生产考量](#production-considerations)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## 为什么需要混合搜索

稠密检索和稀疏检索都不是普遍更优的方案，它们擅长不同类型的查询。

### 查询类型分析

| 查询类型 | 示例 | 更适合的检索 |
|------------|---------|------------------|
| 概念型 | “Transformer 如何学习？” | 稠密 |
| 关键词型 | “GPT-4 API 速率限制” | 稀疏 |
| 命名实体 | “John Smith 关于 BERT 的研究” | 稀疏 |
| 缩写/代码 | “HTTP 429 是什么意思？” | 稀疏 |
| 改写型 | “如何让 AI 更快”与“LLM 优化” | 稠密 |
| 混合型 | “GPT-4o API 的成本是多少？” | 混合 |

**细节**：纯稠密检索在技术文档上容易失败，因为特定版本号和函数名承载了 90% 的信息价值。

### 差距问题

稠密检索可能漏掉精确匹配：

```
Query: "Configure NVIDIA_VISIBLE_DEVICES"
Document: "Set the NVIDIA_VISIBLE_DEVICES environment variable..."

Dense search may miss this because:
- "NVIDIA_VISIBLE_DEVICES" might tokenize poorly
- Semantic embedding does not capture exact string matching
- Training data may not have this specific term
```

稀疏搜索（BM25）会立即找到它，因为存在精确 Token 匹配。

---

## 稠密检索与稀疏检索

### 稠密（语义）检索

使用神经网络 Embedding 匹配含义。

```python
def dense_search(query: str, top_k: int = 10) -> list[Result]:
    query_embedding = embedding_model.encode(query)
    results = vector_db.search(query_embedding, top_k=top_k)
    return results
```

**优点：**
- 理解改写和同义词
- 捕获概念相似性
- 使用多语言模型时支持跨语言

**缺点：**
- 可能漏掉精确关键词匹配
- 难以处理实体、代码和缩写
- 需要 Embedding 模型

### 稀疏（关键词）检索

使用词频和统计信息（BM25、TF-IDF）。

```python
def sparse_search(query: str, top_k: int = 10) -> list[Result]:
    tokens = tokenize(query)
    results = bm25_index.search(tokens, top_k=top_k)
    return results
```

**优点：**
- 精确匹配能力出色
- 能处理稀有词、代码和实体
- 快速且可解释
- 无需训练

**缺点：**
- 无法捕获语义相似性
- 不理解同义词
- 对词汇不匹配敏感

### 正面对比

| 方面 | 稠密 | 稀疏 | 混合 |
|--------|-------|--------|--------|
| 语义匹配 | 最佳 | 差 | 最佳 |
| 精确匹配 | 差 | 最佳 | 最佳 |
| 稀有词 | 差 | 最佳 | 很好 |
| 零样本领域 | 很好 | 最佳 | 最佳 |
| 延迟 | 中 | 快 | 中 |
| 实现 | 中 | 简单 | 复杂 |

---

## 混合搜索架构

### 架构 1：并行检索与融合

```
                    +------------------+
                    |      Query       |
                    +--------+---------+
                             |
              +--------------+--------------+
              v                             v
    +-------------------+         +-------------------+
    |  Dense Retrieval  |         |  Sparse Retrieval |
    |   (Vector DB)     |         |    (BM25/ES)      |
    +---------+---------+         +---------+---------+
              |                             |
              +--------------+--------------+
                             v
                    +-------------------+
                    |      Fusion       |
                    |  (RRF, weighted)  |
                    +---------+---------+
                              |
                              v
                    +-------------------+
                    |  Final Results    |
                    +-------------------+
```

**优点**：职责清晰，每种能力都可以使用最佳方案（例如 Pinecone + Algolia），并且可以独立调优。
**缺点**：需要维护两个独立系统，延迟更高（必须等待较慢的引擎）。

### 架构 2：原生混合（单一系统）

部分向量数据库原生支持混合：

```python
# Weaviate
results = client.query.get("Document", ["text"]).with_hybrid(
    query="Configure NVIDIA_VISIBLE_DEVICES",
    alpha=0.5  # 0 = sparse only, 1 = dense only
).do()

# Qdrant (with sparse vectors)
results = client.search(
    collection_name="docs",
    query_vector=NamedVector(name="dense", vector=dense_embedding),
    query_sparse_vector=NamedSparseVector(name="sparse", vector=sparse_vector),
)
```

**优点**：单一系统，运维简单，延迟较低。
**缺点**：融合定制能力有限，关键词与向量基础设施无法灵活独立扩展。

### 架构 3：分阶段检索

```
Query --> Sparse (fast, broad) --> Top 1000
                    |
                    v
          Dense reranking --> Top 100
                    |
                    v
           Cross-encoder --> Top 10
```

**优点**：高效，每个阶段逐步细化。
**缺点**：更复杂，存在早期阶段错误的风险。

---

## 融合方法

### 互惠秩融合（RRF）

RRF 是组合两个不同搜索引擎结果的黄金标准。它不查看不同引擎之间无法比较的**分数**，而只查看**排名**。

```python
def reciprocal_rank_fusion(
    rankings: list[list[str]],  # List of doc_id lists
    k: int = 60
) -> list[tuple[str, float]]:
    scores = defaultdict(float)

    for ranking in rankings:
        for rank, doc_id in enumerate(ranking):
            scores[doc_id] += 1 / (k + rank + 1)

    sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_docs
```

**特性：**
- 基于位置，忽略原始分数
- 对分数尺度差异稳健——防止某个引擎仅仅因为数值分数较高就“支配”结果
- `k` 参数控制对排名的敏感度（`k` 越高，对位置越不敏感）
- 实现简单，除了 `k` 外几乎无需调参

**常用 `k` 值**：60（原论文），实践中为 10～100。

### 加权分数融合

组合归一化后的分数：

```python
def weighted_fusion(
    dense_results: list[Result],
    sparse_results: list[Result],
    alpha: float = 0.5  # Weight for dense
) -> list[Result]:
    # Normalize scores to [0, 1]
    dense_normalized = normalize_scores(dense_results)
    sparse_normalized = normalize_scores(sparse_results)

    # Combine
    combined = {}
    for r in dense_normalized:
        combined[r.id] = alpha * r.score
    for r in sparse_normalized:
        combined[r.id] = combined.get(r.id, 0) + (1 - alpha) * r.score

    sorted_docs = sorted(combined.items(), key=lambda x: x[1], reverse=True)
    return sorted_docs

def normalize_scores(results: list[Result]) -> list[Result]:
    if not results:
        return []
    min_score = min(r.score for r in results)
    max_score = max(r.score for r in results)
    range_score = max_score - min_score + 1e-6

    return [
        Result(id=r.id, score=(r.score - min_score) / range_score)
        for r in results
    ]
```

**特性：**
- 使用实际分数（信息比排名更多）
- 需要分数归一化
- `alpha` 控制稠密与稀疏的平衡

### 相对分数融合

考虑分数分布：

```python
def relative_score_fusion(
    dense_results: list[Result],
    sparse_results: list[Result]
) -> list[Result]:
    # Use z-score normalization
    dense_normalized = z_score_normalize(dense_results)
    sparse_normalized = z_score_normalize(sparse_results)

    # Combine
    combined = {}
    for r in dense_normalized:
        combined[r.id] = r.score
    for r in sparse_normalized:
        combined[r.id] = combined.get(r.id, 0) + r.score

    return sorted(combined.items(), key=lambda x: x[1], reverse=True)

def z_score_normalize(results: list[Result]) -> list[Result]:
    scores = [r.score for r in results]
    mean = sum(scores) / len(scores)
    std = (sum((s - mean) ** 2 for s in scores) / len(scores)) ** 0.5 + 1e-6

    return [Result(id=r.id, score=(r.score - mean) / std) for r in results]
```

### 融合方法对比

| 方法 | 使用分数 | 查询自适应 | 复杂度 |
|--------|-------------|------------|------------|
| RRF | 否（仅排名） | 否 | 低 |
| 加权 | 是 | 否 | 低 |
| 相对分数 | 是 | 部分 | 中 |
| 学习型 | 是 | 是 | 高 |

---

## 学习型稀疏 Embedding（SPLADE）

生产技术栈已经从 BM25（简单词频）发展到**学习型稀疏 Embedding**，用于混合搜索中的稀疏分支。

**技术**：**SPLADE v3** 等模型会为词典中的每个词预测“重要性权重”。

**为什么需要它？** SPLADE 可以扩展查询。如果搜索“CPU”，即使查询中没有“processor”，它也可能自动为“processor”分配较小权重。它在单一存储格式中结合了稀疏搜索的精确匹配能力与稠密搜索的概念理解能力。

### SPLADE 实现

```python
from transformers import AutoModelForMaskedLM, AutoTokenizer

class SpladeEncoder:
    def __init__(self, model_name="naver/splade-cocondenser-ensembledistil"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForMaskedLM.from_pretrained(model_name)

    def encode(self, text: str) -> dict[str, float]:
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
        outputs = self.model(**inputs)

        # Get sparse weights
        weights = torch.max(
            torch.log(1 + torch.relu(outputs.logits)) * inputs["attention_mask"].unsqueeze(-1),
            dim=1
        ).values.squeeze()

        # Convert to sparse dict
        non_zero = weights.nonzero().squeeze().tolist()
        sparse_vec = {
            self.tokenizer.decode([idx]): weights[idx].item()
            for idx in non_zero
            if weights[idx] > 0
        }

        return sparse_vec
```

**什么时候选择 SPLADE 而不是 BM25 + 稠密混合？** SPLADE 会生成可存储在现代向量数据库（如 Milvus 或 Qdrant）中的稀疏向量，并与稠密向量并列存储，从而无需单独的 Elasticsearch 或 BM25 索引，就能以一次查询完成混合搜索。如果数据集包含极其稀有的非语言 Token（例如唯一序列号），而神经模型可能在训练时没有见过它们，则应坚持使用 BM25。

---

## 实现模式

### 模式 1：Elasticsearch + 向量数据库

```python
class HybridSearcher:
    def __init__(self, es_client, vector_db, embedding_model):
        self.es = es_client
        self.vector_db = vector_db
        self.embedding_model = embedding_model

    def search(self, query: str, top_k: int = 10, alpha: float = 0.5) -> list[Result]:
        # Parallel retrieval
        dense_future = self.dense_search(query, top_k * 3)
        sparse_future = self.sparse_search(query, top_k * 3)

        dense_results = dense_future.result()
        sparse_results = sparse_future.result()

        # Fusion
        combined = reciprocal_rank_fusion([
            [r.id for r in dense_results],
            [r.id for r in sparse_results]
        ])

        return combined[:top_k]

    async def dense_search(self, query: str, top_k: int) -> list[Result]:
        embedding = self.embedding_model.encode(query)
        return self.vector_db.search(embedding, top_k=top_k)

    async def sparse_search(self, query: str, top_k: int) -> list[Result]:
        response = self.es.search(
            index="documents",
            body={
                "query": {"match": {"content": query}},
                "size": top_k
            }
        )
        return [
            Result(id=hit["_id"], score=hit["_score"])
            for hit in response["hits"]["hits"]
        ]
```

### 模式 2：使用 Weaviate 的原生混合

```python
import weaviate

def hybrid_search_weaviate(
    client: weaviate.Client,
    query: str,
    alpha: float = 0.5,
    top_k: int = 10
) -> list[dict]:
    result = client.query.get(
        "Document",
        ["text", "title", "source"]
    ).with_hybrid(
        query=query,
        alpha=alpha,  # 0 = BM25 only, 1 = vector only
        fusion_type=weaviate.HybridFusion.RELATIVE_SCORE
    ).with_limit(top_k).do()

    return result["data"]["Get"]["Document"]
```

---

## 调优与优化

### Alpha 调优

`alpha` 参数平衡稠密与稀疏：

```python
def find_optimal_alpha(
    test_queries: list[tuple[str, list[str]]],  # (query, relevant_doc_ids)
    alpha_range: list[float] = [0.0, 0.3, 0.5, 0.7, 1.0]
) -> float:
    best_alpha = 0.5
    best_ndcg = 0

    for alpha in alpha_range:
        ndcg_scores = []
        for query, relevant in test_queries:
            results = hybrid_search(query, alpha=alpha)
            ndcg = compute_ndcg(results, relevant)
            ndcg_scores.append(ndcg)

        avg_ndcg = sum(ndcg_scores) / len(ndcg_scores)
        if avg_ndcg > best_ndcg:
            best_ndcg = avg_ndcg
            best_alpha = alpha

    return best_alpha
```

**最佳实践/典型发现：**
- 技术文档和代码：alpha 0.3～0.4（偏关键词）
- 通用文本：alpha 0.5（平衡）
- 聊天和创意探索：alpha 0.7～0.9（偏语义）

### 查询自适应 Alpha

预测每个查询的最佳 alpha：

```python
def predict_alpha(query: str) -> float:
    # Heuristics-based
    has_quotes = '"' in query
    has_code = any(c in query for c in ['_', '()', '{}', '[]'])
    has_numbers = any(c.isdigit() for c in query)

    # More sparse for exact match queries
    if has_quotes or has_code:
        return 0.3
    if has_numbers:
        return 0.4

    # More semantic for natural language
    if len(query.split()) > 5:
        return 0.7

    return 0.5  # Default balanced
```

### 检索深度

融合前要获取多少结果：

```python
# Rule of thumb: fetch 3-5x more from each source
def hybrid_search(query: str, final_k: int = 10):
    fetch_k = final_k * 4

    dense_results = dense_search(query, top_k=fetch_k)
    sparse_results = sparse_search(query, top_k=fetch_k)

    fused = rrf([dense_results, sparse_results])
    return fused[:final_k]
```

---

## 生产考量

### 延迟预算

```
Typical hybrid search latency breakdown:

Dense embedding:           30-50ms
Dense retrieval:          30-50ms
Sparse retrieval:         20-40ms  (parallel with dense)
Fusion:                    1-5ms
Total:                   60-100ms
```

**优化方式：**
- 并行运行稠密和稀疏检索
- 为常见查询预计算 Embedding
- 两条路径都使用近似搜索
- 为重复查询缓存融合结果

### 缓存策略

```python
class HybridSearchCache:
    def __init__(self, ttl_seconds: int = 300):
        self.cache = TTLCache(ttl=ttl_seconds)

    def search(self, query: str, **kwargs) -> list[Result]:
        cache_key = self._make_key(query, kwargs)

        if cache_key in self.cache:
            return self.cache[cache_key]

        results = self._do_search(query, **kwargs)
        self.cache[cache_key] = results
        return results

    def _make_key(self, query: str, kwargs: dict) -> str:
        return hashlib.sha256(
            f"{query}:{sorted(kwargs.items())}".encode()
        ).hexdigest()
```

### 兜底策略

```python
def hybrid_search_with_fallback(query: str, top_k: int = 10) -> list[Result]:
    try:
        return hybrid_search(query, top_k=top_k)
    except DenseSearchError:
        # Fallback to sparse only
        return sparse_search(query, top_k=top_k)
    except SparseSearchError:
        # Fallback to dense only
        return dense_search(query, top_k=top_k)
```

---

## 面试问题

### Q：什么时候应该选择混合搜索，而不是纯稠密搜索？

**参考答案：**
以下情况我会使用混合搜索：

1. **查询包含特定术语**：产品码、API 名称、错误码，稠密搜索可能漏掉精确匹配。
2. **领域有专用词汇**：技术文档、法律、医疗，稀疏检索能够捕获特定术语。
3. **零样本检索**：新领域没有经过微调的 Embedding，稀疏检索能提供稳健基线。
4. **质量至关重要**：混合通常不会比单一路径差，但会增加复杂度。

**以下情况坚持纯稠密：**
- 查询完全是概念/语义型
- 延迟预算非常紧
- 优先考虑架构简单
- Embedding 模型已经针对领域充分调优

这个决定需要用数据验证。我会在真实查询分布上对混合和稠密进行 A/B 测试。

### Q：为什么互惠秩融合（RRF）比“简单相加分数”更安全？

**参考答案：**
简单相加很危险，因为向量分数（例如 0.0～1.0 的余弦相似度）和关键词分数（例如 0 到无穷的 BM25）使用完全不同的尺度。一次幸运的关键词匹配得到的极高 BM25 分数，可能“淹没”10 个高度相关的语义匹配。RRF 忽略绝对分数，只关心相对顺序（排名），因此在数学上对离群值和不同检索引擎的“分数漂移”更稳健。

### Q：什么时候会选择 SPLADE，而不是标准的 BM25 + 稠密混合？

**参考答案：**
当我想简化基础设施时会选择 SPLADE。SPLADE 产生可以存储在许多现代向量数据库（如 Milvus 或 Qdrant）中的稀疏向量，并与稠密向量并列存储。这样数据库无需单独的 Elasticsearch 或 BM25 索引，就能一次完成“混合搜索”。但如果数据集包含极其稀有的非语言 Token（例如唯一序列号），而神经模型可能在训练时没有见过它们，我会坚持使用 BM25。

### Q：如何平衡混合搜索中的稠密与稀疏？

**参考答案：**
`alpha` 参数控制平衡（通常 alpha 表示稠密权重）：

**调优方式：**
1. 从 alpha=0.5（权重相等）开始
2. 创建包含查询和相关性标签的评估集
3. 在 [0.1, 0.3, 0.5, 0.7, 0.9] 中网格搜索 alpha
4. 衡量每种设置下的 NDCG 或 MRR
5. 选择评估指标最大的 alpha

**查询自适应调优：**
- 检测查询类型（关键词型、概念型、混合型）
- 按查询调整 alpha
- 可以使用简单启发式规则或学习型分类器

**经验法则：**
- 技术/代码查询：alpha 0.3～0.4
- 通用文本：alpha 0.5
- 对话式查询：alpha 0.7～0.8

---

## 参考资料

- Cormack 等。《Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods》（2009）
- Formal 等。《SPLADE: Sparse Lexical and Expansion Model for First Stage Ranking》（2021/2025）
- Weaviate Hybrid Search: https://weaviate.io/developers/weaviate/search/hybrid
- Qdrant Hybrid Search: https://qdrant.tech/documentation/concepts/hybrid-queries/

---

*上一篇：[向量数据库](04-vector-databases.md) | 下一篇：[重排序策略](06-reranking-strategies.md)*
