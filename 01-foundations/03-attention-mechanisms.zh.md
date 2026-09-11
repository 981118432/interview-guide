# Attention 机制

## 核心概念

Attention 通过 Query、Key、Value 计算序列中不同位置之间的相关性。Scaled Dot-Product Attention 会除以 √d_k，避免点积过大导致 Softmax 梯度过小；Causal Mask 保证生成 token 不能看到未来内容。

## 效率优化

- Sparse Attention 只连接部分位置，减少长序列计算。
- Linear Attention 用近似形式降低复杂度，但可能损失表达能力。
- FlashAttention 通过分块和 IO 优化减少显存读写，通常不改变数学结果。
- MQA/GQA 共享 Key/Value 头，显著减少 KV Cache 和带宽。
- Sliding Window Attention 只关注局部窗口，适合局部依赖明显的任务。

## 生产视角

区分 Prefill 和 Decode：Prefill 处理整段输入，计算密集；Decode 逐 token 生成，通常受 KV Cache、内存带宽和批处理影响。面试中应把注意力机制连接到 TTFT、TPS、上下文长度和 GPU 显存，而不只是讲公式。
