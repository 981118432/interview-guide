# 实时语音 Agent

语音 Agent 是围绕 LLM 包装的软实时媒体系统。推理反而是简单部分，困难在于**时序**：接收音频、判断人真正停止说话的时机、完成思考，再足够快地输出音频，让对话感觉鲜活。时序出错，用户会与 Agent 抢话、重复表达，最后挂断。本章覆盖架构、延迟预算、2026 年技术栈和生产故障模式。

范围提示：如果正在构建电话、客服或语音优先产品，请阅读本章。否则，[Agent 基础](../07-agentic-systems/01-agent-fundamentals.md)和[工具使用](../17-tool-use-and-computer-agents/01-tool-use-landscape.md)章节覆盖可迁移部分。以下具体模型名、价格和延迟数字是 2026 年年中的快照，变化很快，引用前应核验。

## 目录

- [两种架构](#the-two-architectures)
- [逐组件拆解流水线](#the-pipeline-component-by-component)
- [延迟预算](#latency-budgets)
- [2026 年技术栈](#the-2026-stack)
- [生产注意事项](#production-concerns)
- [诚实的成熟度判断](#honest-maturity)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## 两种架构

每个语音 Agent 都属于两种形态之一。

**级联流水线：** `mic -> VAD -> streaming STT -> endpointing -> LLM -> streaming TTS -> speaker`。音频在每个边界都变成**文本**，每个阶段都可以替换，通常来自不同供应商。

**语音到语音（S2S）：** 单个多模态模型直接接收音频帧并输出音频帧，文本仅作为旁路输出。OpenAI Realtime API、Google Gemini Live 原生音频和 AWS Nova Sonic 是 2026 年的例子。

| 维度 | 级联 | 语音到语音 |
|-----------|----------|------------------|
| **延迟下限** | 朴素实现更高；完整流式化后总延迟趋近 `max(stage)`，约 400-800ms | 结构上更低（没有文本往返） |
| **可控性** | 高：每次交接都有文本，可独立替换 LLM/声音、A/B 测试、注入 Prompt | 低：只有一个模型，替换供应商等于重构架构 |
| **中断** | 确定性、由运行时控制（VAD 触发、取消 TTS、回滚本轮） | 全双工更自然，但故障不透明 |
| **成本** | 可预测，通常按分钟计费 | 按 Token 计费，每轮重新发送音频历史，随通话时长增长 |
| **可观测性** | 每个边界都有文本产物，易记录和审计 | 需要并行转写流做日志 |
| **韵律/情绪** | 从文本重建，情感常在 STT 瓶颈处丢失 | 原生保留并生成语气、笑声和强调 |
| **语言/代码切换** | 受每个组件能力限制 | 更自然地处理中途代码切换 |

**决策指南。** 需要组件级调试和审计轨迹、监管合规（HIPAA、金融）、供应商灵活性、深度工具调用和可预测成本时，选择**级联**。这是 2026 年企业生产的默认方案，部分原因是可替换的 STT/TTS 供应商很多，而 S2S 供应商只有少数。需要最大对话自然度、最低中断延迟和富有表现力的声音（陪伴、辅导、消费级演示），并能容忍较弱的可调试性和可变成本时，选择 **S2S**。一种常见的**混合方案**是让 S2S 负责对话核心，同时运行并行 STT 流，专门用于日志和评估。

适用于两者的现实检查是：默认情况下谁都不会自动赢得延迟。WebSocket 建立、VAD 配置、网络跳数、编解码器和采样率都可能占主导；调优良好的级联在许多部署中可以匹敌 S2S。

---

## 逐组件拆解流水线

**语音活动检测（VAD）。** 第一层实时把每个音频帧分类为语音或静音。Silero VAD 是事实上的开源标准，已原生集成到主要框架中，只增加约 10～50ms。VAD 本身无法区分句中停顿和一轮结束，这就是下一个问题。

**语义端点检测与轮次交接是核心。** 有两种方法：
- **静音阈值端点检测**等待 N 毫秒静音。简单，但每一轮都要付出代价：800ms 超时会在流水线开始前平白增加接近一秒。
- **学习式轮次检测**读取部分转写文本，预测想法是否在语义上完整，并在尾部静音前触发。2026 年具体系统包括小型 Transformer 轮次检测器（从小型基座微调的约 1.35 亿参数模型，在 CPU 上几十毫秒运行，并提供多语言版本），以及流式 STT 端点检测：发出带可调置信度阈值的学习式轮次结束 Token。收益是把 Agent 轮次间隔收窄到约 300ms，同时不打断用户。

**抢话/中断。** Agent 说话时轮次检测仍然活跃。用户音轨触发 VAD 后，运行时取消活动 TTS 流，回滚被打断的 LLM 轮次，并重新进入 STT。WebRTC 传输比 WebSocket 更适合中断，因为 UDP 在丢包时不会产生队头阻塞。

**流式转写。** 用户仍在说话时，流式 STT 每约 50ms 发出部分转写，因此转写与语音并行运行，用户停止后几乎不增加额外延迟。要区分三种 STT 延迟：部分转写、最终转写（说话结束后）和端点检测延迟。语音 Agent 优化的是最后一项。

**TTS 与首音频时间（TTFA）。** Agent 应该在第一批词语生成后立即开始说话，而不是等待完整句子生成。TTS 按块流式输出音频；TTFA（第一个音频字节的时间）是核心指标，现代流式引擎的首块目标约为 100～200ms。

---

## 延迟预算

自然的人类对话中，一方说完到另一方开口的间隔平均约为 **200ms**。端到端低于约 700ms 时，Agent 感觉像人；超过这个值，来电者就会开始插话和重复。完整流式级联的一轮现实预算如下：

| 阶段 | 典型预算 | 备注 |
|-------|---------------|-------|
| 网络传输（单向） | 30-80ms | WebRTC/UDP 小于 100ms；SIP 每跳增加 20-50ms |
| VAD 帧决策 | 10-50ms | 持续运行 |
| 端点/轮次决策 | 150-300ms | 主要由静音/置信度配置决定 |
| STT 最终转写 | 说完后 50-100ms | 说话时已经流式输出部分结果 |
| **LLM 首 Token 时间** | **150-400ms**（可能更高） | 通常是唯一最大的可控成本 |
| TTS 首音频时间 | 100-200ms | 仅首块；其余内容流式输出 |
| **实际端到端（TTFA）** | **约 600-800ms，表现良好** | 流式化让总延迟趋近 `max(stage)` 而不是总和 |

朴素的非流式技术栈通常需要 1000～2000ms，甚至更久。按影响排序的杠杆是：**所有环节流式化**（部分转写、Token 流、分块 TTS，把求和变成最大值）；**调优端点检测**（学习式轮次检测器替代固定的长静音超时）；**选择快速首 Token 路径**（更小/更快的模型或投机草稿，因为 LLM 首 Token 时间是最长木板）；**按 TTFA 选择 TTS**并在第一小句出现时就开始播放；以及使用 **UDP 上的 WebRTC**，把抖动控制在约 20ms 以内。

---

## 2026 年技术栈

把具体名称、版本和价格视为时间点快照。

- **编排框架**：LiveKit Agents 和 Pipecat 是开源领先者（原生 WebRTC，支持自带 STT/LLM/TTS 或接入 S2S 模型，并提供 VAD + 轮次检测器）。Vapi、Retell 和 Bland 是托管平台。计入工程时间后，托管方案在每月约 1 万分钟以下通常更便宜；超过这一规模，框架方案据报道单通成本更低。
- **STT**：Deepgram 和 AssemblyAI 领先实时流式转写，两者都内置端点检测，报告词错误率约为 6%～7%（取决于基准）。
- **S2S 实时模型**：OpenAI Realtime API（`gpt-realtime` 系列；当前支持版本见[模型分类](../02-model-landscape/01-model-taxonomy.md)，因为后缀经常变化）、Google Gemini Live 原生音频和 AWS Nova Sonic。这些模型支持函数调用；OpenAI 还支持在实时会话中使用远程 MCP 服务器。
- **TTS**：Cartesia 和 ElevenLabs 在低延迟流式方面领先；供应商声称 TTFA 从几十毫秒到约 200ms 不等，需以基准为准。
- **传输**：客户端到 Agent 的媒体使用 WebRTC（UDP、Opus 编解码器）；服务器到模型的一侧使用 WebSocket（TCP）更简单，但丢包会有队头阻塞。常见混合方式是 WebRTC 客户端到中继、WebSocket 中继到模型 API。SIP 连接电话网络（PSTN），每个运营商跳都会增加延迟。

---

## 生产注意事项

**ASR 错误是主要故障。** 值得记住的基准结论是：认证是瓶颈，因为一旦 Agent 听错姓名、邮箱或确认码，下游都会失败。防御措施包括：用置信度阈值把低置信度片段转成澄清问题（“你说的是……吗？”），以及为姓名、SKU 和字母数字串使用自定义词汇/关键词增强。

**对话中途的工具调用。** 两种架构都支持函数调用。发出“我来查一下”这样的口头填充语，覆盖工具延迟，避免工具运行时线路无声。

**跨轮次记忆。** S2S 模型每轮重新发送音频历史，因此 Token 成本和上下文压力随通话长度增长；应裁剪工具输出并做摘要。语音路径的持久化跨会话记忆仍然较弱；把记忆放在文本/LLM 层（级联）成本更低。参见[Agent 记忆与状态](../07-agentic-systems/05-agent-memory-and-state.md)。

**电话场景。** SIP 中继接入 PSTN，提供 8kHz mu-law 音频；如果处理不当，会破坏 VAD 和轮次检测，这是电话线路上有文档记录的 S2S 故障模式。

**可观测性与评估。** 级联技术栈免费提供文本产物；S2S 需要并行转写流。需要了解的基准是 **tau-Voice**（Sierra，arXiv:2603.13686），它把 Agent 工具使用评测扩展到带噪声、口音和中断的全双工语音，并隔离语音特有的故障类别：ASR 听错、中断管理错误、多步骤上下文丢失和无法从断线中恢复。参见[评估 Agent 系统](../07-agentic-systems/10-evaluating-agentic-systems.md)。

**音频 Token 比文本贵得多。** OpenAI 实时模型的报告价格中，音频输入约为文本输入的 8 倍，音频输出约为文本输出的 4 倍；音频按时长编码（粗略地说，用户语音约每 100ms 1 Token，合成语音约每 50ms 1 Token）。据报告，Prompt 缓存和裁剪工具输出可以显著降低每分钟成本。语音 Agent 应按分钟而不是抽象的每 Token 预算，并参见[FinOps 与 Token 经济学](../11-infrastructure-and-mlops/04-finops-and-token-economics.md)。

---

## 诚实的成熟度判断

2026 年已经做得好的事情：调优后的级联和 S2S 都能达到亚秒级、接近自然的单轮延迟；学习式轮次检测优于静音阈值；级联运行时能确定性地处理抢话；S2S 具有富有表现力的韵律；工具生态已经成熟。

仍然困难的事情：全双工自然度（优雅重叠、附和、可靠的思路中途打断）；真实噪声音频；句中代码切换；以及语音路径中的长上下文记忆。tau-Voice 的核心提醒是：在真实噪声条件下，即便是前沿语音 Agent 也只保留等价文本 Agent 任务能力的大约 30%～45%，绝大多数失败来自 Agent 行为，而不是测试 Harness。**语音还不是“文本 Agent 加一支麦克风”。** 应针对差距设计：明确确认关键槽位（姓名、代码、金额），保留人工转接路径，并在噪声和中断条件下评估，而不只是干净音频。

---

## 面试问题

### Q：请说明语音 Agent 的延迟预算。毫秒花在哪里，最大的单一杠杆是什么？

**强回答：**
自然对话的轮次间隔约 200ms，端到端低于约 700ms 时 Agent 感觉像人。预算分布在传输（每个方向 30～80ms）、VAD（10～50ms）、端点检测（150～300ms，由静音或置信度配置决定）、STT 最终转写（说完后 50～100ms，部分结果在说话时已经流出）、LLM 首 Token 时间（150～400ms，通常是最长木板）和 TTS 首音频时间（100～200ms）。最大的杠杆是让所有环节流式化，因为这样总延迟会从阶段之和变成接近最大阶段：部分转写、Token 流和分块 TTS 可以重叠，而不是串行。之后用学习式轮次检测器替换固定的长静音超时，可以移除每轮固定成本；选择快速首 Token 模型则直接攻击最长木板。

### Q：级联流水线和语音到语音如何选择？

**强回答：**
需要可审计性、合规、供应商灵活性、深度工具使用和可预测成本时选择级联，因为每个边界都有文本，提供日志、可替换组件和审核钩子；它是企业默认方案。对话自然度和最低中断延迟最重要，并且能接受故障不透明、供应商更少以及随通话长度增长的 Token 成本时选择语音到语音，因为它每轮重新发送音频历史。很多团队使用混合方案：S2S 负责对话核心，并行 STT 流只用于日志和评估。我不会假设 S2S 自动拥有更低延迟；调优良好的级联很有竞争力，而传输和端点配置无论如何都会占主导。

---

## 参考资料

- Sierra：《tau-Voice: advancing agent benchmarking to knowledge and voice》，arXiv:2603.13686，以及[博客](https://sierra.ai/blog/bench-advancing-agent-benchmarking-to-knowledge-and-voice)
- OpenAI，[Introducing the Realtime API](https://openai.com/index/introducing-the-realtime-api/)
- LiveKit，[turn detection for voice agents](https://livekit.com/blog/turn-detection-voice-agents-vad-endpointing-model-based-detection)及[用于轮次结束检测的 Transformer](https://livekit.com/blog/using-a-transformer-to-improve-end-of-turn-detection)
- AssemblyAI，[turn detection and endpointing](https://www.assemblyai.com/blog/turn-detection-endpointing-voice-agent)
- Deepgram，[speech-to-speech vs cascade architecture](https://deepgram.com/learn/speech-to-speech-vs-cascade-voice-agent-architecture)
- Pipecat，[open-source voice agent framework](https://github.com/pipecat-ai/pipecat)
- Cekura，[voice AI evaluation metrics](https://www.cekura.ai/blogs/voice-ai-evaluation-metrics)

---

*上一篇：[安全与治理](../17-tool-use-and-computer-agents/07-safety-and-governance.md) · 下一篇：[多模态生成](../19-multimodal-generation/01-multimodal-generation.md)*
