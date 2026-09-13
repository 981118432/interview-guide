# PagedAttention

PagedAttention 是高吞吐服务引擎（vLLM、SGLang、TensorRT-LLM）背后的基础算法。它解决了过去限制 LLM 扩展能力的“内存碎片”问题。

## 目录

- [连续内存问题](#contiguous-memory)
- [PagedAttention 如何工作](#how-it-works)
- [管理虚拟内存（Block Manager）](#block-manager)
- [KV Cache 共享（写时复制）](#sharing)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## 连续内存问题

标准深度学习框架会以大块、连续的方式分配内存。
对于一个 LLM 请求，你可能会为 `max_sequence_length` 为 8192 Token 的序列预先分配内存。

**浪费：**
1. **内部碎片**：如果用户只生成 10 个 Token，预留块的 99.9% 都被浪费。
2. **外部碎片**：内存被分割成许多空隙，单个空隙太小，无法容纳新的“大块”，即使总空闲内存仍然很多。

---

## PagedAttention 如何工作（vLLM）

PagedAttention 的灵感来自操作系统中的虚拟内存。

1. **Token 到 Block**：一个请求的 KV Cache 被拆成小而固定大小的 **Block**（例如每个 Block 16 个 Token）。
2. **逻辑与物理**：模型认为自己关注的是连续序列（逻辑内存），但这些 Block 实际分散在 VRAM 各处（物理内存）。
3. **查找表**：**Block Table** 将逻辑索引映射到物理地址。

**主要收益**：内存浪费从约 60～80% 降至**低于 4%**。

---

## 管理虚拟内存（Block Manager）

服务框架（vLLM、SGLang）充当 GPU 上的“迷你操作系统”。

- **分配**：新请求开始时，Block Manager 为其分配一组空闲物理 Block。
- **淘汰**：如果 VRAM 已满，管理器可以把不活跃的 KV Block“换出”到 CPU RAM，需要时再换回来（Paged Swap）。

---

## KV Cache 共享（写时复制）

PagedAttention 可以轻松共享“公共前缀”。

**场景**：100 个用户都在使用同一个 5,000 Token 的系统 Prompt 对话。
- **传统方式**：将这份 5,000 Token 的 KV Cache 存储 100 次（VRAM 中共 **500k Token**）。
- **PagedAttention**：通过 Block Table 只存储**一次**，让 100 个用户都指向相同的物理 Block。
- **写时复制**：如果某个用户生成了独有 Token，就只为他创建一个新 Block，共享 Block 保持不变。

---

## 面试问题

### Q：为什么 PagedAttention 能显著提升吞吐量？

**强回答：**

PagedAttention 允许使用更大的**批大小**，从而提升吞吐量。因为它消除了内部和外部内存碎片，我们可以在同一块 GPU VRAM 中放入更多请求。传统服务可能只能容纳 4 个请求，因为必须为最大长度预留 Block；使用 PagedAttention 后，由于只为实际存在的 Token 使用内存，可以容纳 20～30 个请求。更大的批次会带来更高的 GPU 利用率和明显更高的聚合每秒 Token 数。

### Q：在 vLLM 中解释 Block Table。

**强回答：**

Block Table 是一种映射结构，用来弥合模型期望数据连续、而物理内存实际分散这一差距。表中的每个条目对应一组 Token 的“逻辑 Block”，并记录该 Block 的 Key 和 Value 张量存放在 GPU 内存中的物理地址。这样框架就能以小块为单位动态分配和释放内存，并支持前缀共享、高效多线程等高级特性。

---

## 参考资料

- Kwon 等，《Efficient Memory Management for Large Language Model Serving with PagedAttention》（SOSP 2023）
- vLLM Documentation，《PagedAttention Logic》（2024）

---

*下一篇：[服务基础设施](06-serving-infrastructure.md)*
