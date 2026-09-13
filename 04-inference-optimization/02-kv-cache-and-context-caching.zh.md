# KV Cache 与上下文缓存

KV Cache 是长上下文 AI 系统中最主要的内存消费者。有效管理这个缓存，决定了系统能否扩展到 200 万 Token，还是在 1 万 Token 时就崩溃。

## 目录

- [KV Cache 问题](#kv-cache-problem)
- [GQA：分组查询注意力](#gqa)
- [上下文缓存（自托管）](#context-caching-self-hosted)
- [API 级上下文缓存（Prompt Caching）](#api-prompt-caching)
- [RAD-O：检索增强解码](#rad-o)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## KV Cache 问题

在生成过程中，模型需要所有历史 Token 的 Key（K）和 Value（V）张量。把它们存储在内存中代价很高。

**显存计算（Llama 4 70B）：**
- **Token 数**：128,000
- **精度**：BF16（2 bytes/param）
- **内存**：`2 (KV) * layers (80) * context (128k) * heads (8) * head_dim (128) * 2 bytes`
- **总计**：在 128k 上下文下，**每个用户约 42 GB**。

---

## GQA：分组查询注意力

GQA 是在不牺牲性能的情况下缩小 KV Cache 的现代标准。

| 方法 | 比例 | KV Cache 缩减 | 质量损失 |
|------|------|---------------|----------|
| **多头注意力（MHA）** | 1:1 | 1 倍（基线） | 0% |
| **分组查询注意力（GQA）** | 8:1 | **8 倍** | < 0.2% |
| **多查询注意力（MQA）** | All:1 | 64～128 倍 | 2～3% |

**细节**：GQA 允许模型的多个“推理”头关注同一份 KV“记忆”，从而大幅减少 Decode 阶段所需的内存带宽。

---

## 上下文缓存（自托管）

生产系统会为具有公共前缀的 Prompt 使用**共享 KV Cache**（例如，1,000 个用户共享一个 100 页的知识库）。

### 磁盘缓存与显存缓存

- **VRAM Cache**：访问即时，但容量严格受限。
- **磁盘/SSD Cache**：访问更慢，但容量几乎不受限。SGLang 等框架使用分层系统：`Most Recent (VRAM) -> Frequent (HBM) -> Occasional (SSD)`。

---

## API 级上下文缓存（Prompt Caching）

主要供应商（OpenAI、Anthropic、Google、DeepSeek）现在都提供 **Prompt Caching** 折扣。

| 供应商 | 功能名称 | 价格（缓存输入） | 最适合 |
|--------|----------|------------------|--------|
| **Anthropic** | Context Caching | 90% 折扣（Sonnet 4.6 缓存：$0.30/1M） | 长系统 Prompt、工具 Schema |
| **OpenAI** | Prompt Caching | 缓存输入约 50% 折扣（GPT-5.5 缓存：约 $2.50/1M） | 多轮对话 |
| **Google** | Context Caching | 缓存读取 $0.20/1M（Gemini 3.1 Pro，200K 以下）；每小时存储费另计 | 长共享语料库 |
| **DeepSeek** | Context Caching | **$0.003625/M（V4 Pro）/ $0.0028/M（V4 Flash）** | 超大代码库 RAG；市场上最便宜的缓存层 |

**盈亏平衡的细节**：如果缓存前缀复用超过 **1.1～1.5 次**，使用缓存就比直接发送原始 Token 更便宜。Anthropic 对缓存写入收取 25% 的溢价，因此对于较短前缀，盈亏平衡点更高（复用 3～5 次）。DeepSeek 在 2026 年 4 月 26 日将缓存命中价格降至发布时的十分之一。对于缓存密集型工作负载，V4 Flash 当前每个缓存 Token 的价格大约比 GPT-5.5 便宜 30～50 倍。

---

## RAD-O：检索增强解码

RAD-O 是一种上下文缓存技术，模型会把长文档的 KV Cache **压缩**成“潜在 Token”。
- **方式**：不存储 100 万 Token 的完整 KV 向量，而是存储小 10 倍的压缩表示。
- **影响**：让原本只支持 20 万 Token 的硬件能够承载 200 万 Token 以上的上下文。

---

## 面试问题

### Q：PagedAttention 如何帮助管理 KV Cache？（简化版）

**强回答：**

标准 KV Cache 要求连续的内存分配（一个巨大的 RAM 块），这会导致**外部碎片**（内存虽然存在，却分散在无法使用的空隙中）。PagedAttention（vLLM 使用）把 KV Cache 拆成小而固定大小的“页”（类似操作系统的虚拟内存）。这样缓存可以不连续，我们能够在真正需要时精确分配内存，还可以让拥有相同前缀的不同请求共享页面。这通常能把内存利用率从 60% 提高到 96% 以上。

### Q：为什么对于一份 50k Token 的文档，上下文缓存比 RAG 更好？

在上下文缓存很便宜的情况下（DeepSeek、Gemini、Anthropic），对中等大小文档使用 RAG 往往是“杀鸡用牛刀”。
1. **召回率**：上下文缓存能提供 100% 的召回（整篇文档都在上下文窗口中），而 RAG 依赖检索准确率。
2. **连贯性**：模型可以看到整篇文档中的跨段引用。
3. **经济性**：对于 50k Token，缓存输入的成本往往低于维护向量数据库和检索流水线的复杂度。

---

## 参考资料

- Kwon 等，《Efficient Memory Management with PagedAttention》（2023）
- Anthropic，《Prompt Caching Documentation》（2024）
- DeepSeek，《Context Caching Technical Report》（2025）

---

*下一篇：[推测解码](03-speculative-decoding.md)*
