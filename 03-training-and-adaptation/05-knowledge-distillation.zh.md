# 知识蒸馏

## Teacher-Student

大模型 Teacher 生成软概率、答案、解释或轨迹，Student 学习这些信息，在较小体积和更低成本下逼近 Teacher 能力。蒸馏通常比从相同 token 从零训练小模型更有效，因为 Teacher 提供了压缩后的行为信号。

## 方法

Hard Label 蒸馏学习最终答案；Soft Label 使用温度缩放后的概率和 KL Divergence；Output Distillation 学输出，Feature Distillation 学隐藏状态。还可以蒸馏推理过程、工具轨迹和可验证结果。

## 风险

Teacher 的错误、偏见、版权/隐私、格式习惯和奖励投机会被学生继承。使用 GPT-4o 等外部 Teacher 时，要验证许可、数据治理、领域覆盖、通用能力和安全行为，并建立独立测试集。
