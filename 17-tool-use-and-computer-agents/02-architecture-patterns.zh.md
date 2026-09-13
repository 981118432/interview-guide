# 工具使用 Agent 的架构模式

本页与英文原文逐段对应，保留标题层级、列表、表格、代码、公式、链接和面试问答。

2026 年的工具使用 Agent——从 OpenClaw、Claude Code 到 Cursor Background Agent——都建立在少数几种核心架构模式之上。理解这些模式后，可以从第一性原理设计 Agent，而不是照搬某个工具。本章通过详细图示、代码示例、权衡和选型建议逐一拆解这些模式。

## 目录

- [模式 1：函数/工具调用](#pattern-1-functiontool-calling)
- [模式 2：基于视觉的自动化](#pattern-2-vision-based-automation)
- [模式 3：本地代码执行](#pattern-3-local-code-execution)
- [模式 4：多 Agent 工具编排](#pattern-4-multi-agent-tool-orchestration)
- [Sandbox 与非 Sandbox 执行](#sandboxed-vs-unsandboxed-execution)
- [工具调用之间的状态管理](#state-management-across-tool-calls)
- [错误处理与重试模式](#error-handling-and-retry-patterns)
- [MCP 集成模式](#mcp-integration-patterns)
- [架构决策树](#architecture-decision-tree)
- [系统设计面试角度](#system-design-interview-angle)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## 模式 1：函数/工具调用

这是生产环境部署最广泛的模式。LLM 决定调用哪个工具以及传入什么参数，框架执行调用，再把结果反馈到对话中供下一步推理。

### 架构

```
+-------------------------------------------------------------------+
|              Function/Tool Calling Pattern                        |
+-------------------------------------------------------------------+
|                                                                   |
|  +------------------+                                             |
|  |  User Message     |                                            |
|  +--------+---------+                                             |
|           |                                                       |
|           v                                                       |
|  +--------+---------+     +------------------+                    |
|  |  LLM Reasoning   |---->|  Tool Selection  |                   |
|  |                   |     |                  |                    |
|  |  "I need to look  |     |  tool: search_db |                   |
|  |   up the order"  |     |  args: {id: 42}  |                    |
|  +-------------------+     +--------+---------+                   |
|                                     |                             |
|                                     v                             |
|                            +--------+---------+                   |
|                            |  Tool Executor   |                   |
|                            |  (Framework)     |                   |
|                            |                  |                   |
|                            |  Validates args  |                   |
|                            |  Calls function  |                   |
|                            |  Returns result  |                   |
|                            +--------+---------+                   |
|                                     |                             |
|                                     v                             |
|                            +--------+---------+                   |
|                            |  Result Injected |                   |
|                            |  into Context    |                   |
|                            |                  |                   |
|                            |  {status: "shipped",                 |
|                            |   tracking: "1Z..."} |               |
|                            +--------+---------+                   |
|                                     |                             |
|                                     v                             |
|                            +--------+---------+                   |
|                            |  LLM Generates   |                   |
|                            |  Final Response  |                   |
|                            +------------------+                   |
+-------------------------------------------------------------------+
```

### 三个步骤详解

**步骤 1——Schema 展示**：模型接收描述可用工具的 JSON Schema。2026 年的最佳实践是使用动态清单，根据用户意图只获取相关工具，而不是预先加载全部工具 Schema。

**步骤 2——意图与抽取**：模型输出结构化工具调用，而不是自由文本；它是包含 `tool_name` 和 `arguments` 的 JSON 对象，框架可以确定性解析。

**步骤 3——执行与上下文化**：框架使用 Pydantic、Zod 或类似工具校验参数，调用函数，并将结果作为 `role=tool` 的新消息注回对话。

### 代码示例：MCP Server + Client

```python
# MCP Server: defines a tool with strict schema
from mcp.server import Server
from pydantic import BaseModel, Field

server = Server("order-service")

class OrderLookup(BaseModel):
    """Look up an order by ID. DO NOT use for cancelled orders."""
    order_id: str = Field(..., description="The order UUID")

@server.tool()
async def lookup_order(args: OrderLookup) -> dict:
    order = await db.orders.find_one({"id": args.order_id})
    if not order:
        return {"error": "Order not found", "suggestion": "Check order ID format"}
    return {"status": order["status"], "tracking": order.get("tracking_number")}
```

```python
# MCP Client: agent discovers tools dynamically, calls them, feeds results back
tools = await mcp_client.list_tools()
response = client.messages.create(model="claude-sonnet-4-6", tools=tools,
    messages=[{"role": "user", "content": "Where is my order ORD-12345?"}])

if response.stop_reason == "tool_use":
    tool_call = response.content[0]
    result = await mcp_client.call_tool(tool_call.name, tool_call.input)
    # Feed result back as a tool_result message for the next LLM turn
```

### 何时使用此模式

- API 集成（数据库、SaaS 工具、内部服务）
- 结构化数据的读取与修改
- 任何可以预先定义工具接口的工作流
- 需要审计轨迹和输入校验的生产系统

### 权衡

| 优点 | 缺点 |
|-----------|--------------|
| 确定性执行 | 需要预先定义工具 Schema |
| 易于审计和记录日志 | 无法与任意 UI 交互 |
| 快（每次工具调用 50～200ms） | 模型可能幻觉生成工具名或参数 |
| 适用于支持工具使用的任意 LLM | 工具过多时 Schema 负载过重 |

---

## 模式 2：基于视觉的自动化

模型查看屏幕截图，推理下一步操作，并输出低层动作（点击、输入、滚动）。环境执行动作后截取新截图，循环重复；Claude Computer Use 和 Open Interpreter Computer API 都采用这种方式。

### 架构

```
+-------------------------------------------------------------------+
|              Vision-Based Automation Pattern                      |
+-------------------------------------------------------------------+
|                                                                   |
|  +------------------+                                             |
|  |  Task Goal        |  "Fill out the expense form with           |
|  |  (NL instruction) |   last week's receipts"                    |
|  +--------+---------+                                             |
|           |                                                       |
|           v                                                       |
|  +--------+--------------------------------------------------+    |
|  |                    VISION-ACTION LOOP                      |    |
|  |                                                            |    |
|  |   +------------+    +-------------+    +------------+     |    |
|  |   |  OBSERVE   |    |  REASON     |    |  ACT       |     |    |
|  |   |            |    |             |    |            |     |    |
|  |   | Screenshot |--->| Analyze     |--->| Emit action|     |    |
|  |   | (base64)   |    | screenshot  |    | {type:     |     |    |
|  |   |            |    | + goal      |    |  "click",  |     |    |
|  |   |            |    | + history   |    |  x: 450,   |     |    |
|  |   |            |    | + prev acts |    |  y: 320}   |     |    |
|  |   +-----^------+    +-------------+    +------+-----+     |    |
|  |         |                                      |          |    |
|  |         +--------------------------------------+          |    |
|  |                    (Loop until done)                       |    |
|  +-----------------------------------------------------------+    |
|                            |                                      |
|                            v                                      |
|  +-------------------------+------------------------------+       |
|  |         Sandboxed Environment (VM / Docker + VNC)      |       |
|  |                                                        |       |
|  |   +----------+  +----------+  +----------+            |       |
|  |   | Desktop  |  | Browser  |  | Apps     |            |       |
|  |   | (Xfce)   |  | (Chrome) |  | (any)    |            |       |
|  |   +----------+  +----------+  +----------+            |       |
|  +--------------------------------------------------------+       |
+-------------------------------------------------------------------+
```

### 观察—推理—行动循环

**观察**：截取当前屏幕状态。Claude Computer Use 将其作为 Base64 编码 PNG 放在图像内容块中发送。2026 年新增的 Zoom Action 可以截取密集 UI 特定区域的高分辨率裁剪图。

**推理**：多模态 LLM 结合任务目标和动作历史分析截图，决定下一步动作。这一步消耗最多 Token。

**行动**：模型输出结构化动作：
- `left_click(x, y)` -- click at coordinates
- `type(text)` -- type a string
- `key(key_combo)` -- press keyboard shortcut
- `scroll(direction, amount)` -- scroll the page
- `screenshot()` -- take a new screenshot without acting
- `zoom(x0, y0, x1, y1)` -- inspect a region at high resolution

### 代码示例：计算机使用循环

```python
tools = [
    {"type": "computer_20250124", "name": "computer",
     "display_width_px": 1280, "display_height_px": 800},
    {"type": "bash_20250124", "name": "bash"},
    {"type": "text_editor_20250124", "name": "str_replace_based_edit_tool"}
]
messages = [{"role": "user", "content": "Open the browser and go to GitHub."}]

while True:  # The vision-action loop
    response = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=4096, tools=tools, messages=messages)
    if response.stop_reason == "end_turn":
        break
    for block in response.content:
        if block.type == "tool_use":
            result = sandbox.execute_action(block.name, block.input)
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": block.id, "content": result}]})
```

### 何时使用此模式

- 自动化没有 API 的遗留应用
- 对图形界面进行端到端测试
- 需要与多个应用交互的任务
- 非开发者用自然语言描述任务的场景

### 权衡

| 优点 | 缺点 |
|-----------|--------------|
| Works with any GUI application | Slow (1-3 sec per action step) |
| No API or integration needed | High token cost (screenshots are large) |
| Handles dynamic UIs | Misclick risk on dense interfaces |
| Accessible to non-technical users | Requires sandboxed VM for safety |

---

## 模式 3：本地代码执行

用户用自然语言描述任务，LLM 生成代码；代码在本地机器或 Sandbox 中运行，模型观察输出后继续生成代码或给出最终答案。这是 Open Interpreter 和 Claude Code 部分功能的工作方式。

### Architecture

```
User (NL): "Analyze the CSV and plot the top 10 products"
  |
  v
[LLM Generates Code] --> Python/Bash/JS
  |
  v
[Permission Gate] --> "Run this code? [y/N]" (auto-approve, always-ask, or rules-based)
  |
  v
[Code Executor] --> Execute, capture stdout/stderr/return value
  |
  v
[Output Observer] --> Error? Feed back to LLM for fix. Success? Present to user.
  |
  v
[LLM Decides] --> Done? Return result. Need more? Generate next code block. (Loop)
```

### 自然语言—代码—执行—观察循环

**1. 自然语言转代码**：LLM 将用户意图翻译为可执行代码。语言取决于任务：数据分析用 Python，系统操作用 Bash，Web 任务用 JavaScript。

**2. 权限闸门**：执行前要求用户批准，这是非 Sandbox 环境中的关键安全机制。实现方式包括：
- **始终询问**（Open Interpreter 默认）：每个代码块都需要明确批准
- **Auto-approve** (trusted mode): Dangerous but fast
- **基于规则**（Claude Code 模式）：在配置中定义允许/拒绝模式。例如允许 `git` 命令，拒绝 `rm -rf`

**3. 执行与捕获**：代码在拥有完整或受限系统权限的运行时执行，捕获 stdout、stderr、返回值和生成文件。

**4. 观察与迭代**：LLM 查看执行输出，有错误就生成修复，输出不完整就生成下一步，由此形成自我纠正循环。

### 代码示例：代码执行 Agent

```python
class CodeExecutionAgent:
    def __init__(self, llm_client, sandbox=None):
        self.llm = llm_client
        self.sandbox = sandbox  # None = unsandboxed (host)
        self.history = []

    async def run(self, task: str) -> str:
        self.history.append({"role": "user", "content": task})
        for iteration in range(10):  # Max 10 code-execute cycles
            response = await self.llm.generate(messages=self.history)
            code = extract_code_block(response)
            if not code:
                return response  # No code = final answer
            if not self.sandbox and not await user_approves(code):
                return "Execution cancelled by user."
            result = await (self.sandbox or LocalExecutor()).run(code, timeout=30)
            self.history.append({"role": "assistant", "content": response})
            self.history.append({"role": "user",
                "content": f"stdout: {result.stdout}\nstderr: {result.stderr}"})
        return "Max iterations reached."
```

### 何时使用此模式

- Data analysis and visualization tasks
- System administration and DevOps automation
- File processing and transformation
- Any task where the user describes "what" and the agent figures out "how"

### 权衡

| 优点 | 缺点 |
|-----------|--------------|
| 极其灵活 | 不使用 Sandbox 时存在安全风险 |
| 通过观察循环自我纠错 | 模型可能生成危险代码 |
| 可与本地模型离线工作 | 需要用户评估代码（或选择信任它） |
| 必要时可访问完整系统 | 非确定性（同一 Prompt 可能生成不同代码） |

---

## 模式 4：多 Agent 工具编排

不让一个 Agent 拥有大量工具，而是让多个专业 Agent 各自负责一组工具，由编排器把任务路由给正确的 Agent。这是 Agent 领域的“微服务革命”。

### 架构

```
  [User Request]
       |
       v
  [ORCHESTRATOR] (Frontier model: Claude Opus, GPT-4o)
  Analyzes task, selects agent, routes and waits
       |
  +----+----+----+
  |         |         |
  v         v         v
[Code Agent]  [Data Agent]  [Web Agent]
 bash, edit,   SQL, plot,    fetch, scrape,
 git           csv            browse
  |         |         |
  v         v         v
[Sandbox]  [Sandbox]  [Sandbox]
(Docker)   (Docker)   (Docker)
```

### 编排策略

**1. 基于路由器（最简单）**：编排器充当分类器，查看用户消息、选择专业 Agent 并转发完整任务，不需要 Agent 间通信。

**2. 计划与执行**：前沿级计划模型将任务拆成子任务，分配给对应专业 Agent，再汇总结果。基准显示任务完成率 92%，速度比串行 ReAct 快 3.6 倍。

**3. 层次化**：高层 Agent 将工作分配给低层 Agent，低层 Agent 还可以继续委派。这类似组织结构，适合复杂项目。

**4. 协作式（点对点）**：Agent 可以直接通信、共享观察结果和请求帮助。这是最复杂的模式，但适合涌现型任务。

### 成本优化：计划与执行的优势

```
Traditional: [Frontier Model] handles all steps       Cost: $1.00/task

Plan-and-Execute:
  [Frontier Model] plans (1 call)                     Cost: $0.05
  [Small Model] executes steps 1-3                    Cost: $0.03
  [Frontier Model] aggregates (1 call)                Cost: $0.05
                                                      Total: $0.13/task
                                                      Savings: ~87%
```

2026 年的趋势是把 Agent 成本优化视为一等关注点，类似微服务时代云成本优化变得不可或缺。

---

## Sandbox 与非 Sandbox 执行

这是任何工具使用 Agent 最重要的架构决策。

### 比较

```
  UNSANDBOXED (Host Access)              SANDBOXED (Isolated)
  +------------------------+             +------------------------+
  | LLM output executes    |             | LLM output executes    |
  | directly on host OS    |             | inside Docker/VM/E2B   |
  |                        |             |                        |
  | Risk: rm -rf /         |             | Isolated filesystem,   |
  | Risk: data exfiltration|             | network, processes     |
  |                        |             |                        |
  | Used by: OpenClaw,     |             | Used by: OpenHands,    |
  | Open Interpreter,      |             | OpenAI Codex, Jules,   |
  | Claude Code (default)  |             | Cursor Background Agents|
  +------------------------+             +------------------------+
```

### Sandbox 实现选项

| Technology | Isolation Level | Startup Time | Use Case |
|------------|----------------|-------------|----------|
| Docker | Process + FS | 1-5 sec | Most agent sandboxes (OpenHands) |
| Firecracker | Full VM (microVM) | ~125ms | High-security, multi-tenant |
| gVisor | Kernel-level | ~200ms | Google Cloud Run |
| E2B | Cloud sandbox | 2-3 sec | Remote agent execution |
| WebAssembly | Language-level | <50ms | Browser-based execution |

### 2026 年共识

默认使用 Sandbox，同时为高级用户提供受控出口。OpenClaw 安全危机（公网上暴露 13.5 万个实例）让行业认真对待这一点。新的生产 Agent 应默认隔离，非 Sandbox 执行只适用于单用户、有人监督的环境。

---

## 工具调用之间的状态管理

Agent 需要在工具调用之间保持状态，具体策略取决于生命周期和用例。

### 状态管理模式

| 模式 | 生命周期 | 存储 | 使用者 |
|---------|-----------|---------|---------|
| **对话状态** | 短暂（单次对话） | 消息数组 | 大多数基于 API 的 Agent |
| **会话状态** | 每个会话（工作目录、打开的文件） | Docker 容器 / 临时目录 | OpenHands、Claude Code |
| **持久状态** | 跨会话（数天、数周） | 数据库、文件、Markdown | OpenClaw（Memories/）、CLAUDE.md |
| **环境状态** | 外部（事实来源） | Git 仓库、数据库、文件系统 | Claude Code（git status）、CI/CD |

### 实现：会话状态

```python
class AgentSession:
    """Manages state across tool calls within a single session."""
    def __init__(self):
        self.conversation: list[dict] = []
        self.working_dir: str = tempfile.mkdtemp()
        self.open_files: dict[str, str] = {}  # path -> content cache
        self.tool_call_count: int = 0

    def add_tool_result(self, tool_name: str, args: dict, result: dict):
        self.tool_call_count += 1
        self.conversation.append({"role": "tool", "tool_name": tool_name,
            "args": args, "result": result, "timestamp": time.time()})
        # Update derived state from side effects
        if tool_name == "write_file":
            self.open_files[args["path"]] = args["content"]

    def get_context_for_llm(self, max_tokens: int = 100_000) -> list[dict]:
        """Return conversation history, compressed if over budget."""
        if estimate_tokens(self.conversation) < max_tokens:
            return self.conversation
        return self._compress_history(max_tokens)  # Summarize old results
```

---

## 错误处理与重试模式

工具调用会失败，网络会超时，API 会返回错误，代码会抛出异常。生产 Agent 需要系统化的错误处理。

### 错误分类

| 错误类型 | 示例 | 策略 |
|-----------|----------|----------|
| **瞬时错误** | 网络超时、限流、503 | 指数退避重试（最多 3 次） |
| **输入错误** | 参数无效、格式错误 | 将错误反馈给 LLM，让它修正参数 |
| **权限错误** | 认证失败、访问被拒 | 告知用户，**不要**重试 |
| **逻辑错误** | 工具选错、操作不可能完成 | 将错误反馈给 LLM，让它重新规划 |
| **灾难性错误** | OOM、Sandbox 崩溃、无限循环 | 中止任务、报告错误并清理资源 |

### 重试模式实现

```python
class ToolExecutor:
    MAX_RETRIES = 3

    async def execute_with_retry(self, tool_name: str, args: dict) -> dict:
        for attempt in range(self.MAX_RETRIES):
            try:
                result = await self.call_tool(tool_name, args)
                if not result.get("error"):
                    return result  # Success
                error_type = classify_error(result["error"])
                if error_type == "transient":
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                elif error_type == "input":
                    return {"error": result["error"], "fix_hint": "Adjust args"}
                elif error_type == "permission":
                    return {"error": result["error"], "action": "Report to user"}
                else:  # catastrophic
                    await self.cleanup_sandbox()
                    return {"error": "Fatal error. Task aborted."}
            except TimeoutError:
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
        return {"error": f"Failed after {self.MAX_RETRIES} retries"}
```

### 自我纠正循环

这是 2026 年最强大的错误处理模式：Agent 观察自身失败并自主修复：

```
LLM generates code/tool call
  --> Execute --> Success? -- YES --> Return result
                     |
                     NO
                     |
                     v
              Feed error + stderr to LLM --> LLM generates fix --> Execute again
              (max 5 corrections to prevent infinite loops)
```

Claude Code、OpenHands 和 Cline 都用这种方式处理测试失败：运行测试、查看失败、编辑代码、重新测试，直到全部通过。

---

## MCP 集成模式

到 2026 年，MCP 已成为工具集成的标准协议。以下是将 MCP 集成进 Agent 架构的关键模式。

### 模式 A：直接 MCP 连接

```
[Agent (Client)] <-- stdio / HTTP --> [MCP Server]
```
最简单的模式：一个 Agent、一个 Server，适用于单一用途工具（数据库、文件系统）。

### 模式 B：多 Server 扇出

```
                  +--> [GitHub MCP]
[Agent (Client)]--+--> [Postgres MCP]
                  +--> [Slack MCP]
```
Agent 同时连接多个 MCP Server，将工具 Schema 合并到一个清单中。Claude Code 和多工具助手会采用这种方式。

### 模式 C：MCP Gateway（企业）

```
[Agent 1] --+                          +--> [GitHub MCP]
[Agent 2] --+--> [MCP Gateway]  --+--> [Postgres MCP]
[Agent 3] --+    (Auth, Rate Limit,    +--> [Slack MCP]
                  Audit, Route)
```
中央 Gateway 负责认证、限流和审计日志，Agent 只向 Gateway 认证。适用于企业和多租户部署。

### MCP 路线图缺口

截至 2026 年 5 月，当前 MCP 规范仍缺少三个关键生产原语：

1. **身份传递**：没有将用户身份从客户端传递到 Server 的标准方式，Gateway 模式只是权宜方案。
2. **自适应工具预算**：协议层没有按工具调用限制 Token/成本消耗的支持。
3. **结构化错误语义**：没有标准错误码或错误类别，每个 Server 自定义错误格式。

这些内容已列入 2026 年路线图，但尚未正式批准。

---

## 架构决策树

使用这棵决策树为用例选择合适模式：

```
Does the target system have an API?
 +-- YES --> Pattern 1 (Tool Calling). Wrap as MCP server. Fastest, most reliable.
 +-- NO  --> Does the task require GUI interaction?
              +-- YES --> Pattern 2 (Vision-Based). Sandbox in VM. Accept latency.
              +-- NO  --> Is the task primarily code/data work?
                           +-- YES --> Pattern 3 (Code Exec). Sandbox if multi-tenant.
                           +-- NO  --> Complex enough for multiple specialists?
                                        +-- YES --> Pattern 4 (Multi-Agent Orch.)
                                        +-- NO  --> Pattern 1 with custom tool.
```

### 混合架构

实践中的生产系统会组合模式。Claude Code 使用：
- 模式 1（工具调用）处理文件操作和 Git。
- 模式 2（基于视觉）处理计算机使用功能。
- 模式 3（代码执行）处理 Bash 和测试运行。
- 模式 4（多 Agent）创建子 Agent。

关键是默认使用最简单的模式（函数调用），只有用例确实需要时才增加复杂性。

---

## 系统设计面试角度

在面试中讨论工具使用架构时，可以围绕以下五个维度组织答案：

### 1. 模式选择

先判断哪种模式匹配：“目标系统有 REST API，因此我会使用函数/工具调用模式，用 MCP Server 封装这个 API。”这能体现你理解决策树，而不是只会罗列产品名称。

### 2. Sandbox 边界

一定要回答安全问题：“在多租户部署中，我会把每个用户的 Agent 会话放进无法访问内部服务网络的 Docker 容器。MCP Server 运行在 Sandbox 外部，代理所有外部调用。”

### 3. 状态策略

说明状态如何管理：“工作文件使用 Docker 容器内的会话状态，环境状态（Git 仓库）作为事实来源。这个用例不需要持久化 Agent 记忆。”

### 4. 错误预算

讨论失败模式：“工具调用可能因瞬时错误失败（退避重试）、因输入错误失败（让 LLM 自我纠正），也可能因权限错误失败（反馈给用户）。我会把自我纠正最多设置为 5 次，超过后升级处理。”

### 5. 成本模型

说明经济性：“编排器采用计划与执行模式：由 Opus 规划任务，由 Haiku 执行每一步。与所有步骤都使用 Opus 相比，这样大约可以降低 87% 的成本。”

---

## 面试问题

### 问：设计一个客服 Agent，使用 Zendesk、Salesforce 和内部知识库的数据回答问题。

**强回答：**
使用模式 1（函数/工具调用），为每个数据源配置一个 MCP Server。采用带动态清单的多 Server 扇出模式，每次查询只加载相关工具。生产环境增加 MCP Gateway，负责按数据源处理 OAuth、限流（Salesforce API 配额尤其关键）和审计日志。状态保持短暂即可，客服场景不需要跨会话记忆。

### 问：如何防止 AI Agent 通过工具调用造成破坏？

**强回答：**
采用五层纵深防御：(1) 带拒绝模式的 Schema 约束（用正则拒绝 `DROP TABLE` 等内容）；(2) 对破坏性操作设置权限闸门，Claude Code 的允许/拒绝规则可以作为参考；(3) Sandbox 隔离（Docker 只读挂载、禁止出站网络）；(4) Token 和成本上限，防止循环失控；(5) 通过 MCP Gateway 记录审计轨迹。任何单层都不够：模型可能生成恰好通过校验的幻觉参数，因此需要 Sandbox；Sandbox 也无法阻止经允许路径外传数据，因此还需要审计日志。

### 问：解释基于视觉的计算机使用与基于 API 的工具调用之间的权衡。

**强回答：**
基于 API 的方式更快（每步 50～200ms，而不是 1～3 秒）、更便宜（文本 Token，而不是图像 Token）、更可靠（确定性调用，而不是按坐标点击），也更容易测试。只要存在 API，就应优先使用。基于视觉的方式适合作为没有 API 的应用、遗留系统或跨应用工作流的后备方案。2026 年的 Zoom Action 可以降低密集 UI 中的误点击。最佳实践是：有 API 支持的 80% 任务使用 API 调用，其余 20% 使用视觉模式。

---

## 参考资料

- Anthropic：《Computer Use Tool Documentation》（2024～2026）
- Anthropic：《Model Context Protocol Specification》（2025～2026）
- MCP 2026 Roadmap：《Transport Evolution, Agent Communication, Governance》（2026）
- IBM Developer：《MCP Architecture Patterns for Multi-Agent AI Systems》（2026）
- Google Cloud：《Choose a Design Pattern for Your Agentic AI System》（2025～2026）
- Microsoft Azure：《AI Agent Orchestration Patterns》（2025～2026）
- OpenHands Documentation：《Runtime Architecture》（2025～2026）
- OpenClaw Documentation：《Architecture and SOUL.md Guide》（2025～2026）
- Open Interpreter GitHub Repository（2024～2026）
- ArXiv 2603.13417：《Design Patterns for Deploying AI Agents with MCP》（2026）

---

*上一篇：[工具使用与计算机 Agent 版图](01-tool-use-landscape.md)*
*下一章：[案例研究](../16-case-studies/)*
