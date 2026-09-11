# Embedding 与向量空间

Embedding 是捕获语义含义的文本稠密向量表示，是 RAG 系统、语义搜索和许多 AI 应用的基础。

## 目录

- [什么是 Embedding](#什么是-embedding)
- [Embedding 模型架构](#embedding-模型架构)
- [训练目标](#训练目标)
- [距离度量](#距离度量)
- [Embedding 模型对比](#embedding-模型对比)
- [Matryoshka 与自适应维度](#matryoshka-与自适应维度)
- [Late Interaction 与 Late Chunking](#late-chunking-与-interaction)
- [二值量化与标量量化](#用于规模化的量化)
- [实践注意事项（批处理、缓存）](#实践注意事项)
- [Embedding 漂移与版本管理](#embedding-漂移与版本管理)
- [面试问答](#面试问答)
- [参考资料](#参考资料)

---

## 什么是 Embedding

Embedding 把离散文本（词、句子、文档）映射到连续向量空间，使语义相似性对应于几何上的接近程度。

**关键特性：**
- 含义相近的内容彼此接近
- 关系可以编码为向量运算（king - man + woman = queen）
- 通过近似最近邻算法实现高效相似度搜索

**心智模型：**
把 Embedding 想象成高维空间中的坐标。维度（512 到 4096）提供了表达能力。每个维度都捕获含义的某个方面，但单个维度通常无法直接解释。

---

## Embedding 模型架构

### 词 Embedding（历史方案）

早期方法对单个词做 Embedding：

| 模型 | 年份 | 方法 | 局限 |
|-------|------|----------|------------|
| Word2Vec | 2013 | Skip-gram、CBOW | 静态：“bank”在所有上下文中相同 |
| GloVe | 2014 | 共现矩阵 | 静态 |
| FastText | 2017 | 子词 Embedding | 静态，但能处理 OOV |

**关键局限：**同一个词无论上下文如何都会得到相同的 Embedding。

### 上下文 Embedding

基于 Transformer 的模型会产生依赖上下文的 Embedding：

```python
# Static embedding (Word2Vec)
embed("bank") = [0.1, 0.3, ...]  # Same vector always

# Contextual embedding (BERT)
embed("river bank") = [0.1, 0.3, ...]   # Geography sense
embed("bank account") = [0.5, 0.2, ...]  # Finance sense
```

### 句子/文档 Embedding

对于检索，需要对完整文本做 Embedding：

| 方法 | 做法 | 优点 | 缺点 |
|----------|------|------|------|
| Mean pooling | 对 token Embedding 求平均 | 简单 | 丢失信息 |
| CLS token | 使用 [CLS] token 的 Embedding | BERT 的标准做法 | 可能无法捕获全文 |
| Last token | 使用最后一个 token | 适用于解码器模型 | 存在位置偏差 |
| Trained pooling | 学习池化权重 | 质量更好 | 需要训练 |

现代 Embedding 模型是专门为句子/文档 Embedding 训练的，而不是简单从语言模型改造而来。

### 双编码器架构

标准的检索 Embedding 架构：

```
Document -> Encoder -> Document Embedding
Query    -> Encoder -> Query Embedding

Similarity = cosine(doc_embedding, query_embedding)
```

**特性：**
- 文档可以预先计算并建立索引
- 查询 Embedding 在查询时计算
- 使用 ANN 时，每个文档只需 O(1) 的相似度计算

### 交叉编码器架构

一种把 Query 和文档放在一起处理的替代方案：

```
[Query, Document] -> Encoder -> Relevance Score
```

**特性：**
- 精度更高（同时看到二者）
- 不能预计算：n 个文档需要 O(n) 次推理
- 用于重排序，而不是第一阶段召回

---

## 训练目标

### 对比学习

大多数现代 Embedding 模型使用对比学习：

```python
# Simplified contrastive loss
def contrastive_loss(anchor, positive, negatives):
    pos_sim = cosine_similarity(anchor, positive)
    neg_sims = [cosine_similarity(anchor, neg) for neg in negatives]

    # Push positive close, negatives far
    loss = -log(exp(pos_sim / tau) /
                (exp(pos_sim / tau) + sum(exp(neg_sim / tau) for neg_sim in neg_sims)))
    return loss
```

**关键因素：**
- **正样本对**：语义相近的文本（平行句、Query-文档对）
- **困难负样本**：相似但不匹配的文本（BM25 召回但不相关的结果）
- **批内负样本**：把同一批中的其他样本作为负样本（高效）

### 训练数据来源

| 来源 | 正样本对 | 质量 | 规模 |
|-------|---------------|---------|-------|
| 平行句 | 翻译对 | 高 | 中 |
| Query-文档 | 搜索日志 | 高 | 中 |
| 标题-正文 | 文档结构 | 中 | 大 |
| 改写句 | NLI 数据集 | 高 | 小 |
| 生成数据 | LLM 创建样本对 | 不稳定 | 大 |

### 指令微调 Embedding

近期模型可以接受任务指令：

```python
# Instruction-tuned (e.g., E5, BGE)
query_embedding = embed("Represent this query for retrieval: What is RAG?")
doc_embedding = embed("Represent this document for retrieval: RAG combines...")
```

通过明确使用目的，这种方式可以提升性能。

---

## 距离度量

### 余弦相似度

文本 Embedding 最常用的度量：

```python
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
```

**特性：**
- 范围：[-1, 1]（归一化向量且相似度为正时为 [0, 1]）
- 衡量角度，而不是大小
- 对向量长度不敏感

**适用场景：**文本 Embedding 的默认选择。

### 点积

```python
def dot_product(a, b):
    return np.dot(a, b)
```

**特性：**
- 向量大小会产生影响
- 范围无界
- 对归一化向量而言等价于余弦相似度

**适用场景：**Embedding 已归一化，或向量大小本身有意义时。

### 欧氏距离

```python
def euclidean_distance(a, b):
    return np.linalg.norm(a - b)
```

**特性：**
- 衡量绝对差异
- 受向量大小影响
- 对归一化向量：sqrt(2 - 2 * cosine)

**适用场景：**文本中较少使用，图像 Embedding 更常见。

### 度量选择

| 度量 | 向量数据库 | 常见用途 |
|--------|------------------|------------|
| 余弦 | Pinecone、Qdrant、Weaviate | 文本 Embedding |
| 点积 | 所有主流数据库 | 归一化 Embedding |
| 欧氏距离 | 所有主流数据库 | 图像、多模态 |

---

## Embedding 模型对比

### 当前领先模型（2025 年 12 月）

| 模型 | 维度 | 最大 token 数 | MTEB 检索 | 每 1M token 成本 |
|------|------------|------------|----------------|------------------|
| OpenAI text-embedding-4 | 3072 | 16k | 68.2 | $0.10 |
| Voyage-4 | 1024 | 128k | 70.1 | $0.05 |
| Cohere embed-v3.5 | 1024 | 512 | 67.5 | $0.10 |
| Google text-embedding-005 | 768 | 8k | 67.2 | $0.02 |

*MTEB 分数是近似值，会因基准子集而变化。务必核对当前值。当前英文榜单由 Gemini Embedding 001（68.32）领先，多语言榜单由 Qwen3-Embedding-8B（70.58）和 Llama-Embed-Nemotron-8B 领先。*

### 开源模型

| 模型 | 维度 | 最大 token 数 | MTEB 检索 | 说明 |
|-------|------------|------------|----------------|-------|
| BGE-large-en-v1.5 | 1024 | 512 | 63.9 | 强大的开源模型 |
| E5-large-v2 | 1024 | 512 | 62.4 | 指令微调 |
| GTE-large | 1024 | 512 | 63.1 | 阿里巴巴 |
| Nomic-embed-text-v1.5 | 768 | 8192 | 62.3 | 长上下文、开源 |

### 选择标准

| 因素 | 考虑事项 |
|--------|----------------|
| 质量（MTEB） | 越高越好，但任务专用评估更重要 |
| 维度 | 越高表达能力越强，但存储/计算更多 |
| 最大 token 数 | 必须容纳你的文档大小 |
| 成本 | API 与自托管的权衡 |
| 延迟 | Embedding 生成时间 |
| 多语言 | 如果服务非英语内容，需要重点考虑 |

---

## Matryoshka 与自适应维度

### 思想

Matryoshka 表征学习（MRL）训练 Embedding，使完整向量的前缀同样有意义：

```python
full_embedding = model.encode(text)  # 1024 dimensions

# All these are valid embeddings with decreasing quality
dim_512 = full_embedding[:512]
dim_256 = full_embedding[:256]
dim_128 = full_embedding[:128]
dim_64 = full_embedding[:64]
```

### 为什么重要

| 使用场景 | 维度 | 权衡 |
|----------|-----------|----------|
| 完整检索 | 1024–3072 | 峰值精度 |
| **两阶段检索**| 128 → 1024 | **生产标准**：用 128 维召回 1000 个，再用 1024 维细化前 100 个。 |
| 成本敏感 | 256 | 节省 12 倍存储，MRR 损失小于 2% |
| 边缘设备/移动端 | 64 | 速度最快，适合简单意图 |

### 支持 Matryoshka 的模型

- OpenAI text-embedding-3-*（原生支持）
- Nomic-embed-text-v1.5
- 若干微调模型

### 使用 Matryoshka Embedding

```python
from openai import OpenAI
client = OpenAI()

# Request smaller dimensions
response = client.embeddings.create(
    model="text-embedding-3-large",
    input="Your text here",
    dimensions=256  # Request 256 instead of full 3072
)
```

---

### Late Chunking（2025 年的转变）

**传统分块：**
`Document -> Split into chunks -> Embed chunks individually`
- **问题**：分块 2 会丢失分块 1 的上下文。

**Late Chunking（Jina AI/Voyage 引入）：**
`Full Document -> Model Encoder -> Token-level Embeddings -> Pool into chunk boundaries`
- **收益**：每个分块的 Embedding 都包含**整篇文档**的信息，因为 Transformer 的自注意力在池化之前已经作用于完整序列。
- **要求**：模型支持长上下文（至少 8K+ token）。

---

## 用于规模化的量化

为了处理数十亿个向量，**二值量化**和**标量（Int8）量化**已经成为标准方案。

| 类型 | 数据大小 | 节省内存 | 质量损失 | 支持者 |
|------|-----------|--------------|----------------|--------------|
| Float32 | 4 字节/维 | 基准 | 0% | 全部 |
| Int8 | 1 字节/维 | 4 倍 | <1% | Cohere、BGE |
| **Binary** | **1 位/维** | **32 倍** | 约 5–10% | Cohere v3、v4 |

**二值量化模式：**
1. 使用二值 Embedding 高速召回前 1000 个结果。
2. 使用 Float32 或 Cross-Encoder 对前 50 个结果重排序，以获得高精度。

### 什么时候使用 ColBERT

- 检索精度至关重要
- 可以承受存储开销
- 查询延迟预算 > 50ms

### 实现

```python
# Using RAGatouille
from ragatouille import RAGPretrainedModel

model = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")

# Index documents
model.index(
    collection=documents,
    index_name="my_index"
)

# Search
results = model.search(query="What is RAG?", k=10)
```

---

## 实践注意事项

### 批处理

```python
# Inefficient: one API call per document
embeddings = [embed(doc) for doc in documents]

# Efficient: batch API calls
batch_size = 100
embeddings = []
for i in range(0, len(documents), batch_size):
    batch = documents[i:i + batch_size]
    batch_embeddings = embed_batch(batch)
    embeddings.extend(batch_embeddings)
```

### Embedding 分块

长文档在做 Embedding 前必须分块：

```python
def embed_document(document: str, max_tokens: int = 512) -> list[np.array]:
    chunks = chunk_document(document, max_tokens=max_tokens)
    embeddings = []
    for chunk in chunks:
        embedding = embed(chunk)
        embeddings.append(embedding)
    return embeddings
```

**注意事项：**
- 分块大小应小于模型最大 token 数
- 重叠有助于保留分块边界两侧的上下文
- 保存分块到文档的映射，便于检索

### 归一化

许多系统要求使用归一化 Embedding：

```python
def normalize(embedding):
    norm = np.linalg.norm(embedding)
    return embedding / norm

# Cosine similarity of normalized vectors = dot product
similarity = np.dot(normalize(a), normalize(b))
```

大多数向量数据库和 Embedding API 会处理归一化，但仍需确认。

### 缓存

Embedding 计算成本高，应积极使用缓存：

```python
import hashlib

def get_embedding(text: str, cache: dict) -> np.array:
    key = hashlib.sha256(text.encode()).hexdigest()

    if key in cache:
        return cache[key]

    embedding = compute_embedding(text)
    cache[key] = embedding
    return embedding
```

---

## Embedding 漂移与版本管理

### 问题

以下 Embedding 之间不可直接比较：
- 不同模型产生的 Embedding
- 同一模型不同版本产生的 Embedding
- 有时，同一 API 的不同调用也不可直接比较（部分 API 存在非确定性）

### 后果

如果更新 Embedding 模型：
- 所有已有 Embedding 都会变得不兼容
- 必须对整个语料重新做 Embedding
- 迁移期间搜索结果会不一致

### 缓解策略

**1. 为 Embedding 做版本管理：**
```python
embedding_metadata = {
    "model": "text-embedding-3-large",
    "model_version": "2024-01",
    "dimensions": 3072,
    "created_at": "2025-12-16"
}
```

**2. 规划重新 Embedding：**
- 估算完整重建的成本和时间
- 构建可在后台运行的流水线
- 切换前测试新 Embedding

**3. 蓝绿部署：**
```
Index A: Current embeddings
Index B: New embeddings (building)

Query -> Both indexes -> Merge or switch
```

**4. 跟踪 Embedding 质量：**
- 持续监控检索指标
- 检测 Embedding 分布漂移
- 质量下降时告警

---

## 面试问答

### 问：Embedding 模型如何学习语义相似度？

**强回答：**
Embedding 模型通过对比学习训练。目标是让语义相近文本的 Embedding 彼此接近，让不相似文本彼此远离。

训练过程：
1. 正样本对：应该相似的文本（Query-文档对、改写句、翻译句）
2. 负样本对：应该不相似的文本（通常来自同一批次，或 BM25 召回的困难负样本）
3. 损失函数：拉近正样本，推远负样本

模型学会把文本放置在高维空间中，使距离与语义相似度相关。这样就能实现检索：对 Query 做 Embedding，再在文档 Embedding 空间中查找最近邻。

E5、BGE 等现代模型还进行了指令微调，即添加任务指令前缀，让 Embedding 专门适配特定用途。

### 问：什么时候应该使用 ColBERT，而不是双编码器？

**强回答：**
ColBERT 使用 Late Interaction：不是每个文档只保留一个 Embedding，而是保留每个 token 的 Embedding。在查询时计算 token 级别的相似度。

以下情况选择 ColBERT：
- 检索精度至关重要（法律、医疗、高风险场景）
- 可以承受每个文档 10–100 倍的存储开销
- 查询延迟预算为 50ms 以上（略慢于双编码器）
- 查询受益于词法匹配（技术术语）

以下情况选择双编码器：
- 存储受限
- 需要低于 20ms 的延迟
- 双编码器的检索精度已经足够
- 需要频繁重建索引（ColBERT 重建索引成本高）

实际中常见的模式是：双编码器完成第一阶段召回（前 100 个），再使用 Cross-Encoder 或 ColBERT 重排序。

### 问：更新模型时如何处理 Embedding 漂移？

**强回答：**
Embedding 模型生成的向量只有在相同模型下才有意义。更新模型后，所有旧 Embedding 都会不兼容。

我的做法是：
1. **永不原地更新。** 创建包含新 Embedding 的并行索引。
2. **切换前测试。** 使用测试集比较新旧 Embedding 的检索质量。
3. **后台重建。** 在后台使用新模型为整个语料重新做 Embedding。
4. **原子切换。** 新索引完成并通过验证后，以原子方式切换流量。
5. **准备回滚。** 保留旧索引，以便快速回滚。

成本估算示例：如果有 1000 万个文档，平均每个文档 500 个 token，text-embedding-3-large 的价格是每 1M token $0.13，那么重新 Embedding 的成本约为 $650。考虑更新模型时应把这项成本纳入计划。

### 问：如何选择 Embedding 的维度？

**强回答：**
更高维度能捕获更多信息，但需要更多存储和计算。

考虑因素：
- **存储**：1024 维 Float32 的一个 Embedding 是 4 KB。1000 万个文档仅 Embedding 就需要 40 GB。
- **搜索速度**：维度越高，近邻搜索越慢。
- **质量**：对大多数任务来说，超过某个维度后收益递减。

实际做法：
1. 从模型推荐的维度开始。
2. 如果使用 Matryoshka 模型（如 text-embedding-3），在自己的任务上试验更低维度。
3. 比较不同维度下的质量：256–512 维通常可以达到完整质量的 95%。
4. 对两阶段检索：第一阶段使用低维度，重排序使用完整维度。

大多数应用使用 768–1024 维可以取得良好平衡。例外是极高精度要求的场景，此时 2048–4096 维可能有帮助。

---

## 参考资料

- Reimers、Gurevych：《Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks》（2019）
- Khattab、Zaharia：《ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction over BERT》（2020）
- Wang 等：《Text Embeddings by Weakly-Supervised Contrastive Pre-training》（E5，2022）
- Xiao 等：《C-Pack: Packaged Resources To Advance General Chinese Embedding》（BGE，2023）
- Kusupati 等：《Matryoshka Representation Learning》（MRL，2022）
- MTEB Leaderboard：https://huggingface.co/spaces/mteb/leaderboard
- OpenAI Embeddings Guide：https://platform.openai.com/docs/guides/embeddings

---

*上一篇：[Transformer 架构](04-transformer-architecture.md) | 下一篇：[推理流水线](06-inference-pipeline.md)*
