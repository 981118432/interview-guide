# 推理基础

推理是从训练好的模型生成预测的过程。为了应对 Hopper（H100）和 Blackwell（B200）级硬件上的重推理工作负载，推理优化已经从“简单提速”转向“架构效率”。

## 目录

- [推理的两个阶段](#two-phases)
- [瓶颈：计算受限与内存受限](#bottlenecks)
- [性能指标：TTFT 与 TPOT](#metrics)
- [硬件支持的优化（FP8）](#hardware-optimizations)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## 推理的两个阶段

LLM 推理不是单一操作，而是由两个不同的计算阶段组成。

### 1. Prefill 阶段（Prompt 处理）

模型在一次前向过程中处理完整的输入 Prompt。
- **计算**：高并行度的矩阵乘法。
- **瓶颈**：**计算受限**（受 GPU TFLOPS 限制）。
- **时间复杂度**：$O(N)$，其中 $N$ 是输入长度（但会被并行化）。

### 2. Decode 阶段（Token 生成）

模型逐个生成 Token，每个 Token 都依赖前一个 Token。
- **计算**：顺序处理，每次处理权重矩阵的一行。
- **瓶颈**：**内存受限**（受内存带宽限制）。
- **时间复杂度**：$O(M)$，其中 $M$ 是输出长度（顺序执行）。

---

## 瓶颈：计算受限与内存受限

理解系统的瓶颈在哪里，对于选择正确的优化方式至关重要。

| 阶段 | 瓶颈 | 原因 | 主要优化 |
|------|------|------|----------|
| **Prefill** | 计算（FLOPs） | 并行处理会让 GPU 的算术单元达到饱和。 | FlashAttention、FP8/FP16 精度。 |
| **Decode** | 内存带宽 | **每生成一个 Token** 都必须从 VRAM 加载权重。 | 量化（4-bit）、GQA、批处理。 |

**内存墙的启示**

随着模型变大，内存带宽（HBM3/HBM3e）的增长没有计算能力（TFLOPS）那么快。因此，Decode 阶段成为生产环境优化的主要目标。

---

## 性能指标

| 指标 | 全称 | 目标 | 重要性 |
|------|------|------|--------|
| **TTFT** | Time To First Token（首 Token 时间） | < 200ms | 用户感知的响应速度。 |
| **TPOT** | Time Per Output Token（每个输出 Token 的时间） | < 30ms | 阅读速度和对话流畅度。 |
| **吞吐量** | Tokens/Second（聚合） | 最大化 | 决定每次查询的成本。 |
| **延迟** | 端到端时间 | < 2.0s | Agent 一轮交互的总往返时间。 |

---

## 硬件支持的优化（FP8）

**FP8（8 位浮点数）**是 H100 和 B200 GPU 上用于推理的原生精度。

- **收益**：相比 FP16/BF16 快 2 倍，同时精度损失可以忽略（<0.1%）。
- **工作方式**：它使用更小的尾数和更大的指数，相比 Int8 能更准确地表示 LLM 激活值的动态范围，无需复杂的校准。

**Principal-level 细节**：当前的服务框架已经使用**动态 FP8 缩放**，按层调整量化 scale，避免离群值影响整个模型的逻辑。

---

## 面试问题

### Q：为什么 LLM 生成比分类更慢？

**强回答：**

分类是“仅 Prefill”的任务：它处理完整输入，并在一次并行前向过程中产生单个输出，因此计算效率高。而 LLM 生成是**自回归**的，每个 Token 都依赖前一个 Token，必须执行顺序的“Decode”循环。由于循环中的每一步都受内存限制（加载数 GB 的权重，却只生成毫克级的数据），系统大部分时间都在等待内存传输，而不是进行数学计算。

### Q：如何分别优化 TTFT 和 TPOT？

**强回答：**

要优化 **TTFT**，就必须优化 Prefill 阶段：使用 FlashAttention-3、提高计算并行度（Tensor Parallelism），或者对常见 Prompt 使用 Prefix Caching，完全跳过 Prefill。

要优化 **TPOT**，就必须优化 Decode 阶段的内存带宽：使用量化（4-bit 权重）减少从 VRAM 移动的数据量，使用分组查询注意力（GQA）减小 KV Cache，或者使用推测解码，让每次内存加载生成多个 Token。

---

## 参考资料

- Pope 等，《Efficiently Scaling Transformer Inference》（2022）
- NVIDIA，《Transformer Engine Documentation》（2024）
- vLLM Blog，《Understanding LLM Inference Latency》（2023）

---

*下一篇：[KV Cache 与上下文缓存](02-kv-cache-and-context-caching.md)*
