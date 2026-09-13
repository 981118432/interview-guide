# 向量数据库

向量数据库是专门用于存储、索引和搜索高维 Embedding 的系统。当前市场分为**托管无服务器**引擎和**专用高性能**引擎。我们不再问“它是否支持向量搜索？”（Postgres、Redis 和 Mongo 都支持），而是问：**“它能否在完整元数据过滤下，将 1 亿以上向量的 P99 延迟扩展到 100ms 以内？”**

## 目录

- [什么是向量数据库](#what-is-a-vector-database)
- [向量搜索基础](#vector-search-fundamentals)
- [索引算法](#indexing-algorithms)
- [竞争格局](#competitive-landscape)
- [数据库详细对比](#detailed-database-comparison)
- [元数据过滤](#metadata-filtering)
- [查询模式](#query-patterns)
- [生产运维](#production-operations)
- [托管与自托管（TCO 分析）](#managed-vs-self-hosted-tco-analysis)
- [选型框架](#selection-framework)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## 什么是向量数据库

向量数据库存储 Embedding（稠密向量），并支持对它们进行快速相似度搜索。

```
Traditional DB:      SELECT * FROM docs WHERE category = 'tech'
Vector DB:           SELECT * FROM docs ORDER BY similarity(embedding, query_embedding) LIMIT 10
```

### 核心能力

| 能力 | 用途 |
|------------|---------|
| 向量存储 | 持久化高维 Embedding |
| 相似度搜索 | 快速查找近邻 |
| 元数据过滤 | 将向量搜索与属性过滤组合 |
| CRUD 操作 | 随数据变化更新 Embedding |
| 扩展性 | 处理数百万到数十亿个向量 |

### 为什么不用通用数据库？

传统数据库可以存储向量，但缺少经过优化的搜索能力：

| 方案 | 搜索复杂度 | 大规模实践情况 |
|----------|-------------------|-------------------|
| 暴力搜索（PostgreSQL pgvector） | O(n * d) | 约 100 万向量以内可用 |
| ANN 索引（专用向量数据库） | O(log n) 或 O(1) | 可以，支持数十亿 |

---

## 向量搜索基础

### 精确搜索与近似搜索

**精确搜索（暴力搜索）：**
- 将查询与每个已存储向量比较
- 每次查询 O(n * d)
- 准确率完美

**近似最近邻（ANN）：**
- 使用索引结构剪枝搜索空间
- 次线性复杂度
- 召回率略低（通常为 95%～99%）

### 距离指标

| 指标 | 公式 | 范围 | 最适合 |
|----------|---------|-------|----------|
| 余弦 | 1 - (a . b) / (norm(a) * norm(b)) | [0, 2] | 文本 Embedding |
| 欧氏距离（L2） | sqrt(sum((a - b)^2)) | [0, inf) | 图像 Embedding |
| 点积 | a . b | (-inf, inf) | 已归一化向量 |

**对于文本 Embedding**：使用余弦相似度（如果已预归一化，也可以使用点积）。

### 召回率与延迟的权衡

```
                    ^ Recall
                    |
               100% | ------------------ Brute force
                    |         *          Well-tuned ANN
                    |      *
                    |   *
                95% |*                   Fast ANN
                    |
                    +-----+-------+------> Latency
                       1ms      10ms
```

ANN 索引以部分准确率换取速度，应根据需求进行调优。

---

## 索引算法

### HNSW（Hierarchical Navigable Small World）

生产环境**内存中**向量搜索最流行的算法。

**工作方式：**
1. 构建一个节点代表向量的图
2. 连接相近邻居
3. 使用多层抽象结构
4. 搜索时从顶层向下，以贪心方式寻找最近邻

```
Layer 2:   *--------*--------*
           |        |        |
Layer 1:   *--*--*--*--*--*--*
           |  |  |  |  |  |  |
Layer 0:   ********************  (all vectors)
```

**优点：**
- 召回率与延迟的权衡优秀
- 无需训练
- 原生支持更新

**缺点：**
- 内存占用高（图结构）
- 索引大小约为向量数据的 1.5～2 倍
- 1000 万个 1536 维向量需要约 80GB RAM

**关键参数：**
- `M`：每个节点的最大连接数（16～64）
- `ef_construction`：构建时的探索范围（100～500）
- `ef_search`：查询时的探索范围（50～200）

### DiskANN（基于 SSD）

**PB 级**搜索的行业标准。

**工作方式：**
- 将图保存在 SSD（NVMe）上，只在 RAM 中保留极小索引
- 使用 Vamana 算法高效遍历基于磁盘的图

**优点：**
- 对十亿级数据集，在延迟只增加不到 5ms 的情况下，比 HNSW 便宜 10 倍
- 相比 HNSW 减少 90%～95% 的 RAM 需求

**缺点：**
- 延迟略高于纯内存 HNSW
- 最适合非实时搜索应用

**示例**：一个 1 亿向量、1536 维的索引使用 HNSW 几乎需要 1TB RAM。使用 DiskANN 后，在保持查询时间低于 10ms 的同时，RAM 需求降低 90%～95%。

### IVF（倒排文件索引）

将向量划分为多个聚类，只搜索相关聚类。

**工作方式：**
1. 使用 k-means 创建质心
2. 将每个向量分配给最近质心
3. 查询时找到最近质心，并搜索这些聚类

**优点：**
- 内存占用低于 HNSW
- 可以使用量化（IVF-PQ）

**缺点：**
- 需要训练
- 更新需要重新聚类或采用混合方案

**关键参数：**
- `nlist`：聚类数量（经验法则是 sqrt(n)）
- `nprobe`：查询时要搜索的聚类数

### 乘积量化（PQ）

压缩向量，以降低内存占用并加速比较。

**工作方式：**
1. 将向量拆成子向量
2. 将每个子向量量化到码本
3. 存储编码，而不是完整向量

**内存减少**：通常为 4～32 倍

**权衡**：量化损失会降低准确率

### Flat 索引（暴力搜索）

不做近似，执行精确搜索。

**适用场景：**
- 少于 10 万个向量
- 准确率至关重要
- 延迟预算充足

### 算法对比

| 算法 | 内存 | 构建时间 | 查询速度 | 召回率 | 更新 |
|-----------|--------|------------|-------------|--------|---------|
| HNSW | 高 | 中 | 很快 | 95%～99% | 良好 |
| DiskANN | 低（SSD） | 中 | 快 | 95%～99% | 一般 |
| IVF | 中 | 快 | 快 | 90%～98% | 一般 |
| IVF-PQ | 低 | 快 | 快 | 85%～95% | 一般 |
| Flat | 低 | 无 | 慢 | 100% | 即时 |

---

## 竞争格局

### 向量原生（专用）

| 数据库 | 类型 | 最适合 | 定价模式 |
|----------|------|----------|---------------|
| **Pinecone** | 托管云（标准无服务器） | 快速开始、扩展、托管 SLA | 按向量小时 |
| **Qdrant** | 开源 / Cloud（Rust，高性能） | 自托管控制、常见负载下最快的开源方案（1000 万向量时约 12ms p99） | Cloud 按 GB，否则免费 |
| **Weaviate** | 开源 / Cloud | 单次查询原生混合（BM25 + 稠密 + 元数据），多模态 | 按维度小时 |
| **Milvus** | 开源 / Cloud（Zilliz） | 分布式扩展（5000 万以上向量）、异构节点、分层存储 | 自托管免费或 Zilliz Cloud |
| **Chroma** | 开源 | 原型、本地开发、嵌入式使用 | 免费 |

### 通用数据库（插件/扩展）

| 数据库 | 类型 | 最适合 | 定价模式 |
|----------|------|----------|---------------|
| **pgvector（v0.8+）** | PostgreSQL 扩展 | 小规模、已有 PG（现在支持 HNSW + IVFFlat） | 仅计算 |
| **Elasticsearch（v9.0）** | 搜索引擎 | 使用交叉熵融合的混合搜索 | 按许可证 |

---

## 数据库详细对比

### 功能矩阵

| 功能 | Pinecone | Qdrant | Weaviate | Milvus | pgvector |
|---------|----------|--------|----------|--------|----------|
| **语言** | 专有 | Rust | Go | Go/C++ | C |
| 托管选项 | 是 | 是 | 是 | 是（Zilliz） | 通过云 PG |
| 自托管 | 否 | 是 | 是 | 是 | 是 |
| **无服务器** | 是（最佳） | 是 | 是 | 是（Zilliz） | 否 |
| **云原生** | 任意 | 任意 | 任意 | 仅 K8s | 任意 |
| 元数据过滤 | 良好 | 优秀 | 良好 | 良好 | 通过 SQL |
| **混合搜索** | 原生 | 原生 | 原生 | 原生 | 多阶段（有限） |
| 最大向量数 | 数十亿 | 数十亿 | 数十亿 | 数十亿 | 约 1000 万 |
| HNSW 索引 | 是 | 是 | 是 | 是 | 是 |

---

## 元数据过滤

对多租户和过滤用例至关重要。

```python
# Pinecone
results = index.query(
    vector=query_embedding,
    top_k=10,
    filter={"tenant_id": "123", "category": {"$in": ["tech", "science"]}}
)

# Qdrant
results = client.search(
    collection_name="documents",
    query_vector=query_embedding,
    limit=10,
    query_filter=Filter(
        must=[
            FieldCondition(key="tenant_id", match=MatchValue(value="123")),
            FieldCondition(key="category", match=MatchAny(any=["tech", "science"]))
        ]
    )
)
```

**性能影响**：过滤发生在搜索过程中，而不是搜索之后。预过滤索引更快，但灵活性较低。

**为什么元数据过滤经常成为瓶颈**：在朴素向量搜索中，我们先找到最接近的 Top K 邻居，**然后**再按元数据过滤。如果过滤条件非常严格，过滤后可能得到 0 个结果。现在专用数据库使用 **HNSW 预过滤**，遍历图时只考虑满足布尔元数据约束的节点。这需要专用位掩码或硬件加速（SIMD）来保持低延迟。

**磁盘原生元数据**：**Qdrant** 等现代数据库将元数据卸载到内存映射的磁盘分段中，可以在不耗尽 RAM 的情况下处理复杂过滤（例如全文 + 地理 + 向量）。

---

## 查询模式

### 模式 1：简单语义搜索

```python
def semantic_search(query: str, top_k: int = 5) -> list[Document]:
    query_embedding = embed(query)
    results = vector_db.search(query_embedding, top_k=top_k)
    return [Document(id=r.id, text=r.payload["text"], score=r.score) for r in results]
```

### 模式 2：过滤搜索

```python
def filtered_search(query: str, filters: dict, top_k: int = 5) -> list[Document]:
    query_embedding = embed(query)
    results = vector_db.search(
        query_embedding,
        top_k=top_k,
        filter=filters  # {"tenant_id": "abc", "created_after": "2025-01-01"}
    )
    return results
```

### 模式 3：混合搜索（稠密 + 稀疏）

```python
def hybrid_search(query: str, alpha: float = 0.5, top_k: int = 5) -> list[Document]:
    # Dense (semantic)
    dense_embedding = embed(query)
    dense_results = vector_db.search(dense_embedding, top_k=top_k * 2)

    # Sparse (keyword)
    sparse_results = bm25_search(query, top_k=top_k * 2)

    # Combine with reciprocal rank fusion
    combined = reciprocal_rank_fusion(
        [dense_results, sparse_results],
        weights=[alpha, 1 - alpha]
    )

    return combined[:top_k]
```

部分数据库（Weaviate、Qdrant、Pinecone）原生支持混合搜索：

```python
# Weaviate native hybrid
results = client.query.get("Document", ["text"]).with_hybrid(
    query=query,
    alpha=0.5  # 0 = BM25 only, 1 = vector only
).with_limit(5).do()
```

### 模式 4：多向量查询

用于父子文档或多角度检索：

```python
def multi_vector_search(queries: list[str], top_k: int = 5) -> list[Document]:
    all_results = []

    for query in queries:
        embedding = embed(query)
        results = vector_db.search(embedding, top_k=top_k)
        all_results.extend(results)

    # Dedupe and rerank
    unique = dedupe_by_id(all_results)
    reranked = rerank(queries[0], unique)  # Use primary query for reranking

    return reranked[:top_k]
```

---

## 生产运维

### 容量规划

```python
def estimate_resources(
    num_vectors: int,
    dimensions: int,
    metadata_size_bytes: int = 500
) -> dict:
    # Vector storage
    vector_size = dimensions * 4  # float32
    total_vector_storage = num_vectors * vector_size

    # Index overhead (HNSW ~1.5x)
    index_overhead = total_vector_storage * 1.5

    # Metadata
    metadata_storage = num_vectors * metadata_size_bytes

    # Total
    total_gb = (total_vector_storage + index_overhead + metadata_storage) / 1e9

    # QPS estimate (rough)
    qps_per_gb = 50  # depends heavily on config
    estimated_qps = total_gb * qps_per_gb

    return {
        "storage_gb": total_gb,
        "estimated_qps": estimated_qps,
        "recommended_replicas": max(1, int(total_gb / 50))  # ~50GB per replica
    }
```

### 索引维护

```python
class VectorDBMaintenance:
    def __init__(self, client):
        self.client = client

    def add_documents(self, documents: list[Document]):
        """Upsert documents with batching."""
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            embeddings = embed_batch([d.text for d in batch])

            self.client.upsert([
                {
                    "id": doc.id,
                    "vector": embedding,
                    "payload": doc.metadata
                }
                for doc, embedding in zip(batch, embeddings)
            ])

    def delete_documents(self, doc_ids: list[str]):
        """Delete by document ID."""
        self.client.delete(ids=doc_ids)

    def update_metadata(self, doc_id: str, metadata: dict):
        """Update metadata without re-embedding."""
        self.client.set_payload(
            collection_name="documents",
            payload=metadata,
            points=[doc_id]
        )
```

### 高可用

```
+-------------------------------------------------------------+
|                    Load Balancer                              |
+----------------------------+--------------------------------+
                             |
            +----------------+----------------+
            v                v                v
     +--------------+ +--------------+ +--------------+
     |  Replica 1   | |  Replica 2   | |  Replica 3   |
     |   (Read)     | |   (Read)     | |   (Primary)  |
     +--------------+ +--------------+ +--------------+
                                             |
                                       (Replication)
                                             |
                                       +-----v-----+
                                       |  Storage   |
                                       +-----------+
```

**关键模式：**
- 写入采用主从模式
- 使用读副本扩展查询
- 使用异步复制实现高可用

### 监控

```python
VECTOR_DB_METRICS = [
    "query_latency_p50",
    "query_latency_p99",
    "queries_per_second",
    "index_size_gb",
    "vector_count",
    "filter_latency",
    "upsert_latency",
    "cache_hit_rate"
]

def alert_rules():
    return {
        "query_latency_p99_high": {
            "condition": "query_latency_p99 > 500ms",
            "severity": "warning"
        },
        "query_latency_p99_critical": {
            "condition": "query_latency_p99 > 2000ms",
            "severity": "critical"
        },
        "low_recall": {
            "condition": "bench_recall < 0.90",
            "severity": "warning"
        }
    }
```

---

## 托管与自托管（TCO 分析）

### 成本对比

| 方面 | Pinecone（无服务器） | 自托管（Qdrant/Milvus） |
|--------|-----------------------|-----------------------------|
| **运维开销** | 无 | 高（需要 K8s + SRE） |
| **扩展** | 即时（可缩容到零） | 手动（配置节点） |
| **小规模成本** | $0～100/月 | $50/月（最低实例） |
| **规模化成本** | 按 Token/向量计费较高 | 单位成本低 |

### 托管服务定价（仅供参考，务必在供应商页面核实）

| 供应商 | 模式 | 示例：1000 万向量，1536 维 |
|----------|------|--------------------------------|
| Pinecone | Pod 或无服务器 | 无服务器约 $70～150/月 |
| Qdrant Cloud | 按 GB | 约 $50/月（20GB） |
| Weaviate Cloud | 按维度 | 约 $100/月 |
| Zilliz（Milvus） | 按 CU | 约 $75/月 |

### 自托管成本

```python
def estimate_self_hosted_cost(
    vectors: int,
    dimensions: int,
    cloud: str = "aws"
) -> dict:
    storage_gb = (vectors * dimensions * 4 * 2.5) / 1e9  # 2.5x for index

    # Instance sizing
    if storage_gb < 50:
        instance = "r6g.large"  # 16 GB RAM, ~$60/month
    elif storage_gb < 200:
        instance = "r6g.xlarge"  # 32 GB RAM, ~$120/month
    else:
        instance = "r6g.2xlarge"  # 64 GB RAM, ~$240/month

    return {
        "storage_gb": storage_gb,
        "instance": instance,
        "monthly_compute": instance_pricing[instance],
        "monthly_storage": storage_gb * 0.10,  # EBS
        "total_monthly": instance_pricing[instance] + storage_gb * 0.10
    }
```

### 决策：托管还是自托管

| 因素 | 托管 | 自托管 |
|---------|---------|-------------|
| 运维开销 | 低 | 高 |
| 小规模成本 | 较高 | 较低 |
| 大规模成本 | 可变 | 通常较低 |
| 控制力 | 较少 | 完全控制 |
| 合规 | 取决于供应商 | 完全控制 |
| 供应商锁定 | 有 | 无（如果使用开源） |

**结论**：从无服务器开始。只有在拥有超过 5 亿个向量，或有严格的**本地部署/GPU 本地化**要求时，才考虑自托管。

---

## 选型框架

### 决策树

```
Need < 100K vectors?
+-- Yes -> pgvector (if already using PostgreSQL)
|          +-- Chroma (for prototyping)
|
+-- No -> Need managed service?
          +-- Yes -> Cloud-first?
          |          +-- Yes -> Pinecone (easiest)
          |          +-- No -> Qdrant Cloud or Zilliz
          |
          +-- No -> Need enterprise features?
                    +-- Yes -> Milvus on Kubernetes
                    +-- No -> Qdrant or Weaviate self-hosted
```

### 评估标准

| 标准 | 权重 | 要问的问题 |
|-----------|--------|------------------|
| 规模 | 高 | 现在有多少向量？一年后呢？ |
| 延迟 | 高 | p99 要求是什么？ |
| 运维能力 | 高 | 我们能运维它吗？ |
| 成本 | 中 | 预算约束是什么？ |
| 功能 | 中 | 混合搜索？多模态？ |
| 锁定风险 | 低～中 | 是否偏好开源？ |

### 概念验证清单

选择向量数据库前：

- [ ] 加载具有代表性的数据量
- [ ] 在目标 QPS 下压测查询延迟
- [ ] 测试元数据过滤性能
- [ ] 验证更新/删除性能
- [ ] 测试故障恢复
- [ ] 评估监控和可观测性
- [ ] 计算总拥有成本

---

## 面试问题

### Q：你会如何在 Pinecone 和自托管方案之间进行选择？

**参考答案：**
决策取决于多个因素：

**选择 Pinecone 的情况：**
- 团队没有运维有状态基础设施的能力
- 需要快速推进（几天而不是几周）
- 规模适中（少于 1 亿个向量）
- 预算允许支付托管服务溢价
- 合规允许依赖云供应商

**选择自托管（Qdrant、Milvus）的情况：**
- 拥有 Kubernetes 和运维能力
- 对规模化成本敏感
- 需要完全控制数据
- 有特定合规要求
- 希望避免供应商锁定

对于大多数初创公司，我会先使用 Pinecone 或 Qdrant Cloud 以换取交付速度，等规模化成本变得难以接受时再评估迁移。由于向量数据库 API 相似，切换成本适中。

### Q：解释 HNSW 的工作方式，以及什么时候不应使用它。

**参考答案：**
HNSW 构建向量的分层图：

**工作方式：**
1. 将向量作为节点插入多层图
2. 高层节点更少、跳跃距离更大
3. 搜索从顶层开始，贪心地移动到最近邻
4. 逐层下降，直到底层（包含所有向量）

**它的优点：**
- 查询复杂度 O(log n)
- 无需训练
- 支持实时更新
- 召回率与延迟权衡优秀

**不应使用的情况：**
- 数据集很小（少于 1 万）：暴力搜索就足够
- 内存极度受限：HNSW 的图会占用向量大小 1.5～2 倍的空间
- 需要精确搜索：HNSW 是近似算法
- 更新负载很重且延迟要求严格：更新可能造成临时退化

替代方案：内存受限时使用 IVF-PQ；十亿级且追求成本效率时使用 DiskANN；需要精确搜索时使用 Flat 索引；超高维稀疏向量使用 LSH。

### Q：什么时候应该使用 DiskANN 这类磁盘索引，而不是基于 RAM 的 HNSW？

**参考答案：**
当索引的内存成本超过预算或单台高内存节点的容量时，我会使用磁盘索引。例如，一个 1 亿向量、1536 维的 HNSW 索引几乎需要 1TB RAM。使用 DiskANN，可以把其中大部分存储放在 NVMe SSD 上，在保持查询时间低于 10ms 的同时，将 RAM 需求减少 90%～95%。对于非实时搜索应用，这会大幅降低 TCO（总拥有成本）。

### Q：为什么元数据过滤经常是向量数据库的瓶颈？

**参考答案：**
在朴素向量搜索中，我们先找到最近的 Top K 邻居，**然后**按元数据过滤（例如“只要 2024 年的文档”）。如果过滤条件非常严格，过滤后可能没有结果。现在的专用数据库使用 **HNSW 预过滤**，遍历图时只考虑满足布尔元数据约束的节点。这种做法计算成本较高，因为它破坏了 HNSW 的“短路”逻辑，需要专用位掩码或硬件加速（SIMD）来保持低延迟。

### Q：如何在向量数据库中处理多租户？

**参考答案：**
有三种主要方案：

**1. 元数据过滤（最常见）：**
```python
results = db.search(
    vector=query,
    filter={"tenant_id": current_tenant}
)
```
- 优点：简单、单索引
- 缺点：所有租户共享资源，存在因 Bug 暴露数据的风险

**2. 每个租户一个集合：**
```python
results = db.collection(f"tenant_{tenant_id}").search(vector=query)
```
- 优点：隔离性强，可按租户扩展
- 缺点：集合多，运维开销大

**3. 每个租户一个命名空间（Pinecone）：**
```python
results = index.query(vector=query, namespace=tenant_id)
```
- 优点：在单一索引内隔离
- 缺点：供应商特定

**我的选择：**
- 大多数情况使用元数据过滤（简单、成本有效）
- 高安全要求使用独立集合
- 绝不要后过滤（先全部检索再过滤），因为存在泄露风险

---

## 参考资料

- Malkov and Yashunin。《Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs》（HNSW，2018）
- Microsoft Research。《Vamana/DiskANN: A Disk-based Index for ANN Search》（2019/2023）
- Pinecone Documentation: https://docs.pinecone.io/
- Pinecone。《The Managed Architecture of Serverless Vector DBs》（2024）
- Qdrant Documentation: https://qdrant.tech/documentation/
- Weaviate Documentation: https://weaviate.io/developers/weaviate
- Milvus Documentation: https://milvus.io/docs
- pgvector: https://github.com/pgvector/pgvector

---

*上一篇：[Embedding 模型](03-embedding-models.md) | 下一篇：[混合搜索](05-hybrid-search.md)*
