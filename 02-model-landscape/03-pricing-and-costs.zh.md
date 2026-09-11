# 价格与成本

理解 LLM 系统的成本结构，是进行生产规划的基础。本章介绍定价模型、成本优化策略和总拥有成本分析。

## 目录

- [定价模型](#定价模型)
- [当前 API 价格](#当前-api-价格)
- [成本计算](#成本计算)
- [成本优化策略](#成本优化策略)
- [上下文缓存的经济性](#上下文缓存的经济性)
- [自托管与 GPU 云套利](#自托管与-gpu-云套利)
- [总拥有成本](#总拥有成本)
- [面试问答](#面试问答)
- [参考资料](#参考资料)

---

## 定价模型

### 按 Token 定价

大多数 LLM API 按 token 收费：

```
Cost = (input_tokens × input_rate) + (output_tokens × output_rate)
```

**关键观察：**
- 输出 token 的价格通常是输入 token 的 2–5 倍
- 不同模型层级的价格差异很大
- 一些提供商提供批处理折扣

### 分层定价

一些提供商会提供用量折扣：

| 层级 | 月消费 | 折扣 |
|------|---------------|----------|
| Standard | $0–$5K | 0% |
| Growth | $5K–$50K | 10–20% |
| Enterprise | $50K+ | 定制谈判 |

### 承诺用量定价

预先购买 token，以获得折扣：

```
Standard: $2.50 / 1M input tokens
Committed (1-year): $2.00 / 1M input tokens (20% savings)
```

---

## 当前 API 价格

### 2026 年 8 月价格

> **最后核验：2026 年 8 月 15 日。**价格变化频繁，请始终重新核对：[OpenAI](https://developers.openai.com/api/docs/pricing)、[Anthropic](https://platform.claude.com/docs/en/about-claude/pricing)、[Google](https://ai.google.dev/gemini-api/docs/pricing)、[xAI](https://docs.x.ai/developers/models)、[DeepSeek](https://api-docs.deepseek.com/quick_start/pricing)
>
> **2026 年 8 月最重要的两次价格变化：****Claude Sonnet 5 每 1M token 2/10 美元的介绍价于 8 月 10 日永久化**，原定 9 月 1 日上调至 3/15 美元的计划取消，因此 Sonnet 5 永久低于它替代的 Sonnet 4.6。另一方面，**DeepSeek 从 2026 年 8 月 16 日 16:00 UTC 起将 V4 价格提高 3–12 倍**，改为高峰/非高峰计费，结束其绝对低价选项的阶段：高峰时 V4-Flash 输出价格为每 1M token 1.32 美元，高于 GPT-5.6 Luna 的 1.20 美元。新增的还有：GPT-5.6-Cyber（8 月 10 日，12.50/75 美元，受限访问）、Gemini 3.7 Flash（2026 年 12 月 31 日前半价 0.75/3.75 美元），以及 Grok 4.6（2/6 美元；Prompt 达到 200K 后，较高价格适用于请求的每个 token）。
>
> **2026 年 8 月退役和日落：**Claude Opus 4.1 于 2026 年 8 月 5 日从 Claude API 退役（最后一个 15/75 美元 Opus 档位；Bedrock 和 Google Cloud 仍按自己的计划提供）。OpenAI **Assistants API 将于 2026 年 8 月 26 日停止服务**，由 Responses API + Conversations API 取代，Thread 没有自动迁移。OpenAI 还将在 **2026 年 11 月 30 日**关闭 Evals Platform、Agent Builder 和 Reusable Prompts（10 月 31 日起评测只读；OpenAI 建议评测用户使用第三方 Promptfoo）。Anthropic 的旧 Workbench 和实验性 prompt-tools API 将于 8 月 17 日关闭。
>
> **2026 年生效的弃用：**OpenAI 于 2026 年 2 月 13 日从 ChatGPT 退役 GPT-4o、GPT-4.1、GPT-4.1-mini、o4-mini；gpt-5.2-chat-latest 和 gpt-5.3-chat-latest 于 5 月 8 日弃用；Realtime API Beta 于 5 月 12 日移除；Sora 应用于 4 月 26 日关闭（API 于 9 月 24 日 EOL）。Anthropic 于 6 月 15 日退役 Claude Sonnet 4 和 Claude Opus 4，并于 8 月 5 日退役 Claude Opus 4.1。Google Vertex 于 3 月 26 日退役 `gemini-3-pro-preview`；Project Mariner 于 5 月 4 日关闭；Gemini 2.5 Pro/Flash 于 6 月 17 日弃用。
>
> **价格变化：**Anthropic 于 6 月 9 日发布 Claude Fable 5，价格为每 1M token 10/50 美元：这是其最强的广泛发布模型（带安全措施的 Mythos 级），价格是 Opus 4.8 的 2 倍但不到 Claude Mythos Preview 的一半。Claude Mythos 5（同一模型、部分解除安全措施、仅 Glasswing）同价。Anthropic 于 5 月 28 日发布 Claude Opus 4.8，价格与 Opus 4.7 相同，为 5/25 美元，另有 10/50 美元的 Fast 模式（约快 2.5 倍，比 Opus 4.7 Fast 的 30/150 美元便宜 3 倍）。DeepSeek 于 5 月 22 日将 V4 Pro 的 75% 折扣永久化：2026 年 6 月 1 日起新标价降至原价的 25%（每 1M token 输入/输出 0.435/0.87 美元），4 月 26 日所有 DeepSeek 模型的缓存命中输入价格降至发布价格的 1/10。DeepSeek V4 Flash（每 1M token 0.14/0.28 美元，1M 上下文）是价格大幅领先的前沿级 API。

#### OpenAI（GPT-5.x 世代）
| 模型 | 输入 / 1M | 输出 / 1M | 说明 |
|-------|------------|-------------|-------|
| **GPT-5.6 Sol** ⭐ 新 | $5.00 | $30.00 | 2026 年 7 月 9 日 GA。GPT-5.6 三层产品线的旗舰。1M 上下文，最大输出 128K。 |
| **GPT-5.6 Terra** ⭐ 新 | $2.00 | $12.00 | 2026 年 7 月 30 日从 2.50/15 下调 20%。GPT-5.5 级质量，约一半价格；通用生产默认。 |
| **GPT-5.6 Luna** ⭐ 新 | $0.20 | $1.20 | 2026 年 7 月 30 日从 1/6 下调 80%。对标开放权重竞争；分类、抽取、路由的批量层。 |
| **GPT-5.6-Cyber** ⭐ 新 | $12.50 | $75.00 | 2026 年 8 月 10 日。缓存输入 1.25 美元，400K 上下文。仅 Daybreak Red，必须身份验证、法律声明、获批用例、Responses API；2026 年 9 月 1 日起个人账户须硬件安全密钥。 |
| **GPT-5.5** | $5.00 | $30.00 | 2026 年 4 月 23 日发布。1M 上下文；新一代多模态旗舰。 |
| **GPT-5.5 Instant** ⭐ 新 | 查最新 | 查最新 | 2026 年 5 月 5 日起为 ChatGPT 和 `chat-latest` 默认。高风险 Prompt 幻觉少 52.5%。 |
| **GPT-Realtime-2** ⭐ 新 | $32.00（音频） | $64.00（音频） | 2026 年 5 月 7 日发布。GPT-5 级实时语音。 |
| **GPT-Realtime-Translate** ⭐ 新 |（音频价格）|（音频价格）| 70+ 输入语言 → 13 种输出语言。 |
| **GPT-5.4 Pro** | $30.00 | $180.00 | 最大推理能力；长上下文价格翻倍至 60/270 美元。 |
| **GPT-5.4** | $2.50 | $15.00 | 旗舰；原生计算机使用；缓存输入 1.25 美元。 |
| **GPT-5.4-mini** | $0.75 | $4.50 | GPT-5 层级质量/成本最佳。 |
| **GPT-5.4-nano** | 查最新 | 查最新 | 最小 GPT-5.4 变体；2026 年 3 月发布。 |
| **GPT-4o** | $2.50 | $10.00 | 2026 年 2 月 13 日从 ChatGPT 退役；API 可用性不一。 |
| **GPT-4o-mini** | $0.15 | $0.60 | 遗留模型；检查 API 是否可用。 |

#### Anthropic（Claude Fable + 4.x 世代）
| 模型 | 输入 / 1M | 输出 / 1M | 上下文 | 说明 |
|-------|------------|-------------|---------|-------|
| **Claude Opus 5** ⭐ 新 | $5.00 | $25.00 | 1M | 2026 年 7 月 24 日发布（`claude-opus-5`）。与 Opus 4.8 相同。Fast 为 10/50 美元，约快 2.5 倍；Claude Max 新默认。 |
| **Claude Sonnet 5** ⭐ 新 | $2.00 | $10.00 | 1M | 2026 年 6 月 30 日发布（`claude-sonnet-5`），全产品默认。介绍价于 8 月 10 日永久化；缓存写入 2.50（5 分钟）/4.00（1 小时），命中 0.20，Batch 1/5；永久低于 Sonnet 4.6。 |
| **Claude Fable 5** ⭐ 新 | $10.00 | $50.00 | 1M | 2026 年 6 月 9 日发布（`claude-fable-5`），覆盖 Claude API、AWS、Bedrock、Vertex、Foundry。最强广泛发布 Anthropic 模型；敏感主题不到 5% 的会话回退 Opus 4.8；始终自适应思考，最大输出 128K，数据保留 30 天。 |
| **Claude Mythos 5** ⭐ 新 | $10.00 | $50.00 | 1M | 与 Fable 5 基础模型相同，部分区域解除安全措施。Project Glasswing 合作伙伴和部分生物学研究人员可用；价格不到 Mythos Preview 一半。 |
| **Claude Opus 4.8** | $5.00 | $25.00 | 1M | 2026 年 5 月 28 日 API/Bedrock/Vertex 发布；Dynamic Workflows 研究预览；Fast 10/50，约快 2.5 倍，比 Opus 4.7 Fast 便宜 3 倍；SWE-bench 88.6%、SWE-Bench Pro 69.2%、OSWorld-Verified 82.3%。 |
| **Claude Opus 4.7** | $5.00 | $25.00 | 1M | 2026 年 4 月 16 日发布；高分辨率视觉、SWE 改进；不再提供 Fast 模式，快速请求会报错。 |
| **Claude Opus 4.6** | $5.00 | $25.00 | 1M | 最大输出 128K；标准价格下的自适应思考。 |
| **Claude Sonnet 4.6** | $3.00 | $15.00 | 1M | 被 2026 年 6 月 30 日的 Sonnet 5 取代，后者更新且更便宜。 |
| **Claude Haiku 4.5** | $1.00 | $5.00 | 200K | Anthropic 最快模型；缓存命中输入每 1M token 0.10 美元。 |
| **Claude Mythos Preview** | n/a | n/a | - | 受限研究预览（约 11 个 Glasswing 合作伙伴）；6 月 9 日由 Mythos 5 接替。 |

> [!NOTE]
> **Claude 1M 上下文的标准价格：**Fable 5、Opus 4.8、Opus 4.7、Opus 4.6 和 Sonnet 4.6 在标准价格下包含完整 1M token 上下文，没有长上下文溢价。Batch API 折扣 50%，缓存命中是标准输入价格的 10%。Opus 5 和 Opus 4.8 提供每 1M token 10/50 美元的 Fast 模式；Opus 4.7 不再提供 Fast（会报错），Opus 4.6 以标准速度和价格运行；历史 Opus 4.7 Fast 为 30/150 美元。Fast 价格会叠加缓存倍率，但不适用于 Batch API 或 AWS Claude Platform。Fable 发布时没有 Fast 档。

#### Google（Gemini 3.x 世代）
| 模型 | 输入 / 1M | 输出 / 1M | 上下文 | 说明 |
|-------|------------|-------------|---------|-------|
| **Gemini 3.7 Flash** ⭐ 新 | $0.75 | $3.75 | 1M | 2026 年 8 月 13 日 GA。12 月 31 日前半价，此后 1.50/7.50；缓存 0.075；Batch 0.375/1.875。长期成本模型应使用 2027 年 1 月价格。 |
| **Gemini 3.1 Pro** | $2.00 | $12.00 | 1M | 200K+ 上下文价格为 4/18。 |
| **Gemini 3.1 Flash** | $0.10 | $3.00 | 1M | 质量/价格最佳；适合高并发。 |
| **Gemini 2.5 Flash-Lite** | $0.10 | $0.40 | 1M | 2026 年 6 月弃用。 |

> [!WARNING]
> **Gemini 2.5 弃用：**Gemini 2.5 Pro 和 2.5 Flash 计划于 2026 年 6 月 17 日弃用，请迁移到 Gemini 3.x。

#### xAI（Grok）
| 模型 | 输入 / 1M | 输出 / 1M | 上下文 | 说明 |
|-------|------------|-------------|---------|-------|
| **Grok 4.6** ⭐ 新 | $2.00 | $6.00 | 500K | 2026 年 8 月 12 日发布。缓存输入 0.50；Prompt 达到 200K 后所有 token 价格变为 4/12；Fast 价格翻倍。 |
| **Grok 4** | $3.00 | $15.00 | 256K | 原生工具使用；实时搜索。 |
| **Grok 4.1 Fast** | $0.20 | $0.50 | 2M | 高并发、低成本。 |
| **Grok 3 mini** | 查最新 | 查最新 | - | 更快但准确度较低。 |

#### 通过 API 提供的开放权重与价值层模型（2026 年 8 月）
| 模型 | 输入 / 1M | 输出 / 1M | 上下文 | 提供商示例 |
|-------|------------|-------------|---------|-------------------|
| **DeepSeek V4 Pro** ⭐ 8 月 16 日重新定价 | $1.32 高峰 / $0.66 非高峰 | $3.96 高峰 / $1.98 非高峰 | 1M | 8 月 16 日 16:00 UTC 生效；按 token 类型涨价 3–12 倍；缓存命中输入从 0.003625 升至 0.044；MIT 权重。 |
| **DeepSeek V4 Flash** ⭐ 8 月 16 日重新定价 | $0.44 高峰 / $0.22 非高峰 | $1.32 高峰 / $0.66 非高峰 | 1M | 同日重新定价（此前为 0.14/0.28）；MIT 权重；高峰输出超过 GPT-5.6 Luna 的 1.20 美元。 |
| **Qwen3.8-Max** ⭐ 新 | 查最新 | 查最新 | 262K（至约 1M） | 阿里巴巴 API；8 月 12 日开放权重，商业门控许可证。 |
| **Tencent Hy3** ⭐ 新 | ~$0.13 | ~$0.53 | 256K | OpenRouter；295B/21B 激活 MoE，Apache 2.0。 |
| **MAI-Code-1.1-Flash** ⭐ 新 | $0.20 | $1.20 | 查最新 | Microsoft，8 月 11 日；相较 MAI-Code-1-Flash 降价 73%，已进入 GitHub Copilot。 |
| **Muse Spark 1.2** ⭐ 新 | $1.25 | $4.25 | 1M | Meta Model API；`muse-spark-1.2-contributor` 为 0.10/0.20，条件是允许使用 Prompt 和补全训练模型。 |
| **DeepSeek-V3.2** | $0.28 | $0.42 | 128K | DeepSeek API；缓存命中折扣 98%；路由后有效价格可低 10–30 倍。 |
| **Mistral Medium 3.5** ⭐ 新 | $1.50 | 查最新 | 256K | 统一聊天/推理/编码/视觉；SWE-Bench Verified 77.6%。 |
| **Kimi K2.6** ⭐ 新 | 查最新 | 查最新 | - | Moonshot API；1T MoE/32B 激活；Agent Swarm 可达 300 个子智能体。 |
| **Qwen 3.6-35B-A3B** ⭐ 新 | 查最新 | 查最新 | - | Apache 2.0 权重；自托管或通过 API 提供商使用。 |
| **Llama 4 Scout** | $0.11 | $0.34 | 10M | Together AI、Groq、Fireworks；32K 后有效上下文快速退化。 |
| **Llama 4 Maverick** | $0.27 | $0.85 | 1M | Together AI、Groq、Fireworks；需要 MoE 感知的服务。 |
| **DeepSeek-V3** | $0.25 | $1.10 | 128K | DeepSeek API、Together AI。 |
| **DeepSeek-R1** | $0.55 | $2.19 | 128K | DeepSeek API。 |
| **Mistral Large 3** | $0.50 | $1.50 | 256K | Mistral API、AWS Bedrock。 |
| **Llama 3.3 70B** | ~$0.10–0.20 | ~$0.30–0.60 | 128K | Groq、Together AI。 |
| **Qwen2.5-Coder-32B** | ~$0.50 | ~$1.00 | 32K | Together AI。 |
| **Gemma 4（31B/26B-A4B MoE/E4B/E2B）** ⭐ 新 | 自托管 | 自托管 | 256K | Apache 2.0；140+ 语言；原生视觉/音频；函数调用。 |

#### Embedding 模型
| 模型 | 每 1M token 成本 | 维度 |
|-------|------------------|-----------|
| **Cohere Embed 4** ⭐ 新 | $0.10 | 256/512/1024/1536（Matryoshka） |
| **text-embedding-3-large** | $0.13 | 3072 |
| **text-embedding-3-small** | $0.02 | 1536 |
| **Voyage-3** | $0.06 | 1024 |
| **Cohere embed-v3** | $0.10 | 1024 |

> [!IMPORTANT]
> **推理时计算成本：**对于启用“扩展思考”或推理模式的模型（GPT-5.4 Pro、Claude Opus 4.6），即使内部思考 token 没有展示给用户，也会计费。逻辑密集型任务的总成本可能增加 2–10 倍。生产环境始终要设置 `budget_tokens` 上限。

---

## 成本计算

### 基本成本公式

```python
def calculate_request_cost(
    input_tokens: int,
    output_tokens: int,
    model: str
) -> float:
    pricing = {
        "gpt-5.4": {"input": 2.50, "output": 15.00},
        "gpt-5.4-mini": {"input": 0.75, "output": 4.50},
        "claude-sonnet-4.6": {"input": 3.00, "output": 15.00},
        "claude-opus-4.6": {"input": 5.00, "output": 25.00},
        "gemini-3.1-flash": {"input": 0.10, "output": 3.00},
    }

    rates = pricing[model]
    cost = (
        (input_tokens / 1_000_000) * rates["input"] +
        (output_tokens / 1_000_000) * rates["output"]
    )
    return cost
```

### 成本计算示例

**场景 1：RAG 聊天机器人**
```
Per request:
- System prompt: 500 tokens
- Retrieved context: 2,000 tokens
- User message: 100 tokens
- Response: 300 tokens

Input: 2,600 tokens, Output: 300 tokens

GPT-5.4 cost: (2600 × $2.50 + 300 × $15) / 1M = $0.0110 per request

At 10,000 requests/day:
Daily: $95
Monthly: $2,850
```

**场景 2：文档摘要**
```
Per document:
- Document: 8,000 tokens
- Summary: 500 tokens

GPT-5.4 cost: (8000 × $2.50 + 500 × $15) / 1M = $0.0275

1,000 documents: $27.50
10,000 documents: $275
```

### 月度成本预测

```python
def project_monthly_cost(
    requests_per_day: int,
    avg_input_tokens: int,
    avg_output_tokens: int,
    model: str
) -> dict:
    per_request = calculate_request_cost(
        avg_input_tokens, avg_output_tokens, model
    )

    daily = per_request * requests_per_day
    monthly = daily * 30
    yearly = monthly * 12

    return {
        "per_request": per_request,
        "daily": daily,
        "monthly": monthly,
        "yearly": yearly
    }

# Example
costs = project_monthly_cost(
    requests_per_day=50000,
    avg_input_tokens=2000,
    avg_output_tokens=400,
    model="gpt-5.4"
)
# Output: ~$18,750/month
```

---

## 成本优化策略

### 策略 1：模型路由

将请求路由到合适的模型层级：

```python
class ModelRouter:
    def __init__(self):
        self.classifier = load_complexity_classifier()

    def route(self, query: str, context: str) -> str:
        complexity = self.classifier.predict(query)

        if complexity < 0.3:
            return "gpt-5.4-mini"  # Simple queries
        elif complexity < 0.7:
            return "gpt-5.4-mini"  # Medium, try cheap first
        else:
            return "gpt-5.4"  # Complex queries

    def route_with_fallback(self, query: str, context: str) -> str:
        # Try cheap model first
        response = self.try_model("gpt-5.4-mini", query, context)

        if self.is_quality_sufficient(response):
            return response

        # Fallback to expensive model
        return self.try_model("gpt-5.4", query, context)
```

**潜在节省：**在质量影响很小的情况下节省 50–70%。

### 策略 2：Prompt 优化

在不损失质量的情况下减少 token 数：

```python
# Before: 2,500 tokens
system_prompt = """
You are a helpful customer support assistant for Acme Corp.
You have access to our product documentation and should answer
questions accurately and helpfully. Always be polite and professional.
If you don't know something, say so rather than making things up.
Format your responses clearly with bullet points when listing items.
[... more verbose instructions ...]
"""

# After: 800 tokens
system_prompt = """
You are Acme Corp's support assistant.
Rules:
- Answer from provided context only
- Admit uncertainty
- Use bullet points for lists
- Be concise
"""

# Savings: 1,700 tokens × $2.50/1M = $0.00425 per request
# At 10K requests/day: $42.50/day = $1,275/month
```

### 策略 3：缓存

缓存重复或相似请求的响应：

```python
class ResponseCache:
    def __init__(self, ttl_seconds: int = 3600):
        self.exact_cache = TTLCache(maxsize=10000, ttl=ttl_seconds)
        self.semantic_cache = SemanticCache(threshold=0.95)

    def get_or_generate(self, query: str, context: str) -> tuple[str, bool]:
        # Check exact cache
        cache_key = self.make_key(query, context)
        if cache_key in self.exact_cache:
            return self.exact_cache[cache_key], True  # Cache hit

        # Check semantic cache
        similar = self.semantic_cache.find_similar(query)
        if similar:
            return similar.response, True  # Semantic hit

        # Generate new response
        response = self.generate(query, context)
        self.exact_cache[cache_key] = response
        self.semantic_cache.add(query, response)

        return response, False  # Cache miss

# With 30% cache hit rate:
# Baseline: $3,000/month
# With caching: $2,100/month
# Savings: $900/month
```

### 策略 4：批处理

把多个请求一起处理以提高效率：

```python
# Real-time: pay full price
for query in queries:
    response = model.generate(query)

# Batch API (OpenAI offers 50% discount):
batch_responses = model.batch_generate(queries)
# Cost: 50% of real-time pricing
```

### 策略 5：控制输出长度

适当限制响应长度：

```python
# Reduce unnecessary output
response = model.generate(
    prompt=prompt,
    max_tokens=300,  # Limit output
    stop=["\n\n"]    # Stop at natural break
)

# Cost impact:
# Before: avg 500 output tokens = $0.0075 per request (GPT-5.4)
# After: avg 250 output tokens = $0.00375 per request
# Savings: 50% on output costs
```

### 成本优化汇总

| 策略 | 付出 | 潜在节省 |
|----------|--------|-------------------|
| 模型路由 | 中 | 50–70% |
| **上下文缓存** | 低 | **60–90%（输入）** |
| Prompt 优化 | 低 | 20–40% |
| 响应缓存 | 中 | 20–40% |
| 批处理 | 低 | 50%（OpenAI/Anthropic） |

---

## 上下文缓存的经济性

**RAG 的“黄金法则”（2026 年仍适用）。**
如果固定系统 Prompt 或共享知识库（前缀）超过 10,000 token，**上下文缓存是必需的**。

**盈亏平衡分析（Claude Sonnet 4.6）：**
- **标准输入**：每 1M token 3.00 美元
- **缓存输入**：每 1M token 0.30 美元（折扣 90%）
- **缓存写入费用**：每 1M token 3.75 美元（5 分钟 TTL，1.25 倍）；6.00 美元（1 小时 TTL，2 倍）

`Break-even = (Write Fee) / (Standard Rate - Cached Rate) ≈ 1.4 requests (5-min) or 2.2 requests (1-hour)`

如果长前缀被**超过 2 个用户**使用，缓存它严格来说就比每次原样发送更便宜。OpenAI 和 Anthropic 都提供 Batch API 折扣（50%），且可以与缓存叠加。

---

## 自托管与 GPU 云套利

**预留实例与无服务器的权衡：**

| 模型规模 | 无服务器（RunPod/Together） | 预留（Lambda/AWS） |
|------------|-----------------------------|-----------------------|
| **突发容量** | 无限（冷启动） | 固定 |
| **利用率** | 只为实际计算时间付费 | 7×24 固定成本 |
| **TCO 盈亏平衡**| **利用率 < 40% 时更划算** | **利用率 > 40% 时更划算** |

**Principal 级别的细节：**
“GPU 云套利”指根据**竞价实例的可用性**在提供商之间迁移生产负载。Skypilot 等工具可以自动化这个过程，跟随全球“低需求”区域，最多节省 60% 的自托管成本。MoE 模型的兴起（Llama 4 Scout 可运行在单张 H100，Maverick 约需 2 张 H100，DeepSeek V4 Flash 需 4 张 H100）相较稠密模型进一步降低了自托管 GPU 要求。

### 什么时候适合自托管

```
Break-even analysis:

API cost at scale:
- 1M requests/month
- 2,500 tokens average
- GPT-5.4: ~$37,500/month
- Claude Sonnet 4.6: ~$30,000/month

Self-hosted equivalent (Llama 4 Maverick via MoE):
- 2x H100 80GB: ~$6/hour × 730 = $4,380/month
- Engineering time: $5,000/month (0.5 FTE)
- Ops overhead: $2,000/month
- Total: ~$11,380/month

Savings vs GPT-5.4: $26,120/month = 70%
Savings vs Claude Sonnet 4.6: $18,620/month = 62%
```

### 自托管成本组成

| 组成 | 月成本 | 说明 |
|-----------|--------------|-------|
| GPU 计算 | $5K–20K | 取决于模型规模 |
| 存储 | $200–500 | 模型权重、日志 |
| 网络 | $100–500 | 出站流量、负载均衡 |
| 工程 | $5K–15K | 运维兼职 FTE |
| 监控 | $100–500 | 可观测性工具 |

### 不同模型规模的 GPU 需求

| 模型规模 | GPU 配置 | 估计月成本 |
|------------|------------|---------------------|
| 7B（INT4） | 1× A10G | $500–800 |
| 7B（FP16） | 1× A100 40GB | $1,500–2,500 |
| 70B（INT4） | 2× A100 80GB | $5,000–8,000 |
| 70B（FP16） | 4× A100 80GB | $10,000–15,000 |
| 405B（INT4） | 8× H100 | $20,000–30,000 |

### 决策框架

```
Choose API when:
- Volume < 100K requests/month
- No ML ops expertise
- Need highest quality (frontier models)
- Fast iteration needed

Choose self-hosting when:
- Volume > 500K requests/month
- Have ML infrastructure team
- Data privacy requirements
- Predictable, stable workload
- Custom fine-tuning needed
```

---

## 总拥有成本

### TCO 组成

```python
def calculate_tco(scenario: dict) -> dict:
    # Direct costs
    api_or_compute = scenario["monthly_api_cost"]

    # Engineering costs
    development = scenario["dev_hours"] * scenario["engineer_rate"]
    maintenance = scenario["maintenance_hours"] * scenario["engineer_rate"]

    # Infrastructure
    vector_db = scenario["vector_db_cost"]
    monitoring = scenario["monitoring_cost"]

    # Indirect costs
    downtime_risk = scenario["expected_downtime_hours"] * scenario["revenue_per_hour"]

    monthly_tco = (
        api_or_compute +
        development / 12 +  # Amortized over year
        maintenance +
        vector_db +
        monitoring +
        downtime_risk
    )

    return {
        "monthly_tco": monthly_tco,
        "yearly_tco": monthly_tco * 12,
        "breakdown": {
            "llm": api_or_compute,
            "engineering": development / 12 + maintenance,
            "infrastructure": vector_db + monitoring,
            "risk": downtime_risk
        }
    }
```

### TCO 对比示例

**场景：客服机器人（每月 50K 请求）**

| 成本组成 | 基于 API | 自托管 |
|----------------|-----------|-------------|
| LLM 成本 | $5,000 | $3,000 |
| 向量数据库 | $70 | $200 |
| 工程（每月） | $500 | $3,000 |
| 监控 | $100 | $200 |
| **每月总计** | **$5,670** | **$6,400** |

*在这个规模下，由于工程开销，API 更便宜。*

**场景：大规模 RAG（每月 2M 请求）**

| 成本组成 | 基于 API | 自托管 |
|----------------|-----------|-------------|
| LLM 成本 | $50,000 | $15,000 |
| 向量数据库 | $500 | $1,000 |
| 工程（每月） | $1,000 | $8,000 |
| 监控 | $200 | $500 |
| **每月总计** | **$51,700** | **$24,500** |

*在这个规模下，自托管明显更便宜。*

---

## 面试问答

### 问：如何优化高并发 RAG 应用的成本？

**强回答：**
我会分层进行成本优化：

**1. 架构优化：**
- 模型路由：简单 Query 使用便宜模型
- 缓存：30–40% 的 Query 可能适合缓存
- Prompt 压缩：减少系统 Prompt token

**2. 模型选择：**
```
Simple queries (60%): GPT-5.4-mini at $0.003/request
Complex queries (40%): GPT-5.4 at $0.011/request
Weighted avg: $0.0062/request (vs $0.011 all GPT-5.4)
Savings: 44%
```

**3. 基础设施：**
- 批量更新 Embedding（便宜 50%）
- 合理配置向量数据库规模
- 尽可能使用竞价实例

**4. 监控：**
- 按 Query 类型追踪成本
- 对异常告警
- 定期复盘成本

### 问：什么时候建议自托管，什么时候使用 API 提供商？

**强回答：**
决策取决于多个因素：

**用量阈值：**
- 低于每月 100K：几乎总是 API
- 100K–500K：逐案评估
- 高于 500K：自托管通常更有优势

**团队能力：**
- 没有 ML 运维能力：无论规模都用 API
- 有强基础设施团队：可以更早考虑自托管

**质量要求：**
- 要求绝对最优：API（前沿模型）
- 质量足够即可：自托管开放模型

**其他因素：**
- 数据隐私：可能强制自托管
- 延迟控制：自托管控制力更强
- 微调需求：自托管提供更多定制能力

**我的推荐流程：**
1. 从 API 开始，以获得最快迭代
2. 构建模型切换抽象层
3. 月消费超过 10K 美元时评估自托管
4. 作出承诺前先用影子部署试点

---

## 参考资料

- OpenAI Pricing: https://developers.openai.com/api/docs/pricing
- Anthropic Pricing: https://platform.claude.com/docs/en/about-claude/pricing
- Google AI Pricing: https://ai.google.dev/gemini-api/docs/pricing
- xAI Pricing: https://docs.x.ai/developers/models
- Mistral Pricing: https://docs.mistral.ai/getting-started/changelog
- Lambda Labs GPU Pricing: https://lambdalabs.com/service/gpu-cloud
- RunPod Pricing: https://www.runpod.io/pricing
- LLM Pricing Comparison: https://pricepertoken.com/

---

*上一篇：[模型能力评估](02-capability-assessment.md) | 下一篇：[模型选择指南](04-model-selection-guide.md)*
