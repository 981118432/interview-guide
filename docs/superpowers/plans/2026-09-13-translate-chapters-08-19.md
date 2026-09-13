# Chapters 08-19 Translation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将源仓库 08～19 的 63 篇英文详情逐段翻译为中文详情，并为每篇生成中文概要，复制到当前 `interview-guide` 仓库，扩展 Reader，完成结构校验后提交并推送。

**Architecture:** `ai-system-design-guide` 只读作内容源；`interview-guide` 是唯一写入、提交和推送的目标仓库。每篇文档保留英文的标题层级、列表、表格形状、代码块、公式、链接、URL、面试问答和参考资料，中文详情与概要使用同名 `.zh.md` / `.summary.md` 配对。Reader 继续由 `00-interview-prep/build_reader.py` 生成静态 `reader.html`。

**Tech Stack:** Markdown、Python 3 标准库 Reader 构建脚本、Git、GitHub SSH remote。

**Spec:** 当前用户请求与项目级 `AGENTS.md`；源内容位于 `ai-system-design-guide/08-*` 至 `19-*`。

## Global Constraints

- 源仓库 `ai-system-design-guide` 不提交、不推送。
- 目标仓库固定为 `/Users/zhangshuaishuai/Desktop/MyNote/AIAgent/interview-guide`。
- 每个英文源文档必须有同名 `.zh.md` 和 `.summary.md`。
- 中文详情必须逐段对应英文，保留标题层级、列表、表格、代码、公式、链接、URL、面试问答和参考资料。
- 翻译涉及用户经历时遵循项目背景提示词，不编造生产经验、数字或职责。
- Reader 必须包含英文详情、中文详情、中文概要三个分页，以及 08～19 左侧目录分组。

---

### Task 1: 复制并翻译 08 · Memory and State

**Files:**
- Read: `ai-system-design-guide/08-memory-and-state/*.md`
- Create: `interview-guide/08-memory-and-state/*.zh.md`
- Create: `interview-guide/08-memory-and-state/*.summary.md`

- [ ] 为 6 篇英文文档创建逐段中文详情。
- [ ] 为 6 篇文档生成与中文详情标题及核心内容一致的概要。
- [ ] 校验 6 篇的结构签名与链接目标。

### Task 2: 翻译 09 · Frameworks and Tools

**Files:**
- Read: `ai-system-design-guide/09-frameworks-and-tools/*.md`
- Create: `interview-guide/09-frameworks-and-tools/*.zh.md`
- Create: `interview-guide/09-frameworks-and-tools/*.summary.md`

- [ ] 完成 12 篇中文详情和 12 篇概要。
- [ ] 保留框架 API、命令、代码块、比较表和面试问答。
- [ ] 校验 12 篇结构签名与链接目标。

### Task 3: 翻译 10～12 · Document Processing、Infrastructure、Security

**Files:**
- Read: `ai-system-design-guide/10-document-processing/*.md`
- Read: `ai-system-design-guide/11-infrastructure-and-mlops/*.md`
- Read: `ai-system-design-guide/12-security-and-access/*.md`
- Create: corresponding target `.zh.md` and `.summary.md` files.

- [ ] 完成 10～12 的 7 篇中文详情和概要。
- [ ] 保留文档解析、基础设施、MLOps、鉴权和安全技术细节。
- [ ] 逐目录校验配对文件、代码、公式、链接和表格形状。

### Task 4: 翻译 13～15 · Reliability、Evaluation、Design Patterns

**Files:**
- Read: `ai-system-design-guide/13-reliability-and-safety/*.md`
- Read: `ai-system-design-guide/14-evaluation-and-observability/*.md`
- Read: `ai-system-design-guide/15-ai-design-patterns/*.md`
- Create: corresponding target `.zh.md` and `.summary.md` files.

- [ ] 完成 13～15 的 9 篇中文详情和概要。
- [ ] 保留可靠性、安全、评测、可观测性和设计模式的面试问答。
- [ ] 逐目录校验结构签名、原始 URL 和 Markdown 链接目标。

### Task 5: 翻译 16 · Case Studies

**Files:**
- Read: `ai-system-design-guide/16-case-studies/*.md`
- Create: `interview-guide/16-case-studies/*.zh.md`
- Create: `interview-guide/16-case-studies/*.summary.md`

- [ ] 完成 20 篇案例文档的逐段中文详情。
- [ ] 为每篇案例生成与原文场景、架构、指标、权衡和面试问答一致的概要。
- [ ] 对涉及用户经历的表述使用“示例/可迁移经验”边界，不将案例冒充用户实际经历。
- [ ] 校验 20 篇的结构签名、代码、公式、链接和 URL。

### Task 6: 翻译 17～19 · Computer Agents、Voice、Multimodal Generation

**Files:**
- Read: `ai-system-design-guide/17-tool-use-and-computer-agents/*.md`
- Read: `ai-system-design-guide/18-voice-and-audio-agents/*.md`
- Read: `ai-system-design-guide/19-multimodal-generation/*.md`
- Create: corresponding target `.zh.md` and `.summary.md` files.

- [ ] 完成 9 篇中文详情和概要。
- [ ] 保留工具调用、计算机使用、语音音频、多模态生成的代码、公式、链接和面试问答。
- [ ] 校验 9 篇结构签名和概要标题对应关系。

### Task 7: 扩展 Reader 到 08～19

**Files:**
- Modify: `interview-guide/00-interview-prep/build_reader.py`
- Regenerate: `interview-guide/00-interview-prep/reader.html`

- [ ] 添加 08～19 的目录分组和中文文档标签。
- [ ] 生成所有已有与新增文档的三分页 Reader。
- [ ] 确认新增 63 篇文档全部出现在 Reader，左侧目录分组和分页标签完整。

### Task 8: 全量校验、提交和推送

**Files:**
- Verify: target sections `00-interview-prep` through `19-multimodal-generation`
- Commit: target Git repository only

- [ ] 校验 08～19 的源文档、中文详情、概要一一配对。
- [ ] 校验中文详情的标题层级、列表/表格形状、代码块、公式、链接目标、原始 URL、面试问答和参考资料。
- [ ] 运行 Reader 生成与静态内容检查，运行 `git diff --check`。
- [ ] 确认目标仓库工作区和远端分支状态后提交。
- [ ] 推送 `interview-guide` 的 `main`，并用远端 commit SHA 复核。
