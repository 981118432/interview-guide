# RAG 评估模式

评估是 RAG 中最难解决的问题。一天就能搭建检索流程，但要知道它是否真的有效，往往需要数周。业界已经形成分层评估策略：用 RAG 三元组检查正确性，用组件级指标调试，再用自动化回归测试保障生产安全。Langfuse、LangWatch、Braintrust 和 Arize Phoenix 都提供原生的 RAG 评估方案；选择时应根据部署模式（自托管还是 SaaS），以及是否需要由评估结果控制 CI/CD 阻断来决定。

## 目录

- [RAG 三元组](#the-rag-triad)
- [RAGAS 框架与指标](#ragas-framework)
- [组件级评估](#component-level-evaluation)
- [用于 RAG 的 LLM-as-Judge](#llm-as-judge)
- [构建黄金测试集](#golden-test-sets)
- [自动化回归测试](#regression-testing)
- [生产监控](#production-monitoring)
- [大规模评估成本](#cost-at-scale)
- [工具对比](#tools-comparison)
- [系统设计面试角度](#system-design-interview-angle)
- [参考资料](#references)

---

## RAG 三元组

RAG 三元组是评估 RAG 系统的基础框架。它把正确性拆成三个相互独立的维度，每个维度都能捕获不同的失败模式。

```
                          User Query
                              |
                              v
                    +-------------------+
                    |    RETRIEVER      |
                    +-------------------+
                              |
                   (1) Context Relevance
                    "Did we retrieve the
                     right documents?"
                              |
                              v
                    +-------------------+
                    |    GENERATOR      |
                    +-------------------+
                         /         \
            (2) Groundedness      (3) Answer Relevance
            "Is the answer         "Does the answer
             supported by           address the actual
             the context?"          question?"
                  |                       |
                  v                       v
             No hallucination       No tangential answers
```

### 维度 1：上下文相关性

**问题**：每个检索到的文本块是否真的与用户查询相关？

**它能发现什么**：糟糕的检索——向量搜索返回了错误主题的文档，或者查询有歧义，检索器做出了错误判断。

**如何衡量**：
- 对每个检索到的文本块提问：“这个文本块与回答查询相关吗？”
- 分数 = 相关文本块数 / 检索到的文本块总数
- 0.3 的分数意味着 70% 的上下文是噪声，迫使 LLM 在无关信息中寻找答案。

**为什么重要**：上下文相关性低是大多数 RAG 失败的根源。即使生成器完美无缺，也无法从不相关的上下文中生成好答案。

### 维度 2：有依据性（忠实度）

**问题**：生成答案中的每个主张是否都由检索到的上下文支持？

**它能发现什么**：幻觉——LLM 生成了听起来合理、但检索文档中并不存在的主张。

**如何衡量**：
- 将答案拆分成独立的主张/陈述。
- 对每个主张，在检索到的上下文中搜索支持证据。
- 分数 = 有支持的主张数 / 主张总数
- 0.7 的分数意味着答案中有 30% 是幻觉。

**为什么重要**：这是企业客户最重视的指标。缺乏忠实度的 RAG 系统比没有 RAG 更糟，因为它会带着伪造的引用生成听起来很自信的错误答案。

### 维度 3：答案相关性

**问题**：最终答案是否真正回答了用户的问题？

**它能发现什么**：答非所问——检索是好的，答案也有上下文依据，但没有回答问题。检索器找到相关但不匹配的内容时很常见。

**如何衡量**：
- 生成 N 个假设问题，答案应当是这些问题的良好回答。
- 衡量这些假设问题与原始查询之间的语义相似度。
- 相似度高意味着答案切中了主题。

**为什么重要**：系统可能检索了相关上下文，并忠实地总结了它，但仍然没有抓住问题重点。答案相关性可以发现这一点。

### 三元组失败模式

| 失败模式 | 上下文相关性 | 有依据性 | 答案相关性 | 根因 |
|----------------|-------------------|-------------|-----------------|------------|
| 良好的 RAG | 高 | 高 | 高 | 系统正常工作 |
| 检索失败 | **低** | 高 | 低 | Embedding 或搜索配置错误 |
| 幻觉 | 高 | **低** | 高 | LLM 忽略上下文，Prompt 有问题 |
| 答非所问 | 高 | 高 | **低** | 查询有歧义，索引错误 |
| 完全失败 | **低** | **低** | **低** | 流水线存在根本性问题 |

---

## RAGAS 框架与指标

RAGAS（Retrieval Augmented Generation Assessment，检索增强生成评估）是使用最广泛的开源 RAG 评估框架，提供不需要标准答案的免参考指标。

### RAGAS 核心指标

```
  RAGAS Metric Suite (v0.2+)
  |
  +-- Retrieval Metrics
  |     +-- Context Precision: Are relevant docs ranked higher?
  |     +-- Context Recall: Did we find all relevant docs?
  |     +-- Context Entities Recall: Did we capture key entities?
  |     +-- Context Relevance: Is retrieved context pertinent?
  |
  +-- Generation Metrics
  |     +-- Faithfulness: Are claims supported by context?
  |     +-- Answer Relevance: Does the answer address the query?
  |     +-- Answer Correctness: Does the answer match ground truth?
  |     +-- Answer Similarity: Semantic overlap with reference answer
  |
  +-- Noise & Robustness
  |     +-- Noise Sensitivity: How much does irrelevant context hurt?
  |
  +-- Multi-Modal (2025+)
        +-- Multimodal Faithfulness: Claims supported by images + text?
        +-- Multimodal Relevance: Are retrieved images relevant?
```

### RAGAS 忠实度如何工作（底层原理）

```
Step 1: Claim Extraction
  Answer: "Revenue grew 15% in Q3, driven by APAC expansion
           and the new enterprise tier launched in July."

  Claims:
    c1: "Revenue grew 15% in Q3"
    c2: "Growth was driven by APAC expansion"
    c3: "Growth was driven by the new enterprise tier"
    c4: "The enterprise tier was launched in July"

Step 2: Evidence Matching (per claim)
  c1: Found in Context chunk 3 --> SUPPORTED
  c2: Found in Context chunk 1 --> SUPPORTED
  c3: Not found in any context --> UNSUPPORTED
  c4: Context says "August" not "July" --> CONTRADICTED

Step 3: Score Calculation
  Faithfulness = supported / total = 2/4 = 0.50
```

### RAGAS 上下文精确率如何工作

```
  Retrieved chunks ranked by retriever score:
    Rank 1: Chunk about Q3 revenue    --> Relevant (v_1 = 1)
    Rank 2: Chunk about company history --> Not relevant (v_2 = 0)
    Rank 3: Chunk about Q3 expenses   --> Relevant (v_3 = 1)
    Rank 4: Chunk about office locations --> Not relevant (v_4 = 0)

  Context Precision@K:
    Precision@1 = 1/1 = 1.0
    Precision@2 = 1/2 = 0.5
    Precision@3 = 2/3 = 0.67
    Precision@4 = 2/4 = 0.5

  Average Precision = (1.0*1 + 0.5*0 + 0.67*1 + 0.5*0) / 2
                    = (1.0 + 0.67) / 2 = 0.835
```

### RAGAS 与标准答案指标

| 指标 | 需要标准答案？ | 衡量内容 |
|--------|-------------------|------------------|
| 忠实度 | 否 | 上下文支持的主张 |
| 上下文相关性 | 否 | 检索文本块的相关性 |
| 答案相关性 | 否 | 答案是否回答查询 |
| 上下文召回率 | **是** | 对参考答案的覆盖程度 |
| 答案正确性 | **是** | 与参考答案的匹配程度 |
| 答案相似度 | **是** | 与参考答案的语义重合度 |

**洞察**：快速迭代时先使用免参考指标（忠实度、上下文相关性、答案相关性）。建立黄金测试集后，再加入标准答案指标进行回归测试。

---

## 组件级评估

RAG 三元组评估端到端系统，而组件级评估则隔离每个阶段，从而定位失败原因。

### 检索器评估

```
  Query Set (100+ queries with known relevant documents)
        |
        v
  Run Retriever --> Retrieved docs per query
        |
        v
  Compare against ground truth relevance labels
        |
        v
  Metrics:
    +-- Recall@K: What fraction of relevant docs are in the top K?
    +-- MRR (Mean Reciprocal Rank): How high is the first relevant doc?
    +-- NDCG@K: Quality-weighted ranking metric
    +-- Precision@K: What fraction of top K are relevant?
```

**检索器关键基准**：

| 指标 | 最低阈值 | 良好 | 优秀 |
|--------|------------------|------|-----------|
| Recall@10 | 0.70 | 0.85 | 0.95+ |
| MRR | 0.50 | 0.70 | 0.85+ |
| NDCG@10 | 0.50 | 0.70 | 0.85+ |
| Precision@5 | 0.40 | 0.60 | 0.80+ |

### 生成器评估

固定检索上下文，只改变生成过程，以此隔离生成器。

```
  Fixed Context (known relevant chunks)
  + Query
        |
        v
  Run Generator --> Answer
        |
        v
  Metrics:
    +-- Faithfulness (RAGAS): Does it stay grounded?
    +-- Completeness: Does it cover all relevant info in context?
    +-- Conciseness: Is it appropriately brief?
    +-- Format Compliance: Does it follow the expected output format?
    +-- Citation Accuracy: Do citations point to the right chunks?
```

### 重排序器评估

```
  Query + Initial retrieval results (e.g., top 100 from BM25)
        |
        v
  Run Reranker --> Reranked results
        |
        v
  Metrics:
    +-- NDCG improvement: Did reranking move relevant docs up?
    +-- Recall preservation: Did reranking lose any relevant docs?
    +-- Latency: What did reranking add to query time?
```

---

## 用于 RAG 的 LLM-as-Judge

用一个 LLM 评估另一个 LLM 的输出，是当前主流的评估范式。它能够扩展到人工评估无法覆盖的规模，但也存在已知偏差。

### 工作方式

```
  Evaluation Prompt Template:
  +------------------------------------------------------------------+
  | You are evaluating a RAG system. Given:                           |
  | - User Query: {query}                                             |
  | - Retrieved Context: {context}                                    |
  | - Generated Answer: {answer}                                      |
  |                                                                    |
  | Rate the following on a scale of 1-5:                             |
  | 1. Faithfulness: Are all claims in the answer supported by        |
  |    the context? (1=hallucinated, 5=fully grounded)                |
  | 2. Relevance: Does the answer address the user's question?        |
  |    (1=off-topic, 5=directly answers)                              |
  | 3. Completeness: Does the answer cover all relevant info?         |
  |    (1=missing key info, 5=comprehensive)                          |
  |                                                                    |
  | Provide scores and brief justifications in JSON.                  |
  +------------------------------------------------------------------+
```

### 已知偏差与缓解方式

| 偏差 | 描述 | 缓解方式 |
|------|-------------|------------|
| **冗长偏差** | LLM 评判者偏爱更长的答案 | 按答案长度归一化分数；增加简洁性惩罚 |
| **自我偏好** | GPT-4 给 GPT-4 答案的评分更高 | 使用不同于生成器的评判模型 |
| **位置偏差** | A/B 对比中的第一个选项更容易获得高分 | 随机化展示顺序 |
| **谄媚** | 评判者同意被评估的系统 | 使用包含具体标准的结构化评分规则 |
| **宽松** | LLM 很少给出低于 3/5 的分数 | 使用二值（通过/失败）而不是 Likert 量表 |

### LLM-as-Judge 最佳实践

1. **使用二值决策而不是量表**：“这个主张有上下文支持吗？是/否”比“按 1～5 评估支持度”更可靠。
2. **拆成原子评估**：一次只评估一个主张或一个维度。
3. **要求证据**：强制评判者引用支持或反驳每个主张的具体上下文段落。
4. **用人工一致性校准**：让 LLM 和人工评判者分别评估 100 个以上示例，计算 Cohen's Kappa，目标值大于 0.7。
5. **使用当前最强模型**：使用 Claude Opus 或 GPT-4o 作为评判者；绝不要使用生成答案的同一个模型。

---

## 构建黄金测试集

黄金测试集是经过筛选并版本化的（查询、预期上下文、预期答案）三元组集合，作为回归测试的真实基准。

### 构建流程

```
  Step 1: Seed Collection
  +-------------------------------------------------------+
  | Source production queries (logs, support tickets)       |
  | Target: 200-500 diverse queries                        |
  | Coverage: all topics, question types, difficulty levels |
  +-------------------------------------------------------+
            |
            v
  Step 2: Synthetic Augmentation
  +-------------------------------------------------------+
  | Use RAGAS or DataMorgana to generate additional queries |
  | from your corpus:                                       |
  |   - Simple factual questions (40%)                     |
  |   - Multi-hop reasoning questions (25%)                |
  |   - Conditional/comparative questions (20%)            |
  |   - Adversarial/edge cases (15%)                       |
  +-------------------------------------------------------+
            |
            v
  Step 3: Human Annotation
  +-------------------------------------------------------+
  | For each query, annotate:                               |
  |   - Expected relevant document IDs (for retrieval eval) |
  |   - Reference answer (for generation eval)              |
  |   - Difficulty label (easy / medium / hard)             |
  |   - Category tags (topic, question type)                |
  +-------------------------------------------------------+
            |
            v
  Step 4: Versioning and Freezing
  +-------------------------------------------------------+
  | Store in version control (golden_set_v3.json)           |
  | FREEZE the set for each evaluation cycle                |
  | Never modify a frozen set -- create a new version       |
  +-------------------------------------------------------+
```

### 黄金集组成指南

| 问题类型 | 占比 | 目的 |
|--------------|-----------|---------|
| 简单事实型 | 40% | 基线：应始终通过 |
| 多跳推理 | 25% | 测试跨文档检索 |
| 比较型 | 15% | 测试多个相关文档的检索 |
| 时间型 | 10% | 测试版本化/有日期内容的处理 |
| 对抗型 | 10% | 测试稳健性（无法回答、超出范围） |

### 使用 RAGAS 生成合成测试

```python
# Pseudocode: Generate synthetic test queries from your corpus
from ragas.testset.generator import TestsetGenerator
from ragas.testset.evolutions import simple, reasoning, multi_context

generator = TestsetGenerator.from_langchain(
    generator_llm=ChatOpenAI(model="gpt-4o"),
    critic_llm=ChatOpenAI(model="gpt-4o"),
)
testset = generator.generate_with_langchain_docs(
    documents=load_documents("./knowledge_base/"),
    test_size=200,
    distributions={simple: 0.4, reasoning: 0.35, multi_context: 0.25}
)
# CRITICAL: Always human-review synthetic data before using as ground truth
testset.to_pandas().to_csv("golden_set_draft_v4.csv")
```

**警告**：合成测试集是起点，不是终点。在将其作为真实基准之前，务必经过人工审核，避免测试到生成模型自身产生的伪影。

---

## 自动化回归测试

RAG 流程的每次变更（新的 Embedding、分块大小、Prompt 修改、重排序器更换）都需要在部署前进行自动化回归测试。

### CI/CD 集成

```
  PR (RAG change) --> CI: Load golden set --> Run pipeline --> Compute metrics
                          --> Compare vs. baseline --> FAIL if drop > 5%, WARN if > 2%
                          --> Post metrics table as PR comment
```

### 质量门禁

| 指标 | 绝对最低值 | 回归阈值 |
|-----------------|-----------------|---------------------|
| Recall@10 | 0.85 | 相对基线下降 5% |
| MRR | 0.70 | 下降 5% |
| 忠实度 | 0.80 | 下降 3% |
| 答案相关性 | 0.75 | 下降 5% |
| 答案正确性 | 0.70 | 下降 5% |

任何低于绝对最低值的指标都会阻断 PR。任何超过阈值的回归都会触发警告，并标记质量下降的具体查询。

---

## 生产监控

离线评估是必要条件，但还不够。生产查询与测试集不同，随着语料库变化，检索质量可能随时间下降。

### 生产关键信号

| 信号 | 检测内容 | 衡量方式 |
|------|----------------|----------------|
| **空检索率** | 没有相关结果的查询 | Top-1 相似度低于阈值的查询占比 |
| **相似度分数漂移** | Embedding 或语料库退化 | 随时间跟踪平均相似度，下降时告警 |
| **忠实度抽样** | 生产环境的幻觉率 | 对 5%～10% 的随机样本运行 LLM-as-Judge |
| **用户反馈相关性** | 指标是否反映真实质量 | 对比好评/差评与自动化分数 |
| **延迟 P99** | 性能退化 | 跟踪检索 + 生成延迟 |
| **Token 使用量** | 成本漂移 | 监控每次查询的平均上下文 Token 数 |

### 检索质量漂移

当语料库发生变化，但 Embedding、分块或 Prompt 没有同步更新时，就会产生漂移。常见有四种场景：(1) 新文档使用了不同词汇，导致 Embedding 空间不匹配——为受影响的集合重新生成 Embedding；(2) 用户查询转向没有内容覆盖的主题——通过空检索率监控发现；(3) 过时内容返回旧答案——加入新鲜度元数据并优先选择近期文档；(4) Embedding 模型更新改变了相似度分布——模型变化后重新校准所有阈值。

---

## 大规模评估成本

LLM-as-Judge 评估能力强，但成本高。理解成本结构对预算至关重要。

### 单次查询成本（完整 RAG 三元组）

| 指标 | LLM 调用次数 | Token 数 | GPT-4o 成本 | Claude Haiku 成本 |
|--------|-----------|--------|-------------|-------------------|
| 忠实度 | 约 3（提取 + 验证） | 约 3k | $0.0075 | $0.00075 |
| 上下文相关性 | 约 5（每个文本块） | 约 2.5k | $0.00625 | $0.000625 |
| 答案相关性 | 约 2（问题生成） | 约 1.6k | $0.004 | $0.0004 |
| **完整三元组** | **约 10** | **约 7k** | **约 $0.018** | **约 $0.002** |

### 扩展策略

| 评估类型 | 频率 | 规模 | 评判模型 | 每月成本（每天 1 万次查询） |
|----------------|-----------|--------|-------------|-------------------------------|
| **CI 回归** | 每次 PR | 黄金集（500 个查询） | GPT-4o | 约 $9/次 |
| **每夜批处理** | 每天 | 随机 1000 个生产查询 | Claude Haiku | 约 $60/月 |
| **生产抽样** | 实时 | 流量的 5% | Claude Haiku | 约 $300/月 |
| **深度审计** | 每周 | 完整黄金集 + 分析 | GPT-4o | 约 $36/月 |

**洞察**：高流量生产抽样使用 Claude Haiku 4.5 或 GPT-5.5-mini。将 Claude Opus 4.7 或 GPT-5.5 留给 CI 回归测试和深度审计，因为这些场景的准确率比成本更重要。

---

## 工具对比

### 框架概览

| 工具 | 最适合 | 开源 | 关键优势 | 关键弱点 |
|------|----------|------------|--------------|--------------|
| **RAGAS** | 快速 RAG 评估、合成数据 | 是 | 免参考指标，社区活跃 | 指标结果缺少解释 |
| **DeepEval** | CI/CD 集成、LLM 的 TDD | 是 | 兼容 pytest，可自解释评分 | 配置更重 |
| **TruLens** | RAG 三元组评估、可观测性 | 是 | 提出 RAG 三元组，追踪能力好 | 开发活跃度较低 |
| **UpTrain** | 生产监控、漂移检测 | 是 | 混合评估（LLM + 启发式）、漂移告警 | 排序准确率较低 |
| **Braintrust** | 团队协作、实验跟踪 | 商业 | UI/UX 最好，实验对比出色 | 高级功能付费 |
| **LangSmith** | LangChain 生态、追踪 | 商业 | 深度集成 LangChain，追踪能力强 | 受限于 LangChain 生态 |

### 如何选择

```
  Starting a new RAG project?
    --> RAGAS for quick baseline metrics + synthetic test generation

  Adding RAG eval to CI/CD?
    --> DeepEval (pytest integration, quality gates as assertions)

  Need production monitoring?
    --> UpTrain or Braintrust (drift detection, alerting)

  Want end-to-end observability?
    --> LangSmith (if LangChain) or Braintrust (if framework-agnostic)

  Building custom eval pipeline?
    --> Roll your own with LLM-as-judge + the RAG Triad structure
```

### 自定义评估器模式

自定义评估器的核心模式很简单：针对三元组的每个维度使用二值 LLM-as-Judge 调用，然后聚合结果。

```python
# Pseudocode: Core faithfulness evaluator (other dimensions follow the same pattern)

def evaluate_faithfulness(answer: str, context: str, judge) -> float:
    # Step 1: Extract atomic claims from the answer
    claims = judge.generate(f"List every factual claim as a JSON array:\n{answer}")

    # Step 2: Verify each claim against context (binary YES/NO)
    supported = sum(
        1 for claim in json.loads(claims)
        if "YES" in judge.generate(
            f"Is this claim supported by the context? YES or NO.\n"
            f"Claim: {claim}\nContext: {context}"
        ).upper()
    )
    return supported / max(len(json.loads(claims)), 1)
```

对上下文相关性（逐块询问“它与查询相关吗？”）和答案相关性（生成假设问题并衡量其与原查询的相似度），使用同样的“拆解后判断”模式。

---

## 系统设计面试角度

### Q：你部署了一个 RAG 系统，用户反馈答案有时是错的。你会如何系统地诊断并修复问题？

**参考答案：**

我会使用 RAG 三元组来隔离失败模式：

1. **抽样失败查询**：收集 50～100 个用户标记为错误的答案，并按失败类型分类。
2. **运行三元组**：
   - **上下文相关性低？** → 检索问题。系统取回了错误文档。修复：检查 Embedding 相似度分数，确认查询语言和文档语言是否匹配，尝试混合搜索（BM25 + 稠密检索），增加重排序器。
   - **有依据性低？** → 幻觉问题。LLM 在拥有良好上下文时仍然编造内容。修复：强化系统 Prompt（“只能根据提供的上下文回答”）、降低温度、切换到更遵循指令的模型，或增加引用要求。
   - **答案相关性低？** → 系统检索并忠实总结了相关内容，但错过了实际问题。修复：改进查询理解（查询改写、HyDE），增加查询分类以路由到正确索引。
3. **构建回归测试**：为 50 个失败查询标注预期答案，并加入黄金测试集。未来每次流水线变更都必须通过这些用例。
4. **建立持续监控**：对 5% 的生产流量进行自动化评估抽样。当忠实度低于 0.80 或上下文相关性低于 0.60 时告警。

关键洞察是，“答案有误”不是诊断，而是症状。RAG 三元组可以把模糊的投诉转化为具体、可操作的根因。

### Q：没有标准答案时，如何评估 RAG 系统？

**参考答案：**

这是现实中最常见的场景。我会采用三层方法：

**第一层：免参考指标（第 1 天）**。RAGAS 的忠实度和上下文相关性不需要标准答案。它们告诉你系统是否产生幻觉，以及检索是否有效。可以立即对任意查询运行。

**第二层：合成黄金集（第 1 周）**。使用 RAGAS TestsetGenerator 从语料库生成合成的（查询、答案）对，为答案正确性和上下文召回率提供近似真实基准。人工审核其中一部分，以验证质量。

**第三层：源自生产的黄金集（第 1 个月）**。从生产日志中挖掘用户满意度高的查询（点了赞、没有追问），让标注人员为其标注参考答案。这样得到的黄金集反映真实使用模式，而不是合成分布。

权衡在于准确率与速度。第一层几小时内就能提供信号，但只是近似值；第三层提供真实基准，却需要数周。三层并行运行，先用第一层获得即时反馈。

### Q：你的 RAG 评估流水线每天要花费 500 美元调用 LLM 评判者。如何降低成本？

**参考答案：**

按影响程度排序，我会采用四种策略：

1. **分层评判模型**：生产抽样使用 Claude Haiku（$0.002/查询），覆盖 90% 的流量；CI 回归测试和每周深度审计保留 GPT-4o（$0.018/查询）。单此一项就能削减 80% 的成本。
2. **智能抽样**：不要评估每个查询。对 5% 的生产流量按查询类型和用户群体分层抽样；CI 只运行黄金集（500 个查询），而不是完整的合成集。
3. **缓存**：许多生产查询很相似。对（查询、上下文、答案）三元组进行哈希并缓存评估结果，相同或近似输入直接使用缓存分数。
4. **启发式预过滤**：调用 LLM 评判者前先运行便宜的启发式检查。如果答案包含“我不知道”，或者与上下文完全没有重合（ROUGE-L < 0.1），就跳过昂贵的忠实度评估，直接赋予分数。

目标是把评估预算用在能提供最多信号的地方：也就是 LLM 评判者的细致推理真正有价值的含糊、临界案例。

---

## 参考资料

- Es 等。《RAGAS: Automated Evaluation of Retrieval Augmented Generation》（2023，arXiv:2309.15217）
- TruLens。《The RAG Triad》（2024）
- DeepEval。《Using the RAG Triad for RAG Evaluation》（2025）
- Confident AI。《RAG Evaluation Metrics》（2025）
- Microsoft。《The Path to a Golden Dataset》（2025）
- Prem AI。《RAG Evaluation: Metrics, Frameworks & Testing》（2026）

---

*上一篇：[多模态 RAG](12-multimodal-rag.md) | 下一篇：即将推出*
