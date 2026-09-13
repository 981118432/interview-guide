# Agent 记忆与状态

记忆让 Agent 能够随着时间学习并保持上下文。Agent 记忆已经从“聊天历史”发展为具有四个明确层级（工作、情景、语义、程序）的**多层认知架构**，每层都有自己的写入模式、延迟预算和失败模式。如今的生产系统（Mem0、Letta、Anthropic Memory Tool + Skills、Zep/Graphiti、LangMem）已经把记忆选择视为一等架构决策。

正在塑造本章的 2026 研究浪潮包括：A-MEM（NeurIPS 2025）、HippoRAG（多跳图检索）、多层记忆架构、HaluMem（操作级记忆幻觉基准）、MINJA / MemoryGraft（仅查询型记忆投毒攻击），以及 TTT-E2E（由 Stanford、Berkeley、UCSD、NVIDIA 和 Astera 多个实验室共同参与），后者通过测试时训练将上下文压缩到权重中。

## 目录

- [记忆层级](#hierarchy)
- [短期记忆：推理轨迹](#short-term)
- [情景记忆：过去经验](#episodic)
- [语义记忆：Persona](#semantic)
- [程序记忆：学习到的技能与工作流](#procedural-memory-learned-skills-and-workflows)
- [权衡：事实 X 应该放在哪里？](#tradeoffs)
- [生产实现（2026 年 5 月）](#production-implementations)
- [失败模式与缓解](#failure-modes)
- [Mem0 与 Agent 个性化](#mem0)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## 记忆层级

Agent 使用分层方式存储：

| 层级 | 类型 | 技术 | 用途 |
|------|------|------------|---------|
| **L1** | 工作记忆 | 上下文窗口 / KV Cache | 当前任务步骤、局部变量 |
| **L2** | 情景记忆 | 向量数据库 / 图 | “我上次做了什么？” |
| **L3** | 语义记忆 | SQL / 知识图谱 | 用户偏好、“事实真相” |
| **L4** | 程序记忆 | Skills 注册表 / 工具策略 / 工作流图 | “我如何完成这个任务？” |

### 各层的实际属性

这些层的差异不只在用途。读取模式、写入模式、延迟预算和新鲜度预期都会把它们推向不同的存储技术：

| 维度 | L1 工作 | L2 情景 | L3 语义 | L4 程序 |
|---|---|---|---|---|
| **保存内容** | 当前轮次、工具输出、草稿、系统 Prompt | 过去会话、轨迹、带时间戳的观察 | 提炼后的事实、偏好、实体关系 | Skills、操作手册、系统 Prompt 指令、代码/工具序列 |
| **读取模式** | 每个 Token、每一轮（注意力内） | 按相似度 + 新近度 + 重要性取 Top-K | 提及实体/主题时触发查询 | 匹配任务签名时加载 |
| **写入模式** | 推理引擎持续追加；轮次边界提交 | 只追加日志；轮次边界提交 | 提取、去重、Upsert；写入时解决冲突 | 成功/失败后反思式写入；人工或自编辑 |
| **延迟预算** | <50ms（驻留 GPU HBM） | 100～300ms（向量 ANN + 重排序） | 200～800ms（图遍历 + LLM 提取） | 50～500ms（文件读取或小索引查询） |
| **新鲜度预期** | Token 级最新；会话结束即丢失 | 数小时到数月；容忍过时 | 应反映**当前**状态；过时就是 Bug | 变化慢；更新需要审慎 |
| **存储技术** | HBM 中的 KV Cache（vLLM PagedAttention 块） | 向量数据库（Pinecone、Weaviate、Qdrant）、只追加日志 | 知识图谱（Neo4j、Graphiti）、KV 存储、双时间关系行 | 文件系统（Claude `/memories/`、`SKILL.md`）、Prompt 注册表、微调 LoRA |
| **查询语义** | 位置 + 注意力 | 相似度 + 新近度 + 重要性（Park 等加权） | 实体关系匹配、结构化查询、双时间过滤 | 任务签名匹配，通常是文件名或标签查询 |
| **驱逐** | 滑动窗口、按 KV 块哈希 LRU | 衰减评分、整合到 L3、归档到冷存储 | 通过时间 `valid_to` 替代；GDPR 显式删除 | 手动弃用、与新 Skill A/B 对比、版本固定 |

**实践含义**：事实出现时，架构问题不是“要不要记住它”，而是“*放在哪一层*、采用怎样的新鲜度契约和驱逐规则”。层级选择错误会产生可预测的失败模式（会话偏好提升到 L3 会跨会话泄露；稳定用户事实留在 L2 会在两周后被驱逐）。参见下文的[权衡：事实 X 应该放在哪里？](#tradeoffs)。

---

## 短期记忆：推理轨迹

生产 Agent 不再只存储“消息”，而是存储**状态对象**。
- **草稿区**：Prompt 的专用区域，Agent 在这里给自己“写笔记”，不会展示给用户。
- **KV Cache 分块**：对长时间运行的 Agent，使用**前缀缓存**让“系统指令”和“标准工具”常驻 GPU 内存，只替换动态任务状态。

---

## 情景记忆：过去经验

情景记忆保存“运行”或“轨迹”。
- 如果 Agent 上周二抓取网站时失败，情景记忆应阻止它今天再次尝试同一个失败的选择器。
- **模式**：任务完成时，总结“经验教训”并存进向量数据库；新任务开始时，对类似过去任务执行**自搜索**。

---

## 语义记忆：Persona

语义记忆保存用户或环境的“事实”。
- *“用户偏好 JSON 输出。”*
- *“生产数据库每天凌晨 3 点到 4 点离线。”*

**最佳实践**：语义记忆使用**知识图谱**。向量搜索是模糊的，而图可以确定性地检索实体和关系（例如 `User` -- `OWNER_OF` --> `Project_A`）。

---

## 程序记忆：学习到的技能与工作流

程序记忆保存做事的方法。情景记忆回答“之前发生了什么？”，语义记忆回答“什么是真的？”，程序记忆回答：

“完成这类任务的正确流程是什么？”

这一层包含可复用的 Skills、工具使用模式、操作流程和工作流偏好。

示例：

* “生成周报时，先从 Snowflake 拉取指标，再与仪表盘校验，最后总结异常。”
* “回复客户投诉时，先分类紧急程度，检索政策，起草回复；如果置信度低就升级。”
* “编写 SQL 时，始终先检查 Schema，再生成查询、运行校验并解释假设。”

程序记忆对 Agent 系统尤其重要，因为许多任务不只是记忆事实，还要求遵循正确的动作顺序。

---

## 权衡：事实 X 应该放在哪里？

第一性决策不是“选择哪一层”，而是“*错误的代价由谁承担*”。L2 一次检索遗漏只会影响一轮；L3 中的错误事实在修正前会影响*每一轮*；L4 中被投毒的 Skill 会传播到未来每次调用。

### 层级选择表

| 事实/关注点 | 层级 | 理由 |
|---|---|---|
| “用户的 API 速率限制是 1000 req/min” | L3，带双时间 `valid_to` | 租户范围事实，可按实体查询，必须支持替代。不是 L4——它是数据，不是流程。 |
| “部署我们服务的步骤” | L4，作为版本化 Skill | 带条件分支的多步骤配方。Skills 可以组合，语义三元组不行。 |
| “Agent 上一次执行此任务的失败尝试” | L2 原始记录；若可泛化，再将经验反思到 L4 | 原始轨迹属于情景记忆；通用经验（“绝不要在高峰时段运行迁移”）才值得写入 L4。 |
| “用户偏好简洁回复” | L3 | 稳定偏好，可通过 `user_id` 查询，是单一三元组。 |
| “用户在本次会话中要求简洁回复” | 仅 L1 | 会话范围偏好，不要用可能短暂的偏好污染 L3。 |
| 当前天气、今天的股价 | 无：调用工具 | 有其他真实来源的快速变化事实不应进入记忆。 |
| “Project Phoenix 的成员是 A、B、C” | L3，作为图片段 | 具有多跳遍历价值，适合 Graphiti 或 Neo4j 风格存储。 |

### 成本权衡

- **L1 主导延迟成本**：TTFT 随上下文大小增长；工作记忆越长，首 Token 越慢。KV Cache 压力会使高端加速器内存趋于饱和。
- **L2 在规模化时主导存储成本**：只追加日志随使用量线性增长。[第 30 天问题](https://cipherbuilds.ai/blog/day-30-agent-memory-problem)描述了未剪枝的情景存储如何在一个月后损害 Agent 质量。
- **L3 主导写放大成本**：每轮都可能触发提取、去重和冲突解决。Mem0 的设计明确以写入时工作换取检索速度。
- **L4 主导治理成本**：错误 Skill 会传播到未来每次调用。Anthropic 的“[Claude Dreaming](https://www.mindstudio.ai/blog/what-is-claude-dreaming-anthropic-agent-memory)”定时整合正是通过审核控制 Skill 更新。

### 晋级规则

有趣的设计问题是：L2 情景何时晋级为 L3 或 L4。可辩护的规则应基于阈值，而不是隐式衰减：

1. 同一模式有 **N 次独立观察**（通常 N=3～5）。
2. 按来源进行**置信度加权**：用户明确陈述 > 工具输出 > 模型推断。
3. 在整合步骤进行**人工或 LLM 评判审核**（而不是每一轮都审核）。
4. 使用**定时批量整合**，而不是每轮同步写入（避免写放大）。
5. **双向**：L3 的语义事实可以针对特定任务重新实例化为情景上下文。记忆不是单向通道。

---

## 生产实现（2026 年 5 月）

这些系统的差别不在于“存储什么”，更多在于**写入纪律**、**检索算法**和**治理姿态**。

| 系统 | 最佳场景 | 做得好 | 局限 |
|---|---|---|---|
| **[Mem0](https://github.com/mem0ai/mem0)** | 大规模跨会话个性化 | 图 + 向量 + KV 混合。在 2026 年 4 月单次重设计后，LoCoMo 得分 92.5、LongMemEval 得分 94.4（[基准测试](https://mem0.ai/blog/ai-memory-benchmarks-in-2026)）；正面对比中准确率比 OpenAI 内置记忆高 26%。 | 每条记忆上限 8K 字符（不适合文档）；云优先带来数据主权问题；没有正式信念状态模型（只支持覆盖或追加）。 |
| **[Letta（原 MemGPT）](https://docs.letta.com/concepts/memgpt/)** | 长时间运行、连贯性就是产品价值的自主 Agent | 在核心/召回/归档层间进行类似 OS 的虚拟上下文分页；Agent 通过工具调用将数据分页进出。适合“Agent 永远记得”的用户体验。 | 单轮延迟高于 Mem0 风格；未针对跨用户检索精度优化。 |
| **[Anthropic Memory Tool + Skills](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool)** | 在同一底座中提供文件系统 L3/L4 | 记忆位于 `/memories/`；Skills 是 `SKILL.md` 包及可选脚本；托管 Agent 按会话挂载 `/mnt/memory/`，并支持不可变版本（2026 年 4 月 23 日 GA）。定时的“Claude Dreaming”在会话之间整合记忆。 | 文件系统语义把复杂性推给 Agent，要求 Agent 自己良好地组织目录。 |
| **[Zep + Graphiti](https://github.com/getzep/graphiti)** | 关心事实“何时成立”的时间事实 | 开源时序知识图谱，每条边都有 `valid_from` / `valid_to` / `invalid_at`；在 DMR 上以 94.8% 超过 MemGPT 的 93.4%。双时间查询支持回答“3 月 12 日我们相信什么？”与“现在什么是真的？”。 | 图提取、去重、冲突解决使写路径重于纯向量存储。 |
| **[LangMem + LangGraph](https://langchain-ai.github.io/langmem/)** | 想在 LangGraph 编排中使用四类记忆 | 支持情景、语义和程序记忆；LangMem 的程序记忆让 Agent 可以根据反馈更新自己的系统 Prompt；后台提取异步运行。 | 与 LangGraph 耦合，不在 LangChain 技术栈时吸引力较低。 |
| **[OpenAI ChatGPT Memory](https://openai.com/index/memory-and-new-controls-for-chatgpt/)** | 消费级聊天连续性，而非生产级 Agent 记忆 | 两层架构：显式“保存的记忆”加上预注入上下文的轻量会话摘要；推理时跳过一次检索以降低延迟。 | 精度低于 Mem0 风格检索，没有企业集成所需的细粒度编程 API。 |
| Cursor / Windsurf | 面向代码库的 L2/L3 软件工程 Agent | 打开项目时索引代码库；用 `@` 提及显式加入上下文。Windsurf 的“Memories”在约 48 小时使用后学习架构模式。 | 受限于代码领域，不是通用记忆层。 |
| **[Cognition Devin](https://cognition.ai/blog/devin-sonnet-4-5-lessons-and-challenges)** | 仓库范围的工程 Agent | 每隔数小时自动索引仓库 Wiki；偏好显式压缩/摘要，而不是由模型管理状态。Devin Search 是 Agent 式代码库记忆查询接口。 | 针对工程工作流，观点较强。 |

**Generative Agents（Park 等，2023）**仍是每篇综述都会引用的参考架构。新近度/重要性/相关性检索公式（`alpha_recency * recency + alpha_importance * importance + alpha_relevance * relevance`，每项归一化到 [0,1]，重要性由 LLM 评为 1～10）仍被上述大多数系统用于生产。

**值得关注的新兴框架**（2026 年 5 月）：[Supermemory](https://supermemory.ai)、[Recallr](https://recallrai.com)、AWS [Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory-integrate-lang.html)、[Oracle AI Agent Memory](https://blogs.oracle.com/developers/oracle-ai-agent-memory-a-governed-unified-memory-core-for-enterprise-ai-agents)。

---

## 失败模式与缓解

生产记忆系统反复出现六种失败模式。能说出它们的名字，是区分初级和资深架构讨论的关键。

### 1. 通过 Prompt 注入进行记忆投毒

不可信输入被写入 L3/L4，之后又作为权威内容回放。[MINJA（NeurIPS 2025）](https://openreview.net/forum?id=QVX6hcJ2um) 和 [MemoryGraft（2025 年 12 月）](https://arxiv.org/html/2512.16962v1) 展示了不需要提升权限的**仅查询型**投毒攻击，可达到 95% 的注入率和 70% 的攻击成功率。[Palo Alto Unit 42 的分析](https://unit42.paloaltonetworks.com/indirect-prompt-injection-poisons-ai-longterm-memory/)显示，攻击者可以提前数周植入毒内容。

**缓解：**
- 每次写入都加**来源标签**：`source = user_stated | model_inferred | tool_output`。
- 使用**写入时护栏模型**，拒绝可疑的指令式写入。
- 使用**信任层级**：低信任记忆在影响高风险决策前必须得到佐证。
- 使用**隔离舱**，防止一个租户的投毒横向影响另一个租户。

### 2. 事实过时

昨天的偏好不一定是今天的偏好，例如“用户上月说喜欢深色模式，但现在使用浅色模式”。

**缓解措施：**
- **双时间存储**（Zep/Graphiti 模式）：每个事实都有 `valid_from`、`valid_to` 和 `invalid_at`。
- 对会话范围偏好设置 **TTL**，使其自动过期。
- 在检索评分中加入**衰减权重**。
- 对超过 N 天的高风险事实，使用 Prompt 要求**显式重新确认**。

### 3. 事实冲突

用户先说 X、现在说 Y。不同冲突类型应有不同响应：时间更新覆盖旧事实，纠正应带审计轨迹撤回，偏好变化添加新事实并让旧事实衰减，无法解决的矛盾应询问用户，绝不能静默覆盖。使用 AGM 信念修订跟踪 `ACTIVE` / `SUPERSEDED` / `RETRACTED` 状态，而不是简单的最后写入胜出。

| 冲突类型 | 正确响应 |
|---|---|
| 时间更新（“我搬到了柏林”） | 用 `valid_to = now` 让旧事实失效 |
| 纠正（“我从没说过那句话”） | 保留审计轨迹并撤回 |
| 偏好变化（“我现在想要简洁回复”） | 添加新事实，让旧事实自然衰减 |
| 明显矛盾（没有明确解决方式） | 询问用户，绝不静默覆盖 |

### 4. 记忆漂移

低质量写入会稀释高质量记忆，质量随时间下降。[第 30 天问题](https://cipherbuilds.ai/blog/day-30-agent-memory-problem)记录了情景存储充满噪声后，Agent 在进入生产约 30 天时性能下降的现象。

**缓解措施：**
- **按质量加权检索**：提升具有高验证分数的记忆。
- 运行**定时整合任务**，合并重复项并剪枝低效用记忆。
- 在 CI 中加入**金丝雀事实测试**：“Agent 在 50 轮后仍应记住用户姓名。”

### 5. 幻觉记忆写入

Agent 推断出一个事实并当作真相保存，之后又把它作为权威引用，形成级联故障。[HaluMem 基准（2025 年 11 月）](https://arxiv.org/abs/2511.03506)表明，现有系统会在写入时累积错误，并将错误向前传播到问答阶段。

**缓解措施：**
- 使用**由 Schema 强制约束的记忆对象**，将带来源的 `confirmed_facts` 与带置信度的 `inferred_facts` 分开。
- 没有用户明确信号或工具输出佐证时，绝不自动把推断提升为已确认事实。
- 在 CI 中采用 HaluMem 风格的分阶段评估，分别测量提取精度、更新正确性和问答准确率，而不是只看单一端到端指标。

### 6. 跨租户泄露

向量 ANN 返回另一个租户的邻居，缓存 Prompt 包含另一个租户的数据。[实地测量](https://medium.com/@isuruig/multi-tenant-ai-infrastructure-the-5-isolation-layers-that-determine-whether-your-customers-data-stays-separate-340aaeef4922)显示，在未隔离的多租户 RAG 中，即使是无恶意查询也可能出现约 95% 的自然泄露率。

**缓解措施：**
- **物理隔离**：使用按租户划分的集合，而不是依赖元数据过滤的共享索引。
- 通过服务账号权限在**存储层**强制租户范围，而不是只依赖应用代码。
- 为每个租户分离 KV Cache 前缀。
- 为记忆 Blob 使用按租户加密密钥，使跨命名空间读取在密码学层失败。

---

## Mem0 与 Agent 个性化

**Mem0**、Zep、Letta 和 Cognee 是 Agent 技术栈中“智能记忆”的标准框架。
- 自动从对话中提取“用户洞察”。
- 提供 Agent 可调用的 Memory API，用于 `remember` 或 `forget` 特定信息三元组。
- **影响**：Agent 会记住你三个月前在另一个会话中提到的细节，因此感觉更“有生命力”。

---

## 面试问题

### Q：Agent 系统如何处理“冲突记忆”？

**参考答案：**
通过**时间加权**或**显式争议处理**。为每个记忆三元组分配 `timestamp` 和 `confidence_score`；新事实与旧事实冲突时，让 Agent 询问用户，或默认采用更新时间。对长期未强化的旧记忆使用衰减函数，最终从活动索引中剪枝。

### Q：为什么仅靠上下文窗口不足以支撑资深级 Agent 架构？

**参考答案：**
首先是**成本和延迟**：每轮填充 100 万 Token 即使有上下文缓存也贵得难以接受。其次是**信噪比**：大上下文窗口会受到上下文学习退化影响，模型会被无关历史轮次分散注意力。资深级架构使用**选择性记忆检索**（对历史做 RAG），只拉取最相关的 3～5 次历史交互，让推理引擎聚焦当前子目标。

### Q：如何为生产 AI Agent 设计程序记忆？

**参考答案：**
把程序记忆设计为**Skills 注册表、工作流图和工具使用策略**的组合。每个程序定义任务类型、必需步骤、可用工具、校验、失败模式和升级规则。每次运行后 Agent 可以反思并更新程序。例如，NL2SQL Agent 反复因为跳过 Schema 检查而失败，就把 Schema 检查编码为所有 SQL 生成任务的第一步。

### Q：情景记忆什么时候会从资产变成负担？

**参考答案：**
情景记忆会在三种明确模式下从资产变成负担。第一是**索引过载**：加入 1000 条低质量观察后，高质量的 10 条观察在检索中被淹没，这相当于 RAG 意义上的灾难性遗忘。第二是**第 30 天漂移**：情景存储逐渐充满噪声，检索无法区分信号，Agent 质量通常在进入生产约 30 天后开始下降。第三是**过时上下文渗透**：在一种配置下成功的过去轨迹，在新配置下可能变成错误上下文；例如，Stripe 的成功工具序列在用户切换到 Adyen 后反而会误导 Agent。

缓解措施包括按质量加权检索、整合到 L3，以及对依赖上下文的轨迹设置新近度硬截止。更深层的经验是：情景记忆从第一天就需要剪枝策略，否则技术债务会随使用量线性累积。

### Q：Agent 可以写入自己的长期存储时，如何防止记忆投毒？

**参考答案：**
难点在于，近期攻击（MINJA、MemoryGraft）是**仅查询型**攻击，不需要提升权限，毒内容可以在数周前植入、之后才触发。因此威胁模型应当是：“任何输入都可能成为未来的权威记忆。”防御需要四层：

1. **写入时记录来源**：每条记忆携带 `source`（用户陈述、模型推断、工具输出）、`timestamp` 和 `trust_tier`。
2. **写入时护栏模型**：使用较小的分类器，在写入进入存储前拒绝可疑的指令式写入。
3. **佐证阈值**：高风险决策不能建立在一条低信任记忆上，而需要多次独立佐证。
4. **CI 金丝雀测试**：合成投毒载荷不得传播到输出中，按周运行测试。

最重要的架构分离是：Agent 的工具面与记忆写入面不应共享信任。工具输出在成为记忆前必须经过清洗器。

### Q：记忆层级如何选择？（a）用户 API 速率限制，（b）服务部署步骤，（c）Agent 最近一次失败尝试，（d）今天的股价。

**参考答案：**
(a) **L3 语义记忆**，带双时间有效期。它是有替代生命周期的租户范围事实，不应放进 L4，因为它是数据而非流程。

(b) **L4 程序记忆**，作为版本化 Skill 或操作手册。这是带条件分支的多步骤配方；Skills 可以组合，而语义三元组不能。

(c) **L2 情景原始记录**；如果失败揭示了可泛化的经验，再通过反思跳转写入 L4。原始轨迹属于情景记忆；“绝不要在高峰时段运行迁移”这样的经验，才值得以 Reflexion 风格写入程序记忆。

(d) **不进入记忆，调用工具**。有实时真实来源的快速变化事实不应进入记忆，因为它们按定义会过时。

通用规则是：数据放 L3，流程放 L4，观察放 L2，有实时真实来源的快速变化事实不要存储。

### Q：情景向语义过渡的整合策略如何设计？什么时候一段情景会成为事实？

**参考答案：**
我采用基于阈值的晋级策略，而不是隐式衰减：

- **频率阈值**：同一模式有 N 次独立观察（通常为 3～5 次）。
- **置信度加权**：用户陈述 > 工具输出 > 模型推断。
- **评判者审核**：定时批量整合任务对候选晋级事实运行 LLM 评判者；高风险领域则由人工审核。
- **定时而非同步**：整合在 Cron 等带外任务中完成，而不是每轮同步执行，以避免写放大。
- **双向**：L3 的语义事实可以针对特定任务重新实例化为 L2 情景上下文，记忆可以双向流动。

需要避免的陷阱是仅靠衰减权重进行隐式整合。这种方式在小规模下可行，但在生产规模会悄然失败，因为没有“这个事实为何出现在 L3 中”的审计轨迹。

### Q：你的 Agent 记忆库有 10000 个租户、5000 万条记忆。如何保证跨租户隔离？隔离失败时爆炸半径是多少？

**参考答案：**
架构需要五层隔离：

1. **存储层物理隔离**：按租户使用集合或分片，而不是依赖元数据过滤的共享索引。带 `tenant_id` 的共享索引在出现 Bug 时会默认失效开放。
2. **服务账号范围强制**：应用代码无法选择退出租户范围，数据库角色本身就看不到其他租户。
3. **按租户分离 KV Cache 前缀**：防止缓存 Prompt 在租户之间泄露。
4. **按租户加密密钥**：即使 Bug 返回了跨命名空间的字节，也无法读取。
5. **审计每次跨命名空间查询尝试**：在检测层增加纵深防御。

**隔离失败时的爆炸半径**：一次错误的向量查询可能泄露一个查询 Embedding 的**邻域**，也就是某个租户的数百条记录。实地测量显示，未隔离的多租户 RAG 在无恶意查询下也可能出现约 95% 的自然泄露率。缓解方式不是“更仔细的应用代码”，而是采用无法被应用 Bug 绕过的结构性隔离。

### Q：HaluMem 表明记忆幻觉在写入时累积并传播。如何在生产中监控它？

**参考答案：**
团队最容易犯的错误，是只在问答阶段（端到端）测量记忆质量。HaluMem 表明，60%～80% 的记忆错误源于**提取（写入）阶段**，然后向后传播。需要分别监控三个指标：

1. **提取精度**：Agent 将事实写入 L3 时，该事实是否真的得到源观察支持？每天抽样写入，用更强的评判模型评估。
2. **更新正确性**：冲突事实到来时，冲突解决逻辑是否产生了正确结果？用双时间查询发现“事实发生翻转但没有替代元数据”的情况。
3. **问答准确率**：端到端的召回正确性。

此外，运行**影子模式回放**：写入经过验证模型的影子流程，线上写入与影子验证写入的差异会标记潜在幻觉供审核。CI 中的**金丝雀事实**确保记忆系统不会悄然回归；**定期全库审计**抽样随机记忆，询问“它是否仍与源对话一致？”。

### Q：TTT-E2E 通过测试时训练把上下文压缩进权重。它处于 L1～L4 的哪一层？引入了什么新失败模式？

**参考答案：**
TTT-E2E 位于 **L1 与 L4 之间**：它将上下文派生的信息变成模型自身的一部分，并在本次会话剩余时间内保留。它的吸引力在于延迟：无论上下文长度如何，成本都近似恒定；根据 NVIDIA 的基准，在 H100 上 128K Token 可获得 2.7 倍加速，2M Token 可获得 35 倍加速。

新的失败模式是治理问题。权重中的记忆具有以下缺陷：

- **没有审计轨迹**：无法检查“这个模型现在相信什么？”
- **没有驱逐接口**：记忆一旦被压进权重，就不能删除，除非回滚模型状态。
- **GDPR 被遗忘权的挑战**：监管框架假设数据处于静态存储，而不是藏在模型权重中。
- **更难检测投毒**：没有可检查的存储可以扫描金丝雀签名。

除此之外还有能力层面的失败模式：在超出其注意力窗口的“大海捞针”检索中，该方法报告的成功率会失败（128K 时约为 6%，而完整注意力约为 99%），因此它保留的是上下文大意，而不是逐字事实。这使它不能成为检索关键工作唯一的记忆层。

正确的理解是：TTT-E2E 把记忆治理从存储层转移到训练和部署流水线。成本没有消失，只是换了位置。对 2026 年大多数生产团队而言，它仍是值得跟踪的研究方向，而非已经可以部署的架构；更广泛的测试时训练家族见[研究雷达：主题 12](../RESEARCH-RADAR.md#12-test-time-training-learning-at-inference)。

---

## 参考资料

### 生产框架
- [Mem0: Production-Ready AI Agents with Scalable Long-Term Memory (ECAI 2025)](https://arxiv.org/abs/2504.19413)
- [Mem0 AI Memory Benchmarks 2026](https://mem0.ai/blog/ai-memory-benchmarks-in-2026)
- [Letta (formerly MemGPT) documentation](https://docs.letta.com/concepts/memgpt/)
- [MemGPT：作为操作系统的 LLM（arXiv 2310.08560）](https://arxiv.org/abs/2310.08560)
- [Anthropic Memory Tool documentation](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool)
- [Anthropic Claude Sonnet 4.6 Skills 公告](https://www.anthropic.com/news/claude-sonnet-4-6)
- [Claude Dreaming：定时记忆整合](https://www.mindstudio.ai/blog/what-is-claude-dreaming-anthropic-agent-memory)
- [Zep: Temporal Knowledge Graph Architecture](https://arxiv.org/abs/2501.13956)
- [Graphiti GitHub](https://github.com/getzep/graphiti)
- [LangMem documentation](https://langchain-ai.github.io/langmem/)
- [OpenAI Memory 与 ChatGPT 新控制项](https://openai.com/index/memory-and-new-controls-for-chatgpt/)
- [Cognition：为 Claude Sonnet 4.6 重建 Devin](https://cognition.ai/blog/devin-sonnet-4-5-lessons-and-challenges)

### 研究（2023-2026）
- [Generative Agents](https://arxiv.org/abs/2304.03442)
- [Reflexion](https://arxiv.org/abs/2303.11366)
- [HippoRAG](https://arxiv.org/abs/2405.14831)
- [A-MEM](https://arxiv.org/abs/2502.12110)
- [Multi-Layered Memory Architectures](https://arxiv.org/abs/2603.29194)
- [Memp：探索 Agent 程序记忆（2025 年 8 月）](https://arxiv.org/html/2508.06433v2)
- [LEGOMem：多 Agent LLM 的模块化程序记忆（2025 年 10 月）](https://arxiv.org/pdf/2510.04851)
- [重新思考基础 Agent 的记忆机制（2026 年 2 月综述）](https://arxiv.org/abs/2602.06052)
- [立场：情景记忆是缺失的一块（arXiv 2502.06975）](https://arxiv.org/pdf/2502.06975)

### 安全、投毒与幻觉
- [HaluMem](https://arxiv.org/abs/2511.03506)
- [MINJA Memory Injection Attack](https://openreview.net/forum?id=QVX6hcJ2um)
- [MemoryGraft](https://arxiv.org/html/2512.16962v1)
- [Palo Alto Unit 42：间接 Prompt 注入污染 AI 长期记忆](https://unit42.paloaltonetworks.com/indirect-prompt-injection-poisons-ai-longterm-memory/)
- [多租户 AI 基础设施：决定数据隔离的 5 层](https://medium.com/@isuruig/multi-tenant-ai-infrastructure-the-5-isolation-layers-that-determine-whether-your-customers-data-stays-separate-340aaeef4922)
- [第 30 天问题：Agent 记忆漂移](https://cipherbuilds.ai/blog/day-30-agent-memory-problem)

### 基础设施
- TTT-E2E：《面向长上下文的端到端测试时训练》（arXiv:2512.23675），以及 [NVIDIA：重新构想 LLM 记忆](https://developer.nvidia.com/blog/reimagining-llm-memory-using-context-as-training-data-unlocks-models-that-learn-at-test-time/)
- [vLLM PagedAttention](https://docs.vllm.ai/en/latest/design/paged_attention/)
- [Anthropic Effective Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

---

*下一篇：[规划与分解](06-planning-and-decomposition.md)*
