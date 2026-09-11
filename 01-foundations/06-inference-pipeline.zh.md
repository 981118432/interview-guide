# 推理流水线

本章介绍 LLM 在推理阶段如何生成文本、涉及哪些计算阶段，以及生产服务中的关键指标。

## 目录

- [生成基础](#生成基础)
- [Prefill 与 Decode 阶段](#prefill-与-decode-阶段)
- [采样策略](#采样策略)
- [停止条件](#停止条件)
- [潜在优化：推测解码](#潜在优化推测解码)
- [延迟指标与 TTFT/TPS](#延迟指标)
- [内存与计算需求](#内存与计算需求)
- [Continuous Batching 与 Prefix Caching](#continuous-batching-与-prefix-caching)
- [Multi-LoRA 服务](#multi-lora-服务)
- [流式输出](#流式输出)
- [生产注意事项](#生产注意事项)
- [面试问答](#面试问答)
- [参考资料](#参考资料)

---

## 生成基础

LLM 以自回归方式生成文本：一次生成一个 token，并使用之前的所有 token 作为上下文。

```
Input: "The quick brown"
Step 1: Generate "fox" -> "The quick brown fox"
Step 2: Generate "jumps" -> "The quick brown fox jumps"
Step 3: Generate "over" -> "The quick brown fox jumps over"
...
```

### 生成循环

```python
def generate(prompt: str, max_tokens: int, model) -> str:
    tokens = tokenize(prompt)

    for _ in range(max_tokens):
        # Forward pass: get logits for next token
        logits = model.forward(tokens)

        # Sample next token from probability distribution
        next_token = sample(logits[-1])

        # Check for stop condition
        if next_token == EOS_TOKEN:
            break

        tokens.append(next_token)

    return detokenize(tokens)
```

---

## Prefill 与 Decode 阶段

推理包含两个特征不同的阶段：

### Prefill 阶段

并行处理完整的输入 Prompt。

```
Input: "The quick brown fox" (4 tokens)

Prefill:
- Process all 4 tokens simultaneously
- Compute attention across all pairs
- Populate KV cache for all positions
- Output: logits for next token
```

**特征：**
- 受计算限制（大量矩阵运算）
- 可以在 token 之间并行
- 耗时随 Prompt 长度增长
- 每次生成只发生一次

### Decode 阶段

一次生成一个 token。

```
Decode step 1:
- Input: new token position only
- Attend to all KV cache (prompt + previously generated)
- Generate one token

Decode step 2:
- Append new K, V to cache
- Input: newest token position
- Generate next token

...repeat until done
```

**特征：**
- 受内存限制（从 HBM 加载 KV Cache）
- 顺序执行（必须完成一步才能开始下一步）
- 每个 token 的耗时大致恒定
- 重复执行，直到满足停止条件

### 为什么重要

| 阶段 | 瓶颈 | 优化方向 |
|-------|------------|--------------|
| Prefill | 计算（GPU 核心） | Flash Attention、更快的 GPU |
| Decode | 内存带宽 | GQA、批处理、量化 |

**对服务的影响：**
- Prompt 较长会增加 Prefill 时间（影响 TTFT）
- 生成较长会增加 Decode 时间（影响总延迟）
- 批处理对 Decode 效率的帮助大于对 Prefill 的帮助

---

## 采样策略

计算 logits 后，需要选择下一个 token。不同策略会产生不同输出。

### Greedy Decoding

始终选择概率最高的 token：

```python
def greedy_sample(logits):
    return torch.argmax(logits)
```

**特性：**
- 确定性
- 长文本生成中容易重复
- 适合事实性或结构化输出

### Temperature Sampling

在 Softmax 前缩放 logits，以控制随机性：

```python
def temperature_sample(logits, temperature=1.0):
    scaled_logits = logits / temperature
    probs = torch.softmax(scaled_logits, dim=-1)
    return torch.multinomial(probs, num_samples=1)
```

**Temperature 的影响：**

| Temperature | 行为 | 使用场景 |
|-------------|----------|----------|
| 0 | Greedy（确定性） | 事实问答、代码 |
| 0.3–0.7 | 随机性低 | 通用任务 |
| 1.0 | 基准 | 创意写作 |
| 1.5+ | 随机性高 | 头脑风暴 |

### Top-K Sampling

只考虑概率最高的 K 个 token：

```python
def top_k_sample(logits, k=50):
    values, indices = torch.topk(logits, k)
    probs = torch.softmax(values, dim=-1)
    sampled_idx = torch.multinomial(probs, num_samples=1)
    return indices[sampled_idx]
```

**效果：**过滤掉可能没有意义的低概率 token。

### Top-P（Nucleus）Sampling

不断加入 token，直到累计概率超过 P：

```python
def top_p_sample(logits, p=0.9):
    sorted_probs, sorted_indices = torch.sort(
        torch.softmax(logits, dim=-1), descending=True
    )
    cumulative_probs = torch.cumsum(sorted_probs, dim=-1)

    # Find cutoff
    cutoff_idx = torch.searchsorted(cumulative_probs, p)

    # Sample from truncated distribution
    selected_probs = sorted_probs[:cutoff_idx + 1]
    selected_probs = selected_probs / selected_probs.sum()
    sampled_idx = torch.multinomial(selected_probs, num_samples=1)

    return sorted_indices[sampled_idx]
```

**相对 Top-K 的优势：**会根据概率分布动态调整。高置信度预测只包含较少 token；不确定预测则包含更多 token。

### 常见配置

| 使用场景 | Temperature | Top-P | Top-K |
|----------|-------------|-------|-------|
| 代码生成 | 0–0.2 | 0.95 | - |
| 事实问答 | 0.1–0.3 | 1.0 | - |
| 通用聊天 | 0.7 | 0.9 | - |
| 创意写作 | 1.0 | 0.95 | - |
| 头脑风暴 | 1.2 | 1.0 | - |

### 重复惩罚

降低最近生成过的 token 的概率：

```python
def apply_repetition_penalty(logits, generated_tokens, penalty=1.2):
    for token_id in set(generated_tokens):
        logits[token_id] /= penalty
    return logits
```

**变体：**
- Presence penalty：惩罚所有已经出现过的 token
- Frequency penalty：按出现次数的比例惩罚

---

## 停止条件

生成会持续到满足某个停止条件：

### EOS Token

模型生成序列结束 token：

```python
if next_token == tokenizer.eos_token_id:
    break
```

### 最大 Token 数

对生成长度设置硬上限：

```python
for i in range(max_tokens):
    # generate...
```

### Stop Sequence

用自定义字符串终止生成：

```python
stop_sequences = ["###", "\n\n", "Human:"]

for seq in stop_sequences:
    if output.endswith(seq):
        output = output[:-len(seq)]
        break
```

## 潜在优化：推测解码

**高带宽服务的当前标准方案。**

推测解码使用较小的“草稿模型”在一步中预测多个未来 token，再由更大的“目标模型”并行验证。

```
Draft Model (Small): Predicts 5 tokens -> "The", "quick", "brown", "fox", "jumps"
Target Model (Large): Verifies all 5 tokens in ONE forward pass.
Result: If target agrees on 4 tokens, we've generated 4 tokens for the cost of 1 large forward pass.
```

| 方法 | 做法 | 加速 | 示例 |
|--------|----------|---------|---------|
| Draft Model | 小模型（例如 1B）+ 大模型（70B） | 2–3 倍 | vLLM、TGI |
| **Medusa Heads** | 在同一模型上增加多个 LM Head | 1.5–2 倍 | Medusa、Eagle |
| Prompt Lookup | 使用 Prompt 中的子串进行推测 | 1.2 倍 | RAG/代码补全 |

---

## 延迟指标

### 首 Token 时间（TTFT）

从请求到第一个生成 token 的时间。

```
TTFT = network_latency + queue_time + prefill_time
```

**影响 TTFT 的因素：**
- Prompt 长度（Prefill 为 O(n)）
- 模型大小
- GPU 速度
- 队列深度

**目标：**
- 交互式聊天：< 500ms
- 实时场景：< 200ms
- 批处理：不太关键

### 每秒 Token 数（TPS）

第一个 token 之后的生成速率。

```
TPS = (total_tokens - 1) / (total_time - TTFT)
```

**影响 TPS 的因素：**
- 模型大小
- 批大小
- GPU 内存带宽
- KV Cache 大小

**典型值：**
- H100 上的 Llama 70B：每个请求 30–50 token/s
- 通过 API 调用 GPT-4：20–80 token/s（有变化）
- 小模型（7B）：100+ token/s

### 总延迟

```
Total = TTFT + (output_tokens / TPS)
```

**示例：**
- TTFT：200ms
- TPS：50 token/s
- 输出：100 token
- 总延迟：200ms + 2000ms = 2.2s

### 吞吐量

单位时间内完成的请求数：

```
Throughput = concurrent_requests * TPS / average_output_tokens
```

增大批大小会提高吞吐量，但可能增加单请求延迟。

---

## 内存与计算需求

### 模型权重

```
Memory = parameters * bytes_per_parameter

70B model in FP16:
= 70B * 2 bytes
= 140 GB

70B model in INT4:
= 70B * 0.5 bytes
= 35 GB
```

### KV Cache

```
Per token: 2 * layers * heads * head_dim * bytes
Per request: per_token * sequence_length

Llama 70B (80 layers, 64 heads, 128 dim, FP16):
= 2 * 80 * 64 * 128 * 2 bytes
= 2.6 MB per token

At 4K context: 10.5 GB per request
At 8K context: 21 GB per request
```

### GPU 总内存

```
Total = model_weights + kv_cache * batch_size + activations

Example: Llama 70B serving
- Weights (INT4): 35 GB
- KV cache (8K, batch 4): 84 GB
- Activations: ~5 GB
- Total: ~124 GB (fits on 2x H100 80GB)
```

### 每个 Token 的 FLOPs

```
Forward pass FLOPs ≈ 2 * parameters

70B model:
≈ 140 TFLOPs per token

At 40 tokens/sec:
≈ 5.6 PFLOPs sustained
```

---

## 流式输出

对于交互式应用，应在 token 生成时立即流式返回：

### Server-Sent Events（SSE）

```python
# Server
async def generate_stream(prompt: str):
    for token in model.generate_iter(prompt):
        yield f"data: {json.dumps({'token': token})}\n\n"
    yield "data: [DONE]\n\n"

# Client
async for event in sse_client.stream("/generate"):
    token = json.loads(event.data)["token"]
    display(token)
```

### 优势

| 方面 | 流式 | 非流式 |
|---------------|-----------|---------------|
| 感知延迟 | 只需等待 TTFT | 等待完整生成时间 |
| 用户体验 | 渐进展示 | 等待后一次性完成 |
| 提前终止 | 用户可以停止 | 必须等待 |
| 内存 | 更低 | 更高（要缓冲响应） |

### 实现细节

- 每个 token 后 Flush
- 优雅处理连接断开
- 生成非常快时可以考虑缓冲
- 一些框架默认会缓冲，需要为流式输出关闭缓冲

---

## 生产注意事项

### 通过批处理提升吞吐

把多个请求合并，以最大化 GPU 利用率：

```python
# Without batching: GPU underutilized
for request in requests:
    response = model.generate(request)

# With batching: parallel processing
batch = collect_requests(timeout=10ms, max_batch=32)
responses = model.generate_batch(batch)
```

### Continuous Batching 与 Prefix Caching

**Continuous Batching（迭代级调度）：**
与静态批处理不同，Continuous Batching 会在批中任意请求遇到 EOS token 后立即注入新请求。吞吐量最高可提升 20 倍。

**Prefix Caching（RAD-O）：**
缓存公共前缀（例如系统提示、few-shot 示例）的 KV 张量。
- **TTFT 降低**：90%
- **机制**：对前缀计算 Hash，在 GPU 内存的 LRU Cache 中查找 KV 张量。

### Multi-LoRA 服务

**场景：**在一个基础模型上服务 1000 个不同的微调模型（适配器）。
**挑战：**加载 1000 个独立模型需要数 TB 的显存。

**方案（LoRAX/S-LoRA）：**
1. 把一个基础模型加载到显存。
2. 把 LoRA 适配器（MB 级）存放在主机内存或 SSD 中。
3. 根据请求 ID，在前向过程中动态切换适配器。
4. **实现**：使用专用 Kernel，让同一批中的多个不同适配器执行矩阵向量乘法。

### 请求优先级

```python
class RequestQueue:
    def __init__(self):
        self.high_priority = asyncio.Queue()
        self.low_priority = asyncio.Queue()

    async def get_next(self):
        if not self.high_priority.empty():
            return await self.high_priority.get()
        return await self.low_priority.get()
```

**优先级依据：**
- 客户等级
- 请求类型
- 等待时间
- 预计计算成本

### 超时处理

```python
async def generate_with_timeout(prompt: str, timeout: float):
    try:
        result = await asyncio.wait_for(
            model.generate(prompt),
            timeout=timeout
        )
        return result
    except asyncio.TimeoutError:
        return {"error": "timeout", "partial": partial_output}
```

### 优雅降级

```python
async def generate_with_fallback(prompt: str):
    try:
        return await primary_model.generate(prompt)
    except RateLimitError:
        return await fallback_model.generate(prompt)
    except TimeoutError:
        return await small_fast_model.generate(prompt)
```

### 成本追踪

```python
@dataclass
class RequestMetrics:
    input_tokens: int
    output_tokens: int
    model: str
    latency_ms: float
    cost_usd: float

def calculate_cost(metrics: RequestMetrics) -> float:
    pricing = {
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    }
    rates = pricing[metrics.model]
    return (
        (metrics.input_tokens / 1_000_000) * rates["input"] +
        (metrics.output_tokens / 1_000_000) * rates["output"]
    )
```

---

## 面试问答

### 问：解释 Prefill 和 Decode 阶段的区别。

**强回答：**
LLM 推理有两个明显阶段：

**Prefill：**
- 一次处理完整输入 Prompt
- 所有 token 之间并行进行 Attention
- 为所有 Prompt 位置填充 KV Cache
- 受计算限制：高效使用 GPU 核心
- 耗时随 Prompt 长度增长

**Decode：**
- 一次生成一个 token
- 新 token 关注 KV Cache 中的所有条目
- 把新的 K、V 追加到 Cache
- 受内存限制：瓶颈是加载 KV Cache
- 每个 token 的耗时大致恒定

这对系统设计很重要，因为：
- 长 Prompt 会增加 TTFT（Prefill 密集）
- 批处理对 Decode 的帮助大于对 Prefill 的帮助
- 两个阶段需要采用不同的优化策略

### 问：Temperature 和 Top-P 如何影响生成？

**强回答：**
两者都控制 token 选择时的随机性：

**Temperature：**
- 在 Softmax 前缩放 logits
- 低值（0–0.3）：更确定，选择高概率 token
- 高值（1.0+）：更随机，拉平概率分布
- 零：Greedy Decoding

**Top-P（Nucleus Sampling）：**
- 过滤出累计概率超过 p 的最小 token 集合
- 根据分布动态调整截断点
- 高置信度：考虑较少 token
- 低置信度：考虑较多 token

典型生产配置：
- 事实问答：temperature 0.1、top-p 0.95
- 通用聊天：temperature 0.7、top-p 0.9
- 创意任务：temperature 1.0+、top-p 0.95

关键点是二者会一起工作：Temperature 重塑分布，Top-P 截断分布。

### 问：哪些因素决定 TTFT 和 TPS？

**强回答：**
**TTFT（首 Token 时间）：**
- 到达服务器的网络延迟
- 队列等待时间
- Prefill 计算时间
- 主要受 Prompt 长度、GPU 计算速度影响

**TPS（每秒 Token 数）：**
- Decode 阶段效率
- 加载 KV Cache 的内存带宽
- 主要受内存带宽、批大小、模型规模影响

优化策略不同：
- TTFT：可能时缩短 Prompt、使用更快网络、减少排队
- TPS：增大批大小、使用 GQA/MQA 模型、优化内存访问

权衡是：批处理可以提高 TPS（吞吐），但如果请求要等待组批，可能增加 TTFT（延迟）。

### 问：如何估算服务一个模型所需的 GPU 资源？

**强回答：**
主要有三类内存消耗：

1. **模型权重：**
   - FP16：参数量 × 2 字节
   - INT8：参数量 × 1 字节
   - INT4：参数量 × 0.5 字节

2. **KV Cache：**
   - 每个 token：2 × 层数 × KV 头数 × head_dim × 2 字节（FP16）
   - 每个请求：每 token 大小 × 序列长度
   - 总量：每请求大小 × batch_size

3. **激活值：**通常额外占 5–10%

以服务 Llama 70B 为例：
- 权重（INT4）：35 GB
- KV Cache（8K 上下文、batch 8）：168 GB
- 需要：总计约 200 GB

硬件选择：
- 3× A100 80GB，使用 Tensor Parallelism
- 2× H100 80GB，使用 Tensor Parallelism
- 8× A100 40GB，使用更多并行

然后通过基准测试确认吞吐满足需求。

---

## 参考资料

- Holtzman 等：《The Curious Case of Neural Text Degeneration》（Nucleus Sampling，2020）
- Kwon 等：《Efficient Memory Management for Large Language Model Serving with PagedAttention》（vLLM，2023）
- [vLLM 文档](https://docs.vllm.ai/)
- [TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM)
- [OpenAI API 文档](https://platform.openai.com/docs/api-reference)

---

*上一篇：[Embedding 与向量空间](05-embeddings-and-vector-spaces.md) | 下一篇：[模型分类](../02-model-landscape/01-model-taxonomy.md)*
