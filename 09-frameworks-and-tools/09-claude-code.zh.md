# Claude Code：自主编码 Agent

Claude Code 是 Anthropic 的**终端原生自主编码 Agent**。不同于只建议补全内容的 IDE 插件，Claude Code 作为一名全栈软件工程师工作：读取代码库、编辑文件、运行命令、执行测试，并不断迭代直到任务完成。

## 目录

- [Claude Code 是什么](#what-it-is)
- [核心架构](#architecture)
- [核心工具](#tools)
- [CLAUDE.md 清单模式](#claude-md)
- [运行 Claude Code](#running)
- [子 Agent 与并行](#subagents)
- [自定义 MCP 集成](#mcp-integration)
- [安全与权限模型](#safety)
- [生产使用：CI 流水线](#production)
- [对比：Claude Code 与替代方案](#comparison)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## Claude Code 是什么

Claude Code 由 Anthropic 于 2025 年初发布，它是：

- **CLI 工具**：终端中的 `claude` 命令
- **MCP 原生 Agent**：使用 bash、text_editor 和 computer 工具
- **SDK**：可以嵌入 Python/TypeScript 应用
- **不只是聊天机器人**：自主规划、实现和验证

```
# Install
pip install claude-code  # or: npm install -g @anthropic-ai/claude-code

# Run interactively
claude

# Run headlessly (for CI)
claude -p "Add unit tests for all functions in src/utils.py" --output-format json
```

**与 Copilot/Cursor 的关键区别：**
- Copilot/Cursor：建议代码，由你接受或拒绝
- Claude Code：**自主实现完整任务**，并运行测试进行验证

---

## 核心架构

```
┌─────────────────────────────────────────────────────────┐
│                   CLAUDE CODE ARCHITECTURE               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  User Request                                           │
│       ↓                                                 │
│  ┌─────────────┐    ┌──────────────┐                   │
│  │  Claude 3.7 │    │  CLAUDE.md   │                   │
│  │   Sonnet    │ ←  │  (manifest)  │                   │
│  │ (Extended   │    └──────────────┘                   │
│  │  Thinking)  │                                       │
│  └──────┬──────┘                                       │
│         │ Tool calls                                    │
│         ↓                                               │
│  ┌──────────────────────────────────────┐              │
│  │           TOOL LAYER                 │              │
│  │  ┌─────────┐ ┌───────────┐ ┌──────┐ │              │
│  │  │  bash   │ │text_editor│ │  MCP │ │              │
│  │  └────┬────┘ └─────┬─────┘ └──┬───┘ │              │
│  └───────┼────────────┼──────────┼─────┘              │
│          │            │          │                      │
│   Shell cmds     File edits    Custom tools             │
│   (test, lint,   (read/write)  (DB, APIs,               │
│    git, build)                  internal)               │
└─────────────────────────────────────────────────────────┘
```

Claude Code 以 **Claude 3.7 Sonnet** 为基础模型，默认开启 Extended Thinking，以处理复杂的规划任务。

---

## 核心工具

Claude Code 有三个原生工具，并支持自定义 MCP 工具：

### 1. `bash`——Shell 执行

```python
# Claude calls this internally:
bash(command="pytest tests/ -v --tb=short", timeout=60)
# Returns: stdout, stderr, exit_code
```

**Claude 用它来做什么：**
- 运行测试套件（`pytest`、`jest`、`cargo test`）
- Git 操作（`git diff`、`git commit`、`git log`）
- 构建命令（`npm build`、`make`、`docker build`）
- 安装包（`pip install`、`npm install`）

bash 会话在多轮之间**持久存在**——环境变量和工作目录会在同一会话中延续。

### 2. `text_editor`——文件操作

```python
# Read a file
text_editor(command="view", path="/project/src/auth.py")

# Find in file
text_editor(command="view", path="/project/src/auth.py", view_range=[1, 50])

# Edit (surgical replacement)
text_editor(
    command="str_replace",
    path="/project/src/auth.py",
    old_str="def authenticate(user, password):",
    new_str="def authenticate(user: str, password: str) -> AuthResult:"
)

# Create new file
text_editor(command="create", path="/project/tests/test_auth.py", file_text="...")
```

**为什么外科式替换优于重写：**
- 保留文件上下文
- 减少幻觉（只修改需要修改的部分）
- 支持原子化、可审查的 diff

### 3. `computer`——GUI 自动化（可选）

完整的桌面控制（截图、鼠标、键盘），用于浏览器测试和 UI 验证。需要沙箱环境。

---

## CLAUDE.md 清单模式

`CLAUDE.md` 是高效使用 Claude Code 最重要的**单一模式**。它会把持久化的项目上下文注入每次 Claude Code 会话。

```markdown
# CLAUDE.md — Project: E-Commerce API

## Architecture
- Python 3.11 FastAPI backend
- PostgreSQL 15 with Alembic migrations
- Redis for session caching
- All API responses must be Pydantic models

## Test Commands
- Run all tests: `pytest tests/ -v`
- Run single test: `pytest tests/test_auth.py::test_login -v`
- Lint: `ruff check . --fix`
- Type check: `mypy src/`

## Coding Standards
- Always add type hints
- Never use `global` variables
- All database queries through SQLAlchemy ORM, never raw SQL
- New features require tests with >80% coverage

## Forbidden Patterns
- Do NOT use `os.system()` — use `subprocess.run()` instead
- Do NOT commit secrets — use environment variables
- Do NOT modify `alembic/versions/` — create new migrations

## Architecture Decisions
- Auth: JWT tokens, 1hr expiry, refresh token pattern
- Errors: Always return RFC 7807 Problem Details format
- Logging: structlog with JSON output, always include request_id
```

**嵌套 CLAUDE.md 文件：**
```
project/
  CLAUDE.md          # global project rules
  src/
    auth/
      CLAUDE.md      # auth-specific rules (stricter security)
    payments/
      CLAUDE.md      # payment-specific rules (PCI compliance notes)
```

Claude 在目录中工作时，会自动读取距离当前位置最近的 CLAUDE.md。

---

## 运行 Claude Code

### 交互模式

```bash
# Start session (reads CLAUDE.md automatically)
claude

# With specific model
claude --model claude-3-7-sonnet-20250219

# With MCP config
claude --mcp-config .claude/mcp.json
```

### 无头模式（用于脚本）

```bash
# Single task, JSON output
claude -p "Fix all type errors in src/" \
  --output-format json \
  --max-turns 20

# Pipe from file
echo "Refactor src/utils.py to use async/await" | claude -p -

# Stream output
claude -p "Add logging to all API endpoints" --output-format stream-json
```

### Python SDK

```python
import asyncio
from claude_code_sdk import query, ClaudeCodeOptions

async def run_coding_task(task: str) -> str:
    options = ClaudeCodeOptions(
        max_turns=30,
        allowed_tools=["bash", "str_replace_based_edit_tool"],
        system_prompt_suffix="Always run tests after making changes.",
    )
    
    messages = []
    async for message in query(prompt=task, options=options):
        messages.append(message)
    
    return messages[-1].content[0].text

result = asyncio.run(run_coding_task(
    "Add input validation to all POST endpoints in src/api/"
))
```

---

## 子 Agent 与并行

Claude Code 支持为大型代码库派发**子 Agent**：

```
Main Claude Code session
    ↓
"This codebase has 5 modules. I'll spawn sub-agents for each."
    ├── Sub-agent 1: Fix auth module tests
    ├── Sub-agent 2: Add type hints to utils/
    ├── Sub-agent 3: Migrate payments to async
    └── Sub-agent 4: Update API documentation
```

**使用子 Agent 的情况：**
- 代码库超过 50K 行
- 存在并行的独立变更（无共享状态）
- 模块级重构任务

每个子 Agent 并行运行，主 Agent 随后审查和合并结果。

---

## 自定义 MCP 集成

Claude Code 从 `~/.claude/config.json` 或 `.claude/mcp.json` 读取 MCP 服务器：

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"],
      "description": "Live library documentation"
    },
    "postgres": {
      "command": "uvx",
      "args": ["mcp-server-postgres"],
      "env": {"DATABASE_URL": "postgresql://localhost/myapp"},
      "description": "Direct DB access for schema inspection"
    },
    "jira": {
      "command": "uvx",
      "args": ["mcp-server-jira"],
      "env": {"JIRA_URL": "https://company.atlassian.net"},
      "description": "Task tracking integration"
    }
  }
}
```

使用该配置，Claude Code 可以：
1. 使用 Context7 查阅最新库文档后再写代码
2. 读取实际数据库 Schema 后再编写 SQL
3. 完成实现后把 Jira 工单标记为完成

---

## 安全与权限模型

Claude Code 采用**分层权限模型**：

```
Permission Level    Who approves       What it covers
────────────────────────────────────────────────────────
Auto               Claude (no prompt)  Read files, run tests
Ask per-turn       User confirms       Shell command execution
Explicit allow     User pre-approves   Specific commands/dirs
Blocked            Never runs          Network calls outside allowlist
```

### 配置

```json
{
  "permissions": {
    "allow": [
      "bash(pytest*)",           // Always allow test runs
      "bash(ruff*)",             // Always allow linting
      "bash(git diff*)",         // Always allow git reads
      "str_replace_based_edit_tool"  // Always allow file edits
    ],
    "deny": [
      "bash(rm -rf*)",           // Block destructive deletions
      "bash(curl https://external*)", // Block external network
      "bash(pip install*)"       // Block package installs without approval
    ]
  }
}
```

### 生产安全规则

1. **始终使用沙箱**：在 Docker 容器或 E2B 云 VM 中运行
2. **Git 隔离**：开始前创建特性分支；合并前审查 diff
3. **人工检查点**：生产部署要求人工审查最终 diff
4. **密钥扫描**：对每次 Claude Code 输出运行 `truffleHog` 或 `git-secrets`
5. **速率限制**：设置 `max_turns` 防止循环失控（建议 20～30）

---

## 生产使用：CI 流水线

### GitHub Actions 集成

```yaml
# .github/workflows/ai-fix.yml
name: AI Bug Fix
on:
  issues:
    types: [labeled]

jobs:
  ai-fix:
    if: github.event.label.name == 'ai-fix'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Claude Code
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          pip install claude-code
          
          ISSUE_BODY="${{ github.event.issue.body }}"
          
          claude -p "Fix the following bug: $ISSUE_BODY
          
          Rules:
          - Read the relevant files first
          - Make minimal changes
          - Run tests and verify they pass
          - Do not change unrelated code
          " --output-format json --max-turns 15 > result.json
      
      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v5
        with:
          title: "AI Fix: ${{ github.event.issue.title }}"
          body: "Automated fix by Claude Code"
          branch: "ai-fix/${{ github.event.issue.number }}"
```

### CI 成本模型

| 任务类型 | 平均轮数 | 平均 Token | 预估成本 |
|-----------|---------|------------|---------|
| 小型 Bug 修复 | 8 | 15K | $0.23 |
| 测试生成 | 12 | 25K | $0.38 |
| 功能实现 | 20 | 50K | $0.75 |
| 大型重构 | 30 | 100K | $1.50 |

*每天 100 次 CI 运行：根据任务构成约 75～150 美元/天。*

---

## 对比：Claude Code 与替代方案

| 特性 | Claude Code | Cursor/Windsurf | Cline | OpenHands |
|---------|-------------|-----------------|-------|-----------|
| **界面** | CLI + SDK | IDE（VS Code Fork） | VS Code 扩展 | Web UI + CLI |
| **模型** | 仅 Claude | 任意（GPT、Claude、Gemini） | 任意 | 任意 |
| **自主性** | 完整 | 中（需要点击） | 完整 | 完整 |
| **CI/无头** | ✅ 原生 | ❌ | ✅ | ✅ |
| **MCP 支持** | ✅ 原生 | ✅ | ✅ | ✅ |
| **CLAUDE.md** | ✅ | ❌（类似：.cursorrules） | ❌ | ❌ |
| **开源** | ❌ | ❌ | ✅ | ✅ |
| **最适合** | 后端开发者、CI/CD | UI/前端、视觉开发 | 任意开发者 | 自托管团队 |

### SWE-bench Verified 分数（2026 年 5 月）

| Agent | 分数 | 备注 |
|-------|-------|-------|
| GPT-5.5（原始模型领先者） | 88.7% | SWE-Bench Verified 排行榜第 1 |
| Claude Opus 4.7（原始模型） | 87.6% | SWE-Bench Pro 以 64.3% 领先 |
| Claude Code（Opus 4.7 / Sonnet 4.6） | 约 87% | Anthropic 官方 Agent |
| OpenHands + Claude Sonnet 4.6 | 约 75% | 开源框架 |
| Aider + Claude Sonnet 4.6 / GPT-5.5 | 约 74% | 开源 CLI |
| Devin（商业产品） | 约 65% | Cognition AI 产品 |
| SWE-agent + GPT-5.5 | 约 55% | Princeton 研究基线 |

---

## 面试问题

### Q：Claude Code 与 GitHub Copilot 有什么区别？

**强回答：**
Copilot 是**补全工具**——你输入时预测接下来的几行代码。Claude Code 是**自主 Agent**——你给它一个任务（例如“给这个 API 增加认证”），它会读取代码库、规划实现、编辑多个文件、运行测试、修复失败，并且只有测试通过后才完成。两者的体验有本质区别：Copilot 让你编码更快；Claude Code 在你审查输出的同时替你编码。

### Q：什么是 CLAUDE.md，为什么它很关键？

**强回答：**
CLAUDE.md 就像专门写给 AI 同事的 `README`。没有它，Claude Code 会把项目当作一个通用 Python/JS 项目；有了它，Claude 就知道确切的测试命令、禁止模式（不用原始 SQL，使用 ORM）、架构决策（JWT 认证、特定错误格式）和编码标准。它能把通用 Agent 变成**项目专家**。实践中，写得好的 CLAUDE.md 能让任务完成速度提高 2～3 倍，错误减少 60%。

### Q：如何在生产 CI 中安全运行 Claude Code？

**强回答：**
三层措施：
1. **沙箱**：在没有外部网络访问的 Docker 容器中运行 Claude Code，只开放 Git 仓库和测试运行器。
2. **权限白名单**：通过权限配置精确允许测试运行器、Lint 等 bash 命令，并阻止破坏性操作（`rm -rf`、未经审查的 `pip install`）。
3. **人工门禁**：Claude Code 输出一个带 diff 的分支。人工在 PR 中审查 diff 并合并，Claude 绝不直接合并到 main。最终决策始终保留人工判断。

### Q：如何处理高频 CI 中 Claude Code 的成本？

**强回答：**
我从三个方面优化：
1. **任务范围**：Claude Code 适合独立、边界清晰的任务（Bug 修复、测试生成），不用于开放式探索，因为探索由人工完成仍然更便宜。
2. **最大轮数**：设置 `max_turns=15`，防止失控任务因循环推理消耗超过 10 美元。
3. **模型路由**：语法错误和明显拼写错误等简单 Bug，通过 SDK 使用 Claude 3.5 Haiku，成本低 5 倍；架构重构则使用带 Extended Thinking 的 Claude 3.7 Sonnet。

---

## 参考资料

- Anthropic：《Claude Code: Building Agentic Coding Experiences》（2025）— https://docs.anthropic.com/claude-code
- Anthropic：《Claude Code SDK Documentation》— https://github.com/anthropics/claude-code
- Anthropic：《CLAUDE.md Best Practices》— https://docs.anthropic.com/claude-code/settings#claudemd
- SWE-bench Verified 排行榜 — https://www.swebench.com/

---

*下一篇：[OpenCoder / AI 编码 Agent 版图](10-opencoderguide.md)*
