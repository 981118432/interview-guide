# 上下文工程

上下文工程是一门科学：把最有价值的 Token 填入 LLM 有限的“工作记忆”。随着上下文窗口已经达到 100 万 Token 以上（Claude Sonnet 4.6、Gemini 3.1 Pro、GPT-5.5），并且模型获得了扩展思考能力，重点已经从“把数据塞进去”转向“对相关性排序”和“管理计算预算”。

## 目录

- [长上下文范式（100 万+ Token）](#long-context)
- [Agent 上下文工程](#agentic-context-engineering)
- [扩展思考与预算 Token](#extended-thinking)
- [中间丢失](#lost-in-the-middle)
- [上下文预算与 Token 感知](#budgeting)
- [Prompt 缓存经济学](#prompt-caching)
- [上下文压缩（RAD-L）](#compression)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## 长上下文范式（100 万+ Token）

Gemini 3.1 Pro（1M）、Claude Sonnet 4.6（1M）、Claude Opus 4.7（1M）和 GPT-5.5（1M）等模型拥有巨大的上下文窗口。

**启示**：“上下文就是新的 RAG。”
对于少于 100,000 篇文档的数据集，把整个数据集放进上下文窗口，往往比使用外部向量数据库更准确、更快。这称为**“上下文内 RAG”**。

---

## Agent 上下文工程

Prompt Engineering 写出一条好的指令。**上下文工程**则整理 Agent 循环中**每一次推理轮次**模型能看到的完整 Token 集合：系统 Prompt、工具、检索数据、之前的工具结果以及持续增长的消息历史。这个区别很重要，因为 Agent 会一轮一轮地积累上下文，所以整理问题是持续性的，而不是一次性的。这也是 Anthropic、OpenAI 和 Google 当前构建 Agent Harness 所围绕的框架。

### 上下文腐化：为什么上下文是有限资源

拥有 100 万 Token 窗口，并不意味着应该把它填满。模型会出现**上下文腐化**：随着 Token 数增长，准确率下降，因为注意力需要处理 n 的平方级两两关系，而训练数据又偏向较短序列。应把上下文当成具有边际收益递减的预算，而不是免费空间。任务是保留仍足以让模型正确行动的**最小高信号 Token 集合**。

### 五项核心技术

| 技术 | 作用 | 使用时机 |
|------|------|----------|
| **压缩（Compaction）** | 总结消息历史，用压缩摘要和最近的少量产物重新初始化循环 | 长时间来回对话即将达到窗口上限时 |
| **即时加载** | 在上下文中保留轻量标识符（文件路径、URL、行 ID），通过工具按需加载完整内容 | 无法全部放入上下文的大型语料库或数据库、探索性任务 |
| **结构化记笔记** | Agent 把进度笔记写入窗口外的文件或记忆存储，稍后再读回来 | 跨越数十次工具调用的长期任务 |
| **子 Agent 隔离** | 为子任务启动一个拥有干净窗口的专门子 Agent，只返回 1k～2k Token 的摘要 | 并行研究、深度搜索，以及任何会让主窗口充满中间细节的任务 |
| **系统 Prompt 校准** | 以“金发姑娘区间”为目标：足够具体以保证可靠，又足够通用以避免脆弱；使用清晰的 XML 或 Markdown 分区 | 始终作为其他四项技术的基础 |

### 压缩

当历史变得很长时，把它交给模型总结，保留承重细节（架构决策、未解决的 Bug、关键约束），丢弃重复的工具输出。Claude Code 就使用这种模式：它带着压缩摘要和最近访问的文件继续工作。首先要针对召回率调优（保留所有重要内容），然后再提高精确率（删除冗余）。

### 即时加载

Agent 不预先加载每份文档，而是持有引用，并且只在某一步需要时获取内容。这类似人类根据文件树工作：打开需要的文件，而不是把整个仓库都打开。它保持较小的窗口，也让 Agent 能通过探索发现结构。代价是延迟，因此混合方式（预加载明显需要的内容，其余按需获取）通常最好。

### 结构化记笔记（Agent 记忆）

Agent 把笔记持久化到上下文窗口之外，需要时再取回来。这让 Agent 能够在远超自身窗口长度的任务中保持连贯。关于存储基础设施（文件系统、向量、图），参见[Agent 记忆与状态](../07-agentic-systems/05-agent-memory-and-state.md)和[记忆架构](../08-memory-and-state/01-memory-architectures.md)。

### 子 Agent 隔离

协调器把专门的子任务委托给拥有独立干净窗口的子 Agent，子 Agent 返回压缩摘要。详细的搜索或分析上下文不会污染协调器窗口。这是多 Agent 系统有效的上下文管理原因，与并行能力带来的收益无关。参见[多 Agent 编排](../07-agentic-systems/04-multi-agent-orchestration.md)。

---

## 扩展思考与预算 Token

现在有一些前沿模型能够在生成响应之前提供**可控制的内部推理**：

### Claude（Sonnet 4.6、Opus 4.7）：扩展思考

```python
response = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000  # max internal reasoning tokens
    },
    messages=[{"role": "user", "content": "Refactor this codebase to be async..."}]
)

# Response has two blocks:
# 1. thinking block (visible for debug, not shown to user)
# 2. text block (the actual answer)
for block in response.content:
    if block.type == "thinking":
        print("[THINKING]", block.thinking)
    elif block.type == "text":
        print("[ANSWER]", block.text)
```

**关键参数：**
- `budget_tokens`：1,024 → 100,000。越高 = 准确度越好，成本越高。
- 思考 Token 按标准费率计费。10K 思考预算 = 每次请求额外 $0.15。
- 支持流式传输——思考块会在文本块之前流出。

### o3（OpenAI）——推理力度

```python
response = client.chat.completions.create(
    model="o3",
    reasoning_effort="medium",  # "low" | "medium" | "high"
    messages=[{"role": "user", "content": "Prove P=NP or disprove it."}]
)
# Reasoning tokens are invisible — o3 never exposes its internal chain
```

**不同力度与成本（约数）：**
| 力度 | 速度 | 成本倍数 | 最适合 |
|------|------|----------|--------|
| low | 快 | 1 倍 | 简单逻辑、快速查询 |
| medium | 中等 | 3～5 倍 | 编码、分析 |
| high | 慢 | 8～20 倍 | 博士级问题、ARC-AGI |

### 什么时候启用思考/推理

| 条件 | 建议 |
|------|------|
| 复杂的多步代码重构 | ✅ 启用（预算：8K～20K） |
| 简单问答/抽取 | ❌ 禁用——会增加成本和延迟 |
| STEM/数学问题 | ✅ 启用（o3-mini medium） |
| 高流量聊天机器人 | ❌ 禁用——使用标准模式 |
| 安全关键决策 | ✅ 启用——额外推理可以捕捉边界情况 |

**生产模式**：使用复杂度分类器控制 Extended Thinking。如果查询复杂度得分 < 0.5，则完全跳过思考模式（在重推理工作负载上节省 60～80%）。

```python
def smart_generate(query: str) -> str:
    complexity = classifier.predict(query)  # 0-1 score

    if complexity > 0.7:
        # Enable Extended Thinking for hard problems
        return claude_with_thinking(query, budget_tokens=8000)
    else:
        # Standard fast mode for simple tasks
        return claude_standard(query)
```

---

## 中间丢失

2023 年，模型对 Prompt 中间信息的准确率会下降。
**现状**：前沿模型（Claude Sonnet 4.6、Claude Opus 4.7、Gemini 3.1 Pro、GPT-5.5）表现显著更好，但**注意力梯度**仍然存在。
- **最佳实践**：把关键指令和黄金标准示例放在 Prompt 的**最开始**和**最末尾**。中间放原始数据/知识块。
- **使用块排序**：重新排序检索到的文档，让最相关的内容位于最前和最后。

---

## 上下文预算与 Token 感知

每个 Token 都要花钱，也会增加 TTFT（Time to First Token，首 Token 时间）。

| 组件 | 预算（Token） | 原因 |
|------|---------------|------|
| **系统 Prompt** | 500～1,000 | 核心逻辑和人格。 |
| **历史** | 2,000～5,000 | 对话“状态”。 |
| **数据/搜索** | 10k～1M | 取决于任务深度。 |
| **输出预留** | 1,000～4,000 | 必须为推理预留空间。 |

---

## Prompt 缓存经济学

几乎所有主要供应商（OpenAI、DeepSeek、Anthropic、Google）都支持**前缀缓存**。

- **交叉点**：如果一个 100k Token 的上下文（例如代码库）被复用超过 2 次，缓存折扣实际上会让它比 RAG 更便宜。
- **缓存命中**：$0.05/1M Token。
- **缓存未命中**：$5.00/1M Token。

**架构选择**：设计系统时保持“系统 Prompt + 基础知识”静态，以维持 100% 的缓存命中率。

---

## 上下文压缩（RAD-L）

对于极长上下文（10M+），可以使用**推理感知删除（RAD-L）**。
- **方式**：一个很小的辅助模型（0.1B）扫描文本，在 Prompt 发送给巨型前沿模型*之前*删除“填充”词、常见语言模式和无关段落。
- **收益**：Prompt 大小减少 20～50%，准确率下降低于 1%。

---

## 面试问题

### Q：什么时候选择长上下文而不是 RAG？

**强回答：**

当高保真检索和跨文档推理很关键时，我会选择长上下文。RAG 存在“检索缺口”——如果向量搜索漏掉相关块，模型就永远看不到它。长上下文（最高 200 万 Token）提供 100% 召回。具体来说，我会把它用于代码库分析、法律文档审查和多文件财务审计。对于动态 Web 规模数据，或超出任何上下文窗口的十亿文档数据集，我会坚持使用 RAG。

### Q：如何处理百万 Token Prompt 带来的高 TTFT？

**强回答：**

主要方案是**上下文缓存**。通过在 GPU 集群上缓存重型文档，模型就不必在每一轮重新“读取”（Prefill）完整的 100 万 Token。缓存 Prompt 的 TTFT 几乎与 1k Token Prompt 相同。此外，对于未缓存请求，我会使用**流式 Prefill**：模型在处理超大上下文后半部分的同时，先生成初始摘要或“思考”。

### Q：Agent 处理短任务很好，但长时间运行时表现下降。如何修复？

**强回答：**

这是**上下文腐化**：窗口被过时的工具输出填满，模型失去主线。我会应用 Agent 上下文工程。首先是**压缩**：达到阈值后总结历史，从摘要和最近产物继续。其次是**即时加载**：保留文件路径和 ID，而不是完整内容，需要时再获取。第三是**结构化记笔记**：让 Agent 把进度写入可以重新读取的临时文件，从而保持工作记忆很小。对于会产生大量中间细节的子任务（深度搜索、多文件分析），我会使用**子 Agent 隔离**，让细节以短摘要返回，而不是淹没主窗口。目标是每一轮保留最小的高信号 Token 集合，而不是最大的集合。

---

## 参考资料

- Liu 等，《Lost in the Middle》（2023/2024 更新）
- [Anthropic，《Effective context engineering for AI agents》（2025）](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Anthropic，《Effective harnesses for long-running agents》（2026）](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- Anthropic，《Extended Thinking: Technical Guide》：https://docs.anthropic.com/
- OpenAI，《o3 and o3-mini System Card》（2025）

---

*下一篇：[结构化生成](06-structured-generation.md)*
