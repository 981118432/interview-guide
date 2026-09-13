# 应对框架变动

AI 编排框架变化的速度，超过了讲授它们的内容更新速度。LlamaIndex 和 LangChain 都在 2024 年重构了完整的包布局，并在一年内移除了原本最醒目的抽象。结果是：一门十二个月前录制的课程，第一次 `import` 就可能失败。本页讨论问题为何发生，以及如何学习和构建，让知识与代码经得起这种变动。

一句话版本：**框架是你本季度交付产品的方式，原语才是你要保留的东西。锁定前者，学习后者。**

## 目录

- [触发因素：为什么课程在全新安装中失效](#the-trigger-why-a-course-breaks-on-a-fresh-install)
- [究竟发生了什么变化](#what-actually-changed)
  - [2026 年 8 月快照](#the-august-2026-snapshot)
- [为什么课程和教程会过时](#why-courses-and-tutorials-go-stale)
- [这个教程是最新的吗？30 秒检查](#is-this-tutorial-current-a-30-second-check)
- [应对变动：锁版本、锁依赖、隔离](#surviving-churn-pin-lock-isolate)
- [框架、原始 SDK 与薄层](#framework-vs-raw-sdk-vs-thin-layer)
- [跨版本可迁移的内容](#what-transfers-across-versions)
- [必须升级时如何迁移](#migrating-when-you-must-upgrade)
- [持久学习行动手册](#a-durable-learning-playbook)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## 触发因素：为什么课程在全新安装中失效

一个常见而真实的例子：学习者开始一门口碑很好的 LlamaIndex 视频课程，复制第一个代码单元格，却遇到

```
ImportError: cannot import name 'SimpleDirectoryReader' from 'llama_index'
```

或者稍后遇到

```
TypeError: Can't instantiate abstract class OpenAI with abstract method _prepare_chat_with_tools
```

学习者和课程录制本身都没有问题。课程的 Notebook 环境锁定了旧版本（某门流行的 LlamaIndex 课程提供的 `requirements.txt` 中有 `llama-index==0.10.30` 和 `llama-index-llms-openai==0.1.26`），视频也是基于这些版本录制的。而今天全新执行 `pip install llama-index` 会得到新几个小版本的包，导入路径和类层级已经发生变化。第一个错误是导入位置移动；第二个错误是**部分版本不匹配**：核心包和集成包没有同步升级，而基类新增了旧集成包尚未实现的抽象方法。

这不是 LlamaIndex 的问题，也不是课程质量的问题，而是快速变化的框架与固定录制内容结合后的默认结果。理解机制，才能在几秒内修好而不是放弃。

---

## 究竟发生了什么变化

### 2026 年 8 月快照

版本变化不仅会破坏教程，也会让整套产品表面退役。这一时间窗口有四件事值得加入日历，而不是等运行时才发现：

| 变化 | 日期 | 含义 |
|---|---|---|
| **OpenAI Assistants API 下线** | 2026 年 8 月 26 日 | 在为期 12 个月的弃用期后从 API 中移除。替代品是 Responses API + Conversations API，且 Threads **没有自动迁移**：Assistant 需要重建为 Responses 调用，Thread 需要重新创建。仍使用 Assistants、Threads 和 Runs 的教程、图表或示例描述的是已经失效的 API |
| **OpenAI Evals Platform、Agent Builder 和 Reusable Prompts 关闭** | 2026 年 11 月 30 日 | Evals 将于 10 月 31 日变为只读。OpenAI 建议评测用户使用第三方开源工具 Promptfoo，Agent Builder 用户使用 Agents SDK。应将其理解为 OpenAI 退出托管式评测和可视化 Agent 构建，并统一到 SDK |
| **Agents SDK 默认模型变化** | 2026 年 8 月 11 日 | Python Agents SDK 0.20.0 将默认模型改成更便宜的层级。默认模型变化会让从未显式设置模型的人遇到静默行为变化，这正是不会在代码中自我提示的变化类型 |
| **可观测性整合** | 2026 年 8 月 13 日 | Dynatrace 宣布协议，将以约 9.15 亿美元收购 Arize AI。开源和供应商评测工具仍会持续整合，应选择能导出数据的工具 |

本章关于导入问题的持久教训同样适用于这里：**锁定你的依赖，并订阅关键链路上每个供应商的弃用通知**。Assistants 下线提前整整一年宣布，这意味着真正被它影响的团队是从未阅读通知的团队。

两个重构定义了现代框架变动。下面的版本号截至 2026 年 6 月准确；把它们视为快照，因为它们还会继续变化。

### LlamaIndex

- **v0.10（2024 年 2 月）：大拆分。** 单体 `llama-index` 包拆成只有抽象的 `llama-index-core`，以及数百个独立版本的集成包（`llama-index-llms-openai`、`llama-index-embeddings-*`、`llama-index-vector-stores-*`、`llama-index-readers-*`）。独立的 `llama-hub` 也被合入。导入同时发生两种变化，这正是旧 Notebook 立刻失败的原因：
  - 从顶层移到 Core：`from llama_index import VectorStoreIndex` 变为 `from llama_index.core import VectorStoreIndex`
  - 集成移到独立包：`from llama_index.llms import OpenAI` 变为 `from llama_index.llms.openai import OpenAI`
- **v0.11（2024 年 8 月）：移除旗舰抽象。** `ServiceContext`（所有 0.10 以前的教程用来连接 LLM、Embedding 和解析器的对象）在 0.10 中弃用，在 0.11 中**移除**。替代品是全局 `Settings` 对象。同一版本还把代码库迁移到 Pydantic v2。
  ```python
  # OLD (pre-0.10, removed in 0.11)
  from llama_index import ServiceContext, set_global_service_context
  service_context = ServiceContext.from_defaults(llm=llm, embed_model=embed)
  set_global_service_context(service_context)

  # CURRENT
  from llama_index.core import Settings
  Settings.llm = llm
  Settings.embed_model = embed
  ```
- **Workflows（2025 年 6 月达到 1.0，如今处于 2.x）：新的应用表面。** 事件驱动、类型化状态的 Agent 编排被提取为独立的 `llama-index-workflows` 包。很多概要会弄错一个修正点：达到 1.0、随后进入 2.x 的是 **Workflows**，核心框架仍在 0.x 线（2026 年年中 `llama-index` 约为 0.14.x），并不是“1.x”线。
- **Codemod**：`llamaindex-cli upgrade <dir>` 会自动重写旧导入。

### LangChain

- **包拆分。** `langchain-core`（Runnable、消息、基础接口，也是唯一具有向后兼容保证的包）、`langchain-community`（第三方集成）、`langchain`（链和 Agent）以及各供应商合作伙伴包（`langchain-openai`、`langchain-anthropic` 等）。LCEL 的 `|` 管道组合模型取代了旧的 `Chain` 子类。
- **v0.3（2024 年 9 月）：Pydantic v1 到 v2。** 传入 Pydantic v1 模型的用户代码会失败。
- **v1.0（2025 年 10 月）：Agent 运行在 LangGraph 上。** 构建 Agent 的推荐方式变成 `create_agent`，它运行在带中间件系统的 LangGraph 运行时上。旧链（`LLMChain`、`RetrievalQA`、`AgentExecutor`、`initialize_agent`）被移到 `langchain-classic`，已弃用但尚未删除。2026 年年中当前 `langchain` 约为 1.3.x，并要求 Python 3.10+。
- **弃用映射**：`LLMChain` → LCEL 管道（`prompt | llm | parser`）；`RetrievalQA` → `create_retrieval_chain`；`AgentExecutor` / `initialize_agent` → `create_agent`；旧版 `Memory` 类 → LangGraph 检查点。

更深的细节见[LangChain 深入理解](01-langchain-deep-dive.md)和[LlamaIndex 章节](04-llamaindex.md)。这里的重点是模式：单体拆为 Core + 插件，原来的便利抽象被移除，Agent 层转移到图运行时。两大框架大约相隔一年走过了同一条路。

---

## 为什么课程和教程会过时

录制课程和博客文章捕捉的是一个**快照**：视频以及通常会随附的锁定版 `requirements.txt` 或托管 Notebook 环境，在录制时是固定的；在线包索引不是。当学习者全新安装时，解析器会拉取已经超过锁定版本的当前版本，录制代码就不再匹配已安装的 API。

失败模式是可预测的：

- **导入移动**（`cannot import name ... from 'llama_index'`）：符号移动到了 `.core` 或合作伙伴包。
- **符号移除**（`ImportError: ServiceContext`，引用 `LLMChain` / `RetrievalQA`）：抽象被删除，而不只是移动。
- **部分升级不匹配**（`Can't instantiate abstract class ...`）：核心包和集成包没有同步；通常应一起升级这组包（`pip install -U llama-index llama-index-llms-openai`）。
- **模型名称弃用**（`gpt-3.5-turbo-0301` 不再可用）：教程锁定的模型 ID 已被供应商退役。这是同样的变动，只是发生在下一层。

多数教学平台只把版本契约编码在随附锁文件或冻结的托管环境中，而不是显眼地标注“本课程录制于版本 X”。因此，过时性要等到代码真正崩溃才会暴露。

---

## 这个教程是最新的吗？30 秒检查

在为一门课程、文章或 Notebook 投入数小时之前：

1. **结合框架发布节奏检查日期。** 2024 年的 LlamaIndex 或 LangChain 教程必然至少早于一次完整重构。
2. **打开随附的 `requirements.txt` 或锁文件，与当前版本比较锁定值。** 当前为 `0.14.x` 时仍锁定 `llama-index==0.10.x`，或使用任何 `langchain<1.0`，都意味着应预期会出错。
3. **搜索已知被移除的符号。** 它们的存在能立刻标记材料年代：
   - LlamaIndex：`ServiceContext`、`LLMPredictor`、`set_global_service_context`，或不带 `.core` 的 `from llama_index import`。
   - LangChain：`LLMChain`、`RetrievalQA`、`initialize_agent`、`AgentExecutor`。
4. **优先把项目自己的当前 Quickstart 当作事实来源**，第三方课程只用来学习概念，而不是复制粘贴代码。

---

## 应对变动：锁版本、锁依赖、隔离

防止“昨天还能用，今天就坏了”的纪律：

- **锁定精确版本。** 宽松、不带版本的 `llama-index` 是意外破坏的最大来源。至少要用 `==` 锁定直接依赖。
- **使用真正的锁文件**，同时记录传递依赖。快速变化的 2026 年首选是 [`uv`](https://docs.astral.sh/uv/)（`uv.lock`、`uv sync`）；Poetry（`poetry.lock`）和 pip-tools（`pip-compile`）也很成熟。工具无关的 `pylock.toml`（PEP 751）正在成为新标准。把 `pyproject.toml` 当成意图，把锁文件当成现实，并提交锁文件。
- **将拆分包作为一组锁定。** 对 LlamaIndex 和 LangChain 来说，Core 与每个集成包必须一起移动。“抽象类”错误正是部分升级的结果。升级整组包，而不是单个包。
- **隔离每个项目**到自己的虚拟环境或容器中。绝不安装到系统 Python。锁定 Python 基础镜像和锁文件的容器，就是托管课程 Notebook 实际使用的方式，也是本地学习者常常忽略的地方。
- **把弃用警告当作时钟，而不是噪声。** 在警告可见的情况下运行；每条警告都会指出替代品，通常还会指出移除版本。被静默的警告会让正常运行的应用在下一次例行升级时变坏。

---

## 框架、原始 SDK 与薄层

这是一个 2026 年仍然活跃的问题，因为框架最初存在的理由已经部分消失。LangChain 和 LlamaIndex 出现时，供应商 API 不一致，统一层物有所值。此后，工具/函数调用和结构化输出已经在主要供应商 SDK 中收敛为原生且相似的功能，因此框架抽象的价值下降了，而变化成本没有下降。

| 抽象高度 | 使用时机 | 成本 |
|----------|----------|------|
| **原始供应商 SDK**（`anthropic`、`openai`） | 只进行少量模型调用、希望使用最稳定表面和最清晰堆栈，或正在写库代码 | 需要自己构建检索、Agent 循环和重试 |
| **框架**（LangChain、LlamaIndex） | 需要大量集成（几十种向量存储、Loader），或需要开箱即用的 RAG/Agent 脚手架快速推进 | 依赖扩散、堆栈深、版本变化 |
| **薄层**（SDK 之上的自有接口） | 生产系统希望不改调用点就能更换模型或框架 | 需要少量前期设计 |

对于生产系统，薄层往往是最佳平衡点：依赖供应商 SDK（或仅依赖 `langchain-core`），用自己的小接口包起来，把框架细节集中在一个可替换模块中。抽象泄漏的经验法则是：一层隐藏的东西越多，而这些东西又是调试时必须理解的（检索排序、Token 预算、工具调用循环），风险就越高。正是泄漏的 Agent 抽象推动 LangChain 构建了 LangGraph。详细选择见[框架选择指南](08-framework-selection-guide.md)。

---

## 跨版本可迁移的内容

这是持久学习的核心。框架 **API** 的半衰期大约是一年；其下方**概念**的半衰期就是整个领域本身，应把投入放在概念上。

**可以迁移（深入学习）：**
- **RAG 机制**：分块策略、Embedding + 相似度搜索、检索、重排序，以及上下文相关性/有依据性/答案相关性的评测三件套。这些内容经得住 `VectorStoreIndex` 的每次改名。
- **Agent 循环**：模型调用、工具选择、工具执行、观察、重复，以及状态、记忆和人在环。无论它叫 `AgentExecutor`、`create_agent` 还是手写的 `while` 循环，循环本质都一样。
- **供应商原生原语**：工具/函数调用、结构化输出、流式处理、Token 和上下文预算。它们现在已跨供应商标准化，是最持久的一层。
- **工程纪律**：锁文件、可复现环境、阅读变更日志、评测 Harness。这些能力具有纯粹的迁移价值。

**无法迁移（不要过度投入）：**精确导入路径、类名、构造函数签名、当月的全局配置对象（`ServiceContext` 与 `Settings`），以及本季度推荐的链辅助工具（`LLMChain`、LCEL、`create_agent`）。记忆这些，就是记忆会贬值的资产。

---

## 必须升级时如何迁移

确实需要推进真实代码库时：

1. **在分支中升级，先锁文件**，一次只跨一个大版本（0.10 到 0.11 到 0.12），不要一次跨很多版本。
2. **在有官方 Codemod 时使用它**（`llamaindex-cli upgrade`），再让弃用警告和导入错误驱动工作清单。
3. **依靠桥接包**（`langchain-classic`、`llama-index-legacy`），让应用在渐进迁移期间保持运行，而不是一次性大爆炸。
4. **用评测 Harness 确认行为**，不只确认导入能解析。能编译但悄悄改变检索质量或 Agent 成功率的迁移是回归，应该在生产前被捕获。见[LLM 评测](../14-evaluation-and-observability/01-llm-evaluation.md)。

---

## 持久学习行动手册

1. **先用原始 SDK 无框架地构建一次循环**，理解框架自动化了什么。之后调试框架故障会快很多。
2. **再采用框架**来获得广度和速度，但把它的 API 视为可替换的，并置于薄接口之后。
3. **锁定一切、提交锁文件、保持弃用警告可见。**
4. **重新推导，而不是重新背诵。** 框架重命名时，把新 API 映射回它实现的原语（“`create_agent` 只是在 LangGraph 上运行的 Agent 循环”），不要从头再学。
5. **用上面的 30 秒检查审查课程时效性**后再投入。过时课程学习概念，项目当前文档学习代码。

如需经过筛选并核验时效性的课程，见 [COURSES.md](../COURSES.md)。这个文件需要注明日期并重新核验，原因正是本页讨论的框架变动。

---

## 面试问题

### Q：同事跟着一门六个月前的 LlamaIndex 教程学习，导入失败。请说明发生了什么以及你会如何修复？

**强回答：**
这门教程基于旧的锁定版本录制，而全新安装拉取了包布局已经改变的新版本。自 v0.10 起，LlamaIndex 由 `llama-index-core` 和独立集成包组成，因此 `from llama_index import SimpleDirectoryReader` 这样的顶层导入现在要改为 `from llama_index.core import SimpleDirectoryReader`；`ServiceContext` 也在 v0.11 中被移除，替代品是全局 `Settings` 对象。如果错误变成“can't instantiate abstract class OpenAI”，那就是 Core 和 OpenAI 集成包没有同步的部分升级，应该一起升级。持久解决方案是使用锁文件让环境可复现，并阅读迁移指南而不是猜。更长期地，我会让同事用项目当前 Quickstart 学代码，把教程只用于理解概念。

### Q：考虑到这些框架变化如此快，你如何决定是否使用框架？

**强回答：**
我会看框架实际上带来了什么。它最初的职责是抹平不一致的供应商 API，但工具调用和结构化输出已经在主要 SDK 中收敛，所以这部分价值变小了。需要大量集成或开箱即用脚手架来快速推进时，框架值得使用；只做少量模型调用或写库代码时，原始供应商 SDK 更稳定、更易调试。生产环境中，我通常把 SDK 放在自己的薄接口后面，让框架或模型替换只触及一个模块。无论选择什么，都锁定版本并隔离框架代码，因为我默认本季度被推荐的 API 下季度可能就会弃用。

---

## 参考资料

- LlamaIndex v0.10 迁移指南：https://developers.llamaindex.ai/python/framework/getting_started/v0_10_0_migration/
- LlamaIndex ServiceContext 到 Settings 指南：https://developers.llamaindex.ai/python/framework/module_guides/supporting_modules/service_context_migration/
- LlamaIndex Workflows 1.0 公告（2025 年 6 月）：https://www.llamaindex.ai/blog/announcing-workflows-1-0-a-lightweight-framework-for-agentic-systems
- LangChain 与 LangGraph 1.0（2025 年 10 月）：https://www.langchain.com/blog/langchain-langgraph-1dot0
- LangChain v0.3 迁移（Pydantic v2）：https://docs.langchain.com
- `uv`（锁文件与可复现环境）：https://docs.astral.sh/uv/
- PEP 751（`pylock.toml` 标准锁文件格式）：https://peps.python.org/pep-0751/

---

*下一篇：[文档处理](../10-document-processing/01-ocr-and-layout.md)*
