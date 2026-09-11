# Transformer 架构

## 前向过程

输入文本先经过 Token Embedding 和位置表示，依次进入多个 Transformer Block。每个 Block 通常包含 Pre-Norm、Self-Attention、残差连接和 Feed-Forward Network，最后经过归一化和 Language Model Head 得到下一 token 的概率。

## 现代变体

Llama 类模型常使用 Pre-Norm、RoPE、RMSNorm 和 GQA；Mistral 等架构会加入滑动窗口或其他效率优化；MoE 通过专家路由扩大参数规模而控制激活计算；MLA 通过压缩潜在表示降低 KV Cache。

## 系统设计要点

参数数量影响训练和权重显存，序列长度和并发影响 KV Cache，token 生成速度决定在线延迟。解释 GPT-2 到现代模型的变化时，可从归一化、位置编码、注意力头、上下文、训练数据和服务优化几个维度比较。
