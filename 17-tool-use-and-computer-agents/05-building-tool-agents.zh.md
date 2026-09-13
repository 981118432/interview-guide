# 构建工具使用 Agent

本页与英文原文逐段对应，保留标题层级、列表、表格、代码、公式、链接和面试问答。

本章覆盖工具使用 Agent 的实践工程：设计可被 LLM 可靠调用的工具 Schema，构建承载工具的 MCP Server，将工具组合成工作流，并测试完整系统。这些模式决定了系统是演示品还是生产部署。

## 目录

- [为 LLM 设计工具 Schema](#designing-tool-schemas-for-llms)
- [创建 MCP Server](#mcp-server-creation)
- [工具注册与发现](#tool-registration-and-discovery)
- [输入校验与输出格式](#input-validation-and-output-formatting)
- [工具组合：串联工具](#tool-composition-chaining-tools)
- [构建自定义 Agent Skill](#building-custom-agent-skills)
- [创建函数调用端点](#creating-function-calling-endpoints)
- [测试工具使用 Agent](#testing-tool-use-agents)
- [工具使用的可观测性](#observability-for-tool-use)
- [常见错误与反模式](#common-mistakes-and-anti-patterns)
- [工具版本与向后兼容](#tool-versioning-and-backwards-compatibility)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## 为 LLM 设计工具 Schema

工具 Schema 是 LLM 与系统之间的契约。设计良好的 Schema 可以减少幻觉参数、防止误用，并让模型更可靠地选择工具。

### 优秀工具定义的组成

```json
{
  "name": "search_customers",
  "description": "Search for customers by name, email, or account ID. Returns up to 10 matching customer records. Use this when the user asks about a specific customer. Do NOT use this for aggregate queries like 'how many customers do we have'.",
  "input_schema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Search term: customer name, email address, or account ID (e.g., 'john@acme.com' or 'ACC-12345')"
      },
      "limit": {
        "type": "integer",
        "description": "Max results to return (1-10). Default: 5",
        "default": 5,
        "minimum": 1,
        "maximum": 10
      }
    },
    "required": ["query"]
  }
}
```

### Schema 设计规则

**1. 精确命名**：使用 `verb_noun` 格式，例如 `search_customers`，而不是 `search` 或 `customer_tool`。

**2. 说明何时不要使用**：模型需要反例。“不要用于聚合查询”比只列出正确用途更能防止误用。

**3. 提供参数示例**：在描述字符串中加入示例值，模型会据此校准输出。

**4. 约束范围**：使用 `minimum`、`maximum`、`enum` 和 `pattern` 在 Schema 层阻止无效参数，而不是把检查全放在处理器中。

**5. 保持工具原子性**：一个工具只做一件事。不要创建同时负责增删改查的 `manage_customer`，应拆成四个工具。

**6. 使用 `strict: true`**：严格模式保证模型输出完全匹配 Schema，生产环境应始终启用。

```
Good Tool Design:                    Bad Tool Design:

+-------------------+                +-------------------+
| search_customers  |                | customer_tool     |
| - query (string)  |                | - action (string) |
| - limit (int 1-10)|                | - data (object)   |
+-------------------+                | - options (any)   |
| create_customer   |                +-------------------+
| - name (string)   |                "action" can be
| - email (string)  |                "search", "create",
+-------------------+                "update", "delete"
| update_customer   |                => model confused,
| - id (string)     |                   schema too loose,
| - fields (object) |                   hard to validate
+-------------------+
```

---

## 创建 MCP Server

MCP Server 是向任意兼容 MCP 的客户端（Claude、GPT、基于 Llama 的 Agent）暴露工具、资源和 Prompt 的独立进程。Server 只需编写一次，任意 LLM 都能使用。

### MCP 架构

```
+------------------+          JSON-RPC           +------------------+
|                  |  ========================>  |                  |
|   MCP Client     |                             |   MCP Server     |
|   (AI App)       |  <========================  |   (Your Code)    |
|                  |                             |                  |
|  - Claude Code   |  Transport:                 |  Exposes:        |
|  - Custom Agent  |  - stdio (local)            |  - Tools         |
|  - IDE Plugin    |  - Streamable HTTP (remote)  |  - Resources     |
|                  |                             |  - Prompts       |
+------------------+                             +------------------+
```

### TypeScript MCP Server

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({ name: "customer-service", version: "1.0.0" });

server.tool(
  "search_customers",
  "Search customers by name, email, or ID. Returns up to 10 matches.",
  {
    query: z.string().describe("Search term: name, email, or account ID"),
    limit: z.number().min(1).max(10).default(5).describe("Max results"),
  },
  async ({ query, limit }) => ({
    content: [{ type: "text",
      text: JSON.stringify(await db.customers.search(query, limit), null, 2) }],
  })
);

const transport = new StdioServerTransport();
await server.connect(transport);
```

### Python MCP Server（FastMCP）

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("customer-service")

@mcp.tool()
async def search_customers(query: str, limit: int = 5) -> str:
    """Search customers by name, email, or ID. Returns up to 10 matches.
    Args:
        query: Search term - customer name, email, or account ID
        limit: Max results to return (1-10, default 5)
    """
    return json.dumps(await db.customers.search(query, limit), indent=2)
```

两个 SDK 遵循同一模式：创建 Server、用类型化 Schema 注册工具、连接传输层。TypeScript SDK 使用 Zod 校验，Python 使用类型提示和文档字符串。

### 部署模式

| Mode | Transport | Use Case |
|------|-----------|----------|
| Local (stdio) | stdin/stdout pipe | Desktop tools, IDE plugins |
| Remote (Streamable HTTP) | HTTP + SSE | Cloud services, shared servers |
| Hybrid | Both | Develop local, deploy remote |

---

## 工具注册与发现

生产环境中的 Agent 应动态发现可用工具，而不是把工具硬编码。

### 静态注册

在配置文件（如 `claude_desktop_config.json`）中声明 MCP Server。每个条目将 Server 名称映射到命令、参数和可选环境变量。这种方式简单但不灵活，因为每个 Server 无论是否相关都会在启动时加载。

### 动态发现（工具搜索）

Anthropic 的 Tool Search（2025）解决了 Schema 过载。Agent 不把 200 个工具 Schema 全部加载到上下文，而是发送轻量搜索查询，只接收 3～5 个相关 Schema，让上下文专注于推理而不是解析未使用 Schema。

### MCP 发现协议

MCP 客户端通过标准 JSON-RPC 方法发现能力：`tools/list` 返回可用工具，`resources/list` 返回数据资源，`prompts/list` 返回 Prompt 模板，从而支持运行时发现而无需硬编码。

---

## 输入校验与输出格式化

### 输入校验层

```
+---------------------+
|  Schema Validation   |  <-- JSON Schema / Zod / Pydantic
|  (type, range, enum) |      Catches: wrong types, out-of-range
+----------+----------+
           |
           v
+---------------------+
|  Business Validation |  <-- Your handler code
|  (exists, permitted) |      Catches: invalid IDs, unauthorized
+----------+----------+
           |
           v
+---------------------+
|  Execution           |  <-- Actual operation
+---------------------+
```

始终在两层都做校验：Schema 校验捕获格式错误，业务校验捕获语义无效的输入。

```python
@mcp.tool()
async def transfer_funds(
    from_account: str,
    to_account: str,
    amount: float
) -> str:
    """Transfer funds between accounts."""
    # Schema already enforced types via type hints

    # Business validation
    if amount <= 0:
        return "Error: Amount must be positive."
    if amount > 10000:
        return "Error: Transfers over $10,000 require manual approval."
    if from_account == to_account:
        return "Error: Cannot transfer to the same account."

    from_acct = await db.accounts.get(from_account)
    if not from_acct:
        return f"Error: Account {from_account} not found."

    # Execute
    result = await db.transfers.execute(from_account, to_account, amount)
    return f"Transferred ${amount:.2f}. Confirmation: {result.id}"
```

### 输出格式化

模型还需要继续推理时返回结构化数据；结果已经最终确定时返回人类可读文本。

```python
# Good: structured for further reasoning
return json.dumps({
    "customers": [
        {"id": "ACC-123", "name": "Jane Smith", "email": "jane@acme.com"},
        {"id": "ACC-456", "name": "John Doe", "email": "john@acme.com"}
    ],
    "total_matches": 2,
    "has_more": False
})

# Bad: unstructured blob
return "Found Jane Smith (ACC-123, jane@acme.com) and John Doe (ACC-456, john@acme.com)"
```

---

## 工具组合：工具链

真实任务需要按顺序调用多个工具，常见有两种组合模式：

### 模式 1：LLM 编排的工具链

LLM 根据之前的结果决定下一步调用哪个工具：

```
User: "Find customer Jane Smith and create a high-priority ticket for her billing issue"

Turn 1:  LLM -> search_customers("Jane Smith")
         Result: {"id": "ACC-123", "name": "Jane Smith", ...}

Turn 2:  LLM -> create_ticket("ACC-123", "Billing issue", "...", "high")
         Result: "Ticket TK-789 created."

Turn 3:  LLM -> "I found Jane Smith (ACC-123) and created ticket TK-789."
```

每次工具调用都是一次独立的 API 往返，模型在调用之间对结果进行推理。

### 模式 2：程序化工具调用

Anthropic 的程序化工具调用（2025）允许模型编写串联工具的代码，减少往返：

```
LLM generates code:
  customer = search_customers("Jane Smith")
  if customer.results:
    ticket = create_ticket(customer.results[0].id, ...)
    return f"Created {ticket.id} for {customer.results[0].name}"
  else:
    return "Customer not found"
```

这作为一次 API 调用执行，把延迟从 3 次往返降为 1 次。

### 模式 3：服务端组合

也可以直接在 MCP Server 内组合工具：单个 `resolve_customer_issue` 工具在内部调用搜索和 create_ticket，把多步逻辑隐藏起来。对于固定且定义清晰、LLM 不需要在步骤之间推理的工作流，应使用这种方式。

### 各模式的适用场景

| 模式 | 延迟 | 灵活性 | 最适合 |
|---------|---------|-------------|----------|
| LLM 编排 | 高（N 次往返） | 很高 | 复杂、分支逻辑 |
| 程序化 | 低（1 次往返） | 高 | 线性链、批处理 |
| Server 端 | 最低 | 低 | 固定的常见工作流 |

---

## 构建自定义 Agent Skill

Agent Skill（Anthropic，2025）是 Agent 动态加载的指令、工具和资源集合。一个 Skill 就是一个目录：

```
my-skill/
  SKILL.md          # Instructions the agent loads into system prompt
  tools/            # MCP tool implementations
  resources/        # Data files, templates, schemas
  tests/            # Evaluation cases
```

运行时，SkillManager 注册可用 Skill 并按需激活：将 Skill 指令注入系统 Prompt，并把其工具加入可用工具集。这样既保持基础 Agent 轻量，又支持深度专业化。

---

## 创建函数调用端点

为了让任意 LLM 都能调用你的 API，可以通过带 Pydantic 模型的 FastAPI 暴露它。自动生成的 OpenAPI 规范（`/openapi.json`）可以同时充当函数调用的工具 Schema。也可以把相同逻辑包装进 MCP Server，直接集成 Claude、GPT 或其他兼容 MCP 的客户端。

---

## 测试工具使用 Agent

### 三层测试

```
+---------------------------+
|   Eval Suites             |  End-to-end: does the agent
|   (Agent + LLM + Tools)  |  complete the task?
+-------------+-------------+
              |
+-------------v-------------+
|   Integration Tests       |  Does tool X work correctly
|   (Tool + Dependencies)   |  with real DB / API?
+-------------+-------------+
              |
+-------------v-------------+
|   Unit Tests              |  Does validation logic
|   (Tool Logic Only)       |  handle edge cases?
+---------------------------+
```

### 工具单元测试

使用 Mock 依赖单独测试每个工具处理器。覆盖输入校验边界（超范围值、缺少字段）、错误消息质量（是否能引导模型恢复）和输出格式（有效 JSON、正确 Schema）。

### Agent 行为评测套件

构建包含 100 多个真实查询及预期结果的数据集：

```python
eval_cases = [
    {
        "input": "Find Jane Smith's account and check her last payment",
        "expected_tools": ["search_customers", "get_payment_history"],
        "max_tool_calls": 5,
    },
    {
        "input": "What is the meaning of life?",
        "expected_tools": [],  # Should NOT call any tools
        "max_tool_calls": 0,
    },
]
```

对每个案例衡量：工具选择准确率（是否选对工具）、参数质量（参数是否正确）、任务完成率和效率（工具调用次数）。每次模型版本或工具 Schema 变更都运行评测。

---

## 工具使用的可观测性

每次工具调用都应记录：Trace/Span ID、时间戳、工具名、输入参数、输出大小、延迟、状态、所用模型、Token 用量和会话 ID。

### 关键指标

| 指标 | 衡量内容 | 告警阈值 |
|--------|-----------------|-----------------|
| 工具调用成功率 | 返回有效结果的调用比例 | < 95% |
| 工具选择准确率 | 是否选择了正确工具 | < 90% |
| 每任务平均工具调用次数 | 工具使用效率 | > 基线 2 倍 |
| 每次工具调用延迟 | 工具处理器响应时间 | > 5s（p99） |
| 幻觉参数 | Schema 已有约束但参数仍无效 | > 2% |
| 每任务成本 | LLM + 工具执行总成本 | > 预算 |

### 追踪架构

```
+-------------+     +----------------+     +--------------+
|  Agent      |---->|  Tool Handler  |---->|  Backend     |
|  (LLM call) |     |  (MCP Server)  |     |  (DB/API)    |
+------+------+     +--------+-------+     +------+-------+
       |                     |                     |
       v                     v                     v
+------+---------------------+---------------------+------+
|                    Trace Collector                       |
|              (OpenTelemetry / Langfuse)                  |
+---------------------------+------------------------------+
                            |
                            v
                   +--------+--------+
                   |   Dashboard     |
                   |   - Success %   |
                   |   - Latency     |
                   |   - Cost        |
                   +-----------------+
```

---

## 常见错误与反模式

| 反模式 | 问题 | 修复 |
|-------------|---------|-----|
| 工具过载 | 超过 50 个工具会降低选择准确率 | 动态发现，每轮加载 5～10 个 |
| 描述含糊 | “处理客户运营”过于宽泛 | 写明何时使用、何时不要使用及示例 |
| 上帝工具 | 一个带 `action` 参数的工具包办一切 | 拆成原子工具，每个只做一个操作 |
| 缺少错误上下文 | 工具只返回没有细节的“Error” | 返回可操作消息：“找不到 ACC-999，请使用 search_customers……” |
| 非结构化输出 | 工具返回模型必须解析的散文 | 为结构化推理返回 JSON |
| 没有幂等性 | 两次调用 `create_ticket` 会创建重复记录 | 接受幂等键，创建前检查 |
| 暴露内部 ID | 工具要求模型无法知道的数据库 UUID | 接受人类可读标识符，内部解析 |
| 忽略限流 | Agent 循环调用 100 次 API 后被限流 | 在处理器中退避，并返回“X 秒后重试” |

---

## 工具版本管理与向后兼容

工具不断演进时，必须维护依赖它们的 Agent 的兼容性。

**规则：**
1. **增量变更**（新增可选参数）：无需升级版本，旧调用仍然有效。
2. **破坏性变更**（重命名、删除参数、改变语义）：使用新 Schema 创建新的工具名。保留旧工具运行，并在其描述中加入“DEPRECATED：请改用 new_tool”。记录每次弃用调用以便监控。
3. **确认没有活跃 Agent 依赖工具前，绝不删除工具。**

---

## 面试问题

### Q：需要让 LLM Agent 访问 200 个内部工具，如何处理 Schema 过载？

**强回答：**
我不会把全部 200 个工具 Schema 加载到上下文，而会实现两阶段方案。第一阶段是工具发现：Agent 描述需要完成的事情，由轻量搜索（嵌入相似度或关键词匹配）返回最相关的 5～10 个工具 Schema。第二阶段是工具执行：实际 LLM 调用的上下文中只包含被选中的工具。

这对应 Anthropic 的 Tool Search 模式。发现步骤可以是单独的低成本 LLM 调用，甚至可以是非 LLM 搜索。关键洞见是，无关工具 Schema 占用的上下文空间会直接降低模型推理质量。我会把工具选择准确率作为关键指标：如果 Agent 应调用 `get_customer_by_id` 却调用了 `search_customers`，就需要调优发现阶段。

在 MCP 实现中，我会把工具按领域分组到不同 Server（客服、计费、分析），并只连接与当前对话相关的 Server。

### Q：为处理客服的工具使用 Agent 设计测试策略。

**强回答：**
我会分三层测试。第一层是每个工具处理器的单元测试：校验输入边界、错误消息和输出格式；使用 Mock 依赖，在每次提交的 CI 中运行。

第二层是集成测试，验证工具能否对真实（预发布）数据库工作。例如 `create_ticket` 确实创建记录，`search_customers` 能返回该记录，从而发现工具与后端之间的 Schema 漂移。

第三层是测试完整 Agent（LLM 加工具）的评测套件。我会构建 100 个以上的真实客服查询，并记录预期工具调用序列和输出标准。评测工具选择准确率、参数质量、任务完成率和效率（用了多少次工具调用）。

每次模型版本或工具 Schema 变更都运行评测。如果 Schema 变更后工具选择准确率下降 2%，说明应该修改工具描述，而不是修改模型。

---

## 参考资料

- Anthropic. "Tool Use with Claude" API Documentation (2025)
- Model Context Protocol. "Build an MCP Server" (2025)
- MCP TypeScript SDK: github.com/modelcontextprotocol/typescript-sdk
- MCP Python SDK: github.com/modelcontextprotocol/python-sdk
- Anthropic. "Introducing Advanced Tool Use" (2025)
- Anthropic. "Agent Skills" Beta Documentation (2025)

---

*Previous: [Computer-Use Agents](04-computer-use-agents.md)*
