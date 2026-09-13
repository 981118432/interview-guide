# 多模态 RAG

多模态 RAG 将检索增强生成从纯文本扩展到图像、表格、图表、音频和混合布局文档。如今，生产系统经常需要摄取包含图表的 PDF、幻灯片、扫描发票和研究论文；在这些文档中，视觉布局本身就是含义。当前有三种主流架构：描述并建立索引、统一视觉—文本 Embedding（Cohere Embed v4、Voyage-Multimodal-3.5、Gemini Embedding 001），以及页面即图像结合延迟交互（ColPali、ColQwen2.5、ColNomic）。

## 目录

- [纯文本 RAG 为什么会失败](#why-text-only-rag-fails)
- [架构模式](#architecture-patterns)
- [多模态 Embedding 策略](#multi-modal-embedding-strategies)
- [用于文档理解的视觉语言模型](#vision-language-models)
- [ColPali 与基于视觉的检索](#colpali)
- [表格提取与结构化数据检索](#table-extraction)
- [图表与示意图理解](#chart-understanding)
- [生产架构](#production-architecture)
- [实现示例](#implementation-example)
- [系统设计面试角度](#system-design-interview-angle)
- [参考资料](#references)

---

## 纯文本 RAG 为什么会失败

传统 RAG 流程会把文档解析成文本块，生成 Embedding，然后针对文本查询进行检索。但在真实文档上会出现问题：

| 文档元素 | 纯文本 RAG 的行为 | 实际丢失的信息 |
|-----------------|----------------------|------------------------|
| **柱状图** | 只提取坐标轴标签 | 趋势、比较关系、数量级 |
| **架构图** | 完全遗漏 | 组件关系、数据流 |
| **表格** | 展平行内容后丢失结构 | 行列关联、表头 |
| **信息图** | 捕获零散的文本片段 | 视觉层级、空间分组 |
| **带标题的照片** | 获取标题，丢失图像 | 视觉证据、空间上下文 |

**现实情况**：企业文档中 40%～60% 的内容不是文本。财务报告的价值在于图表，医学论文的关键发现位于图中。忽略视觉内容，就等于忽略了大部分知识。

---

## 架构模式

多模态 RAG 有三种主流模式，各自具有不同的权衡：

### 模式 1：统一 Embedding 空间

```
                     Shared Vector Space
                    +-------------------+
  Text  --> Encoder |  [0.2, 0.8, ...] |
  Image --> Encoder |  [0.3, 0.7, ...] |  --> Single Index --> Retrieve
  Table --> Encoder |  [0.1, 0.9, ...] |
                    +-------------------+

  Query "show revenue trends" --> encode --> nearest neighbors across ALL modalities
```

- **原理**：使用 CLIP 或 SigLIP 等模型，将文本和图像投影到同一个向量空间。
- **优点**：单一索引、单次查询，检索逻辑简单。
- **缺点**：不同模态的 Embedding 质量不一致；表格需要序列化。

### 模式 2：按模态检索并融合

```
  Query --> +----> Text Index    --> Top-K text chunks
            |
            +----> Image Index   --> Top-K images
            |
            +----> Table Index   --> Top-K tables
            |
            v
        Fusion / Reranking Layer --> Combined Top-K --> VLM Generator
```

- **原理**：为每种模态分别生成 Embedding 并建立索引，再由重排序器或互惠秩融合（RRF）合并结果。
- **优点**：每种模态都可以使用最佳 Embedding，并且可以独立调优各个检索器。
- **缺点**：基础设施更复杂；融合逻辑并不简单。

### 模式 3：视觉优先（页面即图像）

```
  Document Page --> Screenshot/Render --> Vision Encoder --> Multi-vector Index
                                              |
  Query ---------> Text Encoder --------------+---> Late Interaction Score
                                                    --> Retrieve top pages
```

- **原理**：把每个文档页面视为一张图像。使用视觉语言模型（例如 ColPali）生成 Patch 级 Embedding，并通过延迟交互（MaxSim）评分。
- **优点**：无需 OCR、布局解析或表格提取流水线；可以端到端训练。
- **缺点**：索引阶段计算量更高；细粒度文本搜索能力较弱。

**建议**：对于文档密集型用例，模式 3（视觉优先）正在快速普及。当需要精确文本搜索与视觉检索并存时，模式 2 仍然是生产环境的主力方案。

---

## 多模态 Embedding 策略

### CLIP（Contrastive Language-Image Pretraining）

最初的双编码器，将文本和图像映射到共享的 512/768 维空间。

- **优势**：生态庞大、原理成熟，有许多经过微调的变体。
- **弱点**：相比自然照片，在图表、表格等文档风格图像上的效果较弱；对比学习损失需要较大的 Batch Size。

### SigLIP / SigLIP 2

它用 Sigmoid 损失替代 CLIP 的 Softmax 交叉熵，使每个图像—文本对都能独立评估。

- **SigLIP 2（2025）**：增加标题生成解码器、自蒸馏和掩码预测，在 109 种语言的 100 亿张以上图像上训练。
- **关键优势**：在较小 Batch Size（4～8k）下超过 CLIP，并提供更稠密、更稳健的特征。
- **生产应用**：挪威国家图书馆、电商视觉搜索、AI 艺术策展。

### 面向 RAG 的对比

| 模型 | 最适合 | Embedding 维度 | 文档质量 | 自然图像质量 |
|-------|----------|--------------|-----------------|----------------------|
| CLIP ViT-L/14 | 通用场景 | 768 | 中 | 高 |
| SigLIP 2 So400m | 多语言文档 | 1152 | 高 | 高 |
| Nomic Embed Vision | 以文本为主的文档 | 768 | 高 | 中 |
| Voyage Multimodal 3 | 混合文档 | 1024 | 高 | 高 |

### Embedding 策略决策

```
Is your content mostly natural images (photos, products)?
  YES --> CLIP or SigLIP fine-tuned on your domain
  NO
    |
    v
Is your content document pages (PDFs, slides, reports)?
  YES --> ColPali / ColQwen (vision-first, no OCR needed)
  NO
    |
    v
Is it a mix of text, images, and structured data?
  YES --> Modality-specific encoders + fusion (Pattern 2)
```

---

## 用于文档理解的视觉语言模型

在多模态 RAG 中，VLM 承担两个角色：(1) 作为从检索到的多模态上下文中综合答案的**生成器**；(2) 作为摄取阶段提取结构化信息的**索引引擎**。

### VLM 能力对比

| 能力 | Claude Opus 4.7 / Sonnet 4.6 | GPT-5.5 | Gemini 3.1 Pro |
|-----------|------------------------------|---------|----------------|
| **图表阅读** | 优秀 | 优秀 | 优秀 |
| **表格提取** | 优秀 | 良好 | 优秀 |
| **示意图理解** | 优秀 | 良好 | 优秀 |
| **手写 OCR** | 良好 | 良好 | 良好 |
| **多页推理** | 优秀（Sonnet 4.6 为 100 万上下文） | 优秀（100 万上下文） | 优秀（100 万上下文） |
| **结构化输出** | 原生 JSON 模式 | 原生 JSON 模式 | 原生 JSON 模式 |

### VLM 增强的摄取流水线

```
  Raw PDF
    |
    v
  Page Renderer (pdf2image, 300 DPI)
    |
    v
  VLM Extraction Pass:
    +-- "Extract all tables as markdown"
    +-- "Describe this chart: axes, trends, key data points"
    +-- "Summarize the diagram: components and relationships"
    |
    v
  Structured Output (JSON)
    |
    +---> Text chunks     --> Text embedding index
    +---> Table markdown  --> Text embedding index (with metadata: "type=table")
    +---> Chart summaries --> Text embedding index (with metadata: "type=chart")
    +---> Page images     --> Image embedding index (CLIP/SigLIP)
```

这种“先描述、再 Embedding”的方式会把视觉内容转换为可搜索的文本，同时保留原始图像，以便在生成阶段使用。

---

## ColPali 与基于视觉的检索

ColPali 代表了一种范式转变：它不再构建复杂的 OCR、布局和表格提取流水线，而是把每个文档页面作为一张完整图像，让视觉语言模型处理所有内容。

### ColPali 如何工作

```
  Document Page Image
        |
        v
  SigLIP Vision Encoder (So400m)
        |
  Splits image into patches (e.g., 32x32 grid = 1024 patches)
        |
        v
  Gemma 2B Language Model (contextualizes patch embeddings)
        |
        v
  Linear Projection --> 128-dim patch embeddings
        |
  Result: 1024 vectors of dim 128 per page
        |
        v
  Stored in Multi-Vector Index

  At query time:
  Query --> Tokenize --> Embed --> 128-dim token embeddings
        |
        v
  Late Interaction (MaxSim):
    Score = Sum over query tokens of Max similarity to any patch
```

### ColPali 与传统流水线对比

| 方面 | 传统流水线 | ColPali |
|--------|---------------------|---------|
| **OCR** | 必需（Tesseract、Azure OCR） | 不需要 |
| **布局检测** | 必需（Detectron2、LayoutLM） | 不需要 |
| **表格解析器** | 必需（Camelot、Tabula） | 不需要 |
| **图表提取器** | 必需（ChartOCR） | 不需要 |
| **索引速度** | 慢（多阶段） | 快（单次前向传播） |
| **检索质量** | 文本上高，视觉上差 | 所有模态都高 |
| **存储** | 文本索引（约较小） | 多向量索引（约较大） |

### ColPali 家族

- **ColPali（v1）**：PaliGemma-3B Backbone，最初版本。
- **ColQwen 2.5**：Qwen2-VL Backbone，多语言支持更好，在亚洲语言文档上有所改进。
- **ColSmol**：面向边缘部署的更小版本，约 10 亿参数。

### ViDoRe 基准结果

ColPali 在 InfographicVQA、ArxivQA 和 TabFQuAD 等视觉复杂基准上表现出色；这些基准分别测试信息图、图形和表格。即使在以文本为中心的文档上，它也能超过传统文本流水线。

---

## 表格提取与结构化数据检索

表格是传统 RAG 最难处理的模态。逐行展平表格会破坏列标题关系，而正是这些关系赋予每个单元格具体含义。

### 策略 1：基于 VLM 的提取

```python
# Pseudocode: Extract tables using a VLM
def extract_tables_from_page(page_image: bytes) -> list[dict]:
    prompt = """
    Extract ALL tables from this document page.
    For each table, return:
    {
      "title": "table title or caption",
      "headers": ["col1", "col2", ...],
      "rows": [["val1", "val2", ...], ...],
      "markdown": "| col1 | col2 |\\n|---|---|\\n| val1 | val2 |"
    }
    Return JSON array. If no tables, return [].
    """
    response = vlm.generate(image=page_image, prompt=prompt)
    return json.loads(response)
```

### 策略 2：专用表格解析器

- **Tabula / Camelot**：基于规则的 PDF 表格提取。速度快，但复杂布局下不够稳健。
- **Table Transformer（基于 DETR）**：从图像中检测表格边界和单元格结构。
- **Unstructured.io**：结合启发式规则与机器学习模型，进行布局感知解析。

### 策略 3：表格感知的分块

```
  Original Table (20 rows x 8 columns)
        |
        v
  Chunk as complete unit (do NOT split tables across chunks)
        |
        v
  Embed the full markdown table as a single chunk
        |
        v
  Add metadata: {"type": "table", "page": 14, "caption": "Q3 Revenue by Region"}
        |
        v
  At generation time: pass the FULL table to the LLM, not a fragment
```

**关键原则**：表格必须是原子检索单元。绝不能在分块边界处拆分表格。

---

## 图表与示意图理解

### 图表类型与提取方式

| 图表类型 | 要提取的内容 | 最佳方式 |
|-----------|----------------|---------------|
| **柱状图/折线图/饼图** | 数据值、趋势、比较关系 | VLM 描述 + 数据表提取 |
| **流程图** | 步骤、决策、连接关系 | VLM 结构化提取（节点 + 边） |
| **架构图** | 组件、关系、数据流 | VLM 描述 + 实体提取 |
| **散点图** | 相关性、离群点、聚类 | VLM 趋势描述 + 可用时提取原始数据 |
| **甘特图** | 时间线、依赖关系、里程碑 | VLM 结构化提取 |

### 双重表示策略

为每个图表或示意图存储两种表示：

```
  Chart Image
    |
    +---> (1) Text Description (for text-based retrieval)
    |         "This bar chart shows Q3 revenue by region.
    |          North America: $4.2M, Europe: $3.1M, APAC: $2.8M.
    |          NA grew 15% QoQ while APAC declined 3%."
    |
    +---> (2) Original Image (for visual retrieval + generation context)
              Stored with CLIP/SigLIP embedding for image-based queries
```

这样，图表既可以通过文本查询（“APAC 的收入是多少？”）检索，也可以通过视觉查询（“给我看看收入图表”）检索。

---

## 生产架构

### 完整的多模态 RAG 流程

```
  INGESTION:
  Raw Docs --> Doc Classifier --+--> Text-Heavy  --> chunking + text embeddings
                                +--> Visual-Heavy --> page render + ColPali
                                +--> Mixed        --> VLM extraction + hybrid
                                         |
                                         v
                          [Text Index] [Image Index] [Table Index]

  RETRIEVAL:
  Query --> Query Analyzer --+--> Text:  BM25 + dense search
                             +--> Image: CLIP/ColPali search
                             +--> Table: metadata-filtered dense
                                    |
                                    v
                             Cross-Modal Reranker --> Context Assembly --> VLM --> Response
```

### 扩展性考量

| 关注点 | 解决方案 |
|---------|----------|
| **索引大小** | ColPali 每页存储约 1024 个向量。100 万页约等于 10 亿个向量。使用量化（二值化、PQ）。 |
| **摄取延迟** | VLM 提取速度较慢（约 2～5 秒/页）。使用 GPU 加速的异步 Worker。 |
| **查询延迟** | 多索引扇出会增加延迟。使用并行检索和激进的 Top-K 剪枝。 |
| **成本** | 摄取阶段的 VLM 调用只发生一次，成本可在查询量上摊销。为提取按每页 0.01～0.05 美元预算。 |
| **存储** | 将页面图像存放在对象存储（S3）中；将 Embedding 存放在向量数据库中；将文本存放在搜索索引中。 |

---

## 实现示例

### 使用 ColPali + VLM 实现端到端多模态 RAG

```python
# Pseudocode: Production multi-modal RAG pipeline

from colpali_engine import ColPali, ColPaliProcessor
from qdrant_client import QdrantClient
import anthropic

# --- INDEXING ---

def index_document(pdf_path: str, collection: str):
    """Index a PDF document using ColPali for visual retrieval
    and VLM extraction for text-based retrieval."""

    pages = render_pdf_to_images(pdf_path, dpi=300)

    colpali_model = ColPali.from_pretrained("vidore/colpali-v1.3")
    processor = ColPaliProcessor.from_pretrained("vidore/colpali-v1.3")
    vlm_client = anthropic.Anthropic()

    for page_num, page_image in enumerate(pages):
        # 1. Generate ColPali multi-vector embeddings
        inputs = processor(images=[page_image])
        patch_embeddings = colpali_model(**inputs)  # shape: [1, 1024, 128]

        # 2. Extract structured content via VLM
        extraction = vlm_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": encode_image(page_image)},
                    {"type": "text", "text": """Extract from this page:
                    1. All text content (preserve structure)
                    2. Tables as markdown
                    3. Chart descriptions with data points
                    Return as JSON with keys: text, tables, charts"""}
                ]
            }]
        )

        structured = json.loads(extraction.content[0].text)

        # 3. Store in vector DB
        qdrant.upsert(collection, points=[
            # ColPali multi-vector for visual retrieval
            PointStruct(
                id=f"{pdf_path}:page:{page_num}:colpali",
                vector={"colpali": patch_embeddings[0].tolist()},
                payload={
                    "source": pdf_path,
                    "page": page_num,
                    "type": "page_image",
                    "text_preview": structured["text"][:500]
                }
            ),
            # Text embeddings for each extracted element
            *create_text_chunks(structured, pdf_path, page_num)
        ])


# --- RETRIEVAL ---

def retrieve(query: str, collection: str, top_k: int = 5):
    """Hybrid retrieval: ColPali visual + text semantic search."""

    # Visual retrieval via ColPali
    query_inputs = processor(text=[query])
    query_embeddings = colpali_model(**query_inputs)

    visual_results = qdrant.query(
        collection,
        query_vector=("colpali", query_embeddings[0].tolist()),
        limit=top_k,
        query_filter=Filter(must=[FieldCondition(key="type", match="page_image")])
    )

    # Text retrieval via dense embeddings
    text_embedding = text_encoder.encode(query)
    text_results = qdrant.search(
        collection,
        query_vector=("text", text_embedding.tolist()),
        limit=top_k
    )

    # Fuse results using reciprocal rank fusion
    fused = reciprocal_rank_fusion(visual_results, text_results, k=60)
    return fused[:top_k]


# --- GENERATION ---

def generate_answer(query: str, retrieved_context: list) -> str:
    """Generate answer using VLM with multi-modal context."""

    content_blocks = [{"type": "text", "text": f"Question: {query}\n\nContext:"}]

    for ctx in retrieved_context:
        if ctx.payload["type"] == "page_image":
            # Include the actual page image
            content_blocks.append({
                "type": "image",
                "source": load_page_image(ctx.payload["source"], ctx.payload["page"])
            })
        else:
            # Include text/table content
            content_blocks.append({
                "type": "text",
                "text": f"[{ctx.payload['type']}] {ctx.payload['content']}"
            })

    content_blocks.append({
        "type": "text",
        "text": "Answer the question using ONLY the provided context. Cite sources."
    })

    response = vlm_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        messages=[{"role": "user", "content": content_blocks}]
    )
    return response.content[0].text
```

---

## 系统设计面试角度

### Q：为一个需要回答包含文本、表格和图表的财报问题的金融研究平台设计 RAG 系统。

**参考答案：**

核心挑战在于，财报中 60% 以上的信息存在于表格和图表，而不是正文中。纯文本 RAG 流程会漏掉收入拆分、趋势线和对比数据。

**架构**：我会采用混合方案（模式 2 + 模式 3 的部分能力）：

1. **摄取**：以 300 DPI 渲染每个 PDF 页面。运行 VLM 提取流程，把表格转换为 Markdown，把图表转换为结构化描述；同时为每个页面图像生成 ColPali 多向量 Embedding。
2. **存储**：建立三个索引——(a) 带稠密 Embedding 的文本块索引（财务正文）；(b) 带稠密 Embedding 和表格类型元数据过滤的 Markdown 表格索引；(c) 用于页面级视觉检索的 ColPali 多向量索引。
3. **检索**：查询分析器对查询类型进行分类。“第三季度收入是多少？”触发文本 + 表格搜索；“给我展示收入趋势”触发视觉（ColPali）搜索。结果通过 RRF 融合，再由交叉编码器重排序。
4. **生成**：VLM 接收融合后的上下文——文本块、Markdown 表格和相关页面图像。它生成有依据的答案，并引用具体页面和表格。

**关键权衡**：ColPali 对视觉内容有出色的召回能力，但每页存储约 1024 个向量，因此 10 万篇文档（50 万页）约有 5 亿个向量。我会使用二值量化将存储量降低 32 倍，同时接受少量召回损失。对于文本路径，BM25 + 稠密混合搜索可以很好地处理金融术语。

### Q：如果一个查询需要同时从不同页面的图表和表格中获取信息，你会怎么处理？

**参考答案：**

这是一个跨模态、跨页面检索问题。解决方案包含三个部分：

1. **检索多样性**：确保检索器返回多个模态的结果。设置最低配额——无论哪个模态的分数最高，每次检索结果中至少包含 2 个文本结果、2 个表格结果和 1 个视觉结果。
2. **上下文组装**：组装 VLM Prompt 时，给所有检索内容附上明确来源：“[第 14 页的表格：按地区划分的第三季度收入]”和“[第 22 页的图表：2024～2026 年收入趋势]”。这样 VLM 就能跨两者进行推理。
3. **Agent 式兜底**：如果初次检索没有找到足够的跨模态上下文，Agent 层可以发起后续检索：“表格展示了收入数字，但用户问的是趋势——我还要搜索与收入有关的图表。”

关键洞察是，跨模态问题本质上是多跳问题。系统需要先从一种模态中检索，识别信息缺口，再从另一种模态中检索。

---

## 参考资料

- Faysse 等。《ColPali: Efficient Document Retrieval with Vision Language Models》（ICLR 2025）
- Google。《SigLIP 2: Multilingual Vision-Language Encoders》（2025）
- NVIDIA。《An Easy Introduction to Multimodal Retrieval-Augmented Generation》（2025）
- HKUDS。《RAG-Anything: All-in-One Multimodal RAG Framework》（2025）
- Vespa Blog。《PDF Retrieval with Vision Language Models》（2024）

---

*上一篇：[高级检索模式](09-advanced-retrieval-patterns.md) | 下一篇：[RAG 评估模式](13-rag-evaluation-patterns.md)*
