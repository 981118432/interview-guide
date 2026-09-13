# Semantic Kernel

**Semantic Kernel（SK）**是微软面向企业级 AI 编排的引擎。对于坚定采用**Azure/Microsoft 生态**和 **C#/.NET** 架构的组织，它仍是主要桥梁；不过现在许多前进动力已经转移到**Microsoft Agent Framework**中（AutoGen + SK 合并后的继任者，2026 年 2 月发布 RC 1.0，2026 年第二季度 GA）。

## 目录

- [企业基因](#dna)
- [插件与规划器](#plugins)
- [记忆与连接器](#memory)
- [多语言支持（C# 与 Python）](#multi-language)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## 企业基因

LangChain 更受初创企业欢迎，而 Semantic Kernel 更受**银行和财富 500 强企业**欢迎。
- **依赖注入**：SK 遵循标准企业设计模式。
- **强类型**：对 C# 类型的一等支持，使它在大规模关键任务系统中高度可靠。
- **安全性**：深度集成 Azure Active Directory（Microsoft Entra ID）和托管身份。

---

## 插件与规划器

1. **Kernel Functions**：逻辑的基本单元（原生代码或 LLM Prompt）。
2. **插件**：函数集合（例如“GitHub 插件”或“SQL 插件”）。
3. **规划器**：SK 的规划器已经从简单 ReAct 演进到**层级规划器**，能够跨越多天协调长时间运行的业务流程。

---

## 记忆与连接器

Semantic Kernel 使用**连接器**抽象底层基础设施。
- **通用连接器**：为 OpenAI、Mistral 和本地 Onyx 模型提供统一接口。
- **向量存储抽象**：无需修改核心业务逻辑，就能在 Azure AI Search、Pinecone 和 Qdrant 之间无缝切换。

---

## 多语言支持

SK 是少数把 C# 和 Python 同等对待的主流框架之一。
- **模式**：用 Python 开发和原型验证；用 C# 部署核心编排以获得性能和类型安全。
- **逻辑共享**：使用两种语言都能工作的共享 Prompt 模板（.yaml）。

---

## 面试问题

### Q：Staff 工程师为什么会选择 Semantic Kernel 而不是 LangChain？

**强回答：**
**架构契合度**。如果组织已经建立在 .NET/Azure 技术栈上，Semantic Kernel 可以自然接入现有的 CI/CD、监控（App Insights）和安全（Entra ID）流水线。LangChain 往往像一块“外部”技术。此外，SK 的**强类型**和**依赖注入**模式可以避免大型 LangChain 项目中经常出现的“意大利面代码”。对于处理敏感金融数据的企业，Azure 原生的安全和审计集成会成为决定性因素。

### Q：Semantic Kernel 中的“函数调用”抽象是什么？

**强回答：**
SK 使用**基于插件的模型**。每个函数（原生 C# 函数或基于 LLM 的函数）都会注册到 Kernel 中。当 LLM 判断需要工具时，Kernel 会在插件注册表中查找函数，校验参数并执行它。SK 现在还支持**自动意图检测**：根据当前上下文窗口，Kernel 可以在用户开口之前主动建议可能需要的插件。

---

## 参考资料
- Microsoft Learn：《Semantic Kernel Documentation》（2025）
- Azure Architecture Center：《AI Design Patterns with Semantic Kernel》（2025）
- Build 2025：《The Future of Copilots with SK》（2025 大会回顾）

---

*下一篇：[AutoGen 与 CrewAI](07-autogen-crewai.md)*
