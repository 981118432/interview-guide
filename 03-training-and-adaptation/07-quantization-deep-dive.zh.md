# 量化深入理解

量化是降低模型权重精度（例如从 16-bit 降到 4-bit）的过程，以节省内存并提高推理速度。这是在消费级硬件和单 GPU 硬件上部署大型模型的主要工具。

## 目录

- [精度与性能的权衡](#精度与性能)
- [量化方法（NF4、GPTQ、AWQ）](#量化方法)
- [GGUF 与 EXL2](#格式)
- [KV Cache 量化（显存节省器）](#kv-cache)
- [量化感知微调](#量化感知微调)
- [面试问题](#面试问题)
- [参考资料](#参考资料)

---

## 精度与性能的权衡

传统模型使用 **BF16**（16-bit）。量化希望将其降低为 **8-bit（FP8）**、**4-bit（Int4/NF4）**，甚至 **1.5-bit（BitNet）**。

| 精度 | 位数 | 权重大小（8B 模型） | 质量损失 | GPU 兼容性 |
|-----------|------|------------------------|--------------|-------------------|
| **BF16** | 16 | 16 GB | 0%（基线） | 所有现代 GPU |
| **FP8** | 8 | 8 GB | < 1% | H100 / B200 / RTX 4090 |
| **4-bit（NF4）** | 4 | 5 GB | 1–2% | 所有现代 GPU |
| **2-bit** | 2 | 2.5 GB | 10–15% | 研究 / 专用场景 |

---

## 量化方法

### 1. NF4（NormalFloat4）

微调（QLoRA）的黄金标准。它假设权重服从正态分布，并把它们映射到 16 个值的集合。

### 2. AWQ（Activation-aware Weight Quantization）

AWQ 不会对所有权重进行同等量化，而是识别对质量最重要的 **1% “显著”权重**，并让它们保持更高精度。
- **优点：**比 GPTQ 有更好的准确率。

### 3. FP8（多节点标准）

由 NVIDIA Transformer Engine 支持的硬件原生量化。
- **为什么有效：**它提供 Int8 的速度，同时拥有 Float16 的动态范围，因此对训练和推理都稳定。

---

## GGUF 与 EXL2

### GGUF（llama.cpp）

- **部署：**CPU + GPU offloading。
- **优点：**跨平台（Mac、Linux、Windows），单文件，高度便携。
- **缺点：**比纯 GPU 格式慢。

### EXL2（ExLlamaV2）

- **部署：**仅 GPU（NVIDIA）。
- **优点：**NVIDIA GPU 上**最快的 4-bit 格式**。比 AutoGPTQ/AWQ 有明显的性能提升。
- **缺点：**不灵活（仅 NVIDIA）。

---

## KV Cache 量化（显存节省器）

在长上下文 RAG（1M+ token）中，**KV Cache** 消耗的显存通常比模型权重本身还多。

- **BF16 KV Cache：**2M token ≈ 32GB 显存（8B 模型）。
- **FP8/Int4 KV Cache：**2M token ≈ 8GB–16GB 显存。

**细节：**现代服务框架（vLLM、SGLang、TensorRT-LLM）现在支持**流式量化（Streaming Quantization）**，KV Cache 会在运行中即时压缩，从而让同一 GPU 支持 4 倍并发。

---

## 量化感知训练（QAT）

模型训练完成后再量化叫作**训练后量化（Post-training Quantization）**；QAT 则在训练过程中模拟量化。
- **结果：**模型学会补偿损失的精度。
- **状态：**为了让参数小于 3B 的模型在 4-bit 下仍然有用，这是必需的。

---

## 面试问题

### Q：QLoRA 为什么使用 NF4，而不是标准 Float4？

**强回答：**
标准 Float4 有固定的网格，无法很好地映射到 LLM 权重的实际分布，而 LLM 权重通常服从以零为中心的正态分布。NF4（NormalFloat4）是一种经过数学优化的数据类型，使每个量化区间包含正态分布中数量相等的值。这能防止权重“聚集”，并确保模型尽可能保留信息（熵），因此精度明显高于标准 4-bit 整数。

### Q：AWQ 与 GPTQ 有什么区别？

**强回答：**
GPTQ 是一种“逐层”量化方法，用于最小化权重的均方误差。AWQ（Activation-aware Weight Quantization）是“输入感知”的：它根据小规模校准运行期间看到的实际激活值，识别哪些权重最“显著”。它只把这些重要权重（通常为 1%）保留在更高精度，对其余权重量化，因此尤其在更小模型或更激进的量化（例如 3-bit）下，能取得比 GPTQ 更好的困惑度。

---

## 参考资料

- Dettmers 等，《QLoRA: Efficient Finetuning of Quantized LLMs》（2023）
- Frantar 等，《GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers》（2022）
- Lin 等，《AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration》（2023）

---

*下一篇：[推理模型训练：RLVR 与 GRPO](08-rlvr-and-reasoning-models.md)*
