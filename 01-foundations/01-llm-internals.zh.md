# LLM 内部机制

## 学习重点

本章从 Transformer、注意力、位置编码、FFN、LayerNorm、MoE 和多模态等组件解释 LLM 如何工作。系统设计面试不要求背出全部公式，但要能说明每个组件对质量、显存、延迟和扩展性的影响。

## 核心内容

- Decoder-only 适合自回归生成；Encoder-only 适合理解和表示；Encoder-Decoder 适合输入输出转换任务。
- MoE 通过只激活部分专家降低每 token 计算量，但会增加路由、通信、负载均衡和显存管理复杂度。
- Self-Attention 的计算和显存通常随序列长度呈二次增长，因此长上下文需要 Flash Attention、稀疏注意力、缓存和分块策略。
- MHA、MQA 和 GQA 在质量、KV Cache 大小和带宽之间做不同权衡；GQA 是生产服务中常见的折中方案。
- RoPE、ALiBi 和学习型位置编码影响长度外推、相对位置表达和模型兼容性。
- Pre-LN 通常更容易稳定训练，RMSNorm 以更低开销提供归一化能力。

## 面试回答角度

解释架构时从输入 token、Embedding、位置编码、Transformer Block、Logits 到采样完整走一遍，再补充 KV Cache、参数规模、显存和吞吐。不要只说模型参数量，要说明推理时真正影响成本的是权重、激活、KV Cache、并发和序列长度。
