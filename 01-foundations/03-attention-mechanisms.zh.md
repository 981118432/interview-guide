# Attention 机制

Attention 是让 Transformer 成为可能的核心创新。本章介绍对系统设计和面试都很重要的数学基础、变体与优化方法。

## 目录

- [Attention 基础](#attention-基础)
- [缩放点积注意力](#缩放点积注意力)
- [多头注意力](#多头注意力)
- [注意力模式](#注意力模式)
- [高效注意力变体](#高效注意力变体)
- [Flash Attention（v2 与 v3）](#flash-attention)
- [多头潜在注意力（MLA）](#多头潜在注意力mla)
- [KV Cache 优化与上下文缓存](#kv-cache-优化与上下文缓存)
- [实际影响](#实际影响)
- [面试问答](#面试问答)
- [参考资料](#参考资料)

---

## Attention 基础

### 核心思想

Attention 允许序列中的每个位置从其他所有位置收集信息。与逐步传递信息的循环机制不同，Attention 建立了直接连接。

**给分布式系统工程师的心智模型：**
- RNN：沿链路传递消息
- Attention：每个节点都能查询其他节点的发布/订阅系统

### Query、Key、Value 框架

Attention 对输入进行三种投影：

| 组件 | 作用 | 类比 |
|-----------|------|---------|
| Query（Q） | 我在寻找什么？ | 搜索查询 |
| Key（K） | 我包含什么？ | 文档索引 |
| Value（V） | 我能贡献什么？ | 文档内容 |

```python
# Input: x of shape [batch, seq_len, d_model]

Q = x @ W_q  # [batch, seq_len, d_k]
K = x @ W_k  # [batch, seq_len, d_k]
V = x @ W_v  # [batch, seq_len, d_v]
```

---

## 缩放点积注意力

Attention 的基础操作：

```python
def scaled_dot_product_attention(Q, K, V, mask=None):
    d_k = Q.shape[-1]

    # Compute attention scores
    scores = Q @ K.transpose(-2, -1)  # [batch, seq_len, seq_len]
    scores = scores / math.sqrt(d_k)  # Scale

    # Apply mask (for causal attention)
    if mask is not None:
        scores = scores.masked_fill(mask == 0, float('-inf'))

    # Convert to probabilities
    attention_weights = F.softmax(scores, dim=-1)

    # Weighted sum of values
    output = attention_weights @ V

    return output, attention_weights
```

### 为什么要除以 d_k 的平方根？

**面试高频题**：这个问题考察数值直觉。

不做缩放时，点积会随维度增大：
- 对于维度为 d 的随机单位向量 q 和 k
- E[q · k] = 0，但 Var[q · k] = d
- 标准差 = sqrt(d)

当 d 很大（512 或更大）时，点积可能非常大或非常小。在大数值上运行 Softmax 会趋近于 one-hot，导致梯度消失。

```python
# Demonstration
import numpy as np

d = 512
q = np.random.randn(d)
k = np.random.randn(d)

unscaled = np.dot(q, k)      # Magnitude ~ sqrt(512) ~ 22
scaled = unscaled / np.sqrt(d)  # Magnitude ~ 1
```

### 因果掩码

对于自回归生成，每个位置只能关注之前的位置：

```python
def create_causal_mask(seq_len):
    # Lower triangular matrix
    mask = torch.tril(torch.ones(seq_len, seq_len))
    return mask

# Example for seq_len=4:
# [[1, 0, 0, 0],
#  [1, 1, 0, 0],
#  [1, 1, 1, 0],
#  [1, 1, 1, 1]]
```

掩码为 0 的位置会被赋予负无穷分数，经过 Softmax 后变为 0。

---

## 多头注意力

不使用一个 Attention 函数，而是使用多个关注不同方面的“头”：

```python
class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super().__init__()
        self.num_heads = num_heads
        self.d_k = d_model // num_heads

        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)

    def forward(self, x, mask=None):
        batch_size, seq_len, d_model = x.shape

        # Project to Q, K, V
        Q = self.W_q(x)  # [batch, seq_len, d_model]
        K = self.W_k(x)
        V = self.W_v(x)

        # Reshape to multiple heads
        Q = Q.view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        K = K.view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        V = V.view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        # Now: [batch, num_heads, seq_len, d_k]

        # Attention per head
        attn_output, _ = scaled_dot_product_attention(Q, K, V, mask)

        # Concatenate heads
        attn_output = attn_output.transpose(1, 2).contiguous()
        attn_output = attn_output.view(batch_size, seq_len, d_model)

        # Final projection
        output = self.W_o(attn_output)
        return output
```

**为什么使用多个头？**
1. 不同的头会学习不同模式（语法、语义、指代）
2. 提供表示多样性（集成效果）
3. 支持在不同头之间并行计算

### 头数模式

| 模型 | d_model | 头数 | 每头 d_k |
|-------|---------|-------|--------------|
| BERT-base | 768 | 12 | 64 |
| GPT-2 | 768 | 12 | 64 |
| GPT-3 175B | 12288 | 96 | 128 |
| Llama 2 70B | 8192 | 64 | 128 |

不同模型规模中，每头的 d_k 为 64 或 128 的情况非常稳定。

---

## 注意力模式

### Attention 学到了什么

不同的头会专门学习不同模式：

| 模式类型 | 捕获的内容 | 示例 |
|--------------|------------------|---------|
| 位置模式 | 相邻 token | 下一个/上一个词 |
| 句法模式 | 语法关系 | 主谓关系 |
| 语义模式 | 含义关系 | 指代消解 |
| 分隔符模式 | 标点、结构 | 章节边界 |
| 罕见模式 | 不常见模式 | 复制罕见词 |

### 可视化 Attention

可以把 Attention 权重可视化为热力图，展示哪些位置关注了哪些位置：

```
Query positions (rows) vs Key positions (columns)

"The cat sat on the mat"

         The  cat  sat  on   the  mat
The     [□    ○    ○    ○    ○    ○ ]
cat     [●    □    ○    ○    ○    ○ ]
sat     [○    ●    □    ○    ○    ○ ]
on      [○    ○    ●    □    ○    ○ ]
the     [○    ○    ○    ○    □    ○ ]
mat     [○    ●    ○    ●    ●    □ ]

● = high attention, ○ = low attention
```

“mat” 强烈关注 “cat”（语义关系）、“on”（句法关系）和 “the”（限定词）。

---

## 高效注意力变体

标准 Attention 的序列长度复杂度是 O(n²)。许多变体会降低这一复杂度：

### 稀疏注意力

只关注部分位置，而不是所有位置：

| 变体 | 模式 | 复杂度 | 示例 |
|---------|---------|------------|---------|
| 局部 | 每个位置周围的窗口 | O(n * w) | Longformer |
| 步进 | 每第 k 个位置 | O(n² / k) | Sparse Transformer |
| 全局 | 特殊 token 关注所有位置 | O(n * g) | Longformer、BigBird |
| Block | 块对角注意力 | O(n * b) | BigBird |

**Longformer 模式：**
```
Local window + Global tokens

[G] [L] [L] [L] [L] [G] [L] [L] [L] [L]

G: Global tokens (attend to/from all)
L: Local tokens (attend within window)
```

### 线性注意力

用可线性化的替代形式替换 Softmax：

```python
# Standard attention (quadratic)
attention = softmax(Q @ K.T) @ V

# Linear attention approximation
attention = (Q @ (K.T @ V))  # Associativity trick
```

**变体：**
- Performer：随机特征近似
- Linear Transformer：elu(Q) @ (elu(K).T @ V)

**权衡：**速度更快，但质量会下降，尤其是在需要精确 Attention 的任务上。

### 复杂度对比

| 方法 | 时间 | 空间 | 质量 | 说明 |
|--------|------|-------|---------|-------|
| 标准 | O(n²) | O(n²) | 最好 | 基准 |
| 稀疏（Longformer） | O(n) | O(n) | 接近最好 | 长文档 |
| 线性（Performer） | O(n) | O(n) | 有下降 | 超长文本 |
| Flash Attention | O(n²) | O(n) | 最好 | 兼得二者 |

---

## Flash Attention

Flash Attention 是当前先进的实现方式，在计算精确 Attention 的同时实现 O(n) 内存。

### 解决的问题

标准 Attention 需要物化 n × n 的注意力矩阵：
- 8K 上下文：每层每头 6,400 万个浮点数 = 256 MB
- 100K 上下文：每层每头 100 亿个浮点数 = 40 GB

这个内存需求限制了批大小和上下文长度。

### 工作方式

Flash Attention 使用分块和重计算，避免存储完整的注意力矩阵：

```
Standard: Q, K -> Attention Matrix (n x n) -> Output
Flash:    Q, K -> Tiles (block_size x block_size) -> Incremental Output
```

**关键思想：**
1. 在适合 SRAM 的块中处理 Attention
2. 从不在 HBM 中物化完整的注意力矩阵
3. 在反向传播中重计算 Attention（比从 HBM 加载更快）

### 性能影响

### FlashAttention-2（工作划分）
通过改进跨头和跨序列长度的并行性，针对 A100/H100 进行了优化。

### FlashAttention-3（FP8 与 H100 优化）
**当前 H100/B200 集群的标准：**
- **异步执行**：在 H100 上使用 TMA（Tensor Memory Accelerator）重叠 GEMM（矩阵乘法）和 Softmax 操作。
- **FP8 支持**：原生支持 FP8 精度，通过随机舍入保持注意力精度的同时，相比 FP16 将吞吐量翻倍。
- **加速**：长上下文 Prefill 相比 FlashAttention-2 快约 1.5–2.0 倍。

---

## 多头潜在注意力（MLA）

MLA 由 DeepSeek（V2/V3）引入，是极端 KV Cache 压力下 GQA 的现代替代方案。

MLA 不只是对头进行分组，而是在把 Key 和 Value 存入 Cache 前，先将它们压缩到**低维潜在空间**。

```
Query (Up-projected) ────────┐
                             ▼
Key, Value (Down-projected) ─▶ [Low-dim Latent Cache] ─▶ [Output]
                             ▲
                             └─ Projection Matrices
```

| 指标 | MHA | GQA | MLA（2025 年 12 月） |
|--------|-----|-----|----------------|
| KV Cache 大小 | 100% | 12.5% | **约 5%** |
| 质量 | 基准 | 接近基准 | **优于 GQA** |
| 延迟 | 基准 | 更快 | **最快（减少 IO）** |

**MLA 为什么更有优势**：它使用“解耦旋转位置编码”，允许压缩后的潜在 KV 在不解码的情况下复用，在长上下文生成中节省大量内存带宽。

---

## KV Cache 优化与上下文缓存

### 上下文缓存（系统级）
API 提供商（OpenAI、Gemini、Anthropic）现在都提供**上下文缓存**。
- **工作方式**：预先计算并存储长“前缀”（例如一本 100K token 的法律书籍）的 KV 张量。
- **收益**：对于重复前缀，TTFT（首 token 时间）可降低 90%，成本可降低 50–90%。

### 滑动窗口注意力（SWA）
Mistral/Gemma 模型使用 SWA，把注意力深度限制在固定窗口（例如 4096 token），避免 KV Cache 无限增长。

### 多查询注意力（MQA）

让所有 Query 头共享一组 K 和 V：

```python
# Standard MHA
Q: [batch, num_heads, seq, d_k]  # 32 heads
K: [batch, num_heads, seq, d_k]  # 32 separate K
V: [batch, num_heads, seq, d_k]  # 32 separate V

# MQA
Q: [batch, num_heads, seq, d_k]  # 32 heads
K: [batch, 1, seq, d_k]          # 1 shared K
V: [batch, 1, seq, d_k]          # 1 shared V
```

**效果：**KV Cache 大小减少 32 倍，但质量会有一定损失。

### 分组查询注意力（GQA）

让多组 Query 头共享 K 和 V：

```python
# GQA with 8 KV heads for 64 query heads (8:1 ratio)
Q: [batch, 64, seq, d_k]  # 64 query heads
K: [batch, 8, seq, d_k]   # 8 KV heads
V: [batch, 8, seq, d_k]   # 8 KV heads

# Each KV head serves 8 query heads
```

**效果：**KV Cache 减少 8 倍，同时质量损失很小。

**使用 GQA 的模型：**
- Llama 2 70B：64 个 Query 头对应 8 个 KV 头
- Mistral 7B：32 个 Query 头对应 8 个 KV 头
- Gemma：多种配置

### 对比

| 注意力 | KV Cache | 质量 | 模型 |
|-----------|----------|---------|--------|
| MHA | 完整 | 最好 | GPT-3 |
| GQA | 通常为 1/8 | 接近最好 | Llama 2、Mistral |
| MQA | 1/n_heads | 有下降 | PaLM、Falcon |

---

## 实际影响

### 对系统设计的影响

1. **批大小与上下文的权衡：**
   - GPU 总内存 = 模型 + KV Cache × batch_size
   - 上下文越长，批大小越小
   - GQA 模型可以服务更多并发请求

2. **延迟预算分配：**
   - Attention 计算复杂度是 O(n²)，使用 Flash 后内存复杂度为 O(n)
   - Prefill（处理 Prompt）随 Prompt 长度扩展
   - Decode（生成）随生成长度 + Prompt 长度扩展

3. **内存带宽瓶颈：**
   - 生成过程通常受内存限制
   - 每个 token 都要加载 KV Cache，这通常是主要开销
   - 更大的批可以摊薄这部分成本

### Prefill 与 Decode

| 阶段 | 计算模式 | 瓶颈 |
|-------|-----------------|------------|
| Prefill | 处理所有输入 token | 计算（GPU 核心） |
| Decode | 一次生成一个 token | 内存（带宽） |

这就是为什么 TTFT（首 token 时间）和 TPS（每秒 token 数）要分别测量。

### 上下文长度扩展

| 上下文 | Attention 计算量 | KV Cache（Llama 70B） |
|---------|-------------------|---------------------|
| 4K | 基准 | 10.7 GB |
| 8K | 4 倍 | 21.5 GB |
| 32K | 64 倍 | 86 GB |
| 128K | 1024 倍 | 344 GB |

长上下文需要：
- Flash Attention（节省内存）
- GQA 或 MQA（减小 KV Cache）
- 必要时使用模型并行

---

## 面试问答

### 问：解释 Attention 机制，以及为什么它的复杂度呈二次增长。

**强回答：**
Attention 计算所有位置之间的两两交互。对于 n 个位置：

1. Q @ K^T 生成 n × n 的分数矩阵
2. 每个注意力分数都是一个 Query 与 Key 的点积
3. 总计需要 n² 次点积

这使复杂度关于序列长度呈二次增长。8K token 每层每头有 6,400 万个成对分数，128K token 则有 160 亿个。

二次增长限制了上下文长度。解决方案包括：
- Flash Attention：计算仍为 O(n²)，但内存为 O(n)
- 稀疏 Attention：只关注子集，复杂度为 O(n)
- 线性 Attention：O(n) 的近似方法

### 问：什么是 KV Cache？为什么它对服务至关重要？

**强回答：**
自回归生成时，我们一次生成一个 token。如果没有缓存，每个新 token 都要重新计算之前所有位置的 K 和 V。

KV Cache 保存之前位置的 K、V 张量。每生成一个新 token：
1. 只为新位置计算 Q、K、V
2. 把新的 K、V 追加到 Cache
3. 对完整的 KV Cache 做 Attention

这会把投影计算的单 token 复杂度从 O(n) 降到 O(1)。

代价是内存：KV Cache 随序列长度线性增长。以 8K 上下文的 Llama 70B 为例，每个请求约需 21 GB。这会直接限制批大小和吞吐量。

GQA 和 MQA 通过让多个 Query 头共享 K、V 来降低这一开销。

### 问：比较 MHA、GQA 和 MQA。

**强回答：**
| 变体 | K、V 头数 | KV Cache | 质量 | 使用场景 |
|---------|-----------|----------|---------|----------|
| MHA | 与 Q 头相同 | 完整 | 最好 | 训练、质量关键场景 |
| GQA | 少于 Q 头 | 减少 | 接近 MHA | 生产服务 |
| MQA | 1 | 最小 | 有下降 | 内存受限 |

MHA：每个 Query 头都有独立的 K 和 V，质量最好，但 KV Cache 最大。

GQA：多组 Query 头共享 K 和 V。Llama 2 使用 64 个 Query 头和 8 个 KV 头（8:1），缓存缩小 8 倍而质量损失很小。

MQA：所有 Query 头共享一组 K 和 V，内存节省最大，但质量下降可以被测量出来。PaLM 使用这一方案。

对于服务，GQA 是最好的折中。它可以在质量几乎与 MHA 相同的情况下支持更大的批大小（更高吞吐）。

### 问：Flash Attention 如何实现 O(n) 内存？

**强回答：**
标准 Attention 会把完整的 n × n 注意力矩阵物化到 GPU 内存。Flash Attention 通过以下方式避免这一点：

1. **分块（Tiling）**：处理适合片上 SRAM 的 Q、K 块
2. **在线 Softmax**：增量计算 Softmax，不存储所有分数
3. **重计算（Recomputation）**：反向传播时重新计算 Attention，而不是加载保存的值

关键洞察是：GPU SRAM（每个 SM 20 MB）比 HBM（80 GB）快 10 倍。让更多算术在 SRAM 中完成、减少 HBM 读写后，Flash Attention 既更快又更省内存。

最终得到的是精确 Attention（而非近似），使用 O(n) 内存，速度提升 2–4 倍。

---

## 参考资料

- Vaswani 等：《Attention Is All You Need》（2017）
- Dao 等：《FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness》（2022）
- Dao：《FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning》（2023）
- Beltagy 等：《Longformer: The Long-Document Transformer》（2020）
- Ainslie 等：《GQA: Training Generalized Multi-Query Transformer Models》（2023）
- Shazeer：《Fast Transformer Decoding: One Write-Head is All You Need》（MQA，2019）
- [Flash Attention 仓库](https://github.com/Dao-AILab/flash-attention)

---

*上一篇：[Tokenization 深入理解](02-tokenization-deep-dive.md) | 下一篇：[Transformer 架构](04-transformer-architecture.md)*
