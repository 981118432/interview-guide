# 上下文检索

上下文检索是一种在摄取阶段使用的技术，用于解决 RAG 失败的第一大原因：**脱离源文档后失去意义的分块**。它由 Anthropic 在 2024 年末率先推广，如今已经成为高精度检索的生产标准。Anthropic 自己的测量显示，单独使用混合搜索可以让检索失败减少 49%，与重排序结合时可减少 67%。

## 目录

- [问题：上下文稀释](#context-dilution)
- [上下文检索如何工作](#how-it-works)
- [上下文 Embedding](#contextual-embeddings)
- [上下文 BM25](#contextual-bm25)
- [完整流水线：混合搜索 + 重排序](#full-pipeline)
- [实现模式](#implementation)
- [成本考量](#cost)
- [上下文检索与其他方法](#comparison)
- [生产架构](#production)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## 问题：上下文稀释

当我们为 RAG 切分文档时，单个分块会丢失赋予它意义的周边上下文。

**上下文稀释示例：**

```
Original Document: "Acme Corp Q3 2025 Financial Report"
  Section 4: Product Pricing

  "The Standard plan costs $200/month. The Enterprise
   plan includes SSO and audit logs for $800/month."

-------- After Chunking --------

Chunk 17: "It costs $200/month."
Chunk 18: "The Enterprise plan includes SSO and audit
           logs for $800/month."
```

**分块 17 的问题**：搜索“Acme Standard 套餐多少钱？”的用户很可能会漏掉这个分块，因为它没有提到“Acme”“Standard”或“plan”。“It costs $200/month”的 Embedding 与查询在语义上相距很远。

**启示**：Anthropic 的研究显示，传统分块在 Top-20 检索块上造成 **5.7% 的检索失败率**。这意味着即使相关信息存在于知识库中，大约每 18 次查询仍有 1 次无法检索到它。

---

## 上下文检索如何工作

核心思想很简单：**在对分块做 Embedding 之前，前置一段简短上下文，说明它在完整文档中讲的是什么。**

```
┌──────────────────────────────────────────────────┐
│              TRADITIONAL CHUNKING                │
│                                                  │
│  Document ──► Split ──► Chunks ──► Embed ──► DB  │
│                                                  │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│              CONTEXTUAL RETRIEVAL                            │
│                                                              │
│  Document ──► Split ──► Chunks ──┐                           │
│                                  ├──► Contextualize ──►      │
│  Document (full) ───────────────┘    (LLM call per chunk)    │
│                                                              │
│  ──► Contextual Chunks ──► Embed ──► DB                      │
│                            + BM25 Index                      │
└──────────────────────────────────────────────────────────────┘
```

**上下文化步骤**会把完整文档和单个分块一起发送给 LLM，并使用如下 Prompt：

```
<document>
{{WHOLE_DOCUMENT}}
</document>

Here is the chunk we want to situate within the whole document:
<chunk>
{{CHUNK_CONTENT}}
</chunk>

Please give a short succinct context to situate this chunk
within the overall document for the purposes of improving
search retrieval of the chunk. Answer only with the succinct
context and nothing else.
```

**分块 17 的结果**：

```
Before: "It costs $200/month."

After:  "This chunk is from the Acme Corp Q3 2025 Financial
         Report, Section 4 on Product Pricing. It describes
         the cost of the Standard plan.
         It costs $200/month."
```

现在，这个分块的 Embedding 包含“Acme”“Standard plan”和“Product Pricing”，也就是用户自然会搜索的全部术语。

---

## 上下文 Embedding

上下文 Embedding 是第一项子技术：对上下文化后的分块做 Embedding，而不是对原始分块做 Embedding。

### 它如何改善检索

| 场景 | 原始分块 Embedding | 上下文 Embedding |
|------|-------------------|------------------|
| 用户询问“Acme 价格” | 漏掉“It costs $200” | 匹配“Acme...Standard plan...costs $200” |
| 用户询问“SSO 特性” | 匹配“SSO and audit logs” | 还会匹配新增的“Enterprise plan”上下文 |
| 用户询问“第三季度财务” | 不匹配（没有提到第三季度） | 通过前置的“Q3 2025 Financial Report”匹配 |

**性能**：单独使用上下文 Embedding，就能把 Top-20 检索失败率从 **5.7% 降至 3.7%**，即检索失败减少 **35%**。

### 向量空间偏移

```
                    ▲ Dimension 2
                    │
                    │    ● "Acme pricing" (query)
                    │         \
                    │          \  close (contextual)
                    │           \
                    │            ● Contextualized chunk
                    │
                    │                          ● Raw chunk "It costs $200"
                    │                            (far from query)
                    │
                    └─────────────────────────────► Dimension 1
```

---

## 上下文 BM25

第二项子技术是对同样上下文化的内容建立**BM25 关键词索引**。

### 为什么 BM25 仍然重要

稠密 Embedding 擅长语义相似度，但不擅长：
- **精确术语**：产品 ID、版本号、缩写。
- **稀有 Token**：Embedding 模型表示不足的领域术语。
- **专有名词**：公司、人名、地点。

**示例**：用户搜索“Widget-X 价格”时，原始分块“It costs $200/month”不会产生任何 BM25 匹配，因为其中没有出现“Widget-X”。上下文 BM25 会把“Widget-X”包含在前置上下文中，从而使 BM25 能够匹配。

### 性能收益（累积）

| 配置 | 失败率 | 相对基线的降低 |
|------|--------|----------------|
| 传统 Embedding（基线） | 5.7% | -- |
| 仅上下文 Embedding | 3.7% | 35% |
| 上下文 Embedding + 上下文 BM25 | 2.9% | **49%** |
| 上下文 Embedding + 上下文 BM25 + 重排序 | 1.9% | **67%** |

**结论**：上下文 Embedding + 上下文 BM25 的组合，是对 RAG 流水线能做的杠杆最大的单项改动。在其上添加重排序器，可以让失败减少 67%。

---

## 完整流水线：混合搜索 + 重排序

生产级上下文检索流水线有四个阶段：

```
┌─────────────────────────────────────────────────────────────────┐
│                     INGESTION PIPELINE                          │
│                                                                 │
│  1. Chunk documents (recursive, 300-500 tokens)                 │
│  2. For each chunk:                                             │
│     a. Send (full_doc + chunk) to LLM                           │
│     b. Get context string (50-100 tokens)                       │
│     c. Prepend context to chunk                                 │
│  3. Embed contextualized chunks ──► Vector DB                   │
│  4. Index contextualized chunks ──► BM25 Index                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     QUERY PIPELINE                              │
│                                                                 │
│  User Query                                                     │
│      │                                                          │
│      ├──► Vector Search (Top 50) ──┐                            │
│      │                             ├──► RRF Fusion (Top 25)     │
│      └──► BM25 Search (Top 50)  ──┘         │                   │
│                                             ▼                   │
│                                      Reranker (Top 5)           │
│                                             │                   │
│                                             ▼                   │
│                                     LLM Generation              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 用倒数排名融合（RRF）合并结果

这里使用与标准混合搜索相同的 RRF 技术：

```
RRF_Score(doc) = sum( 1 / (k + rank_in_list) )
                 for each list where doc appears

k = 60 (standard smoothing constant)
```

---

## 实现模式

### 模式 1：基础上下文检索（Python）

```python
import anthropic
from typing import List

client = anthropic.Anthropic()

CONTEXT_PROMPT = """<document>
{document}
</document>

Here is the chunk we want to situate within the whole document:
<chunk>
{chunk}
</chunk>

Please give a short succinct context to situate this chunk
within the overall document for the purposes of improving
search retrieval of the chunk. Answer only with the succinct
context and nothing else."""


def contextualize_chunk(
    full_document: str,
    chunk: str,
    model: str = "claude-sonnet-4-20250514"
) -> str:
    """Generate context for a single chunk."""
    response = client.messages.create(
        model=model,
        max_tokens=200,
        messages=[{
            "role": "user",
            "content": CONTEXT_PROMPT.format(
                document=full_document,
                chunk=chunk
            )
        }]
    )
    context = response.content[0].text
    return f"{context}\n\n{chunk}"


def process_document(document: str, chunks: List[str]) -> List[str]:
    """Contextualize all chunks in a document."""
    contextualized = []
    for chunk in chunks:
        ctx_chunk = contextualize_chunk(document, chunk)
        contextualized.append(ctx_chunk)
    return contextualized
```

### 模式 2：使用 Prompt Caching 优化成本

最大的成本驱动因素是每个分块都要发送完整文档。**Prompt Caching** 可以解决这个问题：

```python
def contextualize_with_caching(
    full_document: str,
    chunks: List[str],
    model: str = "claude-sonnet-4-20250514"
) -> List[str]:
    """
    Use prompt caching so the full document is only
    processed once across all chunks.
    """
    results = []

    for chunk in chunks:
        response = client.messages.create(
            model=model,
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"<document>\n{full_document}\n</document>",
                        "cache_control": {"type": "ephemeral"}
                    },
                    {
                        "type": "text",
                        "text": (
                            f"<chunk>\n{chunk}\n</chunk>\n\n"
                            "Please give a short succinct context to "
                            "situate this chunk within the overall "
                            "document for the purposes of improving "
                            "search retrieval of the chunk. Answer "
                            "only with the succinct context and "
                            "nothing else."
                        )
                    }
                ]
            }]
        )
        context = response.content[0].text
        results.append(f"{context}\n\n{chunk}")

    return results
```

**Prompt Caching 的成本影响**：对于一份 10,000 Token 的文档，分成 30 个块后，Prompt Caching 会在第一次调用后缓存文档前缀，因此最多可以把上下文化成本降低 **90%**。

### 模式 3：上下文分块标题（轻量替代方案）

如果基于 LLM 的上下文化成本过高，可以使用**上下文分块标题（CCH）**这一确定性替代方案：

```python
def add_chunk_headers(
    document_title: str,
    section_hierarchy: List[str],
    chunk: str
) -> str:
    """
    Prepend document and section metadata to the chunk.
    No LLM call required -- purely structural.
    """
    header_parts = [f"Document: {document_title}"]

    for i, section in enumerate(section_hierarchy):
        prefix = "  " * i
        header_parts.append(f"{prefix}Section: {section}")

    header = "\n".join(header_parts)
    return f"{header}\n\n{chunk}"


# Example usage:
contextualized = add_chunk_headers(
    document_title="Acme Corp Q3 2025 Financial Report",
    section_hierarchy=["Finance", "Product Pricing", "Standard Plan"],
    chunk="It costs $200/month."
)

# Result:
# Document: Acme Corp Q3 2025 Financial Report
#   Section: Finance
#     Section: Product Pricing
#       Section: Standard Plan
#
# It costs $200/month.
```

**什么时候使用 CCH，什么时候使用 LLM 上下文化：**

| 因素 | 分块标题（CCH） | LLM 上下文化 |
|------|-----------------|-------------|
| **成本** | 免费（不调用 LLM） | 每 1M Token $1～5 |
| **质量** | 适合结构化文档 | 适合所有文档，效果优秀 |
| **速度** | 即时 | 每块 50～200ms |
| **最适合** | Markdown、HTML、有清晰标题的 PDF | 非结构化文本、法律、医疗 |

---

## 成本考量

### 上下文化成本

以 10,000 个块（平均每块 400 Token）的知识库为例：

| 模型 | 每块成本 | 总成本 | 质量 |
|------|----------|--------|------|
| Claude Haiku（快、便宜） | 约 $0.0003 | 约 $3 | 良好 |
| Claude Sonnet（均衡） | 约 $0.002 | 约 $20 | 很好 |
| Claude Opus（最高质量） | 约 $0.01 | 约 $100 | 优秀 |

**最佳实践**：使用 Haiku（或其他快速、便宜模型）完成上下文化。上下文字符串短且是事实性的，因此不需要前沿模型。结合 Prompt Caching，可以让反复传入的文档正文成本降低约 90%。

### 什么时候使用上下文检索

**以下情况使用：**
- 语料库包含脱离文档后会失去意义的碎片化文档。
- 领域术语很多，Embedding 模型难以处理。
- 检索失败率超过 3～5%。
- 能够承担一次性的摄取成本。

**以下情况跳过：**
- 分块已经自包含（例如 FAQ 对、产品描述）。
- 语料库很小（< 100 个块），直接使用长上下文即可。
- 需要实时摄取（每个文档 < 1 秒），且无法批处理。

---

## 上下文检索与其他方法

| 方法 | 工作方式 | 检索提升 | 成本 | 复杂度 |
|------|----------|----------|------|--------|
| **朴素分块** | 固定大小切分，Embedding 原始内容 | 基线 | 无 | 低 |
| **分块标题（CCH）** | 前置文档/章节标题 | 10～20% | 无 | 低 |
| **上下文检索** | 每块由 LLM 生成上下文 | 35～49% | 每 10k 块 $3～20 | 中 |
| **上下文 + 重排序** | 上述方法 + Cross-Encoder 重排 | 67% | 每 10k 块 $5～30 | 中高 |
| **HyDE** | 查询时生成假设文档 | 20～40% | 每次查询的 LLM 成本 | 中 |
| **父子分块** | Embedding 子块，检索父块 | 15～30% | 无 | 中 |

**关键区别**：上下文检索是**摄取时**技术（付费一次），HyDE 是**查询时**技术（每次查询都付费）。对于高流量系统，上下文检索的摊销效果好得多。

### 上下文检索与晚分块

**晚分块**（Jina，2024）是相关但不同的方法：

```
Contextual Retrieval:
  Chunk ──► LLM adds context ──► Embed enriched chunk

Late Chunking:
  Full doc ──► Long-context embed model ──► Token embeddings
  ──► THEN chunk the token embeddings (preserving context)
```

晚分块需要长上下文 Embedding 模型（例如 Jina v3），并且完全避免 LLM 调用。它通过 Embedding 模型的注意力机制保留上下文，而不是显式前置文本。代价是晚分块无法帮助 BM25 搜索，只能改善稠密检索。

---

## 生产架构

### 参考架构：规模化上下文 RAG

```
┌─────────────────────────────────────────────────────────────────────┐
│                     INGESTION SERVICE                               │
│                                                                     │
│  Document Store ──► Chunker ──► Contextualization Queue             │
│                       │              │                              │
│                       │         ┌────┴────┐                         │
│                       │         │ Workers  │ (N parallel LLM calls) │
│                       │         │ + Cache  │                        │
│                       │         └────┬────┘                         │
│                       │              │                              │
│                       ▼              ▼                              │
│                  Raw Chunks    Contextualized Chunks                 │
│                       │              │                              │
│                       │         ┌────┴────┐                         │
│                       │         │ Embed + │                         │
│                       │         │ BM25    │                         │
│                       │         └────┬────┘                         │
│                       │              │                              │
│                       ▼              ▼                              │
│                  Metadata DB    Vector DB + BM25 Index               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                     QUERY SERVICE                                   │
│                                                                     │
│  Query ──► [Vector Search] + [BM25 Search]                          │
│                    │               │                                │
│                    └───── RRF ─────┘                                │
│                           │                                         │
│                      Top 25 chunks                                  │
│                           │                                         │
│                      Reranker (Cohere, Cross-Encoder)               │
│                           │                                         │
│                      Top 5 chunks                                   │
│                           │                                         │
│                      LLM Generation                                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 扩展考量

| 关注点 | 解决方案 |
|--------|----------|
| **摄取吞吐量** | 使用异步 Worker 并行调用 LLM（50～100 个并发） |
| **文档更新** | 只对变化的块重新上下文化；原始内容与上下文分开存储 |
| **规模化成本** | 使用 Haiku + Prompt Caching；按大小对文档批处理 |
| **质量监控** | 抽样 1% 的块，由人工评估上下文质量 |
| **索引一致性** | 对每个文档原子地更新向量库和 BM25 索引 |

---

## 面试问题

### Q：解释 Anthropic 的上下文检索。什么时候使用，什么时候跳过？

**强回答：**

上下文检索解决 RAG 的“上下文稀释”问题。文档被切分后，单个块会失去赋予它意义的周边上下文——一个说“它的成本是 200 美元”的块，如果不知道*什么*成本是 200 美元，就没有用。该技术在摄取时使用 LLM 为每个块生成 50～100 Token 的简短上下文，解释它在文档中讲的是什么，然后在 Embedding 和 BM25 索引前把上下文前置到块中。

关键结果是：上下文 Embedding 单独让检索失败减少 35%；加上上下文 BM25 后减少 49%；再加重排序器后减少 67%。

当块经常脱离上下文失去意义时，我会使用它，例如法律合同、财务报告、技术手册。如果块已经自包含（FAQ、产品卡片），或者语料库小到适合长上下文 RAG，我会跳过它。

### Q：一个包含 50,000 份文档的知识库需要上下文检索。如何管理摄取成本？

**强回答：**

有三个策略：
1. **模型选择**：使用小而快的模型（Claude Haiku 级别）完成上下文化。输出是简短的事实文本，而不是创意写作，前沿模型只会增加成本，却不增加质量。
2. **Prompt Caching**：在所有分块上下文化调用中缓存完整文档。对于一份 10,000 Token、包含 30 个块的文档，这能把输入 Token 成本降低约 90%。
3. **分层方案**：不是每份文档都需要 LLM 上下文化。对于结构良好的文档（Markdown、带标题的 HTML），使用确定性的上下文分块标题（前置文档标题和章节层级），它是免费的。把 LLM 上下文化留给非结构化或有歧义的文档。

### Q：上下文检索与 HyDE 在提升检索质量方面有什么区别？

**强回答：**

它们解决的是同一个问题的两侧。上下文检索在摄取时增强**文档**（付费一次），而 HyDE 在搜索时增强**查询**（每次查询付费）。对于每天处理 10,000 次查询、面对 50,000 个块的系统，上下文检索的成本会低得多，因为摄取成本可以摊销。HyDE 还有幻觉风险——假设文档可能把检索引向错误数据。实践中，最强的系统会同时使用两者：用上下文检索进行摄取增强，再用 HyDE（或多查询扩展）为需要查询侧帮助的复杂问题提供支持。

---

## 参考资料

- Anthropic，《Contextual Retrieval》（2024 年 9 月）
- Jina AI，《Late Chunking: Contextual Chunk Embeddings Using Long-Context Embedding Models》（2024）
- Voyage AI，《voyage-context-3: Contextualized Chunk Embeddings》（2025）
- NirDiamant，《RAG Techniques: Contextual Chunk Headers》（GitHub，2024）

---

*上一篇：[高级检索模式](09-advanced-retrieval-patterns.md) | 下一篇：[晚交互与 ColBERT](11-late-interaction-colbert.md)*
