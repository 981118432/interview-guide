# Embedding 模型

Embedding 模型把文本转换成高维向量。前沿方向已经从静态的单向量表示，发展到**多分辨率、晚交互和多模态** Embedding。

## 目录

- [Embedding 前沿（Matryoshka）]( #matryoshka)
- [晚交互（ColBERT v2）]( #late-interaction)
- [二值与 Int8 量化]( #quantization)
- [模型选择标准]( #selection)
- [多模态 Embedding（视觉 + 文本）]( #multimodal)
- [面试问题]( #interview-questions)
- [参考资料]( #references)

---

## Embedding 前沿：Matryoshka Embedding

传统上，如果把文本 Embedding 成 1,536 维，就只能用全部 1,536 维进行搜索。

**Matryoshka 表示学习（MRL）**
- 模型经过训练，会把最重要的信息“存储”在前几个维度中。
- **优势**：可以先以 1,536 维生成 Embedding，但只索引前 **64 维**进行“快速搜索”，再用完整的 1,536 维细化 Top 结果。
- **效率**：内存/索引大小减少 20 倍，准确率下降低于 2%。

---

## 晚交互：ColBERT v2

标准 Embedding 是“Bi-Encoder”（每个块一个向量）。**ColBERT**（Contextualized Late Interaction over BERT）采用“Token 级”方法。

- **方式**：ColBERT 不为每个块存储 1 个向量，而是**每个 Token 存储 1 个向量**。
- **交互**：查询时，模型把查询中的每个 Token 与文档中的每个 Token 比较（即“MaxSim”操作）。
- **现状**：ColBERT v2（以及 ColPali、ColQwen2.5、ColNomic 等后续模型，适用于文档和页面图像）通过 PLAID 索引实现了大幅压缩，已经适合生产。对于“在稻草堆中找针”的技术查询，它能达到高得多的精度。

---

## 二值与 Int8 量化

存储 `float32` 向量成本很高。生产索引高度依赖**模型内量化**。

- **二值 Embedding**：把向量转换成 1 和 0。
  - **内存**：减少 32 倍。
  - **速度**：在现代 CPU 上，汉明距离（XOR 操作）比余弦相似度快 10 倍。
- **Int8/Int4**：`text-embedding-3-small` 等模型原生支持。

---

## 模型选择标准

| 模型 | 供应商 | 特性 | 上下文 |
|------|--------|------|--------|
| **Gemini Embedding 001** | Google | 多模态（文本、图像、视频、音频、PDF），共享 3072 维空间，MTEB-English 领先 | 8k |
| **Qwen3-Embedding-8B** | 开源 | MTEB 多语言领先，指令微调，长文档能力强 | 32k |
| **Llama-Embed-Nemotron-8B** | NVIDIA | 多语言得分领先，开放权重 | 8k |
| **Cohere Embed v4** | Cohere | 多模态（文本 + 图像）、Matryoshka、二值量化 | 128k |
| **Voyage-Multimodal-3.5** | Voyage AI | 统一文本/图像、针对检索优化 | 32k |
| **OpenAI text-embedding-3-large** | OpenAI | Matryoshka、原生 Int8、支持广泛 | 8k |
| **BGE-M3** | 开源 | 多语言、多粒度（稠密 + 稀疏 + 晚交互） | 8k |
| **Jina-Embeddings-v3** | Jina AI | 支持晚交互，长上下文 | 128k |

开放权重模型（Qwen3、Llama-Embed-Nemotron、BGE）现在在纯 MTEB 得分上已经匹敌或超过商业 API。想要托管基础设施和 SLA 时选择商业模型；当高流量下的单次查询成本比延迟下限更重要时，选择开放权重模型。

---

## 多模态 Embedding

纯文本 RAG 会默默丢弃经常包含答案的图表、表格、示意图和布局信息。现代技术栈把页面、截图和图表视为一等检索对象：

- **统一视觉-文本 Embedding**：Cohere Embed v4、Voyage-Multimodal-3.5、Gemini Embedding 001 共享一个向量空间，因此可以针对示意图查询“紧急断电阀在哪里？”。
- **页面即图像与晚交互**：ColPali、ColQwen2.5 和 ColNomic 直接对每个页面的渲染图进行 Embedding，跳过脆弱的 OCR，同时保留视觉层级。
- **CLIP 家族模型**：对图像密集型目录（电商、媒体）仍然有用，因为文本-图像对齐是核心信号。

---

## 面试问题

### Q：Embedding 中的“词汇不匹配”问题是什么？

**强回答：**

Embedding 依赖训练时学到的语义空间。如果用户查询使用了更新的术语（例如 Embedding 模型截止日期之后发布的模型名称），而这个术语不在 Embedding 模型的训练集中，模型可能会把它赋予一个泛化的“AI”向量，漏掉具体细节。标准修复方式是使用**混合搜索**（用 BM25 捕捉具体关键词）加上 **Cross-Encoder 重排序**，后者通过同时查看查询和文档 Token，能更好地处理分布外词汇。

### Q：为什么 10 亿向量的索引会选择 Matryoshka 模型？

**强回答：**

使用标准的 `float32`、1,536 维 Embedding 扩展到 10 亿向量时，HNSW 索引需要约 6TB 高速 RAM，成本高得难以接受。使用 Matryoshka 模型，我可以在初始检索阶段使用前 128 维（并进行二值量化）。这样内存占用减少 90% 以上，可以在便宜得多的硬件上找到“Top 1,000”候选。随后只为这 1,000 个候选获取全分辨率向量，执行最终重排序。

---

## 参考资料

- Kusupati 等，《Matryoshka Representation Learning》（2022/2024 更新）
- Khattab 等，《ColBERT v1 & v2: Efficient Late Interaction》（2021/2023）
- OpenAI，《Introducing New Embedding Models with Matryoshka Support》（2024）

---

*下一篇：[向量数据库](04-vector-databases.md)*
