# 模型选择指南

一个实用的框架，用于根据能力、成本、延迟和运营因素，为你的用例选择合适的 LLM。

## 目录

- [选择框架](#选择框架)
- [能力比较](#能力比较)
- [用例映射](#用例映射)
- [成本分析](#成本分析)
- [运营考量](#运营考量)
- [多模型策略](#多模型策略)
- [面试问题](#面试问题)
- [参考资料](#参考资料)

---

## 选择框架

### 决策树（2026 年 6 月）

```
从这里开始
    │
    ├── 需要绝对的能力上限？
    │   └── 是 ─────────────────────────────────────────┐
    │   └── 否 ──┐                                      │
    │            │                                      ▼
    │            │                              ┌─────────────────┐
    │            │                              │ Claude Fable 5  │
    │            │                              │ ($10/$50, 1M)   │
    │            │                              └─────────────────┘
    │            │
    ├── 需要自主 Agent / 长周期规划？
    │   └── 是 ─────────────────────────────────────────┐
    │   └── 否 ──┐                                      │
    │            │                                      ▼
    │            │                              ┌─────────────────┐
    │            │                              │ Claude Opus 4.8 │
    │            │                              │ GPT-5.5 reason. │
    │            │                              └─────────────────┘
    │            │
    ├── 需要最好的软件工程 / 编码能力？
    │   └── 是 ─────────────────────────────────────────┐
    │   └── 否 ──┐                                      │
    │            │                                      ▼
    │            │                              ┌─────────────────┐
    │            │                              │ Fable 5 上限 /  │
    │            │                              │ GPT-5.5 88.7%   │
    │            │                              │ Opus 4.8 88.6%  │
    │            │                              │ Sonnet 4.6 便宜 │
    │            │                              └─────────────────┘
    │            │
    ├── 需要处理海量上下文（>1M）？
    │   └── 是 ─────────────────────────────────────────┐
    │   └── 否 ──┐                                      │
    │            │                                      ▼
    │            │                              ┌─────────────────┐
    │            │                              │ Gemini 3.0 Pro  │
    │            │                              │（2.5M 上下文）  │
    │            │                              └─────────────────┘
    │            │
    ├── 对成本敏感的高流量？
    │   └── 是 ─────────────────────────────────────────┐
    │   └── 否 ──┐                                      │
    │            │                                      ▼
    │            │                              ┌─────────────────┐
    │            │                              │ Gemini 3 Flash /│
    │            │                              │ o4-mini         │
    │            │                              └─────────────────┘
    │            │
    └── 默认：生产选择
                 ▼
        ┌─────────────────┐
        │ Claude Sonnet 4.6│
        │ GPT-5.5-mini    │
        └─────────────────┘
```

### 关键选择因素

| 因素 | 权重 | 考量 |
|--------|--------|----------------|
| **Agent 可靠性** | 高 | 工具调用准确率、多步规划 |
| **上下文召回** | 高 | 1M+ 上下文的“大海捞针”表现 |
| **速率限制上限** | 高 | **（高级细节）**：供应商能否在不产生 429 错误的情况下处理你的 P99 吞吐？ |
| **生态成熟度** | 高 | 生产记录、SDK 支持和企业 SLA |
| **成本 / 输出 Token** | 中 | Agent 循环会消耗多 5–10 倍的 token |

---

## 能力比较

### 前沿模型比较（2026 年 6 月）

| 模型 | 优势 | 缺点 | 上下文 | 最适合 |
|-------|-----------|------|---------|----------|
| **Claude Fable 5** | 广泛发布模型中能力最强；具备 Mythos 级能力且有安全防护；始终开启的自适应思考；SOTA 视觉能力；可持续最长的自主运行 | 价格是 Opus 4.8 的 2 倍（$10/$50）；敏感主题中低于 5% 的会话会回退到 Opus 4.8；数据保留 30 天 | 1M | 能力上限任务：最难推理、视觉、最长周期 Agent |
| **Claude Opus 4.8** | 长时间 Agent 编码（SWE-bench 88.6%）、带并行子 Agent 的 Dynamic Workflows、$10/$50 快速模式 | GPT-5.5 略微领先单次 SWE-bench；Fable 5 的能力现已高于它 | 1M | 代码库规模迁移、自主编码循环、前沿中最佳性价比 |
| **GPT-5.5** | SWE-bench Verified 第一（88.7%）、Terminal-Bench 第一（78.2%）、原生全模态 | 成本高（$5/$30） | 1M | 多 Agent 系统、单次编码 |
| **Claude Opus 4.7** | 上一代旗舰（SWE-bench 87.6%、SWE-Bench Pro 64.3%） | 同价位已被 4.8 超越 | 1M | 尚无迁移压力的现有 4.7 部署 |
| **Claude Opus 5** | 当前 Opus 旗舰（2026 年 7 月 24 日），价格仍为 $5/$25；可选 Fast 模式 $10/$50 | 比大多数已发布的第三方评测更新 | 1M | 长周期 Agent 编码和计算机使用 |
| **Claude Sonnet 5** | 自 2026 年 6 月 30 日起的生产主力，永久价格 $2/$10（比它替代的 Sonnet 4.6 便宜） | 相对 Opus 档位主动降低了网络安全能力 | 1M | Agent 集群和大规模编码的默认档位 |
| **GPT-5.6 Terra** | 7 月 30 日降价后，以 $2/$12 提供 GPT-5.5 级质量 | 产品线较新，独立评测较少 | 1M | OpenAI 侧的通用生产默认模型 |
| **Claude Sonnet 4.6** | 成本/质量平衡强，标准价格提供完整 1M 上下文 | 已被更新且更便宜的 Sonnet 5 超越 | 1M | 尚未迁移的现有部署 |
| **Gemini 3.1 Pro** | GPQA Diamond 第一（94.3%）、1M 多模态、Deep Think 模式 | Deep Think 延迟会突增 | 1M | 科学推理、多模态 |
| **DeepSeek-R1** | 开源推理、数学有竞争力 | 仅推理；通用能力不属于前沿 | 128K | 数学、复杂调试、开放权重推理 |

### 预算模型比较

| 模型 | 成本（每 1M 输入/输出） | 质量 | 上下文 | 最适合 |
|-------|----------------------------|---------|---------|----------|
| **Gemini 3 Flash** | $0.05 / $0.20 | 前沿级 | 1M | 高流量 RAG |
| **o4-mini** | $0.10 / $0.40 | 优秀 | 128K | 快速推理任务 |
| **Llama 4 8B** | 自托管（H100/L40） | 强 | 128K | 端侧、私有 |

### 开源模型

| 模型 | 参数 | 质量 | 最适合 |
|-------|------------|---------|----------|
| **Llama 4 70B** | 70B | 可与前沿竞争 | 通用开放选择 |
| **Nemotron 3 Ultra** | 500B MoE | Agent 能力强 | 可扩展开放 Agent |
| **DeepSeek V3.2** | 671B MoE | 超高性能 | 前沿质量的最低 TCO |

---

## 用例映射

### 按应用类型（2026 年 6 月）

| 用例 | 推荐模型 | 理由 |
|----------|-------------------|-----------|
| **能力上限研究 / 最难问题** | Claude Fable 5 | Mythos 级能力，普遍可用；只把受能力上限约束的工作以 $10/$50 路由给它 |
| **自主开发** | Claude Opus 4.8（Dynamic Workflows）、Claude Sonnet 4.6 | Claude Code 中的并行子 Agent 运行；SWE-Bench Pro 第一，69.2% |
| **企业 RAG** | Gemini 3.1 Pro、Gemini 3.1 Flash、DeepSeek V4 Flash | 1M 上下文和激进的缓存折扣降低了检索复杂度 |
| **客服** | Gemini 3.1 Flash、GPT-5.5-mini、Claude Haiku 4.5 | 接近零延迟且推理能力强 |
| **推理 / 调试** | GPT-5.5 reasoning、Claude Opus 4.8（thinking）、DeepSeek-R1 | 代码和逻辑的隐式 CoT 能力最好 |
| **视频 / 多模态** | Gemini 3.1 Pro、GPT-5.5、Claude Opus 4.8 | 原生交错多模态处理 |
| **私有 Agent** | Llama 4 Maverick、DeepSeek V4 Pro（开放权重） | 开放权重中最强的 Agent 规划 |

### 按约束

| 约束 | 方法 |
|------------|----------|
| **最大延迟 < 100ms** | Gemini 3.1 Flash、GPT-5.5-mini、Claude Haiku 4.5 或自托管 Nano 模型 |
| **上下文 > 1M token** | Claude Fable 5 / Opus 4.8 / Opus 4.7 / Sonnet 4.6、Gemini 3.1 Pro、GPT-5.5、Llama 4 Scout（10M） |
| **零数据泄漏** | Llama 4 70B、内部 VPC 中的 DeepSeek V4 Pro |
| **复杂工具使用** | Claude Opus 4.8 或 GPT-5.5（规划准确率最佳） |

---

## 成本分析

### 成本建模（2026 年 6 月）

| 模型 | 输入 / 1M | 输出 / 1M | 备注 |
|-------|------------|-------------|-------|
| **Claude Fable 5** | $10.00 | $50.00 | 能力上限；Opus 4.8 的 2 倍；留给能力上限任务 |
| **Claude Opus 4.8** | $5.00 | $25.00 | 前沿编码和 Agent；可选快速模式 $10 / $50 |
| **Claude Opus 4.7** | $5.00 | $25.00 | 标准价格相同；快速模式更贵，为 $30 / $150 |
| **GPT-5.5** | $5.00 | $30.00 | 单次 SWE-bench 第一 |
| **Claude Opus 5** | $5.00 | $25.00 | 当前 Opus 旗舰；快速模式 $10/$50 |
| **Claude Sonnet 5** | $2.00 | $10.00 | 自 2026 年 8 月 10 日起的永久价格；默认主力 |
| **GPT-5.6 Terra** | $2.00 | $12.00 | 2026 年 7 月 30 日降价 20% |
| **GPT-5.6 Luna** | $0.20 | $1.20 | 2026 年 7 月 30 日降价 80%；流量档位 |
| **Claude Sonnet 4.6** | $3.00 | $15.00 | 已被更便宜的 Sonnet 5 超越 |
| **Gemini 3.1 Pro** | $2.00 | $12.00 | 最具性价比的前沿模型；多模态 |
| **DeepSeek V4 Pro** | $0.435 | $0.87 | 2026 年 8 月 16 日起，高峰涨到 $1.32 / $3.96（非高峰为一半） |
| **Gemini 3.1 Flash** | $0.10 | $3.00 | 大规模 RAG；缓存折扣 |
| **DeepSeek V4 Flash** | $0.14 | $0.28 | 最便宜的前沿级 1M 上下文 |

### 成本比较示例

假设每月 1M 次查询，每次 1K 输入 token + 500 输出 token：

| 流量 | GPT-5.5 | Claude Sonnet | Gemini 3 Pro | Gemini 3 Flash |
|--------|---------|---------------|--------------|----------------|
| 每月 10K 次查询 | $150 | $105 | $37.50 | $1.50 |
| 每月 1M 次查询 | $15,000 | $10,500 | $3,750 | $150 |

*洞察：DeepSeek V4 Flash（$0.14 / $0.28）和 Gemini 3.1 Flash（$0.10 / $3.00）实际上已经让 RAG 商品化，使大规模长上下文处理比传统向量搜索基础设施更便宜。*

---

## 运营考量

### 速率限制与配额

| 供应商 | 档位 | RPM | TPM |
|----------|------|-----|-----|
| OpenAI（Tier 1） | 基础 | 500 | 30K |
| OpenAI（Tier 5） | 企业 | 10K | 10M |
| Anthropic（Tier 1） | 基础 | 50 | 40K |
| Anthropic（Tier 4） | 企业 | 4K | 400K |

### 可靠性模式

```python
class ReliableModelClient:
    def __init__(self):
        self.providers = {
            "primary": OpenAIClient(),
            "fallback1": AnthropicClient(),
            "fallback2": GoogleClient()
        }

    async def generate(self, prompt: str) -> str:
        for name, client in self.providers.items():
            try:
                return await client.generate(prompt)
            except RateLimitError:
                continue
            except ServiceError:
                continue

        raise AllProvidersUnavailable()
```

### 抽象层

```python
class LLMClient:
    """多供应商的统一接口。"""

    def __init__(self, config: dict):
        self.default_model = config["default_model"]
        self.clients = self._init_clients(config)

    async def generate(
        self,
        messages: list[dict],
        model: str = None,
        **kwargs
    ) -> str:
        model = model or self.default_model
        client = self._get_client(model)

        # 规范化请求格式
        normalized = self._normalize_request(messages, kwargs)

        # 调用供应商
        response = await client.generate(**normalized)

        # 规范化响应
        return self._normalize_response(response)

    def _normalize_request(self, messages: list[dict], kwargs: dict) -> dict:
        # 处理供应商之间的差异
        # OpenAI 使用 'messages'，Anthropic 也使用 'messages' 但格式不同
        pass
```

---

## 多模型策略

### 模型路由

```python
class ModelRouter:
    def __init__(self):
        self.classifier = QueryClassifier()
        self.models = {
            "simple": "gpt-4o-mini",
            "complex": "claude-3.5-sonnet",
            "code": "claude-3.5-sonnet",
            "long_context": "gemini-1.5-pro",
            "reasoning": "o1-mini"
        }

    async def route(self, query: str, context_length: int) -> str:
        # 对查询复杂度分类
        query_type = await self.classifier.classify(query)

        # 对长上下文覆盖路由
        if context_length > 100_000:
            return self.models["long_context"]

        return self.models[query_type]
```

### 级联模式（2025 年改进）

**逻辑：**永远不要让 70B 模型执行 1B 模型可以完成的任务。使用“路由器”对置信度评分。

```python
class ModelCascade:
    """“效率优先”模式。"""

    async def generate_optimized(self, query: str):
        # 1. 草稿检查（SLM / 分类器）
        if is_simple_intent(query):
            return await gpt4o_mini.generate(query)

        # 2. 主生成（高效模型）
        response = await claude_sonnet.generate(query)

        # 3. 验证 / 升级
        if needs_verification(response):
            return await o3.generate(f"Verify this: {response}")

        return response
```

**高级提示：**实现“语义回退”：错误时不要只重试同一个模型，而要立即切换到更大的模型或不同供应商（OpenAI → Anthropic），避免相关故障。

---

## 面试问题

### Q：生产应用中如何在 GPT-4o、Claude 和 Gemini 之间选择？

**强回答：**

“我的选择取决于具体需求：

**对于大多数生产负载，**我默认使用 Claude 3.5 Sonnet 或 GPT-4o。两者都是优秀的通用模型。Sonnet 在编码方面略有优势，GPT-4o 的生态集成更好。

**对于长上下文应用，**Gemini 1.5 Pro 凭借 100–200 万 token 上下文是明显赢家。如果需要处理完整代码库或很长的文档，我会选择 Gemini。

**对于对成本敏感的高流量场景，**使用 GPT-4o-mini 或 Claude Haiku。它们便宜 10–20 倍，而且能很好处理简单任务。

**我的实际方法：**
1. 用 Sonnet 或 GPT-4o 做原型，验证用例。
2. 在我的具体任务上评测，而不只是看基准。
3. 构建抽象层，以便轻松切换。
4. 把更简单的请求路由到更便宜的模型，优化成本。

我从不只依赖基准分数。一个在 MMLU 上排名较低的模型，可能在我的领域表现出色。”

### Q：什么时候自托管，什么时候使用 API 供应商？

**强回答：**

“这是控制力与运营负担之间的权衡。

**在以下情况下使用 API：**
- 流量低于每月 1M 次查询（成本交叉点）
- 需要立即使用最新模型
- 团队缺少 GPU 基础设施经验
- 工作负载变化大，难以规划容量
- 上市时间很关键

**在以下情况下自托管：**
- 数据不能离开基础设施（合规）
- 流量超过每月 10M 次查询（节省成本）
- 需要低于 100ms 的 P99 延迟
- 需要自定义模型权重或微调
- 需要完全控制模型行为

**混合方案通常最好：**
- 高流量、可预测的工作负载使用自托管。
- 峰值流量和专业模型使用 API。
- 自托管失败时使用 API 作为回退。

自托管的隐藏成本包括 GPU 采购、工程时间、模型更新和监控。应为基础设施预留 1–2 名专职工程师。”

---

## 参考资料

- OpenAI API: https://platform.openai.com/
- Anthropic API: https://docs.anthropic.com/
- Google AI: https://ai.google.dev/
- LMSys Leaderboard: https://chat.lmsys.org/

---

*下一篇：[微调指南](../03-training-and-adaptation/02-fine-tuning-strategies.md)*
