# LoRA、QLoRA 与 PEFT

参数高效微调（PEFT）已经成为适配大语言模型的行业标准。本章介绍 LoRA 的工作机制、QLoRA，以及其他常用的 PEFT 方法和生产部署方式。

## PEFT 的变化

对 GPT-5.5、Claude Opus 4.7、Llama 4 405B 等前沿模型做全参数微调，对大多数企业来说成本难以承受。PEFT 的价值主要体现在：

1. **节省显存：**可以在一张 A100 上训练 70B 模型。
2. **提高速度：**只更新不到 1% 的权重，训练速度可提高约 2 倍。
3. **模块化：**适配器可以挂载到共享基础模型上，不需要重新加载基础权重。

## LoRA 机制

LoRA（Low-Rank Adaptation）在 Transformer 层中注入可训练的低秩分解矩阵。

```python
# 权重矩阵 W 的 LoRA 公式
h = Wx + (BA)x * (alpha/r)
```

- **W：**预训练权重，冻结，不计算梯度。
- **A、B：**LoRA 适配器，可训练。
- **r：**秩，例如 8、16、64。
- **alpha：**缩放因子，通常设置为秩的 2 倍。

### 目标模块是关键细节

早期实践通常只对 query/value 投影（`q_proj`、`v_proj`）应用 LoRA。现代实践更常把所有线性层都作为目标模块：`q、k、v、o、gate、up、down`。即使使用较低的 rank，这种做法也通常能获得更好的稳定性和效果。

## QLoRA：4-bit 微调

QLoRA 进一步压缩成本：把基础模型量化为 4-bit（NF4），同时使用 16-bit 梯度训练 LoRA 适配器。

| 优化 | 方法 | 收益 |
|---|---|---|
| NF4 量化 | Normalized Float 4 | 比普通 Int4 保留更多信息 |
| 双重量化 | 对量化常数再次量化 | 每个模型约节省 0.5 GB 显存 |
| 分页优化器 | 使用 NVIDIA 统一内存 | 将部分状态溢出到 CPU，避免 OOM |

## 高级变体

### 1. DoRA

DoRA（Weight-Decomposed Low-Rank Adaptation）把权重更新分解成**幅度**和**方向**两部分。这样模型可以分别学习“改变多少”和“向哪里改变”，收敛速度和效果通常比标准 LoRA 更接近全参数微调。

### 2. Vera

Vera 使用固定的随机投影和一个很小的可训练向量，而不是 LoRA 的两个低秩矩阵。适配器大小可比 LoRA 再减少约 10 倍，适合大规模多适配器服务。

### 3. RS-LoRA

RS-LoRA 使用 `alpha / sqrt(r)` 作为缩放因子。它允许把 rank 提高到 256 甚至更高，同时降低训练不稳定或必须降低学习率的风险。

## Multi-LoRA 服务

生产系统可以只加载一个基础模型（例如 Llama 4 70B），在同一批请求中动态切换适配器：

```python
# vLLM/LMCache Multi-LoRA 模式
# 请求 1 -> 基础模型 + Finance_Adapter
# 请求 2 -> 基础模型 + Legal_Adapter
# 请求 3 -> 基础模型 + Medical_Adapter
```

连续批处理和 PagedAttention v3 可以支持 100 个以上的适配器，同时相对于只服务基础模型增加约 5%–10% 的延迟。

## 面试问题

### Q：为什么 LoRA 的 alpha 通常设置为 rank 的 2 倍？

**强回答：**alpha 是 LoRA 更新的缩放因子。LoRA 初始化时 B 通常为零、A 为随机值，训练过程中更新大小会受到 rank 影响。使用 `alpha=2r` 或其他固定比例，可以让改变 rank 时更新量保持在相近范围，减少重新调学习率的需要。真正起作用的是 `alpha/r`，它相对于学习率归一化了更新幅度。

### Q：DoRA 是什么？为什么使用它而不是标准 LoRA？

**强回答：**DoRA 是 2024 年提出的权重分解低秩适配方法。它把预训练权重更新拆成幅度和方向，类似 Weight Normalization。标准 LoRA 同时更新两者，而 DoRA 让两者独立学习，因此通常有更好的收敛和精度；在低 rank 下也可能接近全参数微调。

## 参考资料

- Hu 等，《LoRA: Low-Rank Adaptation of Large Language Models》（2021）
- Liu 等，《DoRA: Weight-Decomposed Low-Rank Adaptation》（2024）
- Dettmers 等，《QLoRA: Efficient Finetuning of Quantized LLMs》（2023）

*下一篇：[RLHF 与 DPO](04-rlhf-and-dpo.md)*
