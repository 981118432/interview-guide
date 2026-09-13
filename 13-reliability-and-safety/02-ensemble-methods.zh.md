# 提升 LLM 可靠性的集成方法

集成方法是生产可靠性的关键。本章介绍通过多模型协同提升准确性、减少幻觉的模式。

## 目录

- [为什么需要集成](#why-ensembles-matter)
- [评测集成](#evaluation-ensembles)
- [生成集成](#generation-ensembles)
- [多 Agent 模式](#multi-agent-patterns)
- [集成与仲裁](#ensemble-vs-arbitration)
- [成本与准确率权衡](#cost-accuracy-tradeoffs)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## 为什么需要集成

对于高风险应用，单模型输出并不可靠：
- 模型可能产生事实幻觉。
- 推理可能有缺陷。
- 输出会随温度参数变化。
- 单评审评测存在偏差。

集成通过冗余和多样性提升可靠性。

### 集成方法分类

| 类别 | 目的 | 方法 |
|----------|---------|---------|
| 评测 | 降低评审偏差 | 评审面板、两两比较 |
| 生成 | 提升输出质量 | 自洽性、Best-of-N |
| 验证 | 减少幻觉 | 多 Agent 辩论、事实核验 |
| 综合 | 组合不同视角 | Agent 混合 |

---

## 评测集成

### LLM 评审面板（PoLL）

让多个具有多样性的模型对同一输出打分：

```python
class PanelOfJudges:
    """
    Production implementation of PoLL pattern.
    Key insight: Diversity of judges matters more than individual judge quality.
    """
    def __init__(self, judges: list, aggregation: str = "mean"):
        # Use diverse model families, not just different sizes
        # Good: [Claude, GPT-4, Gemini, Llama-70B]
        # Bad: [GPT-4, GPT-4-turbo, GPT-3.5] - same family bias
        self.judges = judges
        self.aggregation = aggregation
    
    async def evaluate(self, question: str, answer: str, rubric: str) -> dict:
        # Parallel evaluation for latency
        judgments = await asyncio.gather(*[
            judge.score(question, answer, rubric) 
            for judge in self.judges
        ])
        
        scores = [j["score"] for j in judgments]
        
        # Track inter-judge agreement for confidence
        agreement = 1 - (np.std(scores) / max(np.mean(scores), 0.01))
        
        if self.aggregation == "mean":
            final_score = np.mean(scores)
        elif self.aggregation == "median":  # More robust to outliers
            final_score = np.median(scores)
        elif self.aggregation == "trimmed_mean":  # Drop highest and lowest
            final_score = np.mean(sorted(scores)[1:-1])
        
        return {
            "score": final_score,
            "confidence": agreement,
            "individual_scores": scores,
            "needs_review": agreement < 0.7  # Flag for human review
        }
```

**适用场景：**高风险评测、创建基准，以及不能接受单评审偏差的场景。

### 带位置去偏的两两比较

模型有 60～70% 的概率偏好第一个选项，因此始终运行两种排列顺序：

```python
async def pairwise_compare_debiased(model, response_a: str, response_b: str, criteria: str) -> dict:
    """
    Critical: Models have significant positional bias.
    Always run both orderings and aggregate.
    """
    # Run both orderings in parallel
    result_ab, result_ba = await asyncio.gather(
        model.compare(first=response_a, second=response_b, criteria=criteria),
        model.compare(first=response_b, second=response_a, criteria=criteria)
    )
    
    # If A wins in both positions -> Strong signal for A
    if result_ab["winner"] == "first" and result_ba["winner"] == "second":
        return {"winner": "A", "confidence": "high"}
    
    # If B wins in both positions -> Strong signal for B
    elif result_ab["winner"] == "second" and result_ba["winner"] == "first":
        return {"winner": "B", "confidence": "high"}
    
    # Winner depends on position -> Positional bias detected
    else:
        return {
            "winner": "tie",
            "confidence": "low",
            "note": "Positional bias detected"
        }
```

---

## 生成集成

### 自洽性（多数投票）

生成多条推理路径，再对最终答案投票：

```python
class SelfConsistencyDecoder:
    """
    Key parameters:
    - k (sample count): 5-10 for most tasks, 15-20 for hard math
    - temperature: 0.5-0.8 for reasoning tasks
    
    Too low temperature = not enough diversity
    Too high temperature = too much noise
    """
    
    def __init__(self, model, k: int = 7, temperature: float = 0.7):
        self.model = model
        self.k = k
        self.temperature = temperature
    
    async def generate_with_consistency(self, prompt: str) -> dict:
        # Generate k reasoning paths in parallel
        responses = await asyncio.gather(*[
            self.model.generate(prompt, temperature=self.temperature)
            for _ in range(self.k)
        ])
        
        # Extract final answers (task-specific)
        answers = [self.extract_answer(r) for r in responses]
        
        # Majority voting
        answer_counts = Counter(answers)
        majority_answer, majority_count = answer_counts.most_common(1)[0]
        
        # Confidence = proportion of votes for winner
        confidence = majority_count / self.k
        
        # Get best reasoning path that led to majority answer
        best_reasoning = self.select_best_reasoning(
            responses, answers, majority_answer
        )
        
        return {
            "answer": majority_answer,
            "confidence": confidence,
            "num_paths": self.k,
            "reasoning": best_reasoning,
            "vote_distribution": dict(answer_counts)
        }
    
    def extract_answer(self, response: str) -> str:
        # Task-specific answer extraction
        # For math: extract the final number
        # For code: extract the function
        # Implement based on your task
        pass
```

**最适合：**数学、逻辑和答案可验证的编码任务。准确率提升约 5～15%。

### 使用奖励模型的 Best-of-N

生成 N 个候选，用奖励模型评分并返回最佳候选：

```python
class BestOfNSampler:
    """
    Key considerations:
    1. N selection: N=4-8 for interactive, N=16-64 for batch
    2. Reward model ensemble prevents reward hacking
    3. Monitor sample diversity - if too similar, BoN is wasted compute
    """
    
    def __init__(self, generator, reward_models: list, n: int = 8):
        self.generator = generator
        self.reward_models = reward_models  # Ensemble for robustness
        self.n = n
    
    async def generate_best(self, prompt: str) -> dict:
        # Generate N candidates in parallel
        candidates = await asyncio.gather(*[
            self.generator.generate(prompt, temperature=0.8)
            for _ in range(self.n)
        ])
        
        # Score with reward model ensemble
        scored_candidates = []
        for candidate in candidates:
            rm_scores = await asyncio.gather(*[
                rm.score(prompt, candidate) for rm in self.reward_models
            ])
            
            # Conservative aggregation prevents reward hacking
            # Use 25th percentile instead of mean
            conservative_score = np.percentile(rm_scores, 25)
            
            scored_candidates.append({
                "response": candidate,
                "score": conservative_score,
                "rm_agreement": 1 - np.std(rm_scores) / np.mean(rm_scores)
            })
        
        # Select best by conservative score
        best = max(scored_candidates, key=lambda x: x["score"])
        
        # Compute diversity metric
        diversity = self.compute_diversity(candidates)
        
        return {
            "response": best["response"],
            "score": best["score"],
            "n_sampled": self.n,
            "diversity_score": diversity,
            "low_diversity_warning": diversity < 0.3
        }
    
    def compute_diversity(self, candidates: list) -> float:
        # Embed candidates and compute average pairwise distance
        embeddings = [embed(c) for c in candidates]
        similarities = []
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                similarities.append(cosine_similarity(embeddings[i], embeddings[j]))
        return 1 - np.mean(similarities)  # Higher = more diverse
```

**最适合：**开放式生成和创意任务。准确率提升约 10～30%。

---

## 多 Agent 模式

### 多 Agent 辩论

多个模型迭代地互相批评：

```python
class MultiAgentDebate:
    """
    Pattern: Multiple models debate to reduce hallucinations.
    
    Most effective when:
    1. Models have different biases (diverse model families)
    2. 2-3 rounds is optimal (more = diminishing returns)
    3. Explicit "devil's advocate" prompting improves results
    """
    
    def __init__(self, debaters: list, rounds: int = 2):
        self.debaters = debaters
        self.rounds = rounds
    
    async def debate(self, question: str) -> dict:
        # Round 0: Initial positions
        positions = await asyncio.gather(*[
            debater.generate(f"Answer this question with reasoning: {question}")
            for debater in self.debaters
        ])
        
        debate_history = [{"round": 0, "positions": positions}]
        
        # Debate rounds
        for round_num in range(1, self.rounds + 1):
            new_positions = []
            
            for i, debater in enumerate(self.debaters):
                other_positions = [p for j, p in enumerate(positions) if j != i]
                
                critique_prompt = f"""
Question: {question}

Your previous answer: {positions[i]}

Other perspectives:
{self.format_positions(other_positions)}

Consider the other perspectives. If they raise valid points, update your answer.
If you still disagree, explain why with specific reasoning.
Provide your final answer.
"""
                new_position = await debater.generate(critique_prompt)
                new_positions.append(new_position)
            
            positions = new_positions
            debate_history.append({"round": round_num, "positions": positions})
        
        # Final synthesis
        final_answer = await self.synthesize(question, debate_history)
        
        return {
            "answer": final_answer,
            "rounds": self.rounds,
            "consensus_reached": self.check_consensus(positions),
            "debate_history": debate_history
        }
```

**最适合：**事实核验，以及减少复杂回答中的幻觉。

### Agent 混合（MoA）

多个模型将结果输入聚合器的分层架构：

```
┌─────────────────────────────────────────────────────────────────┐
│                    MIXTURE OF AGENTS (MoA)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Layer 1 (Proposers):                                           │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐            │
│  │ Claude  │  │  GPT-4  │  │ Gemini  │  │ Llama   │            │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘            │
│       │            │            │            │                   │
│       └────────────┴─────┬──────┴────────────┘                  │
│                          │                                       │
│  Layer 2 (Aggregator):   ▼                                      │
│  ┌──────────────────────────────────────────────────┐           │
│  │  "Given these perspectives: [R1, R2, R3, R4]    │           │
│  │   Synthesize the best answer..."                │           │
│  └────────────────────────┬─────────────────────────┘           │
│                           │                                      │
│                           ▼                                      │
│                    [Final Output]                                │
└─────────────────────────────────────────────────────────────────┘
```

```python
class MixtureOfAgents:
    def __init__(self, proposers: list, aggregator):
        self.proposers = proposers
        self.aggregator = aggregator
    
    async def generate(self, prompt: str) -> str:
        # Layer 1: Get diverse proposals
        proposals = await asyncio.gather(*[
            proposer.generate(prompt) for proposer in self.proposers
        ])
        
        # Layer 2: Aggregate
        aggregation_prompt = f"""
Given the following question and multiple expert responses, 
synthesize the best possible answer.

Question: {prompt}

Expert responses:
{self.format_proposals(proposals)}

Synthesize the best answer, combining the strongest elements from each response.
"""
        
        final_answer = await self.aggregator.generate(aggregation_prompt)
        return final_answer
```

**最适合：**复杂综合、报告生成和跨领域问题。

---

## 集成与仲裁

### 概念区别

| 方面 | 集成学习 | 模型仲裁 |
|--------|------------------|-------------------|
| **目标** | 组合全部输出 | 选择单个最佳输出 |
| **机制** | 聚合（投票、平均） | 选择（评分、排序） |
| **关系** | 协作 | 竞争 |
| **最终输出** | 所有模型的综合结果 | 单个胜者的输出 |
| **适用场景** | 需要稳健性、降低方差 | 需要最佳质量 |

### 决策框架

```
Is there a single "correct" answer format?
├── Yes (classification, math)
│   └── Use Ensemble (voting/averaging)
│
└── No (creative writing, open QA)
    └── Use Arbitration (best-of-N)
        └── Do you have reliable scoring?
            ├── Yes → Reward model selection
            └── No → LLM-as-judge or human
```

---

## 成本与准确率权衡

### 集成成本矩阵

| 方法 | 成本倍数 | 延迟 | 准确率提升 | 适用场景 |
|--------|-----------------|---------|---------------|-------------|
| 单模型 | 1x | 1x | 基线 | 低风险、高流量 |
| 自洽性 k=3 | 3x | 1x（并行） | +5～8% | 推理、延迟敏感 |
| 自洽性 k=10 | 10x | 1x（并行） | +10～15% | 数学、准确性关键 |
| Best-of-N（N=8） | 8x + 评分 | 1x（并行） | +15～25% | 创意生成 |
| 评审面板（3 个） | 3x 评测 | 1x（并行） | 降低偏差 | 评测任务 |
| 多 Agent 辩论 | 6x | 3x | 幻觉下降 | 事实关键 |
| Agent 混合 | 5～8x | 2x | 综合更好 | 复杂报告 |

### 何时不要使用集成

| 情况 | 不使用原因 | 替代方案 |
|-----------|---------|-------------|
| 简单事实查询 | 没有多样性收益 | 单次 RAG 调用 |
| 要求延迟 <500ms | 集成增加延迟 | 单模型 + 缓存 |
| 成本是首要约束 | 集成会放大成本 | 模型蒸馏 |
| 模型高度相关 | 没有多样性就没有收益 | 先获得多样模型 |

---

## 面试问题

### Q：什么时候使用自洽性，什么时候使用 Best-of-N？

**强回答：**

“它们服务于不同目的：

**自洽性**适用于可以提取并验证答案的任务：
- 数学题：提取最终数字并多数投票。
- 分类：对标签投票。
- 短问答：对答案投票。

关键是答案可以直接比较是否相等。温度 0.5～0.8 能在保持连贯的同时提供多样性；多数任务我使用 k=5～10。

**Best-of-N**适用于没有唯一正确答案的开放式生成：
- 创意写作。
- 解释。
- 可以有多种写法的代码。

此时需要奖励模型或评审为候选打分，不能简单比较相等性。N 通常取 8～16。难点是避免奖励劫持，因此使用奖励模型集成和保守聚合。

我不会在创意写作中使用自洽性（没有可提取答案），也不会在数学题中使用 Best-of-N（直接投票更简单）。”

### Q：如何防止 Best-of-N 中的奖励劫持？

**强回答：**

“奖励劫持是指模型利用奖励模型的弱点，而没有真正提升质量。

**我的缓解措施：**

1. **奖励模型集成**：使用 3 个以上不同的奖励模型。能攻破一个 RM 的样本不太可能同时攻破全部。

2. **保守聚合**：不使用平均分，而使用第 25 百分位或最小值，选择在所有 RM 上都表现好的样本，而非只在一个 RM 上得分高的样本。

3. **监控多样性**：跟踪样本多样性。多样性过低可能意味着模型正在利用狭窄的奖励漏洞，此时调整温度或使用不同 Prompt。

4. **人工校准**：定期验证 RM 选出的样本是否真的符合人类偏好。

5. **多维度**：按质量、安全和相关性等多个标准评分，要求每项都良好，而不是只看综合分。

关键洞察是任何单一奖励信号都可能被钻空子，而集成会大幅提高攻击难度。”

---

## 参考资料

- Verga et al. "Replacing Judges with Juries: Evaluating LLM Generations with a Panel of Diverse Models" (2024)
- Wang et al. "Self-Consistency Improves Chain of Thought Reasoning" (2023)
- Du et al. "Improving Factuality and Reasoning in Language Models through Multiagent Debate" (2023)

---

*Next: [Reliability Patterns Extended](03-reliability-patterns.md)*
