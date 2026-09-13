# 批处理策略

批处理是提升 LLM 吞吐量、降低成本的主要杠杆。服务框架已经从简单的请求级批处理，发展到 Token 子级、迭代级的调度编排。

## 目录

- [静态批处理与动态批处理](#static-vs-dynamic)
- [连续批处理](#continuous-batching)
- [In-Flight Batching（Prefill-Decode 融合）](#in-flight-batching)
- [分块 Prefill 与 RAD-O](#chunked-prefill)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## 静态批处理与动态批处理

在传统机器学习（分类）中，我们使用**静态批处理**，要求所有请求大小相同，并且一起开始、一起结束。由于 LLM 的响应长度不同，这种方式效率很低。

---

## 连续批处理（迭代级）

连续批处理（由 Orca 和 vLLM 首创）允许新请求加入批次，已完成的请求在每一个独立的 Token 生成步骤结束时离开批次。

| 方面 | 静态批处理 | 连续批处理 |
|------|------------|------------|
| **加入/离开** | 仅在开始/结束时 | 任意迭代 |
| **GPU 利用率** | 低（等待最长请求） | 高（始终接近饱和） |
| **吞吐量** | 1 倍 | **4～10 倍** |
| **延迟** | 对短请求最高 | 更均衡 |

---

## In-Flight Batching（Prefill-Decode 融合）

过去，服务引擎要么处理一批“Prefill”（计算密集），要么处理一批“Decode”（内存密集）。
**In-Flight Batching**（TensorRT-LLM）允许把两者混合起来：
- 1 个请求处于 Prefill 阶段。
- 15 个请求处于 Decode 阶段。
- **收益**：Prefill 请求利用 GPU 空闲的计算核心，而 Decode 请求利用内存带宽。

---

## 分块 Prefill 与 RAD-O

超大上下文 Prompt（100 万 Token 以上）可能在 Prefill 阶段阻塞一个批次数秒，从而造成“停顿”。

**解决方案：分块 Prefill**

引擎不再一次 Prefill 128k Token，而是把 Prefill 拆成更小的块（例如每块 4k Token），并与其他用户正在进行的 Decode 步骤交错执行。即使重型请求到达，也能维持稳定的 **TPOT**。

---

## 面试问题

### Q：为什么连续批处理对于 LLM 优于静态批处理？

**强回答：**

静态批处理迫使一个批次中的所有请求等待最长的生成过程完成（即“最长尾部”问题）。如果一个用户请求 500 个 Token，另一个只请求 5 个 Token，那么短请求完成后，GPU 仍会为它空转 495 个周期。连续批处理允许短请求在生成最后一个 Token 后立即离开 GPU，从队列中取出新请求，释放 VRAM 和计算槽位。这样可以最大化整个硬件集群的“每秒 Token 数”。

### Q：LLM 服务中的“停顿”是什么？分块 Prefill 如何缓解它？

**强回答：**

当一个超大的新请求到达时，它的 Prefill 阶段（计算密集型）可能需要 2～3 秒，这就会产生“停顿”。在此期间，GPU 忙于 Prefill，无法为已有用户的 Decode 阶段生成 Token，导致它们的 TPOT 飙升。分块 Prefill 把这 3 秒的 Prefill 拆成若干 200ms 的“小块”：处理一个块，然后为其他所有请求执行一轮 Decode，再回到下一个 Prefill 块。这样能为所有用户保持稳定、平滑的体验。

---

## 参考资料

- Yu 等，《Orca: A Distributed Serving System for [Transformer] Models》（2022）
- NVIDIA，《TensorRT-LLM: In-Flight Batching》（2023）
- vLLM Project，《Iteration-Level Scheduling》（2023）

---

*下一篇：[PagedAttention](05-paged-attention.md)*
