# Tree-of-Thought（ToT）

Tree-of-Thought（ToT）是一种高级 Prompt 架构：模型探索多条推理路径、评估它们，并在某条路径走入死胡同时“回溯”。它是现代自主研究 Agent 背后的蓝图。

## 目录

- [树与链](#tree-vs-chain)
- [ToT 循环：提出、评估、搜索](#tot-loop)
- [自我纠错与回溯](#self-correction)
- [MCTS 与搜索即服务](#mcts)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## 树与链

**Chain-of-Thought** 是线性的（只有一条路径），而 **Tree-of-Thought** 支持分支。

| 特性 | Chain-of-Thought | Tree-of-Thought |
|------|-----------------|-----------------|
| **拓扑** | 线性（1 条路径） | 分支（多条路径） |
| **逻辑** | 顺序 | 并行 + 评估 |
| **自我纠错** | 低（承诺偏差） | 高（回溯） |
| **使用场景** | 数学、简单逻辑 | 解谜、代码架构、战略规划 |

---

## ToT 循环：提出、评估、搜索

ToT 系统由三个模块组成：
1. **思想提出器**：为问题生成 3～5 个潜在的“下一步”。
2. **状态评估器**：为每一步评分（例如“好”“可能”“不可能”）。
3. **搜索算法**：（BFS 或 DFS）决定下一步探索哪个分支。

```python
# The ToT logic (Simplified):
For each branch:
   Score = Evaluate(branch)
   If Score < Threshold:
      Prune branch (Backtrack)
   Else:
      Continue exploring
```

---

## 自我纠错与回溯

ToT 专门用于克服**幻觉级联**。
在线性链中，如果模型在第 1 步犯错，后续每一步很可能都错。在 ToT 中，“评估器”（可以是另一个模型，也可以是基于规则的检查器）会在第 1 步捕捉错误，并迫使模型尝试不同的起点。

---

## MCTS 与搜索即服务

ToT 已经发展为面向 LLM 的**蒙特卡洛树搜索（MCTS）**。
- **搜索时计算扩展**：不使用一个大 Prompt，而是使用 100 个小 Prompt“搜索”最佳答案。
- **RAD-T（Reasoning-as-Data-Tree）**：专门的“搜索器”模型（Gemini 3.1 Pro Deep Think、GPT-5.5 扩展思考、Claude Opus 4.7）原生训练为能够管理这些分支。

---

## 面试问题

### Q：什么时候 ToT 会显著优于简单 CoT？

**强回答：**

当问题具有“巨大的搜索空间”并且需要“全局一致性”时，ToT 更有优势。例如在复杂的软件重构中，一条 Chain-of-Thought 可能开局良好，却在 10 步之后遇到约束冲突。使用 ToT，模型可以提出 3 种不同的重构模式，评估每种模式对代码库的影响，并在真正写代码前丢弃会导致循环依赖的模式。

### Q：面向消费者的应用中，Tree-of-Thought 的主要缺点是什么？

**强回答：**

主要缺点是**指数级成本和延迟**。探索 3 个分支、深度为 5，可能需要 15～20 次独立的 LLM 调用。在消费者应用中，这可能导致单次查询延迟 30 秒、成本 0.50 美元。标准缓解方案是“混合模型”：把 ToT 用于高风险的离线任务（例如生成黄金数据集或安全审计），再把结果蒸馏到快速的线性模型中用于实时交互。

---

## 参考资料

- Yao 等，《Tree of Thoughts: Deliberate Problem Solving with Large Language Models》（2023）
- Silver 等，《Mastering the Game of Go without Human Knowledge》（MCTS 灵感来源）

---

*下一篇：[上下文工程](05-context-engineering.md)*
