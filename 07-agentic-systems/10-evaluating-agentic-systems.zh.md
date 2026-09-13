# Agent 系统评测

评测 Agent 与评测 RAG 有根本区别。RAG 关注“准确率”，Agent 关注**可靠性、效率和安全性**。生产 Agent 评测依赖**轨迹基准**和用于多步推理的 **LLM-as-Judge**，Langfuse、LangWatch、Braintrust 和 Arize Phoenix 等工具都提供原生的 Trace 级评分能力。

> [!NOTE]
> 关于标准 RAG 评测（检索与生成指标），请参见[06-retrieval-systems/09-advanced-retrieval-patterns.md](../06-retrieval-systems/09-advanced-retrieval-patterns.md)和第 14 节。本章专门关注 Agent 的*执行路径*。

## 目录

- [评测转变](#shift)
- [轨迹基准（黄金标准）](#benchmarks)
- [关键指标：成功、成本和时长](#metrics)
- [用 LLM-as-Judge 评估步骤质量](#judge)
- [生产评测（Agent A/B 测试）](#production)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## 评测转变

| 指标 | RAG 应用 | Agent 应用 |
|------|----------|------------|
| **评测单元** | 单次响应 | **轨迹**（全部步骤） |
| **成功标准** | 有依据性/忠实度 | 任务完成/逻辑正确性 |
| **复杂度** | 低（文本相似度） | 高（工具状态验证） |

---

## 轨迹基准

现代评测关注**“通往结果的路径”**。
1. **最优路径**：解决任务所需的最短工具序列。
2. **Agent 路径**：实际采取的步骤。
3. **得分**：`Efficiency = (Optimal Steps / Agent Steps)`。得分为 `0.2` 表示 Agent 过度游荡或循环。

**常见基准：**
- **SWE-bench**：修复 GitHub 问题（代码自主性）。
- **WebArena**：导航菜单和表单（浏览器自主性）。
- **GAIA**：通用工具使用任务（助手自主性）。

---

## 关键指标

### 1. 任务成功率（TSR）

最终状态正确的任务占比。
> [!IMPORTANT]
> 在资深生产环境中，通过“错误路径”得到的“正确答案”得分为 0。

### 2. 动作成功率（ASR）

返回有效数据的独立工具调用占比（不包含错误或幻觉调用）。

### 3. 每任务单位成本

每个已完成目标的总 Token 加基础设施成本（沙箱、API 调用）。

---

## 用 LLM-as-Judge 评估步骤质量

我们使用更强的模型（Claude Opus 4.7、GPT-5.5 reasoning）审查小 Agent 的**推理日志**。
- **思考质量**：Agent 使用工具 X 的逻辑是否来自观察 Y？
- **冗余检查**：Agent 是否重复了刚刚执行过的搜索？
- **反馈循环**：这个“裁判”输出随后用于 **DPO（直接偏好优化）**，以对齐 Agent 未来的行为。

---

## 生产评测

生产团队使用**影子执行**。
1. **V1 Agent** 响应用户。
2. **V2（实验）Agent** 在“隐藏沙箱”中运行相同查询。
3. **比较**：比较两条轨迹。如果 V2 持续用更少步骤解决任务且没有安全违规，就将它提升到生产环境。

---

## 面试问题

### Q：环境非确定（例如 Web）时，如何评测 Agent？

**强回答：**

我们使用**模拟环境**或**快照状态**。为了高保真测试，使用容器化浏览器，每次测试运行前都重置到干净状态，然后把 Agent 轨迹与**参考 Trace**比较。如果环境确实是实时的，则使用**基于状态的验证**：不比较文本，而是检查外部世界的状态（例如“数据库中是否新增了一行正确值的记录？”）。

### Q：为什么“漫游”（步骤过多）是 Staff 级 Agent 设计中的关键失败？

**强回答：**

漫游会导致三种失败：1）**成本**：每一步都是 LLM 调用；2）**延迟**：每一步增加 2～5 秒；3）**熵**：轨迹越长，Agent 遇到奇怪边界情况并触发幻觉的概率越高。标准修复是**步骤预算**：如果 Agent 在 10 步内没有解决任务，就终止它并升级给人工，防止“Token 泄漏”。

---

## 参考资料

- Jimenez 等，《SWE-bench: Can Language Models Resolve Real-World GitHub Issues?》（2024/2025 更新）
- Microsoft Research，《AgentBench: A Comprehensive Benchmark for AI Agents》（2024）
- RAGAS，《Agentic Evaluation Module》（2025）

---

*下一篇：[长时间运行 Agent 的持久化执行](11-durable-execution.md)*
