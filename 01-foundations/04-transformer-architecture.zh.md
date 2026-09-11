# Transformer 架构

本章从整体上介绍完整的 Transformer 架构，把前面各章的组件整合起来，形成统一理解。

## 目录

- [架构概览](#架构概览)
- [输入处理](#输入处理)
- [Transformer Block](#transformer-block)
- [输出处理](#输出处理)
- [现代架构变体（混合 MoE、MLA）](#专家混合moe与混合架构)
- [非绑定 Embedding 与绑定 Embedding](#非绑定-embedding-与绑定-embedding)
- [扩展特性](#扩展特性)
- [架构对比表](#架构对比表)
- [面试问答](#面试问答)
- [参考资料](#参考资料)

---

## 架构概览

仅解码器 Transformer（GPT、Claude、Llama 使用的架构）由以下部分组成：

```
┌─────────────────────────────────────────────────────────────────┐
│                     Token Embeddings                            │
│              + Position Embeddings (or RoPE)                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│    ┌─────────────────────────────────────────────────────┐      │
│    │                  Transformer Block                   │      │
│    │  ┌─────────────────────────────────────────────┐    │      │
│    │  │              RMSNorm/LayerNorm              │    │      │
│    │  └───────────────────┬─────────────────────────┘    │      │
│    │                      ▼                              │      │
│    │  ┌─────────────────────────────────────────────┐    │      │
│    │  │         Masked Multi-Head Attention         │    │      │
│    │  │            (with KV Cache)                  │    │      │
│    │  └───────────────────┬─────────────────────────┘    │      │
│    │                      │                              │      │
│    │                  + Residual                         │      │
│    │                      │                              │      │
│    │  ┌─────────────────────────────────────────────┐    │      │
│    │  │              RMSNorm/LayerNorm              │    │      │
│    │  └───────────────────┬─────────────────────────┘    │      │
│    │                      ▼                              │      │
│    │  ┌─────────────────────────────────────────────┐    │      │
│    │  │             Feed-Forward Network            │    │      │
│    │  │               (SwiGLU/GELU)                 │    │      │
│    │  └───────────────────┬─────────────────────────┘    │      │
│    │                      │                              │      │
│    │                  + Residual                         │      │
│    └──────────────────────┴──────────────────────────────┘      │
│                           │                                     │
│                    Repeat × N layers                            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Output RMSNorm                             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Language Model Head                           │
│              (Linear: hidden_dim → vocab_size)                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
                         Logits
```

---

## 输入处理

### Token Embedding

把 token ID 转换为稠密向量：

```python
class TokenEmbedding(nn.Module):
    def __init__(self, vocab_size, d_model):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)

    def forward(self, token_ids):
        return self.embedding(token_ids)
```

**维度：**
- 输入：[batch_size, seq_len] token ID
- 输出：[batch_size, seq_len, d_model] Embedding

### 位置信息

位置信息可以通过以下方式加入：

**1. 旋转位置编码（RoPE）：**
在 Attention 内应用，而不是加到 Embedding 上：
```python
def apply_rope(q, k, positions):
    # Rotate q and k vectors based on position
    freqs = compute_frequencies(positions)
    q_rotated = rotate_embeddings(q, freqs)
    k_rotated = rotate_embeddings(k, freqs)
    return q_rotated, k_rotated
```

**2. 可学习的位置 Embedding：**
直接加到 token Embedding 上：
```python
position_embeddings = nn.Embedding(max_seq_len, d_model)
x = token_embeddings + position_embeddings(positions)
```

**现代模型（Llama、Mistral、GPT-4）使用 RoPE**，以获得更好的长度泛化能力。

---

## Transformer Block

### Pre-Norm 结构

现代 Transformer 使用前置归一化：

```python
class TransformerBlock(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.attn_norm = RMSNorm(config.d_model)
        self.attn = GroupedQueryAttention(
            d_model=config.d_model,
            n_heads=config.n_heads,
            n_kv_heads=config.n_kv_heads
        )
        self.ff_norm = RMSNorm(config.d_model)
        self.ff = SwiGLUFFN(
            d_model=config.d_model,
            d_ff=config.d_ff
        )

    def forward(self, x, mask=None, kv_cache=None):
        # Attention with residual
        h = x + self.attn(self.attn_norm(x), mask, kv_cache)

        # FFN with residual
        out = h + self.ff(self.ff_norm(h))

        return out
```

### Attention 组件

```python
class GroupedQueryAttention(nn.Module):
    def __init__(self, d_model, n_heads, n_kv_heads):
        super().__init__()
        self.n_heads = n_heads
        self.n_kv_heads = n_kv_heads
        self.head_dim = d_model // n_heads

        self.q_proj = nn.Linear(d_model, n_heads * self.head_dim)
        self.k_proj = nn.Linear(d_model, n_kv_heads * self.head_dim)
        self.v_proj = nn.Linear(d_model, n_kv_heads * self.head_dim)
        self.o_proj = nn.Linear(n_heads * self.head_dim, d_model)

    def forward(self, x, mask, kv_cache):
        B, T, D = x.shape

        # Project
        q = self.q_proj(x).view(B, T, self.n_heads, self.head_dim)
        k = self.k_proj(x).view(B, T, self.n_kv_heads, self.head_dim)
        v = self.v_proj(x).view(B, T, self.n_kv_heads, self.head_dim)

        # Apply RoPE
        q, k = apply_rope(q, k, positions)

        # Update KV cache
        if kv_cache is not None:
            k = torch.cat([kv_cache.k, k], dim=1)
            v = torch.cat([kv_cache.v, v], dim=1)
            kv_cache.update(k, v)

        # Repeat KV heads for GQA
        k = k.repeat_interleave(self.n_heads // self.n_kv_heads, dim=2)
        v = v.repeat_interleave(self.n_heads // self.n_kv_heads, dim=2)

        # Attention (using Flash Attention in practice)
        attn_out = flash_attention(q, k, v, mask)

        # Output projection
        out = self.o_proj(attn_out.view(B, T, -1))
        return out
```

### 前馈网络

```python
class SwiGLUFFN(nn.Module):
    def __init__(self, d_model, d_ff):
        super().__init__()
        # SwiGLU has 3 projections instead of 2
        self.gate_proj = nn.Linear(d_model, d_ff, bias=False)
        self.up_proj = nn.Linear(d_model, d_ff, bias=False)
        self.down_proj = nn.Linear(d_ff, d_model, bias=False)

    def forward(self, x):
        gate = F.silu(self.gate_proj(x))  # SiLU = Swish
        up = self.up_proj(x)
        return self.down_proj(gate * up)
```

对于 SwiGLU，FFN 隐藏维度通常是模型维度的 2.7 倍（标准 GELU FFN 通常为 4 倍）。

### RMSNorm

```python
class RMSNorm(nn.Module):
    def __init__(self, d_model, eps=1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(d_model))
        self.eps = eps

    def forward(self, x):
        rms = torch.sqrt(torch.mean(x ** 2, dim=-1, keepdim=True) + self.eps)
        return self.weight * (x / rms)
```

由于跳过了均值中心化，它比 LayerNorm 更简单、更快。

---

## 输出处理

### 最终归一化

在最后一个 Transformer Block 之后应用 RMSNorm：

```python
hidden_states = self.output_norm(hidden_states)
```

### 语言模型头

投影到词表大小：

```python
class LMHead(nn.Module):
    def __init__(self, d_model, vocab_size):
        super().__init__()
        self.linear = nn.Linear(d_model, vocab_size, bias=False)

    def forward(self, x):
        return self.linear(x)  # Returns logits
```

## 非绑定 Embedding 与绑定 Embedding

**标准模式（GPT-3、Llama 2）：**权重绑定
- 输出头与输入 Embedding 共享权重。
- **优点**：节省内存（vocab_size × hidden_dim）。
- **缺点**：强制输入和输出潜在空间相同，可能不是最优方案。

**2025 年前沿模式（Llama 3/4、GPT-5.2）：**非绑定 Embedding
- 输出头拥有自己的权重。
- **为什么？**：更大的词表（128K+）使 Embedding 表占据模型中相当大的比例。解耦后，输出头可以专门学习“预测逻辑”，输入 Embedding 则专注于“语义理解”。
- **系统影响**：参数量增加，但通常能改善多语言和代码任务的困惑度。

### 获取预测结果

```python
# During generation
logits = lm_head(hidden_states[:, -1, :])  # Last position only
next_token = sample(logits)

# During training
logits = lm_head(hidden_states)  # All positions
loss = cross_entropy(logits, targets)
```

---

## 现代架构变体

### Llama 2/3 架构

| 组件 | 实现 |
|-----------|----------------|
| Attention | 分组查询注意力（GQA） |
| 位置 | 旋转位置编码（RoPE） |
| 归一化 | RMSNorm（Pre-Norm） |
| 激活函数 | SwiGLU |
| 偏置 | 线性层无偏置 |

### Mistral 架构

与 Llama 相同，但增加了：
- **滑动窗口注意力**：每层只关注 4K 个 token
- 通过层叠仍然实现有效的 32K+ 上下文

### 专家混合（MoE）与混合架构

先进模型通常采用**混合 MoE/稠密 Block**：
- **周期性稠密层**：每隔几个 MoE 层加入一个稠密层，确保“全局”知识在所有专家之间共享。
- **专家并行**：把不同专家分布到不同 GPU 上。这使**节点间带宽**（NVLink/InfiniBand）成为主要架构瓶颈。

### 多头潜在注意力（MLA）集成
[DeepSeek-V3 / V4](03-attention-mechanisms.md#multi-head-latent-attention-mla) 以及同类现代架构中的标准 Attention Block，会用低秩潜在压缩替代标准 Q/K/V 投影。
- **架构转变**：KV Cache 现在是压缩的潜在表示，这改变了整个 Transformer Block 的内存/计算比例。

### 方案对比

| 选择 | 旧方案 | 现代方案 | 优势 |
|--------|--------------|-----------------|---------|
| 归一化 | Post-LN | Pre-LN / RMSNorm | 训练稳定、速度快 |
| 位置 | 正弦/可学习 | RoPE | 外推能力更好 |
| 激活函数 | GELU | SwiGLU | 质量提升（基准约 +1%） |
| Attention | MHA | GQA | KV Cache 缩小 8 倍 |
| 偏置 | 有偏置 | 无偏置 | 参数更少，质量相近 |

---

## 扩展特性

### 参数量

| 组件 | 参数量 |
|-----------|------------|
| Token Embedding | vocab_size * d_model |
| 每层 Q/K/V | 3 * d_model * d_model（MHA） |
| 每层 O 投影 | d_model * d_model |
| 每层 FFN | 3 * d_model * d_ff（SwiGLU） |
| LM Head | d_model * vocab_size（通常绑定） |

**仅解码器模型的近似：**
```
Total ≈ 12 * n_layers * d_model^2 (for d_ff = 4 * d_model, MHA)
```

### 计算需求

**训练：**每个 token 的 FLOPs ≈ 6 × 参数量（前向 + 反向）

**推理：**每个 token 的 FLOPs ≈ 2 × 参数量（仅前向）

### 扩展定律

Chinchilla 扩展定律建议这样分配资源：

```
D (data tokens) ≈ 20 * N (parameters)
```

对于 70B 模型，计算最优的训练量约为 1.4T token。

**但是：**许多现代模型为了提升推理效率，相对于 Chinchilla 会进行过度训练。Llama 的训练量超过了 2T token。

---

## 架构对比表

| 模型 | 参数量 | 层数 | d_model | 头数 | KV 头数 | FFN | 上下文 |
|-------|--------|--------|---------|-------|----------|-----|---------|
| GPT-3 | 175B | 96 | 12288 | 96 | 96 | GELU | 2K |
| Llama 2 70B | 70B | 80 | 8192 | 64 | 8 | SwiGLU | 4K |
| Llama 3 405B| 405B | 126 | 16384 | 128 | 16 | SwiGLU | 128K |
| DeepSeek V3 | 671B | 128 | 7168 | 128 | MLA | MoE | 128K |
| Llama 4（规格）| 1T+ | 140+ | 18432 | 192 | 24 | MoE/H | 1M+ |

*Mistral 使用滑动窗口注意力来实现有效的长上下文。*

---

## 面试问答

### 问：请完整讲一下 Transformer 的前向过程。

**强回答：**
对于生成文本的仅解码器模型：

1. **Tokenization**：把输入文本转换成 token ID

2. **Embedding**：从 Embedding 表中查找 token Embedding

3. **逐层经过 Transformer：**
   - 对输入应用 RMSNorm
   - 计算 Q、K、V 投影
   - 对 Q、K 应用 RoPE，加入位置信息
   - 生成时把新的 K、V 追加到 KV Cache
   - 计算 Attention（带掩码，因此每个位置只能看到之前的位置）
   - 投影 Attention 输出并加上残差
   - 应用 RMSNorm
   - 经过 SwiGLU 前馈网络
   - 加上残差

4. **输出归一化**：应用最终 RMSNorm

5. **LM Head**：投影到词表大小，得到 logits

6. **采样**：使用 temperature/top-p 从 logits 选择下一个 token

生成时，对于每个新 token 重复步骤 3–6，并复用前面位置的 KV Cache。

### 问：Pre-Norm 和 Post-Norm 有什么区别？

**强回答：**
区别在于相对于子层（Attention、FFN），LayerNorm 放置的位置不同：

**Post-Norm（原始 Transformer）：**
```
x = LayerNorm(x + Sublayer(x))
```
在加残差之后归一化。

**Pre-Norm（现代 Transformer）：**
```
x = x + Sublayer(LayerNorm(x))
```
在子层之前归一化。

之所以更偏好 Pre-Norm，是因为：
1. 梯度可以更直接地通过残差连接
2. 训练更稳定，尤其适用于深层模型
3. 对初始化和学习率不那么敏感
4. 不需要学习率预热

代价是在部分基准上最终性能略低，但对大模型来说，训练稳定性值得这项代价。

### 问：解释 GQA，以及它为什么对服务很重要。

**强回答：**
分组查询注意力（GQA）让多组 Query 头共享 Key 和 Value 头。

标准多头注意力：64 个 Query 头、64 个 KV 头（1:1）
GQA：64 个 Query 头、8 个 KV 头（8:1）

实现上，每个 KV 头通过复制供 8 个 Query 头使用。

**为什么重要：**
KV Cache 会在生成期间保存所有位置的 K、V。以 8K 上下文的 Llama 70B 为例：
- MHA：2.6 MB/token × 8K = 每个请求 21 GB
- GQA（8:1）：每个请求约 2.6 GB

缩小 8 倍后可以：
- 支持更大的批大小（更多并发用户）
- 支持更长上下文
- 降低 GPU 内存需求

质量影响很小。研究表明，GQA 可以达到 MHA 质量的 99% 以上。

### 问：GPT-2 和 Llama 2 之间发生了哪些变化？

**强回答：**
关键架构改进如下：

| 组件 | GPT-2 | Llama 2 |
|-----------|-------|---------|
| 归一化 | Post-LayerNorm | Pre-RMSNorm |
| 位置 | 可学习绝对位置 | RoPE（旋转位置） |
| 激活函数 | GELU | SwiGLU |
| Attention | MHA | GQA（70B） |
| 偏置 | 有 | 移除 |

影响：
- RMSNorm：速度更快，效果相当
- RoPE：长度外推更好
- SwiGLU：质量提升约 1%
- GQA：服务时 KV Cache 缩小 8 倍
- 无偏置：参数更少，质量不受损

这些变化让更大模型的训练更稳定，也让服务效率更高。

---

## 参考资料

- Vaswani 等：《Attention Is All You Need》（2017）
- Touvron 等：《Llama: Open and Efficient Foundation Language Models》（2023）
- Touvron 等：《Llama 2: Open Foundation and Fine-Tuned Chat Models》（2023）
- Zhang、Sennrich：《Root Mean Square Layer Normalization》（2019）
- Shazeer：《GLU Variants Improve Transformer》（2020）
- Su 等：《RoFormer: Enhanced Transformer with Rotary Position Embedding》（2021）
- Jiang 等：《Mistral 7B》（2023）

---

*上一篇：[Attention 机制](03-attention-mechanisms.md) | 下一篇：[Embedding 与向量空间](05-embeddings-and-vector-spaces.md)*
