# 计算机使用 Agent

本页与英文原文逐段对应，保留标题层级、列表、表格、代码、公式、链接和面试问答。

计算机使用 Agent 让 LLM 像人一样查看屏幕、推理并通过鼠标点击和键盘输入执行操作。模型不再调用结构化 API，而是直接处理原始像素。本章介绍其工作方式、优于传统自动化的场景，以及围绕它们设计生产系统的方法。

## 目录

- [什么是计算机使用 Agent？](#what-are-computer-use-agents)
- [截图—推理—行动循环](#the-screenshot-reason-act-loop)
- [Claude Computer Use：工具与 API](#claude-computer-use-tools-and-api)
- [架构：Sandbox 环境](#architecture-sandboxed-environments)
- [浏览器自动化与桌面自动化](#browser-vs-desktop-automation)
- [与传统自动化比较](#comparison-with-traditional-automation)
- [计算机使用何时优于 API 调用](#when-computer-use-beats-api-calls)
- [错误处理与恢复](#error-handling-and-recovery)
- [性能：延迟、成本、吞吐量](#performance-latency-cost-throughput)
- [真实世界应用](#real-world-applications)
- [安全考虑](#security-considerations)
- [代码示例](#code-examples)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## 什么是计算机使用 Agent？

计算机使用 Agent 是一种 LLM：它理解截图并发出低层输入命令（鼠标移动、点击、按键）控制图形界面，在人机交互循环中承担原本由人工完成的操作。

```
Traditional Tool Use:           Computer Use:

User Request                    User Request
     |                               |
     v                               v
 LLM reasons                    LLM reasons
     |                               |
     v                               v
 Structured API call             Screenshot captured
 {"tool": "search",                  |
  "query": "..."}                    v
     |                          LLM sees pixels, finds button
     v                               |
 API returns JSON                    v
     |                          Mouse click at (x=340, y=220)
     v                               |
 LLM formats answer                  v
                                New screenshot captured
                                     |
                                     v
                                LLM verifies result, continues...
```

关键区别是：传统工具使用依赖预先定义且 Schema 已知的 API；计算机使用适用于任何拥有可视化界面的应用，不需要 API。

### 2026 年版图

如今已有多家供应商提供计算机使用能力：

| 供应商 | Agent | 方法 | 主要优势 |
|----------|-------|----------|--------------|
| Anthropic | Claude Computer Use | 视觉 + 坐标推理 | 桌面 + 浏览器，API 成熟 |
| OpenAI | ChatGPT Agent Mode | 基于 Operator 的浏览器 Agent | 深度网页导航 |
| Google | Project Mariner | Gemini 视觉语言模型 | Chrome 集成 |
| Microsoft | UFO/UFO2 | Windows UI 自动化 + 视觉 | 原生 Windows 支持 |
| Amazon | Nova Act | 专用浏览器模型 | 电商工作流 |

---

## 截图—推理—行动循环

每个计算机使用 Agent 都遵循相同的核心循环，通常称为“Agent 循环”或“行动循环”：

```
+------------------+
|  Capture Screen  |<-----------+
+--------+---------+            |
         |                      |
         v                      |
+------------------+            |
|  Send to LLM     |            |
|  (screenshot +   |            |
|   task context)  |            |
+--------+---------+            |
         |                      |
         v                      |
+------------------+            |
|  LLM Reasons     |            |
|  about next      |            |
|  action           |           |
+--------+---------+            |
         |                      |
    +----+----+                 |
    |         |                 |
    v         v                 |
 [Action]  [Done]               |
    |                           |
    v                           |
+------------------+            |
| Execute Action   |            |
| (click, type,    |            |
|  scroll, key)    |            |
+--------+---------+            |
         |                      |
         +----------------------+
```

每次迭代包括：
1. **截取**：截取当前显示状态的屏幕截图。
2. **发送**：将截图（Base64 图像）和对话历史一起传给 LLM。
3. **推理**：模型分析屏幕内容，确定朝目标前进的下一步。
4. **行动**：模型输出工具调用（例如 `click at (450, 320)`），由运行时执行。
5. **重复**：重新截取屏幕，持续循环，直到模型发出完成信号。

模型通过不断累积截图和动作的对话历史在迭代间保持上下文，这相当于对已发生事件的视觉“记忆”。

---

## Claude Computer Use：工具与 API

Claude 提供三个内置的计算机使用工具。这些工具由 Anthropic 定义，开发者无需自行实现；Claude 知道如何生成调用，运行时则负责在环境中执行。

### 三类工具

**1. `computer`——完整 GUI 控制**

在虚拟显示器上控制鼠标和键盘。能力包括：
- `screenshot`——截取当前屏幕状态
- `left_click`、`right_click`、`double_click`、`triple_click`——在指定坐标点击鼠标
- `left_click_drag`——从一个点拖动到另一个点
- `type`——输入字符串
- `key`——按下键盘按键（例如 `ctrl+c`、`Return`、`Escape`）
- `scroll`——在指定坐标向上/下/左/右滚动
- `move`——将光标移动到指定坐标
- `hold_key`——执行其他动作时按住修饰键
- `wait`——暂停指定时长

**2. `bash`——Shell 命令执行**

在持久会话中运行 Shell 命令：
- 命令共享状态（环境变量、工作目录）
- 支持多行脚本
- 捕获输出并以文本返回

**3. `text_editor`——文件操作**

通过命令进行结构化文件编辑：
- `view`——读取文件内容（可指定行范围）
- `create`——创建带内容的新文件
- `str_replace`——将文件中的特定字符串替换掉（匹配必须唯一）
- `insert`——在指定行号插入文本

### API 请求结构

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    tools=[
        {
            "type": "computer_20250124",
            "name": "computer",
            "display_width_px": 1280,
            "display_height_px": 800,
            "display_number": 1
        },
        {
            "type": "bash_20250124",
            "name": "bash"
        },
        {
            "type": "text_editor_20250124",
            "name": "str_replace_based_edit_tool"
        }
    ],
    messages=[
        {
            "role": "user",
            "content": "Open Firefox, navigate to github.com, and find repos trending today."
        }
    ],
    betas=["computer-use-2025-01-24"]
)
```

响应会包含 `tool_use` 块，运行时必须执行这些调用，并将结果作为 `tool_result` 消息反馈。

---

## 架构：Sandbox 环境

计算机使用 Agent 必须运行在隔离环境中。模型拥有完整的鼠标和键盘控制权，不能让它直接运行在生产工作站上。

### 标准架构：Docker + VNC

```
+-----------------------------------------------------+
|  Docker Container                                   |
|                                                     |
|  Xvfb (Virtual X11) + Mutter (WM) + Tint2 (Panel)  |
|         |                                           |
|         v                                           |
|  +------------------+     +-------------------+     |
|  | Virtual Desktop  |---->| Screenshot Capture|     |
|  | 1280x800         |     | (scrot/maim)      |     |
|  | Firefox, apps    |     +--------+----------+     |
|  +------------------+              |                |
|                                    v                |
|                           +--------+----------+     |
|                           | Agent Runtime     |     |
|                           | - Calls Claude API|     |
|                           | - Executes actions|     |
|                           | - Manages loop    |     |
|                           +-------------------+     |
+-----------------------------------------------------+
```

### 云托管替代方案

E2B（e2b.dev）等服务提供预配置的 Sandbox 环境：
- 预装浏览器和工具的临时 VM
- 用于截取屏幕和注入输入的 API
- 会话结束后自动清理
- 无需承担 Docker 管理开销

### 环境关键组件

| 组件 | 用途 | 示例 |
|-----------|---------|---------|
| Xvfb | 虚拟 X11 显示服务器 | 无需物理显示器即可创建帧缓冲 |
| Mutter/Xfwm | 窗口管理器 | 处理窗口定位和大小调整 |
| Tint2 | 任务面板 | 显示正在运行的应用 |
| xdotool | 输入注入 | 执行鼠标/键盘命令 |
| scrot/maim | 屏幕截取 | 将显示内容保存为 PNG 快照 |

---

## 浏览器自动化与桌面自动化

| 维度 | 仅浏览器 | 完整桌面 |
|-----------|-------------|--------------|
| 范围 | 仅 Web 应用 | 任意 GUI 应用 |
| 配置复杂度 | 较低（无头浏览器） | 较高（完整桌面环境） |
| 性能 | 更快（截图更小） | 更慢（截取完整屏幕） |
| 可靠性 | 更高（布局可预测） | 更低（受操作系统差异影响） |
| 用例 | Web 抓取、表单填写 | 遗留软件、跨应用工作流 |

浏览器自动化控制 Web 浏览器（导航、填写表单、点击按钮、处理 SPA）；桌面自动化控制完整操作系统环境（启动应用、使用原生对话框、操作厚客户端软件，以及串联多个应用中的操作）。

---

## 与传统自动化比较

Selenium、Playwright 和 Puppeteer 通过直接访问 DOM 自动化浏览器；计算机使用 Agent 则处理像素。两者都适合生产环境中的不同场景。

| 特性 | Selenium/Playwright | 计算机使用 Agent |
|---------|--------------------|--------------------|
| 速度 | 快（直接操作 DOM） | 慢（截图 + LLM） |
| 可靠性 | 脆弱（选择器变化会失效） | 有韧性（视觉识别） |
| 维护 | 持续更新选择器 | 较少（适应 UI 变化） |
| 反爬检测 | 经常被阻断 | 更难被检测 |
| 每次动作成本 | 约 $0.001 | 约 $0.01～0.05 |
| 非 Web 支持 | 否 | 是（任意 GUI） |

**混合方案**在生产中效果最好：Playwright 处理高吞吐、定义明确的流程（登录、导航），计算机使用 Agent 处理动态且不可预测的步骤（视觉校验、新布局、反爬站点）。

---

## 计算机使用何时优于 API 调用

**使用计算机使用的情况：**没有 API（遗留系统）、反爬机制阻止 Selenium、需要视觉判断（图表校验、PDF 布局）、UI 变化速度超过选择器维护能力，或工作流跨越多个桌面应用。

**坚持使用 API 的情况：**存在结构化 API（始终优先）、延迟要求高（亚秒级）、吞吐量大（每小时数千次动作），或需要确定性（相同输入得到相同输出）。

---

## 错误处理与恢复

计算机使用 Agent 的失败方式不同于基于 API 的工具，主要失败模式包括：

### 1. 误点击（坐标错误）

模型根据截图计算坐标，但可能偏差几个像素：
- **缓解**：每次点击后使用 `screenshot`，确认预期状态确实发生变化。
- **恢复**：如果点错了元素，模型可以根据新状态推理并纠正方向。

### 2. 过期截图

屏幕可能在截取和执行动作之间发生变化（动画、弹窗、加载）：
- **缓解**：截图前短暂等待；页面加载时使用 `wait` 动作。
- **恢复**：重新截图并重新评估后再继续。

### 3. 无限循环

模型重复同一动作却没有进展：
- **缓解**：设置最大迭代次数（例如每个任务最多 50 个动作）。
- **恢复**：连续重复相同动作 N 次后，强制采用不同方案或升级给人工处理。

### 4. 意外对话框

Cookie 横幅、弹窗和权限对话框可能意外出现：
- **缓解**：在系统 Prompt 中加入处理常见对话框的指令。
- **恢复**：模型通常可以通过视觉推理自然处理这些情况——看到对话框后将其关闭。

### 5. 分辨率与缩放不匹配

模型是在特定分辨率上训练的，分辨率不匹配会导致坐标错误：
- **缓解**：使用推荐分辨率（1280x800），显示缩放设为 100%。
- **恢复**：调整 `display_width_px` 和 `display_height_px`，使其匹配实际显示器。

### 错误处理模式

Agent 循环应跟踪动作历史并检测重复。如果连续输出相同动作达到 3 次，就注入消息要求模型尝试不同方案。始终设置硬性最大迭代次数（例如 50 次），并在每次动作后截取校验截图，以检测状态变化。下面的“代码示例”部分给出了完整 Agent 循环。

---

## 性能：延迟、成本、吞吐量

### 延迟拆解

Agent 循环的每次迭代包括：

```
Screenshot capture:     ~100ms
Image encoding (base64): ~50ms
API call (with image):   ~2-5s  (model inference)
Action execution:        ~100ms
                        --------
Total per action:        ~2.5-5.5s
```

典型的 10 步任务需要 25～55 秒；相比之下，Playwright 完成同样 10 步通常不到 2 秒。

### 单动作成本

每个动作都会发送一张截图（约 800KB 的 Base64）以及对话历史：

| 模型 | 每次动作成本（约） | 备注 |
|-------|-------------------------|-------|
| Claude Sonnet 4 | $0.01～0.03 | 大多数任务推荐 |
| Claude Opus 4 | $0.05～0.15 | 用于复杂视觉推理 |

20 步工作流使用 Sonnet 的成本约为 $0.20～0.60，使用 Opus 约为 $1.00～3.00。

### 吞吐优化

- **并行会话**：运行多个 Docker 容器并发处理任务。
- **选择性截图**：只在不确定动作后截图，输入文本后跳过截图。
- **降低分辨率**：使用 1024x768 而不是 1920x1080，以降低 Token 成本。
- **提前终止**：让模型在确认目标完成后立即发出完成信号。

---

## 真实世界应用

| 应用 | 工作方式 | 为什么使用计算机使用 |
|------------|--------------|------------------|
| 遗留系统集成 | Agent 导航主机/厚客户端 UI，将数据提取为结构化格式 | 遗留软件没有 API |
| 表单填写 / 数据录入 | 读取源文档，逐字段填写 Web 表单，处理多页向导 | 政府门户、条件逻辑复杂的保险理赔 |
| QA 与视觉测试 | 像用户一样导航应用，校验视觉渲染，用自然语言报告问题 | 超越像素差异比较，理解布局和 UX |
| 竞品情报 | 浏览产品页面，从 JS 渲染的小组件抓取价格数据 | 能处理阻挡传统抓取器的网站 |

---

## 安全考虑

| 风险 | 会发生什么 | 缓解措施 |
|------|-------------|------------|
| **可见机密** | 模型在截图中看到密码、会话和通知 | 使用临时容器，用后清除凭证 |
| **不受限动作** | Agent 可以运行 Shell 命令、任意导航和下载文件 | 防火墙规则、只读文件系统、会话时间限制，破坏性操作需要 HITL |
| **数据外传** | 发给 LLM 供应商的截图包含敏感数据 | 受监管行业采用本地部署，遮盖敏感 UI 字段 |
| **通过 UI 注入 Prompt** | 恶意网站显示文本操纵 Agent | 在系统 Prompt 中警告不要遵循与任务冲突的屏幕指令 |

首要规则是：除非位于完整 Sandbox 容器中，否则**绝不要**让计算机使用 Agent 运行在生产工作站上，或让它接触真实凭证。

---

## 代码示例

### 最小 Agent 循环

```python
import anthropic, base64, subprocess

client = anthropic.Anthropic()

def capture_screenshot():
    subprocess.run(["scrot", "/tmp/screen.png", "-o"], check=True)
    with open("/tmp/screen.png", "rb") as f:
        return base64.standard_b64encode(f.read()).decode()

def execute_action(action):
    name = action["action"]
    if name == "left_click":
        x, y = action["coordinate"]
        subprocess.run(["xdotool", "mousemove", str(x), str(y), "click", "1"])
    elif name == "type":
        subprocess.run(["xdotool", "type", "--", action["text"]])
    elif name == "key":
        subprocess.run(["xdotool", "key", action["text"]])

def run_agent(task: str, max_steps: int = 30):
    messages = [{"role": "user", "content": task}]
    tools = [
        {"type": "computer_20250124", "name": "computer",
         "display_width_px": 1280, "display_height_px": 800},
        {"type": "bash_20250124", "name": "bash"},
        {"type": "text_editor_20250124", "name": "str_replace_based_edit_tool"},
    ]
    for step in range(max_steps):
        response = client.messages.create(
            model="claude-sonnet-4-20250514", max_tokens=4096,
            tools=tools, messages=messages, betas=["computer-use-2025-01-24"],
        )
        if response.stop_reason == "end_turn":
            return [b.text for b in response.content if b.type == "text"]

        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            if block.name == "computer":
                execute_action(block.input)
                tool_results.append({
                    "type": "tool_result", "tool_use_id": block.id,
                    "content": [{"type": "image", "source": {
                        "type": "base64", "media_type": "image/png",
                        "data": capture_screenshot()}}],
                })
            elif block.name == "bash":
                r = subprocess.run(block.input["command"],
                    shell=True, capture_output=True, text=True)
                tool_results.append({
                    "type": "tool_result", "tool_use_id": block.id,
                    "content": r.stdout + r.stderr,
                })
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})
    return ["Max steps reached"]
```

### Dockerfile for Sandboxed Environment

```dockerfile
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y \
    xvfb mutter tint2 xdotool scrot firefox-esr python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*
RUN pip3 install anthropic
ENV DISPLAY=:1
COPY agent.py /agent.py
CMD Xvfb :1 -screen 0 1280x800x24 & sleep 1 && mutter & tint2 & \
    sleep 1 && python3 /agent.py
```

---

## 面试问题

### Q：客户每天有 500 份保险理赔 PDF，需要录入没有 API 的遗留 Web 门户。请使用计算机使用 Agent 设计系统。

**强回答：**我会构建三阶段流水线。第一阶段用 LLM 从 PDF 抽取结构化数据（理赔号、申请人姓名、金额、日期）。第二阶段为每份理赔启动运行在隔离 Docker 容器和虚拟显示器中的 Claude Computer Use Agent，导航门户并填入字段，提交后截取确认截图。第三阶段用独立 LLM 调用将确认截图与预期数据比较，发现录入错误。

为了扩展规模，我会并行运行 10～20 个容器，每个容器按顺序处理理赔。按 Agent 每份理赔约 2 分钟计算，20 个容器每天 8 小时可以处理 600 份。我会为重试 3 次后仍失败的理赔增加死信队列，并交给人工复核。

按每份理赔 $0.50（约 20 个动作、每个动作 $0.025）计算，500 份每天成本为 $250，可能低于它所替代的人工录入团队成本。

### Q：比较计算机使用 Agent 与 Selenium 的 Web 自动化。分别何时选择？

**强回答：**
Selenium 直接操作 DOM，快速、确定且便宜，但选择器变化时会失效，可能被反爬系统阻挡，也无法处理需要视觉判断的任务。

计算机使用 Agent 每个动作慢约 100 倍、贵约 10 倍，但它处理的是像素而非选择器，因此能适应 UI 变化；它能生成更像人的交互模式，也能理解视觉布局，例如确认图表是否正确渲染，或读取 Selenium 无法检查的 Canvas 内容。

目标站点由我控制、流程稳定且量大时选 Selenium；一次性任务、频繁变化的第三方站点、跨应用桌面流程，以及维护选择器的人力成本超过 LLM 推理成本时选计算机使用 Agent。

最佳生产系统会结合两者：Playwright 处理可预测步骤（认证、导航），计算机使用 Agent 处理动态步骤（解读结果、做判断）。

---

## 参考资料

- Anthropic. "Computer Use Tool" API Documentation (2025)
- Anthropic. "Bash Tool" and "Text Editor Tool" API Documentation (2025)
- E2B. "Sandboxed Cloud Environments for AI Agents" (2025)
- OSWorld Benchmark: Desktop Agent Evaluation Suite (2025)
- WebArena Benchmark: Web Agent Evaluation Suite (2024)

---

*下一篇：[构建工具使用 Agent](05-building-tool-agents.md)*
