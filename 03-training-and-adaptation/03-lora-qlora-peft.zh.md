# LoRA、QLoRA 与 PEFT

参数高效微调（PEFT）是适配 LLM 的行业标准。本章介绍 LoRA 和其他 PEFT 方法的机制及高级变体。

## 目录

- [PEFT 的革命](#peft-的革命)
- [LoRA 机制](#lora-机制)
- [QLoRA：4-bit 微调](#qlora-4-bit-微调)
- [高级变体（DoRA、Vera、RS-LoRA）](#高级变体)
- [Multi-LoRA 服务（适配器）](#multi-lora-服务)
- [面试问题](#面试问题)
- [参考资料](#参考资料)

---

## PEFT 的革命

对前沿模型（GPT-5.5、Claude Opus 4.7、Llama 4 405B）做全量微调，对大多数企业来说在经济上不可行。PEFT 可以做到：
1. **显存效率：**在单张 A100 上训练 70B 模型。
2. **速度：**只更新不到 1% 的权重，训练速度提高 2 倍。
3. **模块化：**把“技能”（适配器）切换到共享基础模型上，而无需重新加载权重。

---

## LoRA 机制

LoRA（Low-Rank Adaptation）把可训练的秩分解矩阵注入 Transformer 层。

```python
# 权重矩阵 W 的 LoRA 公式：
h = Wx + (BA)x * (alpha/r)
```
- **W：**预训练权重（冻结，Gradient = None）。
- **A、B：**LoRA 适配器（可训练）。
- **r：**秩（例如 8、16、64）。
- **alpha：**缩放因子（通常为 2 * rank）。

### 关键细节：目标模块

过去我们只对 query/value 投影（`q_proj`、`v_proj`）做目标定位。
**现代标准：**为了获得最大稳定性和性能，对**所有**线性层做目标定位（`q, k, v, o, gate, up, down`），即使使用更低的秩也是如此。

---

## QLoRA：4-bit 微调

QLoRA 通过把基础模型量化为 4-bit（NF4），同时保持 16-bit 梯度，把效率进一步提升。

| 优化 | 方法 | 收益 |
|--------------|--------|---------|
| **NF4 量化** | Normalized Float 4 | 比标准 Int4 更高的信息密度 |
| **双重量化** | 量化量化常数 | 每个模型节省约 0.5 GB 显存 |
| **分页** | 统一内存（Nvidia） | 溢出到 CPU RAM，避免 OOM |

---

## 高级变体

### 1. DoRA（Weight-Decomposed Low-Rank Adaptation）

DoRA 把权重更新分解成**幅度**和**方向**。
- **结果：**训练速度比 LoRA 快 2 倍，并且效果更接近全量微调。
- **为什么有效：**它让模型可以独立调整改变多少，以及改变什么。

### 2. Vera（Vector-based Random Aggregation）

Vera 使用固定的随机投影和一个很小的可训练向量，而不是低秩矩阵 `A`、`B`。
- **效率：**与 LoRA 相比，适配器大小减少 **10 倍**。
- **使用场景：**大规模 Multi-LoRA 服务。

### 3. RS-LoRA（Rank-Stabilized LoRA）

使用 `alpha / sqrt(r)` 作为缩放因子。
- **收益：**可以把秩提高到 256 以上，而不会让模型变得不稳定，也不需要更低的学习率。

---

## Multi-LoRA 服务（适配器）

生产系统现在可以服务一个基础模型（例如 Llama 4 70B），并在同一批次中动态切换适配器。

```python
# vLLM/LMCache Multi-LoRA 模式：
# 请求 1 -> 基础模型 + Finance_Adapter
# 请求 2 -> 基础模型 + Legal_Adapter
# 请求 3 -> 基础模型 + Medical_Adapter
```
**技术：****连续批处理 + PagedAttention v3** 允许服务 100 个以上的适配器；相对于基础模型，延迟开销只有 5–10%。

---

## 面试问题

### Q：为什么 LoRA 的 alpha 参数通常设置为秩的 2 倍？

**强回答：**
`alpha` 是 LoRA 更新的缩放因子。初始化 LoRA 矩阵时，B 通常初始化为零，A 为随机值。训练时，更新大小取决于秩 `r`。设置 `alpha=2r`（或任意常数）可以保证之后改变秩（例如从 8 改为 16）时不需要重新调学习率。缩放因子 `alpha/r` 会相对于学习率归一化更新幅度。

### Q：DoRA 是什么？为什么会选择它而不是标准 LoRA？

**强回答：**
DoRA（Weight-Decomposed Low-Rank Adaptation）是 2024 年提出的技术，把预训练权重更新分成幅度和方向两部分，类似 Weight Normalization。标准 LoRA 同时更新幅度和方向，而 DoRA 允许二者独立学习。经验上，DoRA 收敛更好、准确率更高，甚至在低秩下也常常能匹配全参数微调，因此适合高风险领域适配。

---

## 参考资料

- Hu 等，《LoRA: Low-Rank Adaptation of Large Language Models》（2021）
- Liu 等，《DoRA: Weight-Decomposed Low-Rank Adaptation》（2024）
- Dettmers 等，《QLoRA: Efficient Finetuning of Quantized LLMs》（2023）

---

*下一篇：[RLHF 与 DPO](04-rlhf-and-dpo.md)*
