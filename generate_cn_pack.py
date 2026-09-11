"""Generate Chinese detail and summary files for the first three study sections."""

from pathlib import Path


PACK = {
    "01-foundations/01-llm-internals.md": {
        "title": "LLM 内部机制",
        "detail": """# LLM 内部机制

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

解释架构时从输入 token、Embedding、位置编码、Transformer Block、Logits 到采样完整走一遍，再补充 KV Cache、参数规模、显存和吞吐。不要只说模型参数量，要说明推理时真正影响成本的是权重、激活、KV Cache、并发和序列长度。""",
        "summary": "理解 LLM 内部组件如何影响质量、显存、延迟和吞吐。重点掌握 Transformer、注意力、GQA、RoPE、Pre-LN、MoE 和 KV Cache 的系统设计含义。",
    },
    "01-foundations/02-tokenization-deep-dive.md": {
        "title": "Tokenization 深入理解",
        "detail": """# Tokenization 深入理解

## 核心概念

Tokenization 把文本转换成模型处理的 token ID。BPE、WordPiece 和 Unigram/SentencePiece 在词表构造、未知词处理、多语言和 token 数量上各有取舍。

## 为什么影响系统设计

Token 数决定上下文是否超限、输入输出成本、KV Cache 大小、吞吐和延迟。英文、中文、代码、JSON、空格和特殊符号的 token 化方式不同，不能用字符数简单代替 token 数。

## 生产实践

- 使用目标模型对应的 tokenizer 计算预算。
- 在 token 边界做截断和分块，避免把结构或代码从中间切断。
- 为系统提示、历史对话、检索上下文和输出预留独立预算。
- 对多语言、代码和结构化数据建立专门测试集。
- 记录 tokenizer 和模型版本，避免升级后成本和上下文行为发生隐性变化。

## 面试要点

能够解释词表大小、字符/子词/字节级方案的权衡，并说明 token 计数如何影响限流、成本估算、上下文压缩和 RAG 分块。""",
        "summary": "Tokenization 不只是预处理细节，它直接影响成本、上下文长度、分块、缓存和延迟。要掌握 BPE、WordPiece、SentencePiece、特殊 token 和多语言差异。",
    },
    "01-foundations/03-attention-mechanisms.md": {
        "title": "Attention 机制",
        "detail": """# Attention 机制

## 核心概念

Attention 通过 Query、Key、Value 计算序列中不同位置之间的相关性。Scaled Dot-Product Attention 会除以 √d_k，避免点积过大导致 Softmax 梯度过小；Causal Mask 保证生成 token 不能看到未来内容。

## 效率优化

- Sparse Attention 只连接部分位置，减少长序列计算。
- Linear Attention 用近似形式降低复杂度，但可能损失表达能力。
- FlashAttention 通过分块和 IO 优化减少显存读写，通常不改变数学结果。
- MQA/GQA 共享 Key/Value 头，显著减少 KV Cache 和带宽。
- Sliding Window Attention 只关注局部窗口，适合局部依赖明显的任务。

## 生产视角

区分 Prefill 和 Decode：Prefill 处理整段输入，计算密集；Decode 逐 token 生成，通常受 KV Cache、内存带宽和批处理影响。面试中应把注意力机制连接到 TTFT、TPS、上下文长度和 GPU 显存，而不只是讲公式。""",
        "summary": "掌握 Q/K/V、缩放点积、Causal Mask、MHA、MQA、GQA、FlashAttention 和 Prefill/Decode 的区别，理解它们对推理服务的影响。",
    },
    "01-foundations/04-transformer-architecture.md": {
        "title": "Transformer 架构",
        "detail": """# Transformer 架构

## 前向过程

输入文本先经过 Token Embedding 和位置表示，依次进入多个 Transformer Block。每个 Block 通常包含 Pre-Norm、Self-Attention、残差连接和 Feed-Forward Network，最后经过归一化和 Language Model Head 得到下一 token 的概率。

## 现代变体

Llama 类模型常使用 Pre-Norm、RoPE、RMSNorm 和 GQA；Mistral 等架构会加入滑动窗口或其他效率优化；MoE 通过专家路由扩大参数规模而控制激活计算；MLA 通过压缩潜在表示降低 KV Cache。

## 系统设计要点

参数数量影响训练和权重显存，序列长度和并发影响 KV Cache，token 生成速度决定在线延迟。解释 GPT-2 到现代模型的变化时，可从归一化、位置编码、注意力头、上下文、训练数据和服务优化几个维度比较。""",
        "summary": "从输入 token 到最终 logits 梳理 Transformer 前向过程，并理解 Llama、Mistral、MoE、MLA、Pre-Norm 和 GQA 等现代变体。",
    },
    "01-foundations/05-embeddings-and-vector-spaces.md": {
        "title": "Embedding 与向量空间",
        "detail": """# Embedding 与向量空间

## 核心概念

Embedding 把词、句子、文档或其他对象映射到向量空间，使语义相近的内容距离更近。Word2Vec 是静态表示，BERT 等模型提供上下文表示，Sentence/Document Embedding 面向检索和分类。

## 模型与指标

Bi-Encoder 分别编码查询和文档，速度快，适合大规模召回；Cross-Encoder 同时读取二者，精度高但成本更高，适合重排序。常用距离包括 Cosine、Dot Product 和 Euclidean，选择要与训练目标和向量归一化保持一致。

## 生产实践

关注批处理、缓存、分块、维度、量化、版本和漂移。Matryoshka Embedding 允许在不同维度截断向量，用于在质量、索引空间和延迟之间调整。Late Chunking 先编码更长上下文，再按块聚合，可保留跨段落信息。模型升级必须重新评测和管理索引版本。""",
        "summary": "理解 Embedding、Bi-Encoder、Cross-Encoder、距离度量、Matryoshka、Late Chunking、量化和 Embedding 版本漂移，重点关注 RAG 端到端效果。",
    },
    "01-foundations/06-inference-pipeline.md": {
        "title": "推理流水线",
        "detail": """# 推理流水线

## 生成过程

模型先执行 Prefill，处理输入上下文并建立 KV Cache；然后进入 Decode，逐 token 生成输出。采样可以使用 Greedy、Temperature、Top-K、Top-P 和重复惩罚，停止条件包括 EOS、最大 token 和 Stop Sequence。

## 关键指标

- TTFT：从请求到第一个 token 的时间。
- TPS：生成速度。
- Total Latency：完整响应时间。
- Throughput：单位时间处理的请求或 token 数。

## 生产优化

使用 Streaming/SSE 改善体验，Continuous Batching 提高吞吐，Prefix Caching 减少重复 Prefill，Speculative Decoding 提高 Decode 速度，Multi-LoRA 支持多个适配器。还要设置请求优先级、超时、降级、成本追踪和 GPU 显存预算。""",
        "summary": "掌握 Prefill/Decode、采样、TTFT、TPS、Streaming、Continuous Batching、Prefix Caching 和 Speculative Decoding，能把模型生成过程映射到线上指标。",
    },
    "02-model-landscape/01-model-taxonomy.md": {
        "title": "模型分类与版图",
        "detail": """# 模型分类与版图

## 分类方式

可以按能力等级、推理模式、上下文长度、部署方式、开放程度和专业领域分类。不要把模型名单当成永久知识，模型版本、价格和可用性会变化。

## Frontier 与开源模型

Frontier 模型通常在复杂推理、多模态、编码和 Agent 任务上能力强，但成本、配额、延迟和供应商依赖更高。开源模型提供权重控制、自托管、定制和隐私优势，同时要求团队承担 GPU、推理、升级、许可证和安全责任。

## 选择框架

先按任务建立能力基线，再比较质量、工具调用、结构化输出、长上下文、延迟、成本、区域、数据政策和生产成熟度。高频简单任务可路由到小模型，复杂任务使用强模型，关键是保持统一网关和评测体系。""",
        "summary": "模型版图变化很快，重点不是背模型名称，而是掌握按能力、推理、上下文、成本、部署和供应商风险进行分类与选择。",
    },
    "02-model-landscape/02-capability-assessment.md": {
        "title": "模型能力评估",
        "detail": """# 模型能力评估

## 为什么公开 Benchmark 不够

公开榜单的任务、数据、提示词和评分方式可能与实际产品不同，也无法充分反映工具调用、长上下文、领域术语、成本和稳定性。模型选择必须回到自己的任务集。

## 评估维度

包括任务正确性、Agent 工具使用、推理可靠性、校准、上下文召回、结构化输出、延迟、成本和安全。使用固定测试集、分层切片、LLM-as-Judge、人工抽检和线上 A/B。

## 实践流程

第一周定义标准并初筛，第二周做深度评测，第三周小流量生产验证。报告需要记录候选模型、结果、推荐、适用边界、成本、风险和回滚方案。注意小样本、模糊标准、评测泄漏、随机方差和成本盲区。""",
        "summary": "模型评估要从公开榜单转向真实任务集，综合质量、Agent 能力、可靠性、上下文、延迟、成本和安全，并经过离线、人工和线上验证。",
    },
    "02-model-landscape/03-pricing-and-costs.md": {
        "title": "模型价格与成本",
        "detail": """# 模型价格与成本

## 成本结构

API 可能按输入/输出 token、缓存、分层价格、承诺用量或批处理计费。完整成本还包括 Embedding、重排序、存储、GPU、带宽、重试、评测、监控和人工处理。

## 基本计算

```text
月成本 = 请求量 ×（输入 token × 输入单价 + 输出 token × 输出单价）
```

实际计算还要加入缓存命中、模型路由、失败重试和峰值容量。每次上线前都应进行月度预测，并按租户、功能和模型追踪实际成本。

## 优化策略

模型路由、Prompt/上下文压缩、缓存、批处理、输出长度控制和自托管都是常见方向。自托管还需计算 GPU、折旧、电力、工程、维护和闲置成本，不能只比较 API 单价。最终关注单位成功任务成本和质量回归。""",
        "summary": "建立完整成本模型，覆盖 token、缓存、重试、检索、GPU 和运维；用路由、压缩、缓存、批处理和输出控制降低单位成功任务成本。",
    },
    "02-model-landscape/04-model-selection-guide.md": {
        "title": "模型选择指南",
        "detail": """# 模型选择指南

## 选择框架

先判断任务是否需要复杂推理、工具调用、多模态、长上下文、低延迟或高吞吐，再评估质量、价格、可用性、配额、隐私、合规和运营能力。

## 多模型策略

统一模型网关后，可以使用请求路由、Cascade 和 Fallback：简单任务先走便宜模型，失败或质量不足时升级；关键供应商故障时切换备用模型。每个模型必须通过契约测试、质量评测、成本评估和灰度发布。

## 运营注意

不要让业务代码绑定单一 API。记录模型版本、Prompt、参数、路由理由和最终质量；对价格、限流、服务区域和供应商变更建立监控和回滚机制。""",
        "summary": "模型选择不是排行榜选择，而是围绕任务能力、质量、延迟、成本、可用性和风险的决策。推荐统一网关、多模型路由和可回滚设计。",
    },
    "03-training-and-adaptation/01-pretraining-basics.md": {
        "title": "预训练基础",
        "detail": """# 预训练基础

## 目标

预训练通常通过最小化下一个 token 的 Cross-Entropy Loss 学习通用语言和世界知识。数据质量、混合比例、去重、训练 token 数和模型规模共同决定最终能力。

## Scaling Laws

Chinchilla 范式强调模型参数和训练 token 的平衡；推理最优范式则会在部署成本和服务量较高时偏向更小、更高效的模型。不能只根据参数数量判断训练是否合理。

## 稳定性

Loss Spike 可能来自数据异常、学习率、数值精度或分布式同步问题。FP8 节省内存和计算，BF16 通常提供更宽的数值范围；实践中需要监控 loss、梯度、吞吐、通信和 checkpoint。

## 面试角度

能够解释为什么一个 8B 模型可能使用远多于理论最优的 token，也要知道 curriculum 如何改变数据难度和训练顺序。""",
        "summary": "掌握预训练目标、数据质量、Scaling Laws、Chinchilla、训练稳定性和 FP8/BF16，并能解释训练 token 与模型规模的权衡。",
    },
    "03-training-and-adaptation/02-fine-tuning-strategies.md": {
        "title": "微调策略",
        "detail": """# 微调策略

## 什么时候微调

当任务行为、风格、格式、工具调用或领域模式需要稳定改变，且拥有高质量数据时考虑微调。知识频繁变化或必须引用来源时，优先使用 RAG。

## 方法

SFT 使用高质量输入—输出示例；Continued Pretraining 让模型先适应领域语料；PEFT/LoRA 只训练少量参数，降低显存和存储成本；全参数微调成本高，但改变能力更彻底。

## 调参与风险

学习率、LoRA rank、batch、packing、序列长度和数据混合会影响结果。要防止灾难性遗忘，保留通用数据、降低学习率、混合任务、做通用能力回归和设置早停。

## 面试要点

说明为什么选择 Continued Pretraining 或 SFT，如何构建质量层级的数据，如何评估领域能力提升是否以通用能力下降为代价。""",
        "summary": "掌握 SFT、Continued Pretraining、PEFT、全参数微调和关键超参数，并能解释领域适应、质量数据和灾难性遗忘。",
    },
    "03-training-and-adaptation/03-lora-qlora-peft.md": {
        "title": "LoRA、QLoRA 与 PEFT",
        "detail": """# LoRA、QLoRA 与 PEFT

## LoRA 原理

LoRA 冻结基础权重 W，只训练低秩更新矩阵 A、B：`W' = W + α/r · BA`。它减少可训练参数、显存和适配器存储，适合多任务和多租户部署。

## QLoRA 与变体

QLoRA 将基础模型以 4-bit 量化加载，同时训练 LoRA 适配器；NF4、双重量化和分页优化器进一步降低显存。DoRA、rsLoRA 等变体分别改善权重方向/幅度或 rank 稳定性。

## Multi-LoRA Serving

共享一个基础模型，按请求加载 Finance、Legal、Medical 等适配器，可以节省重复权重成本，但要管理适配器版本、缓存、并发、租户权限和切换延迟。评估时同时比较适配效果和基础能力保持情况。""",
        "summary": "理解 LoRA 的低秩更新、QLoRA 的 4-bit 训练、DoRA/rsLoRA 变体和 Multi-LoRA 服务，重点关注显存、适配器隔离和质量保持。",
    },
    "03-training-and-adaptation/04-rlhf-and-dpo.md": {
        "title": "RLHF 与 DPO：对齐训练",
        "detail": """# RLHF 与 DPO

## 对齐问题

预训练模型学习的是语言分布，不一定符合用户偏好、帮助性、安全和格式要求。对齐训练利用偏好数据把模型行为推向目标。

## RLHF

典型 RLHF 流程包括 SFT、训练 Reward Model，再用 PPO 等强化学习优化策略。它灵活但工程复杂，需要处理奖励投机、训练不稳定、KL 约束和昂贵的在线采样。

## DPO

DPO 直接使用偏好对优化 chosen/rejected 概率，不需要单独在线训练 Reward Model，工程更简单、稳定性更好，但依赖高质量偏好数据和正确的参考策略。

## Reasoning 对齐

推理模型可以使用可验证奖励、程序化检查器和在线采样。对齐税表示安全或偏好优化可能损害通用能力，必须做通用能力回归和安全评测。""",
        "summary": "掌握 RLHF 的多阶段流程、DPO 的直接偏好优化、奖励投机、对齐税和推理模型的可验证奖励，能解释 DPO 的工程优势与数据依赖。",
    },
    "03-training-and-adaptation/05-knowledge-distillation.md": {
        "title": "知识蒸馏",
        "detail": """# 知识蒸馏

## Teacher-Student

大模型 Teacher 生成软概率、答案、解释或轨迹，Student 学习这些信息，在较小体积和更低成本下逼近 Teacher 能力。蒸馏通常比从相同 token 从零训练小模型更有效，因为 Teacher 提供了压缩后的行为信号。

## 方法

Hard Label 蒸馏学习最终答案；Soft Label 使用温度缩放后的概率和 KL Divergence；Output Distillation 学输出，Feature Distillation 学隐藏状态。还可以蒸馏推理过程、工具轨迹和可验证结果。

## 风险

Teacher 的错误、偏见、版权/隐私、格式习惯和奖励投机会被学生继承。使用 GPT-4o 等外部 Teacher 时，要验证许可、数据治理、领域覆盖、通用能力和安全行为，并建立独立测试集。""",
        "summary": "理解 Teacher-Student、Hard/Soft Label、Output/Feature Distillation、温度和 KL Loss，并注意 Teacher 错误、偏见、许可和能力退化风险。",
    },
    "03-training-and-adaptation/06-synthetic-data-generation.md": {
        "title": "合成数据生成",
        "detail": """# 合成数据生成

## 为什么使用合成数据

高质量人工数据稀缺且昂贵，合成数据可以扩展长尾场景、生成困难样本、提供程序化标签和训练偏好模型。Evol-Instruct 通过逐步增加约束把简单指令变成复杂任务。

## 质量控制

使用规则验证、编译/单元测试、来源模型交叉检查、去重、难度分层、人工抽样和污染检测。可验证任务应优先使用程序化奖励，而不是完全依赖模型评分。

## 风险

重复使用模型生成数据可能导致 Model Collapse、错误放大、风格收窄和偏差继承。要混合真实数据、保持多样性、去偏、跟踪数据版本，并用隐藏集和人工评测监控质量。""",
        "summary": "合成数据适合扩展长尾和可验证任务，但必须控制重复、错误、偏差和 Model Collapse；质量检测要结合规则、程序验证和人工抽样。",
    },
    "03-training-and-adaptation/07-quantization-deep-dive.md": {
        "title": "量化深入理解",
        "detail": """# 量化深入理解

## 核心权衡

量化把 FP16/BF16 权重或激活转换为更低精度表示，减少显存、带宽和成本，但可能损失质量或引入延迟。需要在目标模型、硬件、任务和并发下做基准。

## 方法

NF4 面向近似正态分布权重，常用于 QLoRA；AWQ 关注激活敏感权重；FP8 在现代 GPU 和多节点服务中提供速度与精度折中。GGUF 适合 llama.cpp 生态，EXL2 适合 ExLlamaV2。

## 进一步优化

KV Cache 量化可以降低长上下文服务的显存；QAT 在训练中模拟量化误差，通常比训练后量化更稳定但成本更高。关键业务要评估事实、格式、工具调用、长上下文和安全能力。

## 面试要点

说明 NF4 与普通 Float4 的区别、AWQ 与 GPTQ 的权衡，以及为什么量化选择必须和硬件、服务框架和质量门禁一起讨论。""",
        "summary": "掌握 NF4、AWQ、FP8、GGUF、EXL2、KV Cache Quantization 和 QAT，理解显存/吞吐/质量损失之间的关系。",
    },
    "03-training-and-adaptation/08-rlvr-and-reasoning-models.md": {
        "title": "RLVR 与推理模型训练",
        "detail": """# RLVR 与推理模型训练

## RLVR

Reinforcement Learning with Verifiable Rewards 使用程序化检查器提供奖励，例如数学答案、代码测试或规则验证。相比主观 Reward Model，它更容易复现、扩展和定位奖励来源。

## GRPO

GRPO 对同一问题采样一组答案，根据组内相对奖励优化策略，不需要为每个样本训练大型 Value Model。实现时要控制组大小、奖励稀疏、长度偏差、格式投机和训练稳定性。

## 能力与采样

强化学习可能创造新能力，也可能只是让模型更稳定地采样已有能力。要使用独立任务集、过程指标、泛化测试和人工分析判断到底发生了什么。

## 实践建议

先建立 SFT/蒸馏基线和可验证检查器，再逐步增加 RL。对奖励函数、失败样本、训练曲线、推理长度和通用能力做监控，并保留回滚模型。""",
        "summary": "理解 RLVR、GRPO、可验证奖励、奖励设计和失败模式；重点区分强化学习创造能力与提升已有能力采样稳定性的差异。",
    },
}


def main() -> None:
    for relative, data in PACK.items():
        source = Path(relative)
        zh = source.with_suffix(".zh.md")
        summary = source.with_suffix(".summary.md")
        zh.write_text(data["detail"].rstrip() + "\n", encoding="utf-8")
        summary.write_text(
            f"# 《{data['title']}》中文概要\n\n{data['summary']}\n",
            encoding="utf-8",
        )
        print(f"generated {zh} and {summary}")


if __name__ == "__main__":
    main()
