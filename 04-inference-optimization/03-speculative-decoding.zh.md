# 推测解码

推测解码已经成为一种标准技术：它允许大型模型（LLM）在一次前向过程中生成多个 Token，从而有效突破顺序 Decode 的内存带宽瓶颈。

## 目录

- [核心概念](#the-core-concept)
- [Draft-Verify 范式](#draft-verify)
- [Medusa 与多 Token 头](#medusa)
- [前瞻解码](#lookahead-decoding)
- [硬件感知的推测](#hardware-aware)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## 核心概念

LLM Decode 受内存限制：加载 140GB 的权重（70B 模型）却只生成一个 2 字节 Token，效率很低。
**推测解码**使用更便宜的方法“猜测”接下来的 $N$ 个 Token，再让大模型在一次并行的“Prefill 风格”前向过程中验证它们。

---

## Draft-Verify 范式

1. **起草**：小而快的“Draft Model”（例如 1B 或 7B）生成 $K$ 个候选 Token。
2. **验证**：大型“Target Model”一次处理全部 $K$ 个 Token。
3. **接受**：使用目标模型的 logits 接受或拒绝候选。如果第 $i$ 个 Token 被拒绝，则其后的所有 Token 都会被丢弃。

| 模型 | 规模 | 速度 | 每 Token 延迟 |
|------|------|------|---------------|
| **Draft** | 1B | 快 | 5ms |
| **Target** | 70B | 慢 | 50ms |
| **Speculative** | - | **快** | **15ms～25ms** |

**最终结果**：墙钟时间提速 2～3 倍，同时**质量零损失**。

---

## Medusa 与多 Token 头

行业正在从独立 Draft Model（会增加 VRAM 开销）转向 **Medusa Head**。

- **它是什么**：附加在目标模型最后一层上的额外“头”（小型线性层）。
- **工作方式**：不只预测 Token $t+1$，Head 1 预测 $t+1$，Head 2 预测 $t+2$，以此类推。
- **收益**：不需要第二个模型，只增加极少 VRAM 就能提速 2.5 倍。

---

## 前瞻解码

一种替代方案，利用模型过去的隐藏状态寻找反复出现的模式（n-gram），从而“向前看”并预测未来 Token。
- **最适合**：结构化数据、代码以及高度重复的技术写作。

---

## 硬件感知的推测

前沿服务框架（vLLM、TensorRT-LLM）现在使用**动态 Draft 长度**。
- 如果 GPU 利用率较低（小批次），系统会增加 Draft Token 的数量（$K$）。
- 如果 GPU 已饱和（大批次），系统会减少 $K$，优先保证吞吐量，而不是单个请求的延迟。

---

## 面试问题

### Q：为什么推测解码不适合高温度的创意写作？

**强回答：**

推测解码依赖 Draft Model 准确预测 Target Model 会说什么。在高温度创意写作中，概率分布更“平坦”，模型会被鼓励选择概率较低的 Token。这会导致很低的**接受率**（Draft Model 的猜测经常被拒绝）。猜测被拒绝后，目标模型的并行计算就浪费了，系统还要退回标准的顺序 Decode，并额外承担 Draft Model 的延迟。

### Q：Medusa 与传统推测解码有什么区别？

**强回答：**

传统推测解码需要单独的小模型（Draft Model），这会占用额外 VRAM，还需要独立管理它的 KV Cache。Medusa 则在基础模型的最终隐藏状态上增加多个“头”。每个头都经过训练，用来预测不同偏移位置的 Token（例如下一个 Token、下下个 Token、再下一个 Token）。这样不需要第二个模型，也减少了步骤之间的通信开销，因为所有“猜测”都在同一个基础模型架构的一次前向过程中生成。

---

## 参考资料

- Chen 等，《Accelerating Transformer Decoding via Speculative Decoding》（2023）
- Cai 等，《Medusa: Simple LLM Acceleration via Multiple Decoding Heads》（2024）
- Fu 等，《Lookahead Decoding》（2024）

---

*下一篇：[批处理策略](04-batching-strategies.md)*
