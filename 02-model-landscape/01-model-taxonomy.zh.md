# 模型分类

本章全面介绍截至 **2026 年 8 月**的模型版图，覆盖模型家族、能力和生产系统中的选择标准。

> **最后核验：2026 年 8 月 15 日。**模型版图变化很快，请始终与提供商的价格页面和发布说明交叉核对。
>
> **2026 年 8 月要点：**本月大多数发布是训练后刷新版本或衍生版本，而不是新的预训练运行；美国前沿实验室没有发布新的旗舰基础模型。变化主要集中在价格、许可证和访问控制上。明显例外是阿里巴巴的 Qwen3.8-Max：这是一个真正全新的 2.4T 基础模型，权重于 8 月 12 日发布。**Claude Sonnet 5 的每 1M token 2/10 美元介绍价于 8 月 10 日转为永久价格**，原定 9 月 1 日上调至 3/15 美元的计划被取消，因此 Sonnet 5 永久低于它所替代的 Sonnet 4.6。另一方面，**DeepSeek 从 8 月 16 日 16:00 UTC 起将 V4 价格提高 3 到 12 倍**，改为高峰/非高峰计费（非高峰价格正好是高峰的一半，高峰只覆盖 01:00–04:00 和 06:00–10:00 UTC），结束了它作为绝对低价选项的阶段。**OpenAI 发布了 GPT-5.6-Cyber**（8 月 10 日，每 1M token 12.50/75 美元），配套新的 Daybreak Blue 和 Daybreak Red 两级访问计划，这是目前能力分级准入最具体的生产案例。**Google 发布 Gemini 3.7 Flash**（8 月 13 日），年末前半价；**SpaceXAI 发布 Grok 4.6**（8 月 12 日），上下文为 500K。在开放权重方面，许可证出现分化：**阿里巴巴的 Qwen3.8-Max**（8 月 12 日，2.4T/95B 激活）使用定制的商业门控许可证，而其 **Qwen3.8-27B** 兄弟模型（8 月 14 日）采用普通 Apache 2.0；**Meta 以 Muse Glimmer 回归开放权重**（8 月 10 日，30B，Apache 2.0）；**Z.ai 暂缓 GLM-5.3 权重**，等待安全评估，因为其网络安全能力增长快于预期。**Claude Opus 4.1 于 8 月 5 日退役**，最后一个 15/75 美元 Opus 档位结束。本节基准数据大多由厂商报告，请在独立榜单上确认。
>
> **2026 年 7 月要点：**Anthropic 发布完整一代更新：**Claude Sonnet 5**（6 月 30 日，`claude-sonnet-5`，全产品新默认，介绍价为每 1M token 2/10 美元，8 月 31 日后原计划调整至 3/15）和 **Claude Opus 5**（7 月 24 日，`claude-opus-5`，价格仍为 5/25，另有 10/50 美元、速度约快 2.5 倍的 Fast 模式）。**Claude Fable 5 于 7 月 1 日全球恢复**，此前曾因出口管制暂停，并新增针对越狱的网络安全分类器；Mythos 5 只通过 Project Glasswing 向约 100 家美国机构恢复。**GPT-5.6（Sol、Terra、Luna）于 7 月 9 日正式可用**；7 月 30 日 OpenAI 将 Luna 价格下调 80% 至 0.20/1.20 美元，将 Terra 下调 20% 至 2/12 美元（Sol 仍为 5/30）。开放权重前沿迎来历史上最强的月份：**Moonshot Kimi K3**（7 月 16 日，权重 7 月 27 日）以 2.8T 总参数/104B 激活参数和 1M 上下文成为迄今最大的开放权重模型，**Thinking Machines Lab** 发布 **Inkling**（7 月 15 日，975B/41B 激活，开放权重），成为领先的美国开放权重模型。Google 发布 Gemini 3.6 Flash、3.5 Flash-Lite 和政府门控的 3.5 Flash Cyber（7 月 21 日），Gemini 3.5 Pro 延期。**Meta Muse Spark 1.1**（7 月 9 日）上线 Meta 首个付费自助模型 API（每 1M token 1.25/4.25 美元）。Black Forest Labs 宣布 **FLUX 3**（7 月 23 日），这是统一的图像、视频、音频和动作模型，处于门控早期访问。本月发布的基准数据大多由厂商报告，请在独立榜单上确认。
>
> **2026 年 6 月要点：**Anthropic 发布 **Claude Fable 5**（6 月 9 日，`claude-fable-5`，每 1M token 10/50 美元，1M 上下文），这是其最强的广泛发布模型：一个为公开可用而加上安全措施的 Mythos 级模型，在敏感主题上有 Opus 4.8 回退保护。**Claude Mythos 5** 同日作为 Project Glasswing 合作伙伴使用的非限制版本发布，价格不到 Mythos Preview 的一半。
>
> **6 月 10–26 日更新：**6 月随后出现密集的第二波发布。**Google DeepMind DiffusionGemma**（6 月 10 日，Apache 2.0）是 Google DeepMind 首个开放权重文本扩散模型：26B 的专家混合模型（约 4B 激活），并行去噪 token 块，在单张 H100 上生成速度约快 4 倍，但质量低于标准 Gemma 4。**Gemini 3.5 Live Translate**（6 月 9 日，基于 Gemini 3 Pro）通过 Gemini Live API 和 AI Studio 公共预览，增加了 70+ 语言的实时语音到语音翻译。**Cohere North Mini Code 1.0**（6 月 9 日，Apache 2.0）是 Cohere 首个开放编码模型，30B/3B 激活的 MoE，可运行在一张 H100 上。**Moonshot Kimi K2.7 Code**（6 月 12 日，Modified MIT）针对长周期软件工作优化 K2.6（1T/32B 激活 MoE），思考 token 约少 30%。**Z.ai GLM-5.2**（6 月 13 日开放编码计划访问，6 月 16–17 日以 MIT 开放权重）是 744B/40B 激活的 MoE，拥有 1M 上下文，报告 SWE-Bench Pro 为 62.1，超过 GPT-5.5，价格约每 1M token 1.40/4.40 美元。**xAI Grok Imagine Video 1.5** 于 6 月 16 日正式可用（带同步音频的图生视频，每秒视频 0.080 美元），**Grok 4.3** 于 6 月 15 日登陆 Amazon Bedrock（每 1M token 1.25/2.50 美元）。阿里巴巴官方 Qwen Cloud 更新日志列出了 6 月快照，其中为 **Qwen 3.7-Max** 增加视觉能力（5 月发布时仅支持文本），但部分独立报道把这一视觉更新归因于 Qwen 3.7-Plus，依赖前请核实。另据报道，Anthropic 在 6 月 12 日因美国出口管制指令暂停 Claude Fable 5 和 Claude Mythos 5 的访问，随后 Mythos 5 获准向有限美国机构开放。6 月 26 日，OpenAI 预览 **GPT-5.6**（Sol、Terra、Luna），因双用途网络安全能力问题，仅向少量获美国政府批准的合作伙伴发布；Sol 声称刷新 Terminal-Bench 2.1 纪录，Terra 目标是以约一半成本提供 GPT-5.5 级质量。本段编码分数大多由厂商报告，请在独立榜单上确认。
>
> **2026 年 5 月回顾：**Anthropic Claude Opus 4.8（5 月 28 日，价格与 Opus 4.7 相同；Dynamic Workflows 研究预览支持数百个并行子智能体；10/50 美元 Fast 模式比 Opus 4.7 Fast 便宜 3 倍）；OpenAI GPT-5.5（4 月 23 日）与 GPT-5.5 Instant（5 月 5 日，ChatGPT 默认）；Claude Opus 4.7（4 月 16 日，在 Bedrock/Vertex/Foundry 正式可用）；Google Gemma 4（4 月 2 日，Apache 2.0）和 Gemini 3.2 Flash（5 月 5 日低调推出）；DeepSeek V4 Pro 和 V4 Flash（4 月 24 日；V4 Pro 的 75% 折扣于 5 月 22 日转为永久，6 月 1 日起每 1M token 新标价为 0.435/0.87 美元）；Moonshot Kimi K2.6（4 月 20 日，1T MoE/32B 激活）；阿里巴巴 Qwen 3.6 Plus/3.6-35B-A3B/3.6 Max-Preview；Mistral Medium 3.5（4 月 29 日，统一聊天/推理/编码/视觉）；Meta Muse Spark（4 月 8 日，Meta 首个闭源权重模型）；Llama 4 Behemoth 因能力问题暂停发布至 2026 年秋。Fable 5 发布前，SWE-bench Verified 已发布领先者为 Claude Mythos Preview 93.9%、GPT-5.5 88.7%、Claude Opus 4.8 88.6%；ARC-AGI-2 领先者为 GPT-5.5 的 85.0%。Anthropic 称 Fable 5 在几乎所有测试基准上达到 SOTA，但发布文章未给出标准数值，请在榜单上核验。

## 目录

- [模型类别](#模型类别)
- [前沿模型（2026 年 5 月）](#前沿模型)
- [推理模型](#推理模型)
- [开源模型](#开源模型)
- [专业模型](#专业模型)
- [Embedding 模型](#embedding-模型)
- [模型选择框架与语义路由](#模型选择框架)
- [主权 AI 与数据驻留](#主权-ai-与数据驻留)
- [能力对比](#能力对比)
- [面试问答](#面试问答)
- [参考资料](#参考资料)

---

## 模型类别

### 按能力等级分类（2026 年 4 月实际情况）

| 层级 | 特征 | 示例 | 使用场景 |
|------|-----------------|----------|----------|
| **前沿** | SOTA 推理、Agent 能力强 | Claude Fable 5、Claude Opus 4.8、GPT-5.5、Gemini 3.1 Pro、Grok 4.3 | 复杂推理、编码、生产 Agent |
| **快速/高效** | 低于 200ms，成本优化 | Gemini 3.1 Flash、GPT-5.5-mini、Claude Haiku 4.5、DeepSeek V4 Flash | 高并发流式、UI、实时任务 |
| **经过验证** | 成熟、广泛部署、稳定 | Claude Sonnet 4.6、GPT-5.5 Instant、Gemini 3.1 Pro | 企业生产负载 |
| **小型/边缘** | 私有、边缘、专用 | Llama 4 Scout、Mistral Small 4、Phi-4 | 本地隐私、端侧、MoE 高效场景 |
| **重推理** | 扩展的内部 CoT | Claude Opus 4.8（thinking）、GPT-5.5 reasoning、Gemini 3.1 Pro Deep Think、DeepSeek-R1 | 数学、代码调试、多步逻辑 |

### 按推理模式分类（2025–2026）

| 模式 | 能力 | 模型 | 使用场景 |
|------|------------|--------|----------|
| **标准** | 快速、直觉式响应 | GPT-5.5-mini、Claude Sonnet 4.6 | 聊天、简单抽取 |
| **扩展思考** | 输出前使用内部草稿本 CoT | Claude Opus 4.8、GPT-5.5 reasoning、DeepSeek-R1 | 数学、代码调试、规划 |
| **混合** | 用户可控制推理深度 | Claude Opus 4.8、GPT-5.5 | 复杂度可变的任务 |

---

## 前沿模型（2026 年 6 月）

### Claude Opus 5（Anthropic）— 2026 年 7 月新发布

| 属性 | 值 |
|-----------|-------|
| 模型 ID | `claude-opus-5` |
| 上下文窗口 | 1M token（默认和上限；最大输出 128K） |
| 输入/输出成本 | 每 1M token 5.00/25.00 美元（与 Opus 4.8 相同） |
| Fast 模式 | 每 1M token 10.00/50.00 美元，速度约快 2.5 倍 |
| 基准 | Anthropic 发布文章报告了其称为 Frontier-Bench v0.1 的预发布基准（后改名为 Terminal-Bench 3.0）：最大努力下 43.3%，GPT-5.6 Sol 为 34.4%、Fable 5 为 33.7%、Opus 4.8 为 18.7%。CursorBench 3.2 上与 Fable 5 相差不到 0.5%，每个任务成本约为其一半；ARC-AGI 3 约为次优模型的 3 倍。厂商报告。 |
| 发布 | 2026 年 7 月 24 日（Claude API、Claude Code、Claude Cowork；Claude Max 新默认） |

**它是什么：**Opus 系列的下一代模型，价格不变，目标是长周期 Agent 编码和计算机使用。Beta 功能包括对话中途更换工具和自动回退路由。双价格 Fast 模式延续了 Opus 4.8 开创的模式：同一模型提供两个延迟档位。

**最适合：**不需要 Fable 5 能力上限的 Agent 编码和计算机使用负载；截至 2026 年 7 月下旬，它是 Claude 系列中性价比最高的旗舰。

### Claude Sonnet 5（Anthropic）— 2026 年 7 月新发布

| 属性 | 值 |
|-----------|-------|
| 模型 ID | `claude-sonnet-5` |
| 上下文窗口 | 第三方报道为 1M token（发布文章未说明） |
| 输入/输出成本 | 每 1M token 2.00/10.00 美元（自 2026 年 8 月 10 日起永久有效） |
| Cache/Batch | Cache 写入每 1M token 2.50 美元（5 分钟）或 4.00 美元（1 小时）；命中 0.20 美元；Batch API 为 1.00/5.00 美元 |
| 定位 | Agent 能力最强的 Sonnet：规划、浏览器和终端工具使用、自主运行能力接近较低成本的 Opus 4.8 |
| 安全姿态 | 默认启用网络安全保护；相较 Opus 级模型刻意降低网络安全能力 |
| 发布 | 2026 年 6 月 30 日（同日成为消费者和开发者产品默认模型） |

**它是什么：**新的生产主力，取代 Sonnet 4.6 成为默认模型。2026 年 8 月 10 日，Anthropic 将 2/10 美元介绍价永久化，并取消 9 月 1 日上调至 3/15 美元的计划，因此 Sonnet 5 永久低于它所取代的 Sonnet 4.6（仍为 3/15）。基于涨价假设建立的成本模型需要下调。

**最适合：**生产 Agent 集群、大规模编码，以及成本感知路由栈中的默认层。

### Claude Fable 5（Anthropic）— 2026 年 6 月新发布

| 属性 | 值 |
|-----------|-------|
| 模型 ID | `claude-fable-5` |
| 上下文窗口 | 1M token（Opus 4.7 Tokenizer；相同文本约比 4.7 之前模型多 30% token） |
| 最大输出 | 128K token |
| 输入成本 | 每 1M token 10.00 美元 |
| 输出成本 | 每 1M token 50.00 美元 |
| 思考 | 始终开启的自适应思考（无单独扩展思考开关） |
| 多模态 | 文本 + 视觉（Anthropic 称其视觉任务达到新 SOTA） |
| 基准 | Anthropic 称在几乎所有测试基准上达到 SOTA；Cognition FrontierCode、Hebbia Finance Benchmark、ViBench、CursorBench 达到最高前沿分数。发布文章未公布 SWE-bench、GPQA 等标准数值。 |
| 发布 | 2026 年 6 月 9 日（Claude API、AWS Claude Platform、Amazon Bedrock、Vertex AI、Microsoft Foundry 正式可用） |

**它是什么：**一个为普遍可用而加入安全措施的 Mythos 级模型。此前 Mythos 系列（Mythos Preview 的 SWE-bench Verified 为 93.9%）因双用途网络安全问题，仅限约 11 个 Project Glasswing 合作伙伴。Fable 5 通过保守安全措施，把这一能力层级带给所有人。

**Opus 4.8 回退保护：**当 Fable 5 的分类器检测到三类请求（攻击性网络技术、生物武器相关的生物/化学内容、试图蒸馏模型）时，响应会静默委托给 **Claude Opus 4.8**，并告知用户。Anthropic 表示该机制触发比例低于 5%，且刻意设置得较保守，因此一些无害请求也可能被捕获。从架构看，这是**模型层级路由作为安全控制**的生产案例，而不只是成本控制。

**最适合：**要求最高的推理、长周期 Agent 工作、视觉密集任务，以及能力上限比单位成本更重要的负载。Anthropic 称它能比此前任何 Claude 模型维持更长时间的自主运行。

**注意事项：**每 token 价格是 Opus 4.8 的 2 倍（10/50 对 5/25），因此只应把受能力上限约束的任务路由到它。Mythos 级流量要求保留数据 30 天（不用于训练、会记录访问日志，几乎所有情况下 30 天后删除），合规审查时需要考虑。订阅计划在 6 月 9–22 日免费包含，随后改用使用额度。发布时没有 Fable 档 Fast 模式，也没有公布缓存/批处理折扣，请核对价格页面。

### Claude Mythos 5（Anthropic）— 受限访问

| 属性 | 值 |
|-----------|-------|
| 模型 ID | `claude-mythos-5` |
| 状态 | 限量可用：Project Glasswing 合作伙伴和部分生物学研究人员 |
| 关系 | 与 Fable 5 使用相同基础模型，但部分区域取消安全措施 |
| 价格 | 每 1M token 10/50 美元（不到 Mythos Preview 的一半） |
| 发布 | 2026 年 6 月 9 日 |

**为什么重要：**它以相当或略强的能力、低得多的价格接替 Claude Mythos Preview。Fable/Mythos 的拆分正式形成双轨发布模式：一个有安全保护、面向大众的版本，一个面向经过审查的防御方的非限制版本。

### Claude Opus 4.8（Anthropic）— 2026 年 5 月

| 属性 | 值 |
|-----------|-------|
| 上下文窗口 | 1M token（整个窗口采用标准价格） |
| 输入成本 | 每 1M token 5.00 美元（与 4.7 相同） |
| 输出成本 | 每 1M token 25.00 美元（与 4.7 相同） |
| 缓存：5 分钟写入 | 每 1M token 6.25 美元 |
| 缓存：1 小时写入 | 每 1M token 10.00 美元 |
| 缓存：命中/刷新 | 每 1M token 0.50 美元 |
| Batch API | 每 1M token 2.50/12.50 美元（折扣 50%） |
| Fast 模式（研究预览） | 每 1M token 10/50 美元（速度约快 2.5 倍；比 Opus 4.7 Fast 的 30/150 美元便宜 3 倍） |
| 扩展思考 | 原生、自适应模式 |
| 多模态 | 文本 + 高分辨率视觉 |
| SWE-bench Verified | 88.6% |
| SWE-Bench Pro | 69.2%（Opus 4.7 为 64.3%） |
| Terminal-Bench 2.1 | 74.6%（GPT-5.5 仍以 78.2% 领先） |
| GDPval-AA | 1890 Elo（Opus 4.7 为 1753） |
| OSWorld-Verified | 82.3% |
| Online-Mind2Web | 84% |
| 发布 | 2026 年 5 月 28 日（Claude API、AWS Bedrock、Vertex AI 正式可用） |

**最适合：**Claude Code 中的长时间自主编码、代码库规模迁移、需要并行子智能体的 Agent 工作流，以及重视对齐和诚实性提升的负载。

**相较 Opus 4.7 的关键功能：**
- **Dynamic Workflows**（研究预览）：Claude 规划工作，在一个 Claude Code 会话中运行数百个并行子智能体，验证结果后返回报告，适合数十万行代码的迁移。
- **任务中途系统消息**：Messages API 现在接受对话中途的系统消息，可在不结束会话的情况下引导长时间 Agent 运行。
- **可选 Fast 模式**：每 1M token 10/50 美元，速度约快 2.5 倍，比 Opus 4.7 Fast 低 3 倍。
- **Effort 控制开关**：`claude.ai` 和 Cowork 允许用户逐轮调节推理深度。
- **扩展 Claude Code 速率限制**。

**注意事项：**Tokenizer 与 Opus 4.7 相同（同一固定文本的 token 数最多比 4.7 之前多 35%）。GPT-5.5 仍以 88.7% 领先 SWE-Bench Verified 榜单，并以 78.2% 领先 Terminal-Bench 2.1。GPQA Diamond 比 Opus 4.7 低 0.6 个百分点。Anthropic 的 Tokenizer 变更意味着，同一文本在 4.7 之前模型与当前模型中的 token 数和账单不能直接比较。没有 Claude Sonnet 4.8；产品线于 2026 年 6 月 30 日直接跳到 **Claude Sonnet 5**，取代 Sonnet 4.6 成为生产主力。

> [!NOTE]
> **2026 年 8 月 5 日退役：**`claude-opus-4-1-20250805` 已从 Claude API 移除，最后一个每 1M token 15/75 美元的 Opus 档位结束。Anthropic 第一方 Opus SKU 现在都是 5/25 美元（Fast 模式为 10/50）。Amazon Bedrock 和 Google Cloud 仍可能提供该模型，并按各自计划退役；因此绑定该 ID 的第一方 API 代码会失败，但合作云上仍可能工作。

### Claude Opus 4.7（Anthropic）

| 属性 | 值 |
|-----------|-------|
| 上下文窗口 | 1M token |
| 最大输出 | 128K token |
| 输入成本 | 每 1M token 5.00 美元（与 4.6 相同） |
| 输出成本 | 每 1M token 25.00 美元（与 4.6 相同） |
| 扩展思考 | 原生、自适应模式 |
| 多模态 | 文本 + 高分辨率视觉 |
| SWE-bench Verified（Adaptive） | 87.6%（2026 年 5 月 13 日） |
| 发布 | 2026 年 4 月 16 日（API、Bedrock、Vertex、Microsoft Foundry 正式可用） |

**最适合：**自主编码 Agent（驱动 Claude Code）、多文件重构、复杂推理。与 4.6 价格相同，对大多数负载是直接升级。
**注意事项：**成本敏感负载使用 Sonnet 4.6；Opus 4.7 主要用于要求最高编码/Agent 质量的任务。

### Claude Mythos Preview（Anthropic）— 已由 Mythos 5 接替

| 属性 | 值 |
|-----------|-------|
| 状态 | 受限研究预览，仅 Project Glasswing 合作伙伴（约 11 个组织：AWS、Apple、Cisco、Google、Microsoft、NVIDIA、Palo Alto 等） |
| 限制原因 | 双用途网络安全能力 |
| SWE-bench Verified | 93.9%（2026 年 5 月 13 日；Fable 5/Mythos 5 发布前已公布的 SOTA） |
| 发布 | 2026 年 4 月 7 日（受限合作伙伴预览）；2026 年 6 月 9 日由 Claude Mythos 5 接替，价格不到其一半 |

**最适合：**历史参考。其能力层级已在 2026 年 6 月 9 日通过 Claude Fable 5 普遍可用；新的 Glasswing 工作应使用 Mythos 5。

### Claude Opus 4.6（Anthropic）

| 属性 | 值 |
|-----------|-------|
| 上下文窗口 | 1M token |
| 最大输出 | 128K token |
| 输入成本 | 每 1M token 5.00 美元 |
| 输出成本 | 每 1M token 25.00 美元 |
| 扩展思考 | 原生自适应思考（可配置 `budget_tokens`） |
| 多模态 | 文本 + 视觉 |
| 亮点 | Anthropic 最强模型；编码和推理能力突出 |
| 发布 | 2026 年 2 月 |

**最适合：**最复杂的推理、自主软件工程、Agent 工作流。
**注意事项：**价格较高；不需要能力上限的任务使用 Sonnet 4.6。

### Claude Sonnet 4.6（Anthropic）

| 属性 | 值 |
|-----------|-------|
| 上下文窗口 | 1M token |
| 输入成本 | 每 1M token 3.00 美元 |
| 输出成本 | 每 1M token 15.00 美元 |
| 扩展思考 | 支持 |
| 多模态 | 文本 + 视觉 |
| 亮点 | 能完成过去需要 Opus 档的任务；质量/成本平衡最佳 |
| 发布 | 2026 年 2 月 |

**最适合：**生产编码 Agent（驱动 Claude Code）、大规模复杂推理。
**注意事项：**以较低成本覆盖大多数 Opus 级任务，是多数负载的强默认选择。

### GPT-5.4（OpenAI）

| 属性 | 值 |
|-----------|-------|
| 上下文窗口 | 272K token（标准；可扩展） |
| 输入成本 | 每 1M token 2.50 美元 |
| 输出成本 | 每 1M token 15.00 美元 |
| 多模态 | 文本、视觉、原生计算机使用 |
| 亮点 | 内置计算机使用；相较 GPT-5.2 少 33% 事实错误；结合编码和 Agent 能力 |
| 发布 | 2026 年 3 月 |

**最适合：**需要计算机使用的 Agent 工作流、编码、专业任务。
**注意事项：**上下文达到 272K+ token 时价格翻倍。

### GPT-5.4-mini（OpenAI）

| 属性 | 值 |
|-----------|-------|
| 上下文窗口 | 272K token |
| 输入成本 | 每 1M token 0.75 美元 |
| 输出成本 | 每 1M token 4.50 美元 |
| 亮点 | 高并发 GPT-5 档负载的质量/成本最佳 |
| 发布 | 2026 年 3 月 |

**最适合：**高并发 API、成本优化推理、生产聊天机器人。

### GPT-5.4 Pro（OpenAI）

| 属性 | 值 |
|-----------|-------|
| 上下文窗口 | 272K token |
| 输入成本 | 每 1M token 30.00 美元 |
| 输出成本 | 每 1M token 180.00 美元 |
| 亮点 | 最大推理能力；最难任务的高级档 |
| 发布 | 2026 年 3 月 |

**最适合：**竞赛级数学、复杂多步推理。
**注意事项：**非常昂贵；批量任务使用标准 GPT-5.4 或 mini。

### GPT-5.6 Sol/Terra/Luna（OpenAI）— 2026 年 7 月 9 日正式可用

| 属性 | 值 |
|-----------|-------|
| 变体 | Sol（旗舰）、Terra（均衡）、Luna（快速、低成本） |
| 上下文窗口 | 三者均为 1M token；最大输出 128K；知识截止日期 2026 年 2 月 16 日 |
| Sol 价格 | 每 1M token 5.00/30.00 美元 |
| Terra 价格 | 每 1M token 2.00/12.00 美元（7 月 30 日从 2.50/15 下调 20%） |
| Luna 价格 | 每 1M token 0.20/1.20 美元（7 月 30 日从 1/6 下调 80%） |
| 推理 | “max” 推理力度，另有使用子智能体加速复杂任务的 “ultra” 模式 |
| GA API 功能 | 程序化工具调用、多 Agent 支持、显式 Prompt Cache 断点 |
| 基准 | Sol 在 Agents' Last Exam 得分 53.6，比 Claude Fable 5 高 13.1 分，并刷新 Terminal-Bench 2.1 纪录。Claude Fable 5 仍在 SWE-Bench Pro 领先（80 对 Sol 的 64.6），OpenAI 公开质疑该基准。厂商报告。 |
| 发布 | 2026 年 6 月 26 日限量预览；2026 年 7 月 9 日正式可用 |

**它是什么：**OpenAI 首次以三个模型推出的下一代旗舰产品线。6 月 26 日的预览版因美国政府担忧双用途网络安全能力而设置门控，13 天审查后正式发布。三层结构和 7 月 30 日的大幅降价（Luna 0.20/1.20 美元，对标开放权重竞争）重新定义了分层模型选择的路由计算。

**最适合：**Sol 用于前沿 Agent 工作和网络安全相关编码；Terra 以约 GPT-5.5 一半的价格作为 GPT-5.5 级生产默认；Luna 用于高并发分类、抽取和路由层。

### GPT-5.6-Cyber（OpenAI）— 2026 年 8 月新发布（受限）

| 属性 | 值 |
|-----------|-------|
| 模型 ID | `gpt-5.6-cyber` |
| 上下文窗口 | 总计 400K（最大输入 272K，最大输出 128K） |
| 输入/输出成本 | 每 1M token 12.50/75.00 美元；缓存输入 1.25 美元 |
| 访问 | 仅 Daybreak Red，要求身份验证、法律声明和获批用例；仅限 Responses API。个人 Daybreak 账户自 2026 年 9 月 1 日起必须使用硬件安全密钥 |
| 拒答姿态 | 针对双用途安全工作训练为较低拒答率：OpenAI 内部 Advanced Cybersecurity Completion Rate 评估完成率 95.0%，GPT-5.6 Sol 为 1.5% |
| 发布 | 2026 年 8 月 10 日（Daybreak Blue/Red 拆分出现在 8 月 7 日 API 更新日志） |

**它是什么：**基于 GPT-5.6 Sol 构建的网络安全模型，与 Daybreak 计划拆分为两级同时发布。**Daybreak Blue**让获批防御方使用通用前沿模型进行漏洞发现、安全代码审查、检测工程和事件响应。**Daybreak Red**需要单独批准，用于漏洞复现、漏洞利用验证、渗透测试和红队工作，并对 `gpt-5.6-cyber` 进行门控。

**架构上为什么重要：**这是目前最清晰的能力分级门控生产实例。一个比前沿默认更宽松、价格为 Sol 2.5 倍、限制在单一 API 表面、并以身份验证和强制硬件双因素认证保护的模型，为实验室如何运营双用途访问提供了参考设计。Anthropic 的 Fable 5/Mythos 5 拆分和 Google 的 Gemini 3.5 Flash Cyber 也属于同一模式的不同变体。

### GPT-5.5（OpenAI）— 2026 年 5 月新发布

| 属性 | 值 |
|-----------|-------|
| 上下文窗口 | 1M token |
| 输入成本 | 每 1M token 5.00 美元 |
| 输出成本 | 每 1M token 30.00 美元 |
| 多模态 | 文本、图像、音频、视频 |
| ARC-AGI-2 | 85.0%（2026 年 5 月 13 日，领先） |
| 发布 | 2026 年 4 月 23 日 |

**最适合：**最高质量的多模态负载；当前 ARC-AGI-2 领先者。定位为“面向真实工作的全新智能类别”，取代 GPT-5.4，承担顶级推理和多模态任务。
**注意事项：**输入价格约为 GPT-5.4 的 2 倍（2.50 → 5.00 美元），输出价格约为 2 倍（15 → 30 美元）。聊天任务若不需要这一质量，可使用 GPT-5.5 Instant。

### GPT-5.5 Instant（OpenAI）— 2026 年 5 月新发布

| 属性 | 值 |
|-----------|-------|
| 状态 | 自 2026 年 5 月 5 日起成为 ChatGPT 和 API `chat-latest` 默认 |
| 幻觉减少 | 与 GPT-5.3 Instant 相比，高风险 Prompt（医疗/法律/金融）幻觉少 52.5% |
| AIME 2025 | 81.2%（GPT-5.3 Instant 为 65.4%） |
| 响应长度 | 比前代少约 30% 的词/行 |
| 发布 | 2026 年 5 月 5 日 |

**最适合：**ChatGPT 等价负载、即时聊天、重视降低幻觉的高风险领域。
**注意事项：**取代 GPT-5.3 Instant 成为聊天默认；GPT-5.2-chat-latest 和 GPT-5.3-chat-latest 于 2026 年 5 月 8 日弃用。

### GPT-Realtime-2、Translate、Whisper（OpenAI）— 2026 年 5 月新发布

| 属性 | 值 |
|-----------|-------|
| 能力 | 具备 GPT-5 级推理的实时语音 |
| 翻译覆盖 | 70+ 输入语言 → 13 种输出语言 |
| 价格 | 每 1M 音频 token 输入/输出 32/64 美元 |
| 发布 | 2026 年 5 月 7 日 |

**最适合：**实时语音 Agent、多语言翻译、语音优先产品。Realtime API Beta 于 2026 年 5 月 12 日移除，Realtime-2 是受支持的路径。

### Gemini 3.1 Pro（Google）

| 属性 | 值 |
|-----------|-------|
| 上下文窗口 | 1M token |
| 输入成本 | 每 1M token 2.00 美元（标准）；200K+ 为 4.00 美元 |
| 输出成本 | 每 1M token 12.00 美元（标准）；200K+ 为 18.00 美元 |
| 多模态 | 原生：文本、视觉、音频、视频 |
| 亮点 | Google 推理 SOTA；Agent 和编码能力强 |
| 发布 | 2026 年 2 月 |

**最适合：**复杂推理、多模态分析、长上下文负载。
**注意事项：**取代 Gemini 3 Pro Preview；Gemini 2.5 Pro/Flash 于 2026 年 6 月弃用。

### Gemini 3.1 Flash（Google）

| 属性 | 值 |
|-----------|-------|
| 上下文窗口 | 1M token |
| 输入成本 | 每 1M token 0.10 美元 |
| 输出成本 | 每 1M token 3.00 美元 |
| 多模态 | 原生：文本、视觉、音频、视频 |
| 亮点 | Google 最快模型；高并发场景质量/价格最佳 |
| 发布 | 2026 年 3 月 |

**最适合：**实时多模态应用、高并发流水线、长上下文 RAG。

### Gemini 3.2 Flash（Google）— 2026 年 5 月新发布

| 属性 | 值 |
|-----------|-------|
| 状态 | 2026 年 5 月 5 日在 iOS Gemini 应用和 Google AI Studio 低调推出（尚无正式公告） |
| 发布 | 2026 年 5 月 5 日 |

**最适合：**可能成为 3.1 Flash 的高并发继任者。应视为预览版，等待正式发布后确认价格和完整能力。

### Gemini Deep Research/Deep Research Max（Google）— 2026 年 5 月新发布

| 属性 | 值 |
|-----------|-------|
| 构建于 | Gemini 3.1 Pro |
| 能力 | MCP 支持；原生图表/信息图生成；扩展测试时计算；异步后台工作流 |
| 发布 | 2026 年 4 月 21 日 |

**最适合：**研究 Agent、文档综合、长时间异步工作流。MCP 支持使其成为首个提供一等工具集成的 Google 研究 Agent 产品。

### Gemini Robotics-ER 1.6（Google DeepMind）— 2026 年 5 月新发布

| 属性 | 值 |
|-----------|-------|
| 领域 | 物理机器人、具身推理 |
| 新能力 | 读取仪表盘/观测镜 |
| 部署 | Boston Dynamics Spot |
| 发布 | 2026 年 4 月 14 日 |

**最适合：**需要视觉—语言落地到物理动作的机器人应用。可通过 Gemini API 和 AI Studio 使用。

### Gemini 3.7 Flash（Google）— 2026 年 8 月新发布

| 属性 | 值 |
|-----------|-------|
| 模型 ID | `gemini-3.7-flash` |
| 上下文窗口 | 输入 1,048,576 token，输出 65,536 token |
| 输入/输出成本 | 2026 年 12 月 31 日前每 1M token 0.75/3.75 美元，此后 1.50/7.50 美元；上下文缓存 0.075 美元；Batch 0.375/1.875 美元 |
| 多模态 | 文本、图像、音频、视频；首个默认启用 Agent 视频处理的 Gemini 模型 |
| 知识截止日期 | 2026 年 3 月 |
| 发布 | 2026 年 8 月 13 日（GA） |

**它是什么：**Google 的主力层，基于 Gemini 3.6 Flash，模型卡称其主要是推理基础的算法改进，而非新的预训练。可按请求配置思考模式，在质量、成本和延迟之间权衡。Google 报告的相较 3.6 Flash 的提升包括 FrontierCode 1.1 Main 43.6% 对 34.4%，WebDev Arena Elo 1588 对 1538。

**注意事项：**半价介绍期于 2026 年 12 月 31 日结束，此后价格翻倍；确定大批量使用前，应使用 2027 年 1 月价格建模。截至 8 月中旬 Gemini 3.5 Pro 仍未发布，`gemini-3.1-pro-preview` 仍是 Google 最高的 Pro 档入口。

### Grok 4.6（SpaceXAI）— 2026 年 8 月新发布

| 属性 | 值 |
|-----------|-------|
| 模型 ID | `grok-4.6` |
| 上下文窗口 | 500K token |
| 输入/输出成本 | Prompt 小于 200K 时每 1M token 2.00/6.00 美元；达到 200K 时 4.00/12.00 美元；缓存输入 0.50 美元 |
| 推理 | low、medium、high（默认）、xhigh |
| 知识截止日期 | 2026 年 2 月 1 日 |
| 发布 | 2026 年 8 月 12 日 |

**它是什么：**SpaceXAI 的前沿模型，关注长时间 Agent 和交互式视觉工作。Artificial Analysis Intelligence Index 为 61，高于 Grok 4.5 High 的 56。

**两个值得知道的陷阱。**一旦 Prompt 达到 200K，更高的长 Prompt 价格会应用于请求中的**全部** token，而不仅是超出部分。缓存输入也从 Grok 4.5 的 0.30 美元上升到 0.50 美元，因此缓存密集型 Agent 循环升级后不会自动变便宜。注意厂商名称：xAI 已完成更名为 SpaceXAI，当前文档和发布说明使用新名称。

### Grok 4（xAI）

| 属性 | 值 |
|-----------|-------|
| 上下文窗口 | 256K token |
| 输入成本 | 每 1M token 3.00 美元 |
| 输出成本 | 每 1M token 15.00 美元 |
| 亮点 | 原生工具使用和实时搜索；推理能力有竞争力 |
| 发布 | 2025 年 7 月（Grok 4.20 Beta：2026 年 2 月） |

**最适合：**实时网络研究、重推理任务、实时 X/网络集成。
**注意事项：**Grok 4.1 Fast 可按每 1M token 0.20/0.50 美元用于高并发。

### 前沿层模型对比（2026 年 6 月）

| 模型 | 推理 | 编码 | 上下文 | Agent 能力 | 成本 |
|-------|-----------|--------|---------|---------|------|
| Claude Fable 5 | ★★★★★ | ★★★★★ | ★★★★★ | ★★★★★ | $$$$$ |
| Claude Mythos 5（受限） | ★★★★★ | ★★★★★ | ★★★★★ | ★★★★★ | $$$$$ |
| Claude Opus 4.8 | ★★★★★ | ★★★★★ | ★★★★★ | ★★★★★ | $$$$ |
| Claude Opus 4.7 | ★★★★★ | ★★★★★ | ★★★★★ | ★★★★★ | $$$$ |
| GPT-5.5 | ★★★★★ | ★★★★★ | ★★★★★ | ★★★★★ | $$$$ |
| Claude Opus 4.6 | ★★★★★ | ★★★★★ | ★★★★★ | ★★★★★ | $$$$ |
| GPT-5.4 | ★★★★★ | ★★★★★ | ★★★★ | ★★★★★ | $$$ |
| Claude Sonnet 4.6 | ★★★★★ | ★★★★★ | ★★★★★ | ★★★★★ | $$$ |
| Gemini 3.1 Pro | ★★★★★ | ★★★★ | ★★★★★ | ★★★★ | $$ |
| Grok 4 | ★★★★ | ★★★★ | ★★★★ | ★★★★ | $$$ |
| GPT-5.4-mini | ★★★★ | ★★★★ | ★★★★ | ★★★ | $ |
| Gemini 3.1 Flash | ★★★ | ★★★ | ★★★★★ | ★★★ | $ |
| GPT-5.5 Instant | ★★★★ | ★★★★ | ★★★★ | ★★★★ | $$ |

### 生产历史与成熟度

虽然前沿模型在基准上领先，许多企业系统仍依赖**经过实战验证**的模型：

| 模型家族 | 生产使用开始 | 成熟度说明 |
|--------------|------------------|---------------|
| **GPT-4o** | 2024 年 5 月 | 生态最成熟；延迟波动最低；速率限制最高。 |
| **Claude 3.5 Sonnet/3.7 Sonnet** | 2024 年 6 月 | 工具使用可靠性和结构化输出的黄金标准。 |
| **Gemini 2.5 Pro** | 2025 年 3 月 | 经规模验证；长上下文稳定。2026 年 6 月弃用，转向 3.x。 |
| **o1/o3** | 2024 年 9 月 | 推理模型失败模式已被充分理解；o3 已取代 o1。 |

**为什么继续使用“旧的”前沿模型？**
1. **一致性**：新模型可能出现“发布窗口”延迟尖峰和行为变化。
2. **成本效率**：新版本发布后，上一代通常便宜 50–80%。
3. **安全策略调优**：安全和审核层更成熟。

---

## 开源模型

### Llama 4 家族（Meta）— 2026 年 4 月新发布

| 模型 | 参数量 | 上下文 | 架构 | 说明 |
|-------|------------|---------|--------------|-------|
| Llama 4 Scout | 17B 激活/16 个专家（MoE） | 10M | 稀疏 MoE | 行业领先的 10M 上下文；适合单张 H100；超过 Gemma 3、Gemini 2.0 Flash-Lite |
| Llama 4 Maverick | 17B 激活/128 个专家（MoE） | 1M | 稀疏 MoE | 超过 GPT-4o 和 Gemini 2.0 Flash；激活参数只有一半但与 DeepSeek V3 相当 |
| Llama 4 Behemoth | 约 288B 激活（估计） | - | 稠密 MoE | 仍在训练；STEM 基准超过 GPT-4.5、Gemini 2.0 Pro |

**优势：**
- Llama 首个使用专家混合架构的世代
- 从底层开始原生多模态（文本、图像、视频输入）
- 在 Hugging Face 提供开放权重；可通过 WhatsApp、Messenger、Instagram 的 Meta AI 使用
- Scout 的 10M token 上下文是开放模型中领先的

### Llama 3.x 家族（Meta）— 上一代

| 模型 | 参数量 | 上下文 | 许可证 | 说明 |
|-------|------------|---------|---------|-------|
| Llama 3.3 70B | 70B | 128K | Llama 3.3 | 仍广泛部署；通用能力强 |
| Llama 3.1 405B | 405B | 128K | Llama 3.1 | Meta 最大的稠密模型；正在被 Llama 4 取代 |

**注意：**Llama 3.x 仍被广泛用于生产，但 Llama 4 Scout/Maverick 借助 MoE，以更少的激活参数提供更好的性能。

### DeepSeek 家族

| 模型 | 参数量 | 上下文 | 状态 | 说明 |
|-------|------------|---------|--------|-------|
| **DeepSeek V4 Pro** | 总计 1.6T/激活 49B（MoE） | 1M | GA | 2026 年 4 月 24 日预览。1M token 时只使用 V3.2 约 27% 的计算和 10% 的内存。SWE-bench Verified 80.6%。NIST CAISI（2026 年 5 月）评估其落后美国前沿约 8 个月（Elo 约 800）。Hugging Face 提供开放权重。**API：每 1M token 输入/输出 0.435/0.87 美元（75% 折扣于 5 月 22 日永久化，6 月 1 日生效）。**缓存命中输入 0.003625 美元/M。 |
| **DeepSeek V4 Flash** | 总计 284B/激活 13B（MoE） | 1M | GA | 面向高吞吐的较小激活版本。**API：每 1M token 0.14/0.28 美元（缓存命中 0.0028 美元/M）。**截至 2026 年 5 月，最便宜的前沿级 1M 上下文 API。 |
| DeepSeek-V3.2 | 671B（MoE） | 128K | 前沿 | 通用；缓存命中折扣 98%（基础价 0.28/0.42 美元/M）。新项目大多被 V4 Flash 取代。 |
| DeepSeek-V3 | 671B（MoE，激活 37B） | 128K | 前沿 | 以很低的训练成本达到 GPT-4o 级别；开放权重。 |
| DeepSeek-R1 | 671B（MoE） | 128K | 推理 | 数学/代码匹敌 o1；首个开源推理模型。 |
| DeepSeek-R1-Distill | 7B–70B | - | 推理 | 蒸馏到更小模型；推理成本高效。 |

**2026 年 5 月关键背景：**DeepSeek V4 Pro（4 月 24 日发布，75% 促销折扣于 5 月 22 日永久化）以很低成本在多个基准上缩小了与美国前沿模型的差距。每 1M token 0.435/0.87 美元时，V4 Pro 在相近任务上约比 Claude Opus 4.7（5/25）便宜 10 倍，比 GPT-5.5（5/30）便宜 5–10 倍。V4 Flash 以相同 1M 上下文进一步把价格降到 0.14/0.28 美元。两者 98% 的缓存命中折扣，使 V4 成为高并发 RAG 和分类的主选，前提是 Prompt 适合缓存。DeepSeek R2（R1 的推理继任者）据报道仍因华为 Ascend 训练挑战延期。

### Moonshot Kimi 家族— 2026 年 5 月新发布

| 模型 | 参数量 | 上下文 | 说明 |
|-------|------------|---------|-------|
| **Kimi K3** | 总计 2.8T/激活 104B（MoE） | 1M | 2026 年 7 月 16 日新发布（权重 7 月 27 日）。迄今最大的开放权重模型。始终开启思考、多模态。每 1M token 3/15 美元（缓存输入 0.30 美元）。Artificial Analysis Intelligence Index 为 57.1，发布时仅次于 Fable 5 和 GPT-5.6 Sol；首个进入 WebDev Arena 前列的开放模型。接替 K2.7 Code。 |
| **Kimi K2.6** | 总计 1T/激活 32B（MoE） | - | 2026 年 4 月 20 日发布。Modified MIT。原生视频输入；Agent Swarm 可扩展到 300 个子智能体和 4000 个协同步骤。SWE-Bench Pro 与 GPT-5.5 持平（58.6%）；SWE-bench Verified 约 80.2%。 |
| **Kimi K2.7 Code** | 总计 1T/激活 32B（MoE） | 256K | 2026 年 6 月 12 日新发布。基于 K2.6 的编码版本（Modified MIT），带 MoonViT 视觉编码器。厂商基准称在自有 Kimi Code Bench v2 上比 K2.6 高约 21.8%，思考 token 少约 30%。API 约每 1M token 0.95/4.00 美元。 |
| Kimi K2-Thinking-0905 | - | - | 首个在 AIME 2025 达到 100% 的模型（推理变体）。 |

**最适合：**长周期 Agent、视频理解、作为闭源前沿模型之外的开放权重 Agent 栈。

### 阿里巴巴 Qwen 3.x 家族— 2026 年 5 月新发布

| 模型 | 参数量 | 许可证 | 说明 |
|-------|------------|---------|-------|
| **Qwen3.8-Max** | 总计 2.4T/激活 95B MoE | Qwen3.8-Max License（门控） | 2026 年 8 月 12 日。原生 262K 上下文，可扩展至约 1,010,000。使用定制许可证而非 Apache：MAU 超过 1 亿或月收入超过 2000 万美元需署名；Model-as-a-Service 或 AI 助手业务总收入超过 5000 万美元需单独付费许可证。开放检查点仅支持文本输入；API 版本支持多模态。 |
| **Qwen3.8-27B** | 稠密 27B | Apache 2.0 | 2026 年 8 月 14 日。更宽松、模态更完整：开放 Max 检查点不支持的图像和视频输入由它支持。262K 上下文，可扩展至约 1M。稠密架构，适合单 GPU。 |
| **Qwen 3.6 Max-Preview** | 约 1T MoE | 商业预览 | 约 2026 年 4 月 20–27 日发布。262K 上下文。阿里称其在六项编码基准上领先。 |
| **Qwen 3.6-Plus** | - | - | 2026 年 4 月 2 日发布。增强编码。 |
| **Qwen 3.6-35B-A3B** | 35B/激活 3B MoE | Apache 2.0 | 2026 年 4 月 16 日发布。开放权重主力。 |
| Qwen2.5-Coder-32B | 32B | Apache 2.0 | 上一代开放编码领先者。 |
| Qwen2.5-72B | 72B | Apache 2.0 | 上一代多语言领先者。 |
| Qwen2.5-7B | 7B | Apache 2.0 | 高效自托管选项。 |

### Mistral 家族

| 模型 | 参数量 | 上下文 | 说明 |
|-------|------------|---------|-------|
| **Mistral Medium 3.5** | 稠密 128B | 256K | 2026 年 5 月新发布，实际发布于 4 月 29 日。将 Magistral（推理）、Pixtral（视觉）、Devstral 2（编码）合并为一个模型。SWE-Bench Verified 77.6%。输入每 1M token 1.50 美元。 |
| **Voxtral TTS** | 开放权重 4B | 流式 | 2026 年 5 月新发布（3 月 23 日发布，CC BY-NC 4.0）。延迟 70ms，9 种语言，3 秒声音克隆。 |
| Mistral Large 3 | 675B（MoE，激活 41B） | 256K | 稀疏 MoE；与最佳开放模型相当；LMArena 非推理开源模型第 2。 |
| Mistral Small 4 | - | 256K | 混合指令/推理/编码；2026 年 3 月发布。 |
| Mistral 3（14B/8B/3B） | 3B–14B | - | 统一家族：多语言、多模态、Apache 2.0。 |
| Mixtral 8x22B | 141B（MoE） | - | 上一代；仍适合吞吐场景。 |

### Google Gemma 家族— 2026 年 5 月新发布

| 模型 | 参数量 | 上下文 | 许可证 | 说明 |
|-------|------------|---------|---------|-------|
| **Gemma 4（31B 稠密）** | 31B | 256K | Apache 2.0 | 2026 年 4 月 2 日发布。140+ 语言；原生视觉/音频；函数调用。 |
| **Gemma 4（26B-A4B MoE）** | 26B/激活 4B | 256K | Apache 2.0 | 稀疏 MoE 变体。 |
| **Gemma 4 E4B** | 8B | 256K | Apache 2.0 | 适合边缘设备。 |
| **Gemma 4 E2B** | 5.1B/激活 2.3B | 256K | Apache 2.0 | 最小变体；移动/嵌入式。 |
| **DiffusionGemma（26B-A4B MoE）** | 26B/约激活 4B | 256K | Apache 2.0 | 2026 年 6 月 10 日新发布。Google DeepMind 首个开放权重文本扩散模型；并行去噪 token 块，生成约快 4 倍（单张 H100 超过 1000 token/s）。质量低于标准 Gemma 4，面向低延迟和行内编辑。 |

### Zhipu/Z.ai GLM 家族— 2026 年 6 月新发布

| 模型 | 参数量 | 上下文 | 许可证 | 说明 |
|-------|------------|---------|---------|-------|
| **GLM-5.3** | 与 GLM-5.2 相同的 744B/40B 激活基础模型上训练后处理 | 1M | 发布时暂不提供权重 | 2026 年 8 月 14 日通过 GLM Coding Plan 发布。全部提升来自扩展训练后处理，而不是新的预训练，这说明当前能力越来越来自哪里。Z.ai 表示扩展训练后网络安全能力增长快于预期，声称领先 CyberGym，并在安全评估完成前分阶段开放权重，目标约两周后（2026 年 8 月 28 日左右）。 |
| **GLM-5.2** | 总计 744B/激活 40B（MoE） | 1M | MIT | 2026 年 6 月 13 日编码计划可用；6 月 16–17 日开放权重。面向长周期 Agent 编码和工具使用。报告 SWE-Bench Pro 62.1，在该基准上领先 GPT-5.5；长周期编码分数接近闭源前沿，数据由厂商报告。API 约每 1M token 1.40/4.40 美元；权重在 Hugging Face。 |

**最适合：**重视 1M 上下文和宽松许可证的开放权重 Agent 编码及长周期工具使用。基准声明需在独立榜单上核验。

### Thinking Machines Inkling— 2026 年 7 月新发布

| 模型 | 参数量 | 上下文 | 许可证 | 说明 |
|-------|------------|---------|---------|-------|
| **Inkling** | 总计 975B/激活 41B（MoE） | 1M（通过实验室 Tinker API 为 64K 或 256K） | 开放权重 | 2026 年 7 月 15 日发布：Thinking Machines Lab 首个公开模型，在 45T 文本、图像、音频和视频 token 上预训练。SWE-Bench Verified 77.6%；Artificial Analysis 称其为领先的美国开放权重模型；实验室称安全分数与前沿模型一致。NVFP4 检查点针对 NVIDIA Blackwell 优化。 |
| Inkling-Small（预览） | 总计 276B/激活 12B | - | 开放权重 | 与 Inkling 同时宣布，成本和延迟更低。 |

**为什么重要：**一家全新的美国实验室发布领先的美国开放权重模型，并明确定位为微调基础。7 月之前开放前沿主要由中国实验室主导；Kimi K3 和 Inkling 同周发布，是有记录以来最强的开放权重月份。

### Meta Muse Spark（闭源权重）— 2026 年 5 月战略转向

| 属性 | 值 |
|-----------|-------|
| 许可证 | **闭源权重**——Meta Superintelligence Labs 的首个专有模型 |
| 能力 | Instant/Thinking/Contemplating 模式的多模态推理 |
| 发布 | 2026 年 4 月 8 日 |

**战略意义：**这是 Meta 自原始 Llama 时代以来首个非开放模型，说明前沿质量可能需要闭源开发反馈循环。Llama 4 Behemoth 同时因能力问题暂停至 2026 年秋。开放与闭源的平衡如今分为两层：闭源前沿领先 6–12 个月，开放权重通过蒸馏、RL 和生态迭代追赶。

**2026 年 7 月更新：** **Muse Spark 1.1** 于 7 月 9 日发布，同时推出 **Meta Model API** 公共预览，这是 Meta 首个自助付费 API：兼容 OpenAI，每 1M token 1.25/4.25 美元，约为竞品旗舰价格的四分之一。厂商报告其在规模化工具使用（MCP Atlas 88.1）和专业工具使用（JobBench 54.7）上领先。Meta 对 API 收费完成了从开放权重 Llama 的转向；没有 Llama 5，Behemoth 仍搁置。

**2026 年 8 月更新：** **Muse Glimmer**（8 月 10 日）是 Meta 自 Llama 4 后首个开放权重发布，也是 Apache 2.0 下 Meta 许可证最宽松的开放模型。它是 30B 稠密多模态模型，面向持续运行的本地 Agent（本地编码 Agent、函数调用、LLM-as-a-judge），上下文为 131,072 token；量化到 4-bit 后低于 20GB，可在单张 24GB 消费级 GPU 上运行。**Muse Spark 1.2** 和终端编码 Agent **Muse Code** 同时发布，其中 `muse-spark-1.2-contributor` 档每 1M token 0.10/0.20 美元（标准价 1.25/4.25），交换条件是允许使用 Prompt 和补全来训练模型。以数据换折扣作为明确公布的 API 档位尚属新模式，启用前应做政策决策。

---

### 2026 年 8 月开放权重许可证分裂

8 月之后，“开放权重”不再只有一种含义。现在三种姿态并存，许可证和基准一样都是设计输入：

| 模型 | 发布 | 规模 | 许可证姿态 | 许可证实际作用 |
|-------|----------|------|-----------------|-------------------------------|
| **Qwen3.8-Max**（阿里巴巴） | 8 月 12 日 | 2.4T/激活 95B | 定制、商业门控 | 可免费使用、修改和转售，但 MAU 超过 1 亿或月收入超过 2000 万美元需署名；Model-as-a-Service 或 AI 助手业务总收入超过 5000 万美元需单独付费许可证 |
| **Qwen3.8-27B**（阿里巴巴） | 8 月 14 日 | 稠密 27B | Apache 2.0 | 无条件。较小兄弟模型比旗舰更宽松，模态也更完整 |
| **Muse Glimmer**（Meta） | 8 月 10 日 | 稠密 30B | Apache 2.0 | 无条件；Meta 迄今最宽松的开放许可证 |
| **Tencent Hy3** | 全球 8 月 5 日（模型 7 月 6 日） | 295B/激活 21B | Apache 2.0 | 完全宽松，无地域限制；逆转 4 月预览版排除欧盟、英国和韩国的限制性许可证 |
| **Ling-3.0-flash/tiny**（蚂蚁集团） | 8 月 5 日/8 月 11 日 | 124B/激活 5.1B；7.9B/激活 1.3B | MIT | 无条件 |
| **Nemotron 3.5 Lightning**（NVIDIA） | 8 月 11 日 | 30B/激活 3B | OpenMDW-1.1 | Linux Foundation 许可证，允许免费商用 |
| **GLM-5.3**（Z.ai） | 8 月 14 日 | 基础模型 744B | 暂不提供权重 | 网络安全能力增长超预期，开放发布暂缓安全评估；Z.ai 目标约两周后（2026 年 8 月 28 日左右） |

对于基于开放权重构建系统的人，有两点结论。第一，**先读许可证，再看模型卡**：门控许可证可能恰好让“开放”旗舰无法用于计划中的 SaaS 业务，而较小兄弟模型不受限制。第二，**暂不提供权重也是合理结果**：实验室可以先商业发布模型，出于安全理由暂缓权重。Z.ai 给出了目标日期，应把它视为有日期的计划，而不是无限期承诺；不要把尚未发布的权重写进路线图。

### 小型与端侧模型— 2026 年 8 月

| 模型 | 规模 | 上下文 | 许可证 | 说明 |
|-------|------|---------|---------|-------|
| **Ling-3.0-tiny**（蚂蚁集团） | 7.9B/激活 1.3B | 256K | MIT | 真正的笔记本级 Agent 模型：8K 上下文峰值内存约 8.3 GiB，M4 Pro MacBook FP8 下 86–90 tok/s |
| **LFM2.5-2.6B**（Liquid AI） | 2.6B | 128K | 开放权重 | 面向端侧工具调用和多步规划而非聊天；内存低于 2.5GB，可运行到 Raspberry Pi |
| **LFM2.5-VL-3B**（Liquid AI） | 3B | - | 开放权重 | 端侧视觉语言模型，用于屏幕理解和 GUI 落地（8 月 12 日） |
| **Shieldstral 1.0**（Mistral） | 3B | 32K | Apache 2.0 | 策略自适应的**多模态**安全分类器（文本和图像，12 种语言）；推理时用自然语言提供审核策略，策略变化无需重新训练。可运行在单张 16GB GPU 上 |
| **Muse Glimmer**（Meta） | 稠密 30B | 131K | Apache 2.0 | 4-bit 下低于 20GB；面向持续运行的本地 Agent |

值得注意的趋势是：小模型层不再只比拼聊天质量，而开始比拼**工具调用、规划和屏幕落地**，这些才是本地 Agent 真正需要的能力。

---

## 专业模型

### 编码能力（2026 年 6 月）

| 模型 | 专长 | 获胜原因 |
|-------|----------------|-------------|
| **Claude Fable 5** | 能力上限 | Mythos 级编码能力普遍可用；Anthropic 称 Cognition FrontierCode 最高前沿分数和 CursorBench SOTA；价格是 Opus 4.8 的 2 倍 |
| **GPT-5.5** | 单次编码领先者（已发布） | SWE-bench Verified 88.7%；Terminal-Bench 2.1 78.2% |
| **Claude Opus 4.8** | 长时间 Agent 编码 | SWE-bench Verified 88.6%；SWE-Bench Pro 69.2%；Claude Code 的 Dynamic Workflows 支持并行子智能体 |
| **Claude Opus 4.7** | 上一代编码旗舰 | SWE-bench Verified 87.6%；SWE-Bench Pro 64.3% |
| **Claude Sonnet 4.6** | 编码主力 | 以更低成本驱动 Claude Code；1M 上下文 |
| **Llama 4 Maverick** | 开源编码 | 开放权重；编码基准有竞争力 |
| **Qwen 3.6 Coder/Qwen2.5-Coder-32B** | 自托管编码 | 自托管 IDE 的价格/性能最佳 |
| **DeepSeek V4 Pro/R1-Distill-70B** | 开放推理 + 代码 | 70B 中最好的开放推理；V4 Pro 是 1.6T/49B 激活 MoE 开放权重 |
| **Z.ai GLM-5.2** | 开放 Agent 编码 | 2026 年 6 月；744B/40B 激活 MoE、1M 上下文、MIT；厂商称 SWE-Bench Pro 62.1，领先 GPT-5.5；每 1M token 约 1.40/4.40 美元 |
| **Kimi K2.7 Code** | 开放长周期编码 | 2026 年 6 月；1T/32B 激活 MoE、Modified MIT；从 K2.6 调整用于软件工作，思考 token 更少 |
| **Cohere North Mini Code 1.0** | 开放轻量编码 | 2026 年 6 月；30B/3B 激活 MoE，可运行在单张 H100，Apache 2.0；Cohere 首个开放编码模型 |

### 推理与数学

| 模型 | 方法 | 最适合 |
|-------|----------|----------|
| **Claude Fable 5** | Mythos 能力层级的始终开启自适应思考 | 能力上限比成本更重要的最难推理问题 |
| **Claude Opus 4.8（thinking）** | 带并行子智能体的自适应思考 | 软件规划、代码库规模工作、Agent 推理 |
| **GPT-5.5 reasoning** | 最大计算量推理 | 竞赛数学（Instant 上 AIME 2025 81.2%）、ARC-AGI-2 85.0% 领先 |
| **Gemini 3.1 Pro Deep Think** | 持续链式思考 | 科学推理、GPQA Diamond 领先 |
| **DeepSeek-R1** | 基于 RL 的思考 | 开源逻辑推理、竞争性数学 |
| **Grok 4.3（DeepSearch）** | 网络增强推理 | 需要实时信息的研究任务 |

### 长上下文（1M+）

| 模型 | 窗口 | 召回表现 |
|-------|--------|-------------------|
| **Llama 4 Scout** | 10M | 行业领先的开放权重上下文窗口 |
| **Gemini 3.1 Pro/Flash** | 1M | 1M 上下文质量最佳，已规模验证 |
| **Claude Fable 5** | 1M | Anthropic 称长会话中持续记忆改善了长上下文表现 |
| **Claude Opus 4.8/4.7/Sonnet 4.6** | 1M | 标准价格覆盖完整 1M；召回可靠 |
| **Llama 4 Maverick** | 1M | 具备 MoE 效率的开放权重 1M 上下文 |

---

## Embedding 模型

### API Embedding 模型（2026 年 5 月）

| 模型 | 维度 | 最大 token 数 | MTEB 分数 | 每 1M 成本 |
|-------|------------|------------|------------|---------|
| OpenAI text-embedding-3-large | 3072 | 8191 | 64.6 | $0.13 |
| OpenAI text-embedding-3-small | 1536 | 8191 | 62.3 | $0.02 |
| Voyage-3 | 1024 | 32000 | 67.8 | $0.06 |
| Cohere embed-v3 | 1024 | 512 | 66.4 | $0.10 |
| Google text-embedding-004 | 768 | 2048 | 66.1 | $0.025 |

### 开源 Embedding 模型

| 模型 | 维度 | 最大 token 数 | MTEB | 说明 |
|-------|------------|---------|------|-------|
| BGE-large-en-v1.5 | 1024 | 512 | 63.9 | 指令微调 |
| E5-mistral-7b-instruct | 4096 | 32768 | 66.6 | 指令效果强 |
| Nomic-embed-text-v1.5 | 768 | 8192 | 62.3 | 长上下文、开放 |
| GTE-Qwen2-7B | 3584 | 32K | 72.1 | 开源 Embedding SOTA |

### Embedding 选择指南

| 要求 | 推荐 | 原因 |
|-------------|-------------|-----|
| 最佳质量 | Voyage-3 或 text-embedding-3-large | MTEB 最高 |
| 成本效率 | text-embedding-3-small | $0.02/1M |
| 自托管 | GTE-Qwen2-7B | 开源 MTEB 最佳 |
| 长文档 | Nomic 或 Voyage-3 | 8K+ 上下文 |
| 多语言 | Cohere embed-v3 | 为多语言设计 |

---

## 模型选择框架

### 决策树

```
What is your primary constraint?

├── Cost → Use smaller model, consider open source
│   ├── Very cost sensitive → DeepSeek V4 Flash, GPT-5.5-mini, Claude Haiku 4.5, Gemini 3.1 Flash
│   └── Moderate budget → Claude Sonnet 4.6, GPT-5.5 Instant, DeepSeek V4 Pro
│
├── Quality + Reasoning → Use frontier models
│   ├── Highest reasoning → Claude Fable 5, Claude Opus 4.8 (thinking), GPT-5.5 reasoning, Gemini 3.1 Pro Deep Think
│   └── Coding + reasoning → Claude Opus 4.8 with Dynamic Workflows, Claude Sonnet 4.6 (Extended Thinking), GPT-5.5
│
├── Latency → Use fast models
│   ├── <100ms response → Gemini 3.1 Flash, GPT-5.5-mini
│   └── <500ms response → Claude Haiku 4.5, Claude Opus 4.8 fast mode, Grok 4.1 Fast
│
├── Self-hosting → Use open models
│   ├── Maximum capability → Llama 4 Maverick, DeepSeek-V3
│   ├── Good balance → Llama 4 Scout, Llama 3.3 70B, Qwen2.5-72B
│   └── Edge/mobile → Mistral 3 3B, Phi-4
│
└── Privacy → Self-host or use on-prem
    └── Choose open models with appropriate license
```

### 语义路由

静态决策树正在被**语义路由器**替代：
- **工作方式**：用小型快速 Embedding 模型把 Query 向量化。如果命中“已知简单”簇，就路由到便宜模型（Gemini 3.1 Flash、DeepSeek V4 Flash、Claude Haiku 4.5）；如果命中“Agent/逻辑”簇，就路由到 Claude Opus 4.8 或带推理的 GPT-5.5。
- **收益**：无需硬编码规则就能自动优化成本。
- **实现**：可使用 `semantic-router`（Python），或自定义 Weaviate/Pinecone 分类器。

---

## 主权 AI 与数据驻留

**2026 年监管现实：**
企业必须遵守 GDPR（欧盟）、DPDPA（印度）、沙特 PDPL 及行业规则。“主权 AI”已经成为产品类别。

| 方案 | 提供方 | 使用场景 |
|----------|----------|----------|
| **Azure Government/Sovereign** | Microsoft | 40+ 地区的专用基础设施；获美国政府/欧盟 NIS2 批准 |
| **AWS Sovereign Cloud** | Amazon | 物理隔离 VPC；符合 GDPR 的欧盟区域 |
| **Google Distributed Cloud** | Google | 隔离网络的本地 Gemini 部署 |
| **Private Llama 4/3.3** | Meta（自托管） | 最大数据主权；开放权重（Llama 4 MoE 或 3.3 稠密） |
| **DeepSeek（自托管）** | DeepSeek（开放） | 开放权重；数据不离开自己的基础设施 |
| **Mistral Large 3（自托管）** | Mistral（Apache 2.0） | 675B MoE；开放权重；多语言能力强 |

**权衡：**主权云比标准全球区域贵 **20–30%**，但金融和政府场景必须使用。

### 规模化成本对比（2026 年 5 月）

假设每天 100 万请求，每次 1K 输入 + 500 输出 token：

| 模型 | 每日输入成本 | 每日输出成本 | 每月总计 |
|-------|----------------|-----------------|-------------|
| Claude Sonnet 4.6 | $3,000 | $7,500 | $315,000 |
| GPT-5.4 | $2,500 | $7,500 | $300,000 |
| Gemini 3.1 Pro | $2,000 | $6,000 | $240,000 |
| GPT-5.4-mini | $750 | $2,250 | $90,000 |
| Gemini 3.1 Flash | $100 | $1,500 | $48,000 |
| 自托管 Llama 4 Scout* | - | - | ~$15,000 |
| 自托管 Llama 3.3 70B* | - | - | ~$50,000 |

*自托管 Llama 4 Scout 可运行在单张 H100；Llama 3.3 70B 假设使用 4 张 H100 GPU。*

---

## 能力对比

### 基准表现（2026 年 5 月）

| 模型 | MMLU | HumanEval | SWE-bench Verified | 说明 |
|-------|------|-----------|--------------------|-------|
| **Claude Opus 4.6** | - | - | - | 推理和编码全能顶级；具体分数请查最新数据 |
| **GPT-5.4** | - | - | - | 比 GPT-5.2 少 33% 事实错误；编码和 Agent 能力强 |
| **Claude Sonnet 4.6** | - | - | - | 许多任务接近 Opus 级别 |
| **Gemini 3.1 Pro** | - | - | - | Google 推理 SOTA |
| **Grok 4** | - | - | - | 推理有竞争力；集成实时网络 |
| **Llama 4 Maverick** | - | - | - | 在已报告基准上超过 GPT-4o、Gemini 2.0 Flash |
| **DeepSeek-R1** | 90.8 | 92.6 | 49.2% | 首个开源推理模型；数学/代码能力强 |

*来源：各技术报告和 LMSYS Chatbot Arena/LMArena，2026 年 4 月。最新模型（Opus 4.6、GPT-5.4、Gemini 3.1）的分数变化很快，请始终核对最新榜单。*

### 特定任务推荐（2026 年 5 月）

| 任务 | 推荐模型 | 原因 |
|------|--------------------|-----|
| **自主编码 Agent** | Claude Sonnet 4.6/Opus 4.6 | 驱动 Claude Code；1M 上下文；工具可靠性高 |
| **复杂推理** | GPT-5.4 Pro、Claude Opus 4.6（thinking）、DeepSeek-R1 | 最大推理能力 |
| **Agent 计算机使用** | GPT-5.4 | 首个具备原生计算机使用能力的通用模型 |
| **高并发 API** | Gemini 3.1 Flash、GPT-5.4-mini | 同类每 token 成本最低 |
| **长上下文 RAG** | Gemini 3.1 Pro/Flash（1M）、Claude Sonnet 4.6（1M） | 长距离召回已验证 |
| **超长上下文** | Llama 4 Scout（10M） | 行业领先的 10M 上下文；开放权重 |
| **实时多模态** | Gemini 3.1 Flash | 原生实时音频/视频/文本 |
| **私有生产** | Llama 4 Maverick、Llama 3.3 70B、Qwen2.5-72B | 本地可控且能力强 |
| **开源编码** | Llama 4 Maverick、Qwen2.5-Coder-32B | 开放权重，编码基准强 |
| **创意/聊天** | GPT-5.4 | 对话质量和指令遵循强 |

---

## 面试问答

### 问：如何为生产 RAG 系统选择模型？

**强回答：**
我会从以下维度评估：

**1. 质量要求：**
- 使用来自真实领域的代表性 Query 测试
- 衡量答案正确率、幻觉率、引用准确率

**2. 成本分析：**
```
Monthly cost = requests/day × 30 × avg_tokens × rate
```
始终为前 2–3 个候选模型计算成本。

**3. 延迟要求：**
- 需要 <200ms TTFT：Gemini 3.1 Flash、Claude Haiku 4.5、GPT-5.4-mini
- 质量优先：接受 Claude Opus 4.6 或 GPT-5.4 的 2–3 秒延迟

**4. 运营要求：**
- 自托管：Llama 4 Scout/Maverick、DeepSeek-V3
- 合规/数据驻留：Azure Sovereign 或自托管

**5. 实际选择：**
- 使用 Claude Sonnet 4.6 或 GPT-5.4 开始原型
- 对 80% 的 Query A/B 测试 Gemini 3.1 Flash（成本）
- 通过语义路由把前沿模型留给困难 Query

### 问：解释专有模型和开源模型之间的权衡。

**强回答：**
| 因素 | 专有模型（OpenAI、Anthropic） | 开源模型（Llama、DeepSeek） |
|--------|--------------------------------|-----------------------------|
| 质量 | 通常略高 | 快速追赶 |
| 成本 | 按 token 计费 | 计算资源 + 运维 |
| 控制 | 有限 | 完全 |
| 隐私 | 数据发送给提供商 | 保留在本地 |
| 更新 | 自动 | 手动 |
| 定制 | 微调受限 | 可完全微调 |
| 运维负担 | 无 | 明显 |

**关键洞察（2026）：**DeepSeek-V3/R1 以及现在的 Llama 4 改变了讨论——开放模型在许多基准上已经匹配或超过 GPT-4o。Llama 4 Maverick 以一半的激活参数达到 DeepSeek V3 的推理水平，差距从未如此小。

### 问：GPT-5.4 Pro 和 Claude Opus 4.6 的扩展思考有什么区别？

**强回答：**
两者都使用内部链式思考，但机制不同：

- **GPT-5.4 Pro**：OpenAI 最大计算量的推理档（每 1M token 30/180 美元），为推理分配高计算量，内部思考不对外展示，是 o3 系列的继任者。
- **Claude Opus 4.6 自适应思考**：在单独的 `<thinking>` Block 返回思考 token，可配置 `budget_tokens`，可以检查推理链以便调试，完整 1M 上下文和最大 128K 输出。

**生产选择：**调试和建立信任时，Claude 的可见思考更透明；数学/竞赛任务追求原始推理能力时，GPT-5.4 Pro 领先；成本敏感的推理使用 Claude Sonnet 4.6 或 GPT-5.4-mini。

---

## 参考资料

- Anthropic: https://platform.claude.com/docs/en/about-claude/models/overview
- OpenAI Platform: https://developers.openai.com/api/docs/models
- Google AI: https://ai.google.dev/gemini-api/docs/models
- Meta Llama: https://www.llama.com/
- DeepSeek: https://api-docs.deepseek.com/
- xAI Grok: https://docs.x.ai/developers/models
- Mistral AI: https://docs.mistral.ai/models/
- LMArena Leaderboard: https://lmarena.ai/
- Hugging Face Open LLM Leaderboard: https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard

---

*下一篇：[模型能力评估](02-capability-assessment.md)*
