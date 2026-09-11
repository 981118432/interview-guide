# 知识蒸馏

知识蒸馏是把大型复杂模型（Teacher）的能力迁移到更小、更高效模型（Student）的过程。很多参数量不大但能力很强的开放权重模型，都使用了大模型生成或筛选的合成数据。

## Teacher–Student 范式

小模型通常不是只在原始网页数据上训练，而是学习大模型生成的高质量样本。

| 模型 | 角色 | 能力来源 |
|---|---|---|
| Teacher | 大模型，通常 100B+ 参数 | 在 50T+ token 上预训练 |
| Student | 小模型，通常 1B–8B 参数 | 学习 Teacher 的行为、答案和推理轨迹 |

Teacher 的作用不只是提供最终答案，也可以提供软概率、解释、工具调用轨迹和可验证的中间结果。Student 学到的是一种压缩后的行为信号。

## 蒸馏如何工作

### 1. Hard Label 蒸馏

Student 只学习 Teacher 的最终答案，把 Teacher 输出当作普通监督标签。它实现简单，但丢失了候选答案之间的概率关系。

### 2. Soft Label 蒸馏

Teacher 输出完整的概率分布，Student 通过 KL Divergence 拟合这个分布。温度参数会把分布变得更平滑，使“次优答案”的相对信息也能传递给 Student。

### 3. 输出蒸馏与特征蒸馏

- **输出蒸馏：**让 Student 的最终 logits 或文本输出接近 Teacher。
- **特征/隐藏状态蒸馏：**让中间层表示也对齐，通常需要处理两种模型维度和层数不同的问题。

## 从证明中自蒸馏

Self-Distillation from Proof（SDP）让模型先生成带证明或推导的样本，再把通过验证的推理过程用于训练。关键是只保留可检查的轨迹，避免把错误或不忠实的解释蒸馏给 Student。

## 量化感知蒸馏

Student 在低精度约束下学习 Teacher 的行为，可以同时获得蒸馏带来的质量提升和量化带来的部署效率。对于小于 3B 的模型，量化感知训练通常比简单的训练后量化更重要。

## 面试问题

### Q：为什么蒸馏得到的 8B 模型可能优于用相同 token 从零训练的 8B 模型？

**强回答：**Teacher 提供的是经过压缩的高层行为信号，不只有原始 token。Student 可以直接学习答案、风格、推理模式和错误边界，因此比从原始数据重新发现这些模式更高效。

### Q：用 GPT-4o 作为 Teacher 蒸馏 Llama Student 有哪些风险？

**强回答：**风险包括 Teacher 的错误、偏见和风格被复制；Student 可能过拟合合成数据，丢失多样性；还可能出现模型坍缩、版权或许可证问题，以及把不可验证的思维链当作真推理。需要去重、事实校验、人工抽检、独立评测，并混合真实数据。

## 参考资料

- Hinton 等，《Distilling the Knowledge in a Neural Network》（2015）
- Gu 等，《MiniLLM: Knowledge Distillation of Large Language Models》（2024）
- DeepSeek-AI，《DeepSeek-R1》中的蒸馏模型说明

*下一篇：[合成数据生成](06-synthetic-data-generation.md)*
