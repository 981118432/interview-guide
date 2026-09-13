# 端侧与边缘部署

并非每个模型都必须运行在别人的云上。2026 年，在笔记本电脑、工作站 GPU、手机或边缘盒子上**本地**运行 LLM 已经是真实的部署目标，驱动力包括隐私、离线运行、延迟和稳定规模下的成本。需要注意的是，让本地模型易于*尝试*的工具（Ollama），并不是用来在*生产环境*中服务模型的工具（vLLM），两者经常被混淆。本章梳理运行时栈、从原型到生产的路径、硬件限制，以及本地部署真正优于 API 的时机。

## 目录

- [运行时栈](#the-runtime-stack)
- [为什么 Ollama 不是生产服务端](#why-ollama-is-not-a-production-server)
- [什么时候本地优于云端（什么时候不是）](#when-local-beats-cloud-and-when-it-does-not)
- [本地服务中的量化](#quantization-for-local-serving)
- [硬件](#hardware)
- [从原型到生产](#prototype-to-production)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## 运行时栈

关键的思维模型是：这些工具**不是替代关系**，而是位于不同层级。

| 工具 | 层级 | 用途 |
|------|------|------|
| **Ollama** | 体验层/本地守护进程 | 一条命令拉取和运行模型，提供类似 OpenAI 的 API，面向单用户开发。底层基于 llama.cpp，近期版本在 Apple Silicon 上使用 Apple MLX。 |
| **LM Studio** | 体验层/GUI | 用于浏览和运行本地模型的桌面 GUI，侧重单用户。 |
| **llama.cpp** | 推理引擎 | 可移植的 C/C++ CPU/GPU 推理（GGUF 格式）；几乎可以运行在任何地方，也是体验层工具的底座。 |
| **MLX** | 推理引擎 | Apple 的数组框架；Apple Silicon 上最快的路径，也用于研究和微调。 |
| **vLLM** | 服务系统 | 使用 PagedAttention 和连续批处理提供高吞吐并发服务，兼容 OpenAI。生产环境的答案。 |
| **TGI/TensorRT-LLM** | 服务系统 | Hugging Face 和 NVIDIA 的高吞吐服务端；适合生产环境。 |
| **ExecuTorch** | 嵌入式/移动端运行时 | PyTorch 原生的端侧推理（从手机到微控制器）；2025 年底达到 1.0，已经进入数十亿用户使用的应用。 |
| **Core ML/ONNX Runtime/MLC LLM** | 嵌入式/移动端运行时 | 分别用于 Apple 端侧、跨平台，以及编译到多种目标（包括浏览器/WebGPU）。 |

---

## 为什么 Ollama 不是生产服务端

Ollama 和 LM Studio 非常适合原型开发，却不适合作为共享生产端点，原因在于一个值得重点讲解的架构差异。

Ollama 默认只提供非常有限的并行度，并且先以先进先出方式排队多余请求；队列满时会返回错误。每个并行槽位还会静态地增加一份上下文内存分配。LM Studio 面向单用户场景，没有限流或认证。两者都不是为了把并发需求转化为吞吐量而设计的。

**vLLM** 则是，依靠两个机制：**PagedAttention**（像操作系统分页一样，把 KV Cache 存储在非连续 Block 中，将朴素服务 60～80% 的 KV 内存浪费降低到约 4% 以下）和**连续批处理**（在批次中途换出已完成请求、换入排队请求）。Red Hat 给出的最清晰的一手基准显示：在单张数据中心 GPU 上运行 8B 模型时，vLLM 达到约 **793 Token/秒，而 Ollama 约为 41**，约 19 倍，并且尾延迟显著更低；即使调优后的 Ollama，在所有并发级别上也落后。

结论不是“vLLM 调得更好”，而是结构不同：Ollama 和 LM Studio 会串行化，vLLM 则连续批处理并对 KV Cache 分页。单用户时差异很小；并发时差异会达到约 16～20 倍。需要诚实说明的是，大多数公开对比都在数据中心 GPU 上运行，以隔离*软件*差异，因此不要把“vLLM 击败 Ollama”理解成“GPU 击败 Mac”。

---

## 什么时候本地优于云端（什么时候不是）

**以下情况倾向于本地或边缘部署：**
- **无法离开设备的隐私或受监管数据**（HIPAA、GDPR、合同约定的数据驻留）。需要说明的是，如今主要 API 供应商已经提供零数据留存的企业层级，因此“隐私”本身不再自动决定使用本地部署。
- **离线或隔离网**运行（现场设备、关键基础设施）。
- **对延迟的硬下限要求**：端侧推理消除了网络往返（通常为 50～200ms），这对紧密交互循环很重要；但总响应延迟仍取决于模型和硬件。
- **稳定的高流量成本**：据报道，预留 GPU 在每天数百万 Token 左右就可能相对于前沿 API 达到盈亏平衡；超过这一点后，因为不再按 Token 付费，拥有硬件会更有优势。具体盈亏平衡点取决于工作负载。

**以下情况应继续使用云 API**：需要前沿质量，流量有尖峰或不可预测（闲置 GPU 也要付费；半价左右的批处理端点在中等流量下通常胜过本地），流量低到中等（低于盈亏平衡点时 API 的总成本更低），或者团队没有能力运维带自动扩缩容和监控的 vLLM。2026 年的共识通常是采用**混合方案**：在同一个产品中，小型、私有、离线或成本敏感路径运行在本地，重型、前沿或突发路径交给云端。

---

## 本地服务中的量化

量化让本地服务成为可能；[量化深入理解](../03-training-and-adaptation/07-quantization-deep-dive.md)会讲解数学原理，这里只讨论部署层。

**GGUF** 是 llama.cpp、Ollama 和 LM Studio 使用的本地模型格式。常见量化级别在质量和大小之间进行权衡：Q4_K_M 是实用的最佳平衡点（相对于 FP16，质量损失约 1～3%，大小约为四分之一），Q5_K_M 在代码和推理上明显更好，损失低于约 1%，Q8_0 基本无损，大小约为 FP16 的一半，而 Q2/Q3 节省最多内存，但会让数学和推理能力下降 5～10% 甚至更多。

**VRAM 经验法则**：

```
VRAM (GB) ≈ (params in billions × bits per weight) / 8   # model weights only
```

然后还要加上 KV Cache（它会随上下文长度和并发请求数增长），以及约 10～20% 的运行时开销。因此，7B 模型的权重大约需要：FP16 为 14GB，Q8_0 约 7.7GB，Q4_K_M 约 4.5GB，以上都还未包含额外开销。大家反复强调的操作原则是：**在能放下的前提下，使用质量最高的量化版本，并为 KV Cache、激活值和上下文预留 10～20% 的余量**。

---

## 硬件

模型大小到硬件的参考指南（假设使用 Q4 量化；这是规划建议，不是保证）：

| 模型大小（Q4） | 最低 VRAM/RAM | 现实可行的硬件 |
|----------------|---------------|----------------|
| 1～3B | 4～6 GB | 任意现代 GPU；高端手机（NPU）；AI PC |
| 7～8B | 8 GB | 主流 GPU；16 GB Mac |
| 13～14B | 12 GB | 中高端 GPU；16～24 GB Mac |
| 32～35B | 24 GB | 24 GB 消费级 GPU；36～48 GB Mac |
| 70B | 约 40 GB+ | 高端或双 GPU；64 GB+ Mac；或数据中心显卡 |
| 200B+ | 48 GB+，通常需要多 GPU/128 GB+ 统一内存 | 多 GPU 设备；大统一内存工作站 |

注意：
- **消费级 GPU** 的 VRAM 通常上限为 24～32 GB，这是限制本地模型大小的关键因素。
- **Apple Silicon** 在 CPU 和 GPU 之间共享一个内存池，因此系统 RAM 也充当 VRAM，让大内存 Mac 能够容纳同价位独立 GPU 无法容纳的模型。Apple 的 MLX 路径还在改进：Ollama 的 MLX 后端（预览版）报告称，利用统一内存后，Apple Silicon 上的 Prefill 和 Decode 有明显提升；另一个更新加入了 NVFP4——NVIDIA 的 4-bit 浮点格式（不是 Apple 的格式），据报道比 Q4_K_M 快约 20%。
- **NPU** 在手机和 AI PC 上宣传很高的 TOPS，但教学时需要强调：TOPS 单独不能预测 LLM 速度，因为算子支持有限和内存带宽才是实际性能的门槛。NPU 适合轻量、省电任务；重型本地推理仍然由独立 GPU 胜出。
- **移动端** 同时受内存带宽和容量限制：手机上现实可行的模型通常小于 1B 到约 3B，即使旗舰机可用 App RAM 也经常低于 4 GB，而移动内存带宽比数据中心 GPU 低 30～50 倍。端侧标准是 4-bit 量化。

---

## 从原型到生产

1. **原型阶段**：使用 Ollama（CLI）或 LM Studio（GUI）运行 GGUF Q4_K_M 模型；用能够通过验证的最小模型验证质量和 Prompt。
2. **选择在目标硬件上放得下且留有 KV Cache 余量的最大模型和最佳量化版本**。
3. **对任何并发端点切换服务引擎**：vLLM（NVIDIA 或 AMD）、TensorRT-LLM（NVIDIA 性能上限）或 TGI。保留 OpenAI 兼容 API，让应用代码几乎不需要变化。
4. **对于移动端或边缘端**，导出到 ExecuTorch、Core ML 或 ONNX Runtime/MLC LLM，量化到 4-bit，并按低于 4 GB RAM 和带宽限制进行预算。

常见陷阱包括：把 Ollama 或 LM Studio 当作服务端（负载下会串行化）；估算内存时忘记 KV Cache（长上下文乘以并行槽位后可能成为主导）；过度量化（Q2/Q3 会伤害推理）；把“vLLM 击败 Ollama”和“GPU 击败 Mac”混为一谈；认为 NPU TOPS 就等于 LLM 速度；以及引擎和硬件不匹配（vLLM 以 GPU 为中心，MLX 仅适用于 Apple，llama.cpp 是可移植性兜底方案）。

**成熟度**：服务端本地服务已经达到生产成熟度（vLLM 通过 OpenAI 兼容 API 得到广泛部署）。端侧和移动端对于*小型*模型（小于 1B 到 3B）已经可以用于生产，但还不适合前沿模型。NPU 作为 LLM 引擎仍处于早期；独立 GPU 和大统一内存 Mac 仍是 2026 年真正严肃的本地路径。

---

## 面试问题

### Q：团队用 Ollama 做了原型，现在想把它作为共享 API 上线。需要做什么改变，为什么？

**强回答：**

Ollama 不适合作为共享端点。它的并行度有限，并以先进先出方式排队多余请求，因此并发下延迟会飙升，请求也会开始失败。解决方案是把服务引擎切换到 vLLM（或 TensorRT-LLM、TGI），同时保留相同的 OpenAI 兼容 API，让应用几乎不需要变化。vLLM 的优势来自结构，而不是调参：PagedAttention 把 KV Cache 存在非连续 Block 中，消除大部分内存浪费；连续批处理则在批次中途换出已完成请求、换入排队请求，把并发需求转化为吞吐量。一手基准显示，负载下吞吐量大约提高一个数量级，尾延迟也显著降低。我还会根据目标 GPU 和 KV Cache 余量合理选择模型与量化版本，并补充自动扩缩容和监控，这些都是 Ollama 不提供的能力。

### Q：什么时候会选择本地或端侧推理，而不是云 API？

**强回答：**

当数据出于隐私或驻留原因不能离开设备时，当系统必须离线或在隔离网中运行时，当我需要通过消除网络往返获得尽可能低的延迟时，或者当流量稳定且规模很高、预留 GPU 的成本低于按 Token 付费时，我会选择本地方案；据报道，这通常在每天数百万 Token 左右达到盈亏平衡。如果追求前沿质量、流量有尖峰且闲置 GPU 会浪费资金、流量低于盈亏平衡点，或者团队缺乏运维服务栈的能力，我会继续使用 API。实际中通常是混合方案：小型、私有或离线路径运行量化模型，重型、前沿或突发路径走云端。对于手机，我会规划小于 1B 到 3B 的模型，因为移动端受内存和带宽限制。

---

## 参考资料

- Red Hat Developer，[“Ollama vs vLLM: a deep dive into performance benchmarking”](https://developers.redhat.com/articles/2025/08/08/ollama-vs-vllm-deep-dive-performance-benchmarking)
- vLLM，[文档](https://docs.vllm.ai/) 和 [PagedAttention 博客](https://blog.vllm.ai/2023/06/20/vllm.html)
- Ollama，[现已由 Apple Silicon 上的 MLX 驱动](https://ollama.com/blog/mlx) 和[并发 FAQ](https://docs.ollama.com/faq)
- PyTorch，[介绍 ExecuTorch 1.0](https://pytorch.org/blog/introducing-executorch-1-0/)
- Chandra 和 Krishnamoorthi（Meta），[“On-Device LLMs: State of the Union, 2026”](https://v-chandra.github.io/on-device-llms/)

---

*下一篇：[Prompt Engineering 基础](../05-prompting-and-context/01-prompt-engineering-fundamentals.md)*
