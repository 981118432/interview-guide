# 长时间运行 Agent 的持久化执行

Agent 运行不是一个请求/响应处理器。它会调用工具、读取文档、触发动作、等待审批，并在可能持续数分钟、数小时甚至数天的步骤之间携带状态。这与普通基础设施发生冲突：进程会被杀死、节点会被回收、部署会滚动重启 Pod。把状态放在内存中的朴素 Agent 循环会在这些事件中丢失一切，而朴素重试又会重新执行副作用。**持久化执行**是一套让长时间运行 Agent 经受这些事件的工程纪律。本章介绍它的模型、工具、如何映射到 Agent 循环，以及什么时候值得承担它的复杂度。

## 目录

- [为什么 Agent 打破了普通故障模型](#why-agents-break-the-normal-failure-model)
- [持久化执行模型](#the-durable-execution-model)
- [工具](#tools)
- [把持久化执行映射到 Agent 循环](#mapping-durable-execution-onto-agent-loops)
- [什么时候需要它](#when-you-need-it)
- [你需要持久化执行吗？](#do-you-need-durable-execution)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## 为什么 Agent 打破了普通故障模型

Agent 是长时间运行、有状态且会产生副作用的进程，因此打破了三个假设：

- **副作用恰好执行一次。**如果工具调用成功，但 Agent 在记录结果前崩溃，恢复后的运行可能重试该调用，造成重复付款、工单或部署。核心歧义是：活动中途崩溃后，你无法判断副作用已经提交，还是只有确认消息丢失，因此朴素重试会发送两次。
- **重启后仍能保留人在回路的暂停。**Agent 可能需要阻塞等待审批数小时或一天，同时不能丢失进度或持续消耗计算。保存在进程内存中的暂停会在下一次部署时消失。
- **记录非确定性。**不能重放 LLM 调用并假设它是同一个事件；相同 Prompt 也可能产生不同响应。输出必须在第一次执行时记录，并在恢复时复用。

朴素重试会重新执行副作用；只在步骤之间保存状态的朴素检查点，仍然会在执行副作用与记录结果之间留下不安全窗口。需要教给面试者的区别是：**检查点捕获状态，而持久化执行捕获步骤日志**；仅凭状态快照无法安全地从副作用执行到一半的位置恢复。

---

## 持久化执行模型

核心模式是**代码即工作流 + 追加式事件历史 + 确定性重放**。Temporal 等系统为每个工作流记录不可变事件历史；如果 Worker 在 10 步中的第 5 步崩溃，另一个 Worker 会重放历史，重建内存状态，并从第 6 步继续。

确定性约束的来源是其中的承重概念：恢复依赖重放，因此重放时执行中的步骤必须与日志中的步骤一致，否则系统无法保证恢复。这意味着**工作流代码本身必须确定**：不能直接调用当前时间、不能使用随机数或 UUID、不能直接发起网络调用，也不能在工作流代码中依赖非确定性的线程交错。非确定性和副作用被推入 **Activity**（步骤）中；Activity 的结果只记录一次，之后从日志重放。

构成模块包括：
- **Activity** 是副作用和非确定性存在的唯一位置，每个 Activity 都独立重试。
- **恰好一次 Activity** 使用幂等 Key，通常由工作流 ID 和步骤 ID 派生，因此重试工具调用不会重复执行。
- **持久化 Timer** 会被持久化并跨越 Worker 重启和部署，因此工作流可以等待数天而无需持续占用进程。
- **Signal** 把外部事件（审批、取消）推送到运行中的工作流；配套的 **Query** 可以读取当前状态而不产生变更（状态、监控）。工作流等待 Signal 或 Timer 时，Worker 会空闲且不消耗计算；事件到达后，它重放历史并继续执行。

基于重放的确定性的成本是**版本管理**：长时间运行的工作流会重放旧历史，修改工作流代码可能破坏重放并导致事故，除非小心进行版本化。这是最常被引用的运维风险。

---

## 工具

| 工具 | 状态存储位置 | 运维体量 | 说明 |
|------|--------------|----------|------|
| **Temporal**（参考） | 独立集群（或 Temporal Cloud） | 高 | 事件历史加确定性重放；多语言；大规模验证；Agent 框架集成最深入。 |
| **Restate** | 轻量引擎、Sidecar 或嵌入式 | 低 | 记录每个步骤；提供 Virtual Objects（按用户/会话 Key 化的有状态 Session，并自动控制并发）。 |
| **DBOS** | Postgres 行 | 最低 | 导入即用的库；工作流状态和事务性副作用可以共享一个 Postgres 事务，从而保证数据库步骤恰好执行一次；无需独立集群。 |
| **Inngest** | 托管式、事件驱动 | 低 | 独立重试步骤，提供 AI 专用原语，并内置用于 LLM 限流的并发和节流。 |
| **AWS Step Functions** | AWS 托管 | 托管 | 使用声明式状态机表达工作流（不是通用代码）；近期增加了 Agent Runtime 集成。 |

这些方案的区别在于持久化边界放在哪里。Temporal 用运维开销换规模；DBOS 把持久化收进现有数据库；Restate 原生支持 HTTP/gRPC 并提供持久化 Session；Inngest 事件驱动且优先支持 TypeScript；Step Functions 原生适配 AWS，但使用声明式状态机而不是通用代码。

---

## 把持久化执行映射到 Agent 循环

核心映射是：**Agent 循环变成工作流，每次模型调用和工具调用变成持久化 Activity。**发生崩溃时，已完成的模型调用和工具调用从日志重放，而不是再次执行，因此不会重复支付 Token 或再次触发副作用；甚至可以修复 Bug 后恢复正在运行的应用。

2026 年的集成版图包括：
- **Temporal + OpenAI Agents SDK** 在 2026 年初达到正式可用，把每次 Agent 调用和工具调用包装为持久化 Activity。
- **Temporal + Google ADK** 处于实验阶段，把 LLM 调用重新路由到 Activity；它的特点是所需代码改动很少（包装器会检测是否处于工作流中，否则回退到直接执行）。
- **LangGraph** 通过 Checkpointer 提供更轻量、框架原生的持久化：在每个 Super-step 把图状态保存到持久存储，并支持选择持久化模式（退出时、异步或每步执行前同步检查点）。它的指南也遵循确定性规则：保持工作流确定且幂等，把副作用包装成任务。
- **DBOS 和 Restate** 在库级别与 Agent 框架集成，把 Agent 运行和子 Agent 调用包装为持久化工作流和子工作流。

需要诚实说明的张力是：**框架原生检查点恢复的是状态；完整的持久化执行引擎还提供恰好一次副作用、持久化 Timer、Signal 以及跨部署的重放语义。**当工具调用具有不可逆的外部副作用时，这个差距最重要。对于主要是 LLM 推理、工具可恢复且幂等的 Agent，框架检查点加少量非幂等工具上的幂等 Key，通常就够了。

把这些能力串起来的典型模式是：如果提议的动作有风险，工作流通过 Signal 暂停并等待人工审批，等待期间不消耗计算，然后持久化恢复——这就是[人在回路](08-human-in-the-loop-patterns.md)审批门的抗崩溃版本。

---

## 什么时候需要它

持久化执行正在成为生产 Agent 可靠性的答案，2026 年的增长是真实的：Temporal 完成了一轮据报道估值达数十亿美元的大额 D 轮融资，许多大型 AI 产品也在此基础上构建 Agent。一份广为引用的供应商案例研究描述了一个深度研究 Agent：它在遇到竞态、脆弱的自定义重试逻辑和难以维护的陈旧状态 Bug 后，**从框架原型迁移到了持久化执行引擎**（这是供应商发布的案例，因此可以把方向视为真实，把表述视为供应商立场）。

但这是一项有意识的复杂度权衡。确定性约束、版本风险、新的测试和监控模型都是真实成本；对于主要只读、生命周期短或单次执行的 Agent，**框架原生检查点，或队列加幂等 Key，通常已经足够**，而且运维便宜得多。相较完整集群，DBOS 和 Restate 显著降低了进入门槛，因此如果反对意见是运维开销，库加 Postgres 的方案也许能获得大部分价值。

---

## 你需要持久化执行吗？

按顺序回答以下问题：

1. **是否有工具调用产生不可逆的外部副作用**（支付、邮件、部署、工单、跨系统写入）？没有：框架检查点或重试/队列可能足够。有：继续。
2. **单次运行是否可能超过进程或部署周期，或者必须跨重启等待人工审批？**没有：内存状态加完成时检查点可能就够了。有：需要持久化 Timer 和持久化暂停。
3. **崩溃时重新运行整个 Agent 是否不可接受**（成本、重复副作用或丢失数小时进度）？是：需要重放和恰好一次，因此持久化执行有合理性。
4. **选择重量级别**：如果副作用主要是写入自有 Postgres 且希望一次部署，选择 DBOS；如果需要低运维、HTTP 原生、有状态 Session，选择 Restate；如果需要事件驱动、TypeScript 优先、AI 原生的限流控制，选择 Inngest；如果全押 AWS 且接受声明式状态机，选择 Step Functions；如果需要大规模、复杂长流程和最深入的 Agent 框架集成，选择 Temporal；如果 Agent 主要做推理且工具可恢复，则继续使用框架原生持久化（LangGraph Checkpointer）加幂等 Key。

对于简单 CRUD、亚毫秒级热点路径、纯高吞吐流式任务，或者一个队列加死信处理器已经能满足需求的小团队，它属于过度设计。

---

## 面试问题

### Q：为什么朴素重试和检查点不足以支持带副作用的生产 Agent？

**强回答：**

因为 Agent 崩溃会产生重试无法安全解决的歧义。如果 Agent 调用一个扣款工具后崩溃，你无法从状态快照判断扣款是否已经提交，还是只有确认消息丢失，因此朴素重试可能扣款两次。只在步骤之间保存状态的普通检查点，仍然在执行副作用与记录已执行之间留下不安全窗口。持久化执行通过记录步骤日志而不是只记录最新状态来关闭这个问题：每个有副作用的步骤都是带幂等 Key 的已记录 Activity，因此重放时，已完成 Activity 会返回已记录结果，而不会重新运行。这为副作用提供恰好一次语义，并让工作流从精确失败点恢复，而不是从头开始。

### Q：什么时候持久化执行属于过度设计？这时会使用什么？

**强回答：**

当 Agent 没有不可逆副作用，运行时间短于进程和部署周期，并且失败时重新运行也可以接受时，它属于过度设计。例如只读研究或摘要 Agent，工具本身是幂等的。这时我会使用 LangGraph Checkpointer 等框架原生持久化来恢复状态，在少数非幂等调用上加幂等 Key，再配合带死信处理器的重试队列。完整引擎（如 Temporal）的确定性约束和版本风险是真实成本，因此只有当 Agent 出现不可逆副作用、必须跨重启等待人工审批，或运行足够长以至于崩溃后重跑不可接受时，我才会承担它。如果运维开销是阻力，但确实需要持久化，那么使用现有 Postgres 的 DBOS 这类库方案，可以在不运维集群的情况下获得大部分价值。

---

## 参考资料

- Resonate，[“From where do deterministic constraints come?”](https://journal.resonatehq.io/p/from-where-do-deterministic-constraints)
- Restate，[“What is durable execution?”](https://www.restate.dev/what-is-durable-execution)
- Temporal，[OpenAI Agents SDK integration](https://temporal.io/blog/announcing-openai-agents-sdk-integration) 和 [Series D announcement](https://temporal.io/news/temporal-raises-300M-to-make-agentic-ai-real-for-companies)
- Temporal，[prototype to production-ready agentic AI: a Grid Dynamics case study](https://temporal.io/blog/prototype-to-prod-ready-agentic-ai-grid-dynamics)
- Google ADK，[Temporal integration](https://adk.dev/integrations/temporal/)
- LangChain，[durable execution in LangGraph](https://docs.langchain.com/oss/python/langgraph/durable-execution)
- Diagrid，[“Checkpoints are not durable execution”](https://www.diagrid.io/blog/checkpoints-are-not-durable-execution-why-langgraph-crewai-google-adk-and-others-fall-short-for-production-agent-workflows)

---

*下一篇：[循环工程](12-loop-engineering.md)*
