# 能力评估

本章介绍如何针对你的具体用例评估和比较模型能力。通用基准很少能说明全部情况；本指南帮助你开展有意义的评估。

## 目录

- [为什么基准还不够](#为什么基准还不够)
- [评估维度](#评估维度)
- [构建自定义评估](#构建自定义评估)
- [常见评估陷阱](#常见评估陷阱)
- [实用评估流程](#实用评估流程)
- [内部基于 Elo 的评估](#内部基于-elo-的评估)
- [推理校准与效率](#推理校准与效率)
- [模型 A/B 测试](#模型-ab-测试)
- [面试问题](#面试问题)
- [参考资料](#参考资料)

---

## 为什么基准还不够

### 基准问题

公开基准（MMLU、HumanEval、GSM8K）存在局限：

| 问题 | 影响 |
|-------|--------|
| 训练数据污染 | 模型可能已经见过测试题 |
| 任务不匹配 | 基准可能无法反映你的用例 |
| 汇总分数掩盖方差 | 模型 A 总体胜过 B，却可能在你的领域失败 |
| 刷榜 | 模型可能针对基准优化，而不是针对真实任务优化 |
| 过时 | 基准落后于模型能力 |

### 基准能告诉你什么

```
基准结果告诉你：“模型 X 在 MMLU 上得分 88%”

你真正需要知道的是：“模型 X 能否正确回答我的客户
关于我们产品文档的问题？”
```

**经验法则：**用基准进行初步筛选，然后开展自己的评估。

---

## 评估维度

### 维度 1：任务表现

| 任务类型 | 评估方法 | 关键指标 |
|-----------|---------------------|------------|
| **自主编码** | CWE/SWE-bench（Verified） | 自主解决的问题百分比 |
| **长周期规划** | Agentic Loop 测试 | 10+ 步计划的成功率 |
| **推理深度** | Thinking 模式分析 | CoT 步骤间的逻辑一致性 |
| **长上下文 RAG** | 大海捞针（2M+） | 大规模下的召回效率 |
| **原生多模态** | 交错视觉/语音/文本 | 跨模态同步准确率 |

### 维度 2：Agent 能力

模型使用工具和遵循多步指令的能力如何？

```python
def evaluate_agentic_flow(agent, task_environment):
    """
    衡量“自主 Agent”任务的成功情况：
    1. 计划生成
    2. 工具选择准确率
    3. 错误恢复
    4. 反馈循环利用
    """
    results = []
    for scenario in task_environment.scenarios:
        traj = agent.run(scenario.goal)
        results.append({
            "success": traj.reached_goal,
            "steps": len(traj.steps),
            "tool_errors": traj.count_invalid_tool_calls()
        })
    return aggregate(results)
```

### 维度 3：推理可靠性

“Thinking”模式相比标准生成，是否提高了输出准确率？

| 模式 | 准确率（数学） | 准确率（代码） | 平均延迟 | Token / 输出 |
|------|-----------------|-----------------|-------------|-----------------|
| **标准** | 72% | 68% | 1.2 秒 | 400 |
| **Thinking** | 94% | 89% | 12.5 秒 | 2400 |
| **混合** | 可变 | 可变 | 用户定义 | 可配置 |

### 推理校准

**“过度思考”问题：**
模型经常为一个只需 10 个 token 就能回答的问题（例如“2+2 等于多少？”）花费 2000+ 个“思考”token。

**高级细节：**
按照**逻辑效率**评估模型：`准确率 /（推理 Token）`。
生产系统使用**模型仲裁**：小模型（Gemini 3.1 Flash、Claude Haiku 4.5、GPT-5.5-mini）检测查询是否需要“Thinking”模式。这样可避免简单查询付出 10 倍的延迟和成本代价。

---

## 内部基于 Elo 的评估

**超越静态评分标准。**
评分量表（1–5 分）容易出现“评审疲劳”和“分数漂移”。现代系统会为内部黄金集使用**成对 Elo**。

**工作流：**
1. **盲测并排比较：**模型 A 与模型 B 为同一查询生成答案。
2. **评审者：**“Ultra”模型（Claude Opus 4.7、GPT-5.5 reasoning 或人工）选择胜者。
3. **Elo 更新：**更新内部排行榜。

```python
def update_elo(winner_elo, loser_elo, k=32):
    expected_winner = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
    new_winner_elo = winner_elo + k * (1 - expected_winner)
    new_loser_elo = loser_elo + k * (0 - (1 - expected_winner))
    return new_winner_elo, new_loser_elo
```

**为什么它更好：**它提供了**相对**排名，对评审者个性或模型版本变化更稳健。

### 维度 4：上下文召回

有了 2M+ 上下文窗口后，简单的“大海捞针”已不够。现在要衡量跨整个窗口的**上下文推理**。

| 指标 | 测量 | 目标 |
|--------|-------------|--------|
| **窗口召回** | 在窗口 90% 深度处的事实召回 | > 98% |
| **跨文档推理** | 连接文档 A（位置 10k）与文档 B（位置 1M）的逻辑 | > 90% |
| **上下文噪声抵抗力** | 窗口 90% 是无关“填充物”时的准确率 | > 95% |

---

## 构建自定义评估

### 第 1 步：定义评估标准

```python
evaluation_criteria = {
    "correctness": {
        "weight": 0.4,
        "description": "答案在事实层面是否正确？",
        "scale": [1, 2, 3, 4, 5],
        "rubric": {
            5: "完全正确，没有错误",
            4: "大部分正确，有少量问题",
            3: "部分正确，有一些错误",
            2: "大部分错误",
            1: "完全错误或毫无意义"
        }
    },
    "relevance": {
        "weight": 0.3,
        "description": "答案是否回应了问题？",
        "scale": [1, 2, 3, 4, 5]
    },
    "completeness": {
        "weight": 0.2,
        "description": "问题的所有部分是否都被回应？",
        "scale": [1, 2, 3, 4, 5]
    },
    "conciseness": {
        "weight": 0.1,
        "description": "答案是否恰当地简洁？",
        "scale": [1, 2, 3, 4, 5]
    }
}
```

### 第 2 步：创建测试集

```python
test_set = [
    {
        "id": "q001",
        "query": "取消订阅后的退款政策是什么？",
        "context": "[相关文档]",
        "ground_truth": "30 天内全额退款，之后按比例退款",
        "difficulty": "简单",
        "category": "政策"
    },
    {
        "id": "q002",
        "query": "如何将 API 与 Python 异步应用程序集成？",
        "context": "[API 文档]",
        "ground_truth": "[预期代码模式]",
        "difficulty": "中等",
        "category": "技术"
    },
    # ... 50–100+ 个测试用例
]
```

**测试集指南：**
- 覆盖所有主要用例。
- 包含简单、中等、困难的示例。
- 在类别之间保持平衡。
- 包含边界案例。
- 具有清晰的标准答案。

### 第 3 步：实现评估

```python
class ModelEvaluator:
    def __init__(self, models: list[str], test_set: list[dict]):
        self.models = models
        self.test_set = test_set
        self.results = {}

    def evaluate_all(self):
        for model in self.models:
            self.results[model] = self.evaluate_model(model)
        return self.results

    def evaluate_model(self, model: str) -> dict:
        scores = []
        latencies = []

        for case in self.test_set:
            start = time.time()
            response = self.generate(model, case)
            latency = time.time() - start
            latencies.append(latency)

            # 使用 LLM 评审者或人工评分
            score = self.score_response(case, response)
            scores.append(score)

        return {
            "mean_score": mean(scores),
            "score_by_category": self.group_by_category(scores),
            "p50_latency": percentile(latencies, 50),
            "p99_latency": percentile(latencies, 99)
        }

    def score_response(self, case: dict, response: str) -> float:
        # 选项 1：LLM 作为评审者
        return self.llm_judge(case, response)

        # 选项 2：精确匹配
        # return exact_match(response, case["ground_truth"])

        # 选项 3：语义相似度
        # return cosine_sim(embed(response), embed(case["ground_truth"]))
```

### 第 4 步：LLM-as-Judge

```python
def llm_judge(case: dict, response: str) -> dict:
    prompt = f"""评估对一条客户查询的这个回答。

查询：{case['query']}
预期答案：{case['ground_truth']}
模型回答：{response}

按以下标准对回答评分（1–5 分）：
1. 正确性：它在事实层面准确吗？
2. 相关性：它回答了问题吗？
3. 完整性：它覆盖所有方面了吗？
4. 简洁性：它是否恰当地简短？

输出 JSON：
{{"correctness": X, "relevance": X, "completeness": X, "conciseness": X, "reasoning": "..."}}
"""

    result = judge_model.generate(prompt)
    return parse_json(result)
```

---

## 常见评估陷阱

### 陷阱 1：测试集太小

**问题：**20 个测试用例不足以进行可靠比较。

**解决方案：**目标是 100+ 个案例，并按难度和类别分层。

### 陷阱 2：标准答案模糊

**问题：**“合理”的答案被标记为错误。

```
查询：“澳大利亚的首都是什么？”
标准答案：“堪培拉”
模型答案：“澳大利亚的首都是堪培拉。”
精确匹配：失败（但显然是正确的）
```

**解决方案：**使用语义匹配或 LLM 评审者，而不是精确匹配。

### 陷阱 3：评估集泄漏

**问题：**开发和评估使用相同案例。

**解决方案：**保留一个永远不用于提示词调优的测试集。

### 陷阱 4：忽略方差

**问题：**每个测试只运行一次，忽略了模型随机性。

**解决方案：**在 temperature > 0 时多次运行，并报告置信区间。

### 陷阱 5：对成本视而不见

**问题：**最佳模型贵 10 倍。

**解决方案：**始终报告经质量调整的成本。

```python
def quality_adjusted_cost(model_results):
    return {
        model: {
            "quality": results["mean_score"],
            "cost_per_1k": results["cost_per_1k_queries"],
            "quality_per_dollar": results["mean_score"] / results["cost_per_1k"]
        }
        for model, results in model_results.items()
    }
```

---

## 实用评估流程

### 第 1 周：设置与初步筛选

```
第 1–2 天：定义评估标准并创建测试集
第 3–4 天：基准测试 4–6 个候选模型
第 5 天：分析结果，筛选到前 2–3 个
```

### 第 2 周：深入评估

```
第 1–2 天：为头部候选扩展测试集
第 3 天：测试边界案例和鲁棒性
第 4 天：测量延迟和吞吐
第 5 天：计算总拥有成本
```

### 第 3 周：生产验证

```
第 1–2 天：影子模式部署
第 3–4 天：如果流量允许，进行 A/B 测试
第 5 天：最终决策和文档化
```

### 决策模板

```markdown
## 模型评估报告

### 已评估的候选模型
- 模型 A：GPT-4o
- 模型 B：Claude 3.5 Sonnet
- 模型 C：Llama 3.1 70B

### 评估结果

| 指标 | 模型 A | 模型 B | 模型 C |
|--------|---------|---------|---------|
| 总体分数 | 4.2/5 | 4.3/5 | 3.9/5 |
| 类别 1 | ... | ... | ... |
| P50 延迟 | 450ms | 520ms | 180ms |
| 每 1K 次查询成本 | $0.85 | $1.10 | $0.25 |

### 建议
将模型 B（Claude 3.5 Sonnet）用于质量关键路径。
将模型 C（Llama 3.1 70B）用于高流量、成本敏感路径。

### 理由
[详细推理]
```

---

## 模型 A/B 测试

### 什么时候进行 A/B 测试

- 高流量（每天 1000+ 次查询）。
- 有清晰的成功指标。
- 可接受质量差异的风险。
- 需要生产验证。

### A/B 测试设计

```python
class ModelABTest:
    def __init__(self, model_a: str, model_b: str, traffic_split: float = 0.5):
        self.model_a = model_a
        self.model_b = model_b
        self.traffic_split = traffic_split
        self.results = {"a": [], "b": []}

    def route_request(self, request_id: str) -> str:
        # 使用确定性路由保证一致性
        hash_val = hash(request_id) % 100
        if hash_val < self.traffic_split * 100:
            return self.model_a
        return self.model_b

    def record_outcome(self, request_id: str, metrics: dict):
        model = self.route_request(request_id)
        bucket = "a" if model == self.model_a else "b"
        self.results[bucket].append(metrics)

    def analyze(self):
        return {
            "model_a": {
                "name": self.model_a,
                "mean_score": mean([r["score"] for r in self.results["a"]]),
                "sample_size": len(self.results["a"])
            },
            "model_b": {
                "name": self.model_b,
                "mean_score": mean([r["score"] for r in self.results["b"]]),
                "sample_size": len(self.results["b"])
            },
            "p_value": self.calculate_significance()
        }
```

### 要跟踪的指标

| 指标类型 | 示例 |
|-------------|----------|
| 质量 | 用户评分、专家评审、LLM 评审者 |
| 参与度 | 点击率、页面停留时间、追问查询 |
| 业务 | 转化、支持升级、解决率 |
| 运营 | 延迟、错误、成本 |

---

## 面试问题

### Q：如何为客服聊天机器人评估模型？

**强回答：**
我会按层次组织评估：

**1. 离线评估（80% 的工作量）：**
- 从真实支持工单创建测试集（200+ 案例）。
- 覆盖所有类别：计费、技术、退货、通用。
- 包含简单、中等、困难的难度。
- 测量：准确性、帮助性、安全性。

**2. 评估方法：**
- 对主观指标使用 LLM-as-Judge。
- 对样本进行人工审核（20%）。
- 跟踪指令遵循（格式、长度）。

**3. 指标：**
```python
metrics = {
    "resolution_accuracy": "回答是否解决问题？",
    "safety": "没有有害/错误的建议？",
    "tone": "专业且有同理心？",
    "escalation_appropriate": "知道何时需要人工介入？"
}
```

**4. 生产验证：**
- 影子模式：运行新模型，比较输出。
- A/B 测试：将 10% 流量给新模型。
- 监控：CSAT、升级率、解决时间。

### Q：用 MMLU 为你的用例比较模型有什么问题？

**强回答：**
MMLU 对具体用例有几个问题：

**1. 领域不匹配：**MMLU 测试学术知识。我的客服机器人需要产品知识。

**2. 格式不匹配：**MMLU 是多项选择。我的用例是自由形式生成。

**3. 污染：**模型可能已经在 MMLU 问题上训练过。

**4. 聚合掩盖方差：**模型 A 可能在 MMLU 上胜过 B，却在我关心的特定类别上失败。

**5. 没有上下文测试：**MMLU 不测试 RAG 或长上下文能力。

**更好的方法：**
- 使用 MMLU 做初步筛选（节省时间）。
- 为最终决策构建自定义评估。
- 在实际用例数据上测试。
- 包含运营指标（延迟、成本）。

---

## 参考资料

- Zheng 等，《Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena》（2023）
- LMSYS Chatbot Arena: https://chat.lmsys.org/
- HELM: https://crfm.stanford.edu/helm/
- LMSys Evaluation: https://github.com/lm-sys/FastChat/tree/main/fastchat/llm_judge
- OpenAI Evals: https://github.com/openai/evals

---

*上一篇：[模型分类](01-model-taxonomy.md) | 下一篇：[定价与成本](03-pricing-and-costs.md)*
