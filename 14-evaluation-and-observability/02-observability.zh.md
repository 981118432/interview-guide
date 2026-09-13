# LLM 可观测性

本页与英文原文逐段对应，保留标题层级、列表、表格、代码、公式、链接和面试问答。

LLM 系统的可观测性需要针对 AI 应用的独特特征，重新适配日志、指标和追踪这三大支柱。

## 目录

- [LLM 可观测性为何不同](#why-llm-observability-is-different)
- [三大支柱](#the-three-pillars)
- [关键指标](#key-metrics)
- [追踪 LLM 流水线](#tracing-llm-pipelines)
- [质量监控](#quality-monitoring)
- [成本跟踪](#cost-tracking)
- [告警策略](#alerting-strategy)
- [可观测性工具](#observability-tools)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## LLM 可观测性为何不同

传统可观测性关注：
- 请求/响应模式。
- 延迟和吞吐量。
- 错误率。
- 资源利用率。

LLM 系统还增加了：
- **质量是一等指标**：一个快速且可用、却持续产生糟糕输出的系统仍然是失败的。
- **非确定性**：相同输入可能产生不同输出。
- **Token 经济学**：成本会以复杂方式随使用量增长。
- **多组件流水线**：RAG 包含检索、重排序和生成步骤。
- **主观正确性**：通常没有可直接比较的事实标准。

---

## 三大支柱

### 日志

```python
class LLMLogger:
    def log_request(
        self,
        request_id: str,
        model: str,
        messages: list[dict],
        parameters: dict
    ):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "type": "llm_request",
            "model": model,
            "parameters": parameters,
            "input_tokens": self.count_tokens(messages),
            # Hash for privacy, full content in secure store
            "content_hash": self.hash_content(messages)
        }
        self.logger.info(json.dumps(log_entry))
    
    def log_response(
        self,
        request_id: str,
        response: str,
        latency_ms: float,
        tokens: dict
    ):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "type": "llm_response",
            "latency_ms": latency_ms,
            "input_tokens": tokens["input"],
            "output_tokens": tokens["output"],
            "ttft_ms": tokens.get("ttft_ms"),
            "content_hash": self.hash_content(response)
        }
        self.logger.info(json.dumps(log_entry))
```

**需要记录的内容：**
- 用于关联的请求 ID。
- 模型和参数。
- Token 数量。
- 延迟（TTFT 和总延迟）。
- 内容（涉及隐私时先做哈希）。

### 指标

```python
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
llm_requests_total = Counter(
    "llm_requests_total",
    "Total LLM requests",
    ["model", "status"]
)

llm_latency_seconds = Histogram(
    "llm_latency_seconds",
    "LLM request latency",
    ["model"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

llm_ttft_seconds = Histogram(
    "llm_ttft_seconds",
    "Time to first token",
    ["model"],
    buckets=[0.05, 0.1, 0.2, 0.5, 1.0, 2.0]
)

# Token metrics
tokens_used_total = Counter(
    "tokens_used_total",
    "Total tokens consumed",
    ["model", "direction"]  # direction: input/output
)

# Cost metrics
llm_cost_dollars = Counter(
    "llm_cost_dollars",
    "LLM cost in dollars",
    ["model"]
)

# Quality metrics (sampled)
quality_score = Gauge(
    "llm_quality_score",
    "Sampled quality score",
    ["model", "task_type"]
)
```

### Trace

对 RAG 流水线进行端到端追踪：

```python
from opentelemetry import trace

tracer = trace.get_tracer("rag_pipeline")

async def rag_query(query: str) -> str:
    with tracer.start_as_current_span("rag_query") as span:
        span.set_attribute("query", query)
        
        # Embedding step
        with tracer.start_as_current_span("embed_query") as embed_span:
            query_embedding = await embed(query)
            embed_span.set_attribute("embedding_dim", len(query_embedding))
        
        # Retrieval step
        with tracer.start_as_current_span("vector_search") as search_span:
            results = await vector_db.search(query_embedding, top_k=10)
            search_span.set_attribute("results_count", len(results))
            search_span.set_attribute("top_score", results[0].score if results else 0)
        
        # Reranking step
        with tracer.start_as_current_span("rerank") as rerank_span:
            reranked = await reranker.rerank(query, results)
            rerank_span.set_attribute("reranked_count", len(reranked))
        
        # Generation step
        with tracer.start_as_current_span("generate") as gen_span:
            response = await llm.generate(query, context=reranked[:5])
            gen_span.set_attribute("model", llm.model)
            gen_span.set_attribute("output_tokens", count_tokens(response))
        
        return response
```

---

## 关键指标

### 运维指标

| 指标 | 说明 | 典型告警阈值 |
|--------|-------------|------------------------|
| 请求率 | 每秒请求数 | 异常检测 |
| 错误率 | 失败请求数 / 总请求数 | > 5% |
| 延迟 p50 | 响应时间中位数 | > 2s |
| 延迟 p95 | 第 95 百分位 | > 5s |
| 延迟 p99 | 第 99 百分位 | > 10s |
| TTFT | 首 Token 时间 | > 1s |
| Token 吞吐 | 每秒 Token 数 | < 基线 |

### 质量指标

| 指标 | 说明 | 收集方式 |
|--------|-------------|-------------------|
| 质量分数 | LLM 评审评分 | 抽样（1～5%） |
| 忠实度 | RAG 回答是否有上下文依据 | 抽样 |
| 相关性 | 回答是否回应问题 | 抽样 |
| 用户满意度 | 点赞/点踩、评分 | 用户反馈 |
| 任务完成度 | 用户是否达成目标？ | 隐式信号 |

### 成本指标

| 指标 | 说明 | 粒度 |
|--------|-------------|-------------|
| 单请求成本 | 平均成本 | 按模型 |
| 每日成本 | 每日总支出 | 总体 + 按模型 |
| 单次用户动作成本 | 完成用户目标的成本 | 按任务类型 |
| Token 效率 | 每个 Token 交付的价值 | 按用例 |

---

## 质量监控

### 采样策略

```python
class QualitySampler:
    def __init__(self, sample_rate: float = 0.05):
        self.sample_rate = sample_rate
        self.judge = LLMJudge()
    
    async def maybe_evaluate(
        self,
        request_id: str,
        query: str,
        context: list[str],
        response: str
    ):
        # Sample randomly
        if random.random() > self.sample_rate:
            return
        
        # Evaluate quality
        scores = await self.judge.evaluate(
            query=query,
            context=context,
            response=response,
            criteria=["relevance", "faithfulness", "helpfulness"]
        )
        
        # Record metrics
        for criterion, score in scores.items():
            quality_score.labels(
                model=self.model,
                criterion=criterion
            ).set(score)
        
        # Store for analysis
        await self.store_evaluation(request_id, scores)
```

### 漂移检测

```python
class QualityDriftDetector:
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.baseline_scores = []
        self.current_scores = []
    
    def add_score(self, score: float):
        self.current_scores.append(score)
        
        if len(self.current_scores) >= self.window_size:
            self.check_drift()
            self.current_scores = []
    
    def check_drift(self):
        if not self.baseline_scores:
            self.baseline_scores = self.current_scores.copy()
            return
        
        # Statistical test for drift
        baseline_mean = np.mean(self.baseline_scores)
        current_mean = np.mean(self.current_scores)
        
        # Simple threshold-based detection
        drift_threshold = 0.1  # 10% degradation
        if (baseline_mean - current_mean) / baseline_mean > drift_threshold:
            self.alert_drift(baseline_mean, current_mean)
    
    def alert_drift(self, baseline: float, current: float):
        alert = {
            "type": "quality_drift",
            "baseline_score": baseline,
            "current_score": current,
            "degradation_pct": (baseline - current) / baseline * 100
        }
        self.send_alert(alert)
```

---

## 成本跟踪

### 实时成本计算

```python
class CostTracker:
    # Pricing per 1M tokens (verify current rates)
    PRICING = {
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "claude-3.5-sonnet": {"input": 3.00, "output": 15.00},
        "claude-3.5-haiku": {"input": 0.25, "output": 1.25},
    }
    
    def track(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        request_id: str
    ) -> float:
        pricing = self.PRICING.get(model, {"input": 0, "output": 0})
        
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost
        
        # Record metrics
        llm_cost_dollars.labels(model=model).inc(total_cost)
        tokens_used_total.labels(model=model, direction="input").inc(input_tokens)
        tokens_used_total.labels(model=model, direction="output").inc(output_tokens)
        
        # Log for analysis
        self.log_cost(request_id, model, input_tokens, output_tokens, total_cost)
        
        return total_cost
```

### 成本归因

```python
class CostAttributor:
    def attribute_cost(
        self,
        request_id: str,
        user_id: str,
        team: str,
        use_case: str,
        cost: float
    ):
        # Store for billing and analysis
        attribution = {
            "request_id": request_id,
            "user_id": user_id,
            "team": team,
            "use_case": use_case,
            "cost": cost,
            "timestamp": datetime.utcnow()
        }
        
        self.store(attribution)
        
        # Update running totals
        self.update_user_total(user_id, cost)
        self.update_team_total(team, cost)
        
        # Check budgets
        if self.exceeds_budget(team):
            self.alert_budget_exceeded(team)
```

---

## 告警策略

### 告警配置

```yaml
alerts:
  # Availability
  - name: high_error_rate
    condition: error_rate > 0.05
    for: 5m
    severity: critical
    runbook: "Check provider status, verify API keys, review recent changes"
    
  # Latency
  - name: high_latency_p95
    condition: latency_p95 > 10s
    for: 5m
    severity: warning
    runbook: "Check model, reduce context size, verify provider status"
    
  # Cost
  - name: cost_spike
    condition: hourly_cost > 2 * rolling_avg_hourly_cost
    for: 1h
    severity: warning
    runbook: "Check for traffic spike, review recent deployments, verify caching"
    
  # Quality
  - name: quality_degradation
    condition: avg_quality_score < 3.5 over 1h
    for: 30m
    severity: warning
    runbook: "Review recent changes, check model performance, sample responses"
    
  # Resource
  - name: rate_limit_approaching
    condition: rate_limit_usage > 0.8
    for: 15m
    severity: warning
    runbook: "Consider model routing, implement backpressure"
```

### 告警优先级

| 严重级别 | 响应时间 | 示例 |
|----------|---------------|----------|
| 严重 | < 15 分钟 | 服务宕机、错误率 > 50% |
| 高 | < 1 小时 | 错误率 > 10%、P99 > 30s |
| 警告 | < 4 小时 | 质量下降、成本激增 |
| 信息 | 下一个工作日 | 趋势变化、容量规划 |

---

## 可观测性工具

### LLM 专用工具

| 工具 | 重点 | 最适合 |
|------|-------|----------|
| LangSmith | LangChain 追踪 | 基于 LangChain 的应用 |
| Langfuse | 开源追踪 | 自托管、隐私要求高的场景 |
| Weights & Biases | 实验跟踪 | ML 团队 |
| Arize Phoenix | LLM 监控 | 生产监控 |
| Helicone | API 代理日志 | 简单集成 |

### 集成示例：Langfuse

```python
from langfuse import Langfuse

langfuse = Langfuse()

async def traced_rag_query(query: str) -> str:
    # Start trace
    trace = langfuse.trace(name="rag_query", input=query)
    
    # Embedding span
    embed_span = trace.span(name="embed")
    embedding = await embed(query)
    embed_span.end()
    
    # Retrieval span
    retrieve_span = trace.span(name="retrieve")
    results = await vector_db.search(embedding)
    retrieve_span.end(output={"count": len(results)})
    
    # Generation span
    gen_span = trace.generation(
        name="generate",
        model="gpt-4o",
        input={"query": query, "context": results}
    )
    response = await llm.generate(query, context=results)
    gen_span.end(output=response)
    
    # End trace
    trace.update(output=response)
    
    return response
```

---

## 面试问题

### Q：生产 LLM 系统需要跟踪哪些指标？

**强回答：**

“我会把指标分为三类：

**运维指标：**这些是任何服务都必须具备的基础指标。
- 请求率和错误率。
- 延迟百分位：p50、p95、p99。
- 流式响应的首 Token 时间（TTFT）。
- 可用性。

**质量指标：**这是 LLM 可观测性的独特之处。
- 使用 LLM 评审对请求抽样评分（抽样率 1～5%）。
- 对 RAG 跟踪忠实度和相关性分数。
- 用户反馈：点赞/点踩和明确评分。
- 在可衡量时跟踪任务完成率。

**成本指标：**
- 按模型统计单请求成本。
- 每日/每周成本趋势。
- 每次成功用户动作的成本。
- Token 效率。

我会为运维问题（错误率 > 5%、P95 超过 SLA）和质量漂移（平均分较基线下降 10%）设置告警。成本激增告警可以帮助发现失控的使用量。

关键洞见是：一个快速、可用但输出糟糕的 LLM 系统仍然是失败的。质量必须是一等指标。”

### Q：如何检测生产环境中的质量下降？

**强回答：**

“我会采用几种方式：

**持续抽样：**使用 LLM 评审对 1～5% 的请求进行评估，在不评测全部请求的情况下获得质量信号。

**漂移检测：**维护质量分布基线，并使用统计检验发现当前分数是否显著偏移。质量下降 10% 时触发警告。

**用户反馈：**收集点赞/点踩以及可用的明确评分，这是用户满意度的事实标准。

**隐式信号：**任务完成率、重试率、升级率和会话长度。如果用户更频繁地遇到困难，质量可能已经下降。

**检测到质量下降后的处理：**
1. 检查近期部署或 Prompt 变更。
2. 抽样具体回答以诊断问题。
3. 确认问题是特定模型/供应商导致，还是普遍存在。
4. 必要时回滚，再继续调查。

我还会维护一组带有预期行为的黄金测试查询，在每次部署时运行，以便在上线前发现回归。”

---

## 参考资料

- OpenTelemetry: https://opentelemetry.io/
- Langfuse: https://langfuse.com/docs
- LangSmith: https://docs.smith.langchain.com/

---

*Next: [Benchmarks and Leaderboards](03-benchmarks-and-leaderboards.md)*
