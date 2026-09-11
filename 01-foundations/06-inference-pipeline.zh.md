# 推理流水线

## 生成过程

模型先执行 Prefill，处理输入上下文并建立 KV Cache；然后进入 Decode，逐 token 生成输出。采样可以使用 Greedy、Temperature、Top-K、Top-P 和重复惩罚，停止条件包括 EOS、最大 token 和 Stop Sequence。

## 关键指标

- TTFT：从请求到第一个 token 的时间。
- TPS：生成速度。
- Total Latency：完整响应时间。
- Throughput：单位时间处理的请求或 token 数。

## 生产优化

使用 Streaming/SSE 改善体验，Continuous Batching 提高吞吐，Prefix Caching 减少重复 Prefill，Speculative Decoding 提高 Decode 速度，Multi-LoRA 支持多个适配器。还要设置请求优先级、超时、降级、成本追踪和 GPU 显存预算。
