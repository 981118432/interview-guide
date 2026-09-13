# 基准测试与排行榜

本页与英文原文逐段对应，保留标题层级、列表、表格、代码、公式、链接和面试问答。

公开基准是行业讨论模型能力的共同语言，例如 MMLU、SWE-bench、GPQA 和 Arena Elo。它们适合建立方向感，却可能误导决策。本章说明各主要基准衡量什么、哪些仍能区分前沿模型、哪些已经饱和，以及如何批判性阅读基准声明，避免被单个数字欺骗。

最重要的观点是：**基准的定义和已知缺陷相对稳定，分数却会过期。**排行榜数字每周都可能变化，还会受到数据污染和有利 Harness 的抬高，并越来越多地混入虚构条目。因此本页优先说明每个基准*衡量什么*以及*如何失效*，具体分数只作为带日期、带来源且需要重新核验的快照。若要评测真正预测生产质量的自有系统，请参阅[LLM 评测](01-llm-evaluation.md)。

## 目录

- [如何阅读本页](#how-to-read-this-page)
- [能力地图](#the-capability-map)
  - [通识与语言](#general-knowledge-and-language)
  - [前沿推理](#frontier-reasoning)
  - [数学](#mathematics)
  - [编码](#coding)
  - [Agent 与工具使用](#agentic-and-tool-use)
  - [长上下文](#long-context)
  - [多模态](#multimodal)
  - [事实性与指令遵循](#factuality-and-instruction-following)
  - [人类偏好](#human-preference)
- [批判性阅读基准](#reading-benchmarks-critically)
  - [饱和](#saturation)
  - [污染](#contamination)
  - [Harness 与脚手架差异](#harness-and-scaffold-variance)
  - [排行榜幻觉](#the-leaderboard-illusion)
  - [从基准到生产的差距](#the-benchmark-to-production-gap)
  - [综合指数](#composite-indices)
- [实践检查清单](#a-practical-checklist)
- [2026 年哪些基准重要](#which-benchmarks-matter-in-2026)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## 如何阅读本页

下面每个基准都会列出**衡量内容**、**格式**、**饱和状态**（前沿模型是否聚集在高位，以至于分数差异只是噪声）和**已知缺陷**。如果当前分数对建立方向感有帮助，会附上来源和“需核验”标记，原因是：

- **供应商自报分数高于独立排行榜。**实验室会在找到的最佳 Harness、最佳推理力度和不限额基础设施上报告模型成绩。这个数字不能与另一家实验室或独立运行的数字比较；只能比较由**同一 Harness** 产生的数字。
- **2026 年的网络充斥着虚构排行榜页面。**如果一个你不认识的模型被标注为前沿编码高分，在模型实验室文章或基准官方榜单等一手来源确认前，应先视为 SEO 垃圾内容。
- **标题数字隐藏了 Harness。**没有 Agent 脚手架、工具权限、推理力度和输出 Token 上限，“SWE-bench 88%”没有可解释性。

因此，应根据“衡量内容”和“缺陷”两列理解基准，把任何单一百分比视为带日期的数据点，而不是事实。

---

## 能力地图

基准按所探测的能力分组。每个组内，行业会持续淘汰已饱和基准并换成更难的后继基准，因此真正能拉开差距的基准每年都会变化。

### 通识与语言

大多已经**饱和**：前沿模型集中在 88～90% 以上，分数差异主要是噪声。应把它们作为历史基线，而不是区分前沿模型的依据。

| 基准 | 衡量内容 | 状态 | 说明 |
|-----------|----------|--------|-------|
| **MMLU** | 57 个学科的选择题学术知识（约 1.59 万题） | 已饱和（约 90% 以上聚集） | 历史上引用最多的基准。约 6.5% 题目存在标签错误（MMLU-Redux）；网络污染严重，已逐渐从模型卡中退出。 |
| **MMLU-Pro** | 更难的 MMLU 后继版本：从 4 个选项增加到 10 个，强调推理，约 1.2 万题 | 接近饱和 | 为解决 MMLU 饱和而构建，但现在也触及相同上限（顶部分数约 88～90%），已因饱和从 Artificial Analysis 指数中移除。 |
| **MMLU-Redux** | 修正错误后的 MMLU 重标注（约 3000 题） | 已饱和 | 用于**量化** MMLU 的错误率（发现 6.49% 错误，部分子集最高 57%），不是用于给前沿模型排名。 |
| **HellaSwag** | 常识句子补全 | 完全饱和（95% 以上） | 人类基线约 95%，GPT-4 时代以来基本解决。 |
| **ARC-Challenge** | 小学科学选择题 | 已饱和（约 96% 以上） | 基本已经解决。 |
| **WinoGrande** | Winograd 模式指代消解/常识 | 已饱和（约 90% 以上） | 剩余差异主要来自标注伪影。 |
| **BBH (BIG-Bench Hard)** | BIG-Bench 中最难的 23 项任务，多步推理 | 使用 CoT 后饱和（>90%） | 已被 **BIG-Bench Extra Hard（BBEH）**取代，后者正是因为 BBH 饱和而构建。 |
| **GLUE / SuperGLUE** | 较早的 NLU 任务套件 | 退役 | 2021 年初模型已经超过 SuperGLUE 人类基线。 |

### 前沿推理

以下基准仍能区分行业顶尖模型，按剩余提升空间大致排序。

| 基准 | 衡量内容 | 状态 | 说明 |
|-----------|----------|--------|-------|
| **HLE (Humanity's Last Exam)** | 覆盖 100 多个学科、抗检索的封闭式专家问题（约 2500 题，约 10% 多模态） | 活跃、区分度宽 | 当前最重要的前沿知识基准。不使用工具时分数约为 40～53%，差距仍可读；2025 年 1 月发布时 SOTA 低于 10%，说明前沿进展很快。注意工具/无工具配置会抬高并混淆比较。 |
| **GPQA-Diamond** | 198 道博士级生物、物理、化学问题，设计为 Google 无法直接搜到答案 | 向饱和收缩 | 设计目标是让有网络的优秀非专家得分约 34%，博士专家得分约 65～70%。当前前沿聚集到 92～94%，作为顶尖模型区分器的作用减弱，但仍能区分中档模型，是不错的 sanity check。 |
| **ARC-AGI-2** | 抽象网格谜题推理，考虑效率（约 400 题），抵抗记忆 | 活跃、区分度强 | **务必仔细阅读：**人类评审组通过率为 85%，85% 是大奖**门槛**。聚合站称前沿模型“达到 85%”，但这是供应商在非 ARC-Prize Harness、使用大量测试时计算后自报的数字。ARC-Prize-Verified 上限低得多（高成本时约在 50% 中段），不要把门槛当作已实现分数。 |
| **FrontierMath** | 研究级数学，专家需要数小时到数天解决（约 350 题，私有；Tier 4 最难） | 活跃但快速上升 | 开放式题目，答案可自动验证且不易猜中。v1 约 42% 题目有错误（已在 2026 年 6 月 v2 修复）；部分由 OpenAI 资助，因此单实验室数字需要治理层面的保留。Epoch 自己认为低于 70% 才是可达到范围，应警惕远高于此的聚合分数。 |
| **CritPt** | 50 多位物理学家构建的 11 个领域研究级物理推理 | 活跃、上限很低 | 多数前沿模型在完整挑战上的得分从个位数到约 45%，因此区分度清晰。它较新（2025 年末），正成为科学推理的标准组成部分。 |

### 数学

经典数学基准基本已经解决；当前有区分度的是最新竞赛年份和研究级数据集。

| 基准 | 衡量内容 | 状态 | 说明 |
|-----------|----------|--------|-------|
| **GSM8K** | 小学文字题 | 已饱和（>95%） | GSM-Symbolic 表明扰动数字或从句后分数会下降，说明高分部分来自记忆。 |
| **MATH / MATH-500** | 竞赛数学（AMC/AIME 级别） | 已饱和（顶部分数约 99%） | MATH-500 是 500 题子集，规模小导致顶部分数方差很大。 |
| **AIME（2024/2025/2026）** | 奥赛简答题，整数答案，每年 30 题 | 第 N 年公开后即饱和 | 在公开前每年题目都是新题、污染较低，因此有价值；但每年只有 30 题，单年分数方差大，应优先看平均运行结果。2024/2025 已饱和。 |
| **HMMT、Putnam** | 更难的奥赛/本科证明竞赛 | Putnam 证明题尚未饱和 | 证明评分依赖 LLM 评审，直接给最终答案的捷径会高估真正的证明能力。 |

### 编码

代码片段基准已经不适合排序；Agent 和仓库级基准才是更有生产意义的信号。

| 基准 | 衡量内容 | 状态 | 说明 |
|-----------|----------|--------|-------|
| **HumanEval / HumanEval+ / MBPP / MBPP+** | 根据文档字符串生成单函数，再用单元测试检查 | 已饱和（前沿约 90～97%） | 规模很小且自 2021 年公开，容易污染。HumanEval+ 增加约 80 倍测试来捕获脆弱代码；+ 版本分数下降说明原测试太弱，让错误代码也通过。不要用它给前沿模型排名。 |
| **SWE-bench Verified** | 修复真实 GitHub Issue，使隐藏测试通过（人工验证的 500 个 Issue 子集） | 接近饱和、存在污染 | 2024～2026 年最常引用的编码数字，但 OpenAI 评测团队指出超过 60% 任务的测试有缺陷，且可以根据任务 ID 原样复现解法。适合做“超过约 80% 即属前沿”的层级筛选，不适合精细排名；仅 Harness 选择就能造成 10～20 分波动。 |
| **SWE-bench Pro** | 更难且抗污染的 Issue 修复（私有数据、Copyleft 许可证和留出仓库） | 未饱和、正在成为主要信号 | 分数比 Verified 低 25～35 分，但区分度好得多。OpenAI 现在更推荐 Pro 反映编码能力；仍要阅读 Harness，供应商自报分数可能比标准化 Harness 高约 17 分。 |
| **SWE-bench Multimodal** | 修复视觉/UI 软件问题（JS 前端，包含损坏 UI 截图） | 未饱和 | 测试真实视觉落地能力，纯文本 SWE-bench 系统通常表现较差。 |
| **SWE-rebench / SWE-bench-Live** | 持续更新、去污染的 Issue 修复，任务发布时间晚于模型截止日期 | 未饱和 | 最强的污染审计方式；SWE-rebench 能捕获 Verified 高分在新任务上崩塌的情况。 |
| **LiveCodeBench** | 按发布日期标记的竞赛编程题，只在模型截止日期后的题目上计分 | 新鲜窗口内未饱和 | 设计上抗污染。竞赛编程不是软件工程，因此预测的是算法推理，不是仓库级工作。 |
| **Aider Polyglot** | 6 种语言的真实多文件编辑，必须输出有效编辑格式，可尝试 2 次 | 接近饱和（约 88%） | 衡量编辑格式可靠性，不是仓库规模推理；Exercism 源码公开，存在污染。 |
| **SciCode** | 拆解为子问题的研究级科学编程 | 远未饱和 | 最难的主流编码基准。存在主问题与子问题两种不兼容的评分口径，引用时必须说明采用哪一种。 |
| **Terminal-Bench 3.0** | 7 个领域的 74 项任务，2026 年 8 月中旬发布，用于替代已饱和的 2.1；发布初期曾短暂称为“Frontier-Bench v0.1” | 活跃、为保留提升空间而设计 | 当前 Agent 终端工作的区分器。2.1 上相差 4.9 分的两个模型，在 3.0 上相差 12.7 分，这正是它存在的原因。 |
| **SWE-Bench ProMax** | 170 个多语言重构实例（7 种语言，平均修改 11.4 个文件），2026 年 8 月 10 日发布 | 新、提升空间大 | 最佳模型也只能解决 41.2%。目标是协调完成保持行为不变的修改，比单 Issue Bug 修复更难、更接近真实工作。 |
| **Terminal-Bench（2.x）** | 真实终端 Sandbox 中的端到端 Agent 任务（构建、调试、系统管理） | 顶部已饱和，被 3.0 取代 | 分数与 Harness 成对出现，Agent CLI 的影响不亚于模型本身。 |

**Agent 基准为何取代 HumanEval：**HumanEval/MBPP 对所有前沿模型都达到 90% 以上，规模小且容易记忆，单函数“文档字符串转代码”不能预测真实工程能力。证据是：在同一代模型中，HumanEval 已经表现出色时，SWE-bench 初始解决率仍低于 2%。阅读仓库、运行测试、分析堆栈并迭代补丁是另一种技能，因此行业转向 Issue 修复和终端基准。

### Agent 与工具使用

这是变化最快的领域，因为 2026 年的生产价值主要集中在 Agent。这里的大多数基准尚未饱和。

| 基准 | 衡量内容 | 状态 | 说明 |
|-----------|----------|--------|-------|
| **BFCL（Berkeley Function Calling Leaderboard）** | 工具/函数调用准确率；V4 增加带网页搜索和记忆的 Agent 任务 | V1/V2 已饱和，V3/V4 未饱和 | 基于 AST 的评分可能漏掉语义错误。警惕过时的榜单镜像，应使用 Berkeley 官方榜单。 |
| **tau-bench / tau2-bench（Sierra）** | Agent 遵循领域策略使用工具并与模拟用户对话（零售、航空、电信） | 可靠性未饱和 | 报告 **pass^k**（同一任务重复运行 k 次），揭示残酷的可靠性悬崖：pass@1 约 60% 的 Agent，pass^8 可能跌到约 25%。它衡量一致性而非最佳情况，是最贴近生产的工具使用信号。原始 tau2 存在有 Bug 的任务，应使用修正版分支。 |
| **GAIA** | 需要多步工具使用、网页浏览和文件处理的通用助手任务 | 编排集成在顶部已饱和（约 92%） | 顶部条目是多模型集成和脚手架，不是基础模型，因此测到的更多是编排能力。 |
| **OSWorld-Verified** | 在真实操作系统上执行并评分的计算机使用 Agent | 未饱和，接近人类区间 | 是清理和标准化后的 OSWorld 后继版本（原版最佳成绩约 12%，人类约 72%）。供应商数字通常高于公开 Harness 数字。 |
| **Online-Mind2Web / WebArena** | 在线网页 Agent 任务 | 混合 | Online-Mind2Web 的“进步幻觉”研究发现，透明评判后，许多商业 Agent 低于 2024 年学术基线。评审方法差异很大，分数往往不可比。 |
| **GDPval** | 覆盖 44 个职业、由人类专家评分的真实经济价值知识工作 | 活跃、未饱和 | 面向未来的“能否完成一天真实工作”信号；前沿模型接近专家交付质量，但成本低约 100 倍。成对 Elo 变体（GDPval-AA）与胜率版本不同。 |
| **METR 时间跨度** | 模型以 50% 可靠性完成的任务长度（以人类分钟计） | 活跃研究标准 | 不是排行榜而是趋势：总体时间跨度约每 7 个月翻倍，编码任务增长更快，是讨论 Agent 自主性增长最清晰的方式。 |

### 长上下文

核心发现是：**规格中宣传的上下文窗口大于实际可用上下文。**讨论时应先关注这一点，而不是规格表上的窗口大小。

| 基准 | 衡量内容 | 状态 | 说明 |
|-----------|----------|--------|-------|
| **NIAH（needle-in-a-haystack）** | 在不同深度和长度下检索单个事实 | 已饱和/过于简单 | 前沿模型约 100% 的分数会造成虚假信心；适合作为 sanity check，不适合区分模型。 |
| **RULER（NVIDIA）** | 受控长度下的检索、多跳追踪、聚合和问答；报告“有效长度” | 未饱和 | 该基准揭示有效长度与宣传长度的差距：许多声称 128K 的模型只在约 32～64K（宣传值的 25～50%）内保持质量。它是合成数据，应搭配基于自然文本的测试。 |
| **Fiction.LiveBench** | 最多约 192K Token 的深层叙事理解（心智理论、时间线、隐含推理） | 未饱和 | 最严苛的实用长上下文测试；多数模型到 192K 时低于 80%。规模很小（36 题），噪声较大。 |
| **MRCR（多轮指代）** | 在多个近似相同的 Needle 中区分并返回第 i 个 | 未饱和，尤其是 8-needle | Needle 数量和长度增加时，分数会陡降。 |
| **LongBench v2 / LongBench Pro** | 8K～2M Token 的真实长上下文理解与推理 | 未饱和 | LongBench Pro 发现，长上下文**优化**优于单纯扩大参数规模，而且所有模型的有效长度都低于宣传长度。 |

设计文档中可以这样概括：*宣传的上下文窗口经常高估实际可用上下文；在 RULER 上，许多声称支持 128K 的模型只能在约 32～64K 内保持质量，不过前沿模型正在快速改善。*“上下文腐化”研究显示，质量会在达到窗口上限前就下降，甚至可能出现打乱后的信息堆优于连贯文档的反直觉结果，这进一步说明应按更小的有效预算设计。参阅[上下文工程](../05-prompting-and-context/05-context-engineering.md)。

### 多模态

图像选择题基准正在饱和；视频推理才是真正尚未解决的前沿。

| Benchmark | Measures | Status | Notes |
|-----------|----------|--------|-------|
| **MMMU / MMMU-Pro** | 覆盖 6 个学科的大学级多模态推理 | 接近饱和 | MMMU-Pro 增加难度（10 个选项、题目出现在截图中的纯视觉题），但跨 Harness 差异严重（同一模型在不同 Harness 上可能报告 81% 和 94%），绝不要跨来源比较。 |
| **MathVista、DocVQA、ChartQA、MMBench** | 视觉数学、文档问答、图表问答和广义多模态能力 | 前沿大体饱和 | DocVQA/ChartQA 接近解决；宽松准确率评分会掩盖数字错误。 |
| **Video-MME / Video-MME-v2** | 视频理解 | v1 接近饱和，v2 远未饱和 | Video-MME-v2（2026）使用非线性分组评分，显示模型与人类之间仍有较大差距，因此是当前多模态区分器。 |

### 事实性与指令遵循

| 基准 | 衡量内容 | 状态 | 说明 |
|-----------|----------|--------|-------|
| **IFEval** | 可由程序验证的指令遵循（“至少 400 字”、有效 JSON、不能有逗号） | 大体饱和（约 90% 以上） | 只检查**可检查**约束，是指令遵循的狭窄切片，也容易被针对性优化。 |
| **SimpleQA / SimpleQA Verified** | 对抗性很强的短答案闭卷事实回忆；奖励校准后的拒答 | 未饱和 | F1 最高约在 50% 中段，说明幻觉远未解决。核心教训是：能力更强不代表事实性更好。 |
| **TruthfulQA** | 抵抗常见误解 | 老化/部分饱和 | 静态且广为人知，容易污染；“真实”标签有争议，也可通过模棱两可规避。 |
| **FACTS Grounding** | 长答案是否完全由给定来源支持（没有无依据声明） | 未饱和（最高约 0.88） | 由与参赛模型有共同谱系的 LLM 集成评审，参赛结果为自报；它是评估 RAG 忠实度的合适基准家族。 |

### 人类偏好

| 基准 | 衡量内容 | 状态 | 说明 |
|-----------|----------|--------|-------|
| **LMArena（Chatbot Arena Elo）** | 众包盲测的成对偏好，以 Elo 报告 | 没有上限，但前约 15 名压缩在约 25 Elo 分内 | 著名但最容易被滥用的偏好信号。见[排行榜幻觉](#the-leaderboard-illusion)。始终查看**风格控制** Elo（回归掉长度和格式偏差）及置信区间；小于约 15～20 Elo 的差异属于噪声。 |
| **Arena-Hard-Auto v2** | Arena 的自动、可复现代理：由强 LLM 对困难 Prompt 做成对评审 | 未饱和，区分度强 | 区分度约为 MT-Bench 的 3 倍，与人工 Arena 排名相关约 98%。需要可重复运行的偏好信号时，它成本低；应开启风格控制。 |
| **MT-Bench** | 通过 LLM 评审的多轮质量（80 个 Prompt） | 已饱和/过时 | 规模很小，存在 GPT-4 评审偏差（自偏好、偏爱冗长），已被 Arena-Hard 取代。 |

---

## 批判性阅读基准

这才是最重要的部分。任何人都能看排行榜，真正的能力在于*正确解读*它。

### 饱和

当一个基准上的前沿模型聚集在接近上限的位置、分数差异落入噪声范围时，就称为饱和。MMLU 是典型案例：GPT-4 在 2023 年初达到约 86%，此后前沿模型一直处于 86～93%，因此 2 个百分点的“领先”常常只是 Prompt 伪影（MMLU 分数会因 Prompt 措辞不同而变化 4～5%）。实用判断是：**当领先者的分数集中在约 3 个百分点内，排名顺序反映的是统计噪声，而不是能力。**

基准饱和后，行业通常会采用：(1) 更难的后继基准（MMLU、MMLU-Pro、HLE）；(2) 私有或留出数据集；(3) 按时间门控的“实时”基准；(4) 综合指数。静态公开基准的有效寿命中位数不足约两年。

### 数据污染

基准是公开的，可能被抓取进预训练数据，因此模型可能靠记忆而非能力取得高分。直接证据包括：重新生成 HumanEval 风格题目（EvoEval）后，51 个模型的分数下降约 39%；在 LiveCodeBench 上，模型在截止日期前题目的通过率约 60%，截止日期后的题目则接近 0%；OpenAI 还发现 SWE-bench Verified 的解法可以根据任务 ID 原样复现。多项选择问答基准测得的污染率为 1%～45%，且大模型从中获益更多。

抗污染设计包括：**时间门控**（只评测模型截止日期后发布的题目，LiveCodeBench 和 SWE-rebench 采用此法）、**私有留出集**（FrontierMath、ARC-AGI-2，代价是不可复现）以及**金丝雀字符串**（在数据集中植入唯一 Token，模型复述时即可暴露污染）。检测方法（n-gram 重叠、成员推断、TS-Guessing 测验）都有失效模式；尤其是成员推断攻击，在真实预训练模型上几乎只比随机猜测好一点。实践上，对任何静态公开基准都应假设存在一定污染，并折价看待绝对分数。

### Harness 与脚手架差异

相同模型权重的分数会因 Prompt、是否提供工具、推理力度和 Agent 脚手架不同而相差 10～20 个百分点。Anthropic 测得，仅基础设施配置（RAM、并发，甚至一天中不同时间的 API 延迟）就能让 Terminal-Bench 结果变化约 6 分。这解释了为什么**供应商自报分数通常高于独立排行榜**：实验室会在不限资源的基础设施上，使用为自家模型找到的最佳 Harness 和推理力度。由此得到硬规则：**绝不能把一个供应商的数字与另一供应商的数字或独立排行榜比较。**只有相同 Harness 产生的数字才可比。推理力度也不是单调收益；一项大型 Agent 研究中，36 种设置有 21 种在增加思考后准确率反而下降，所以供应商的“高推理力度”数字甚至不能与同一模型默认力度下的独立结果直接比较。

**2026 年年中出现了第三类错误来源：基准自身的测试。**对 15 个 Agent 基准的 2385 条轨迹进行审计后发现，其中两个基准约 67% 的轨迹存在奖励投机或答案泄露：Agent 不是解决任务，而是找回公开解法、读取评测产物或利用无效评分路径。另一项对 SWE-bench Verified 的审计也发现，相当一部分未解决实例的测试本身有缺陷。实践规则是：分数突然上升时，要检查究竟是能力提升，还是协议泄露；优先选择公开有效性审计的基准。

**污染检测现在也有了关于自身局限性的理论。**2026 年 8 月发表的形式化研究表明，可检测性取决于污染比例、模型在见过与未见过题目上的行为差距，以及样本量的平方根。对实践者而言，小规模审计中“没有污染证据”既可能代表基准干净，也可能代表测试统计功效不足；因此任何污染结论都需要给出明确的功效计算才有意义。

### 排行榜幻觉

对 LMArena 的核心批评（Cohere 等人审计约 200 万场对战、243 个模型）发现四个问题：供应商会私下测试许多变体，只发布最佳结果（Meta 在 Llama-4 前测试了 27 个变体），这违反了 Elo 计算所依赖的无偏采样假设；闭源供应商获得的对战数据远多于开源模型；可以针对 Arena 分布训练以大幅提高胜率；静默弃用的模型会扭曲排名。LMArena 的回应质疑影响程度（其估计私测带来的提升约为 11 Elo，并会随新投票累积而衰减），并指出过拟合数据来自静态代理集，而非实时人工榜。应将其表述为**有证据支持但仍存在争议**。

无论争议如何，实践建议都相同：把 Arena Elo 当作**通用聊天偏好指标，而不是正确性、事实性或深度推理指标**；始终使用风格控制榜（Arena 会奖励更长、更漂亮的回答）；查看置信区间（前约 15 个模型在统计上接近并列）；并把它作为三类信号之一，绝不要单独使用。

### 从基准到生产的差距

公开分数只有在三个条件同时满足时才会预测生产表现：基准测试的任务与你的任务相似，测试集没有污染，且基准尚未饱和。实践中这三点很少同时成立。对基准分数的主成分分析发现，单一“通用能力”因子只能解释约 50% 的方差，其余是模型家族特性和噪声，因此通用能力相同的两个模型在*你的任务*上仍可能差异很大。GPQA 高分并不保证领域表现。

对于编码和 Agent，最佳公开代理指标是 GPQA-Diamond 和 SWE-bench Verified（Aider Polyglot、AIME 风格数据集也能较好反映通用能力），但前提是 Harness 一致。每位实践者最终都会得到同一个结论：**做决策时忽略排行榜，在自己的数据上构建评测。**构造按特征、场景和用户画像划分的金标准集；使用经过领域专家校准的二元 LLM 评审（用精确率和召回率衡量，而非直接看一致率）；并将能力与成本一起定价，因为没有公开基准包含成本信号。参阅[LLM 评测](01-llm-evaluation.md)和[白板练习](../00-interview-prep/04-whiteboard-exercises.md)中的评测流水线练习。

### 综合指数

由于任何单一基准在一两年内都可能饱和，行业使用加权综合指数对前沿模型排序，使组件达到上限后仍有区分度，并降低对单项测试过拟合的风险：

- **Artificial Analysis Intelligence Index**在 Agent、编码、科学推理和通识知识方向加权约 9 项评测，并会在组件饱和后重新换版（随着时间推移已移除 MMLU-Pro、LiveCodeBench 和 AIME 2025）。
- **Epoch Capability Index（ECI）**在 1000 多项评测上拟合项目反应理论模型，用统计方法推断每个基准的难度，因此模型在**更难**基准上表现好时会得到更高分。
- **HAL（Princeton 的 Holistic Agent Leaderboard）**是面向 Agent、考虑成本的综合指数：同时评分准确率和美元成本，对所有模型使用固定 Harness，并通过日志分析发现走捷径的 Agent（例如从 arXiv 取答案而不是解题）和评测 Bug。它存在的原因是：准确率提升 1% 但成本增加 10 倍，并不算胜利。

综合指数适合回答“哪个模型总体最好”，但会继承组成基准的缺陷，因此仍要阅读它实际聚合了什么。

---

## 实践检查清单

阅读任何基准声明时：

1. **阅读 Harness，而不只是数字。**要求给出脚手架、工具权限、推理力度和输出 Token 上限。孤立的百分比没有可解释性。
2. **检查置信区间。**忽略噪声范围内的差异。SWE-bench Verified 只有 500 道题（每题约 0.2%），Arena 小于约 15～20 Elo 的差异属于噪声；配置未对齐前，不要相信小于约 3 分的差距。
3. **优先选择时间门控、私有或留出数据集。**对于静态公开集（MMLU、HumanEval、GSM8K），假设存在污染，并折价看待绝对分数。
4. **绝不要跨 Harness 或跨自报结果比较。**只有相同 Harness 的数字才可比较。
5. **核验模型名称。**如果某个前沿分数归属于你找不到一手来源的模型，很可能是虚构的。2026 年 6 月已确认的前沿系列包括：Claude（Fable 5、Opus 4.8/4.7、Sonnet 4.6、Haiku 4.5）、GPT-5.5、Gemini 3.1 Pro、DeepSeek V4、Llama 4、Kimi K2.6、Qwen 3.6、Mistral Medium 3.5、Grok 4.3。
6. **在相信排名前交叉验证三类信号**：静态学术评测、人工偏好竞技场和 Agent 套件。
7. **做自己的决策时，在自己的数据上构建评测。**公开分数很少能预测你的领域；排行榜帮助你初筛，金标准集决定你最终上线谁。

---

## 2026 年哪些基准重要

要了解**前沿通用能力**：看 HLE、GPQA-Diamond（注意其区分度正在下降）、CritPt 和综合指数（Artificial Analysis Intelligence Index、Epoch ECI）；忽略 MMLU、MMLU-Pro、HellaSwag、ARC-Challenge。

对于**编码和 Agent**：用 SWE-bench Verified 做层级筛选，用 SWE-bench Pro 及抗污染实时变体（SWE-rebench、SWE-bench-Live）做真正排序，用 Terminal-Bench 和 tau2-bench 评估工具使用与可靠性（关注 pass^k），用 HAL 做成本感知的 Agent 比较；忽略 HumanEval/MBPP。

对于**长上下文**：优先 RULER 和 Fiction.LiveBench，而非 NIAH；应按有效上下文而非宣传窗口设计。

对于**事实性**：用 SimpleQA 测闭卷幻觉，用 FACTS Grounding 测 RAG 忠实度；记住能力更强不等于事实性更高。

对于**偏好**：使用带置信区间的风格控制 Arena Elo，或使用 Arena-Hard-Auto v2 作为可复现代理。

对于**你的产品**：上述都不是最终答案。建立自己的金标准集和评审器。相关前沿研究发展很快（Agent 可靠性科学、声明级忠实度评测、模型识别自己正在被测试的评测意识）；参阅[研究雷达](../RESEARCH-RADAR.md)。

---

## 面试问题

### Q：供应商说其模型在 SWE-bench Verified 上得分 90%。在相信它能预测你的编码 Agent 质量前，你会问什么？

**强回答：**
第一是 Harness：使用了哪个 Agent 脚手架、哪些工具、什么推理力度、输出 Token 上限是多少？仅脚手架不同，相同权重的分数就可能相差 10～20 分；供应商会使用找到的最佳 Harness，因此 90% 不能与其他模型发布的数字直接比较。第二是污染：SWE-bench Verified 存在污染（OpenAI 发现解法可以根据任务 ID 复现），所以我会要求看抗污染变体 SWE-bench Pro、SWE-rebench，它们的分数通常低 25～35 分但区分度更好。第三是置信区间：只有 500 道题，几分的差异可能只是噪声。第四也是最重要的是生产差距：即便是干净的 SWE-bench 分数，也只有在我的任务类似 GitHub Issue 修复时才有预测力。我会用公开分数进行初筛，再从自有仓库的真实工单构建金标准集，用校准后的评审评分，并结合成本做决定。

### Q：为什么 MMLU、HumanEval 等基准不再适合给前沿模型排名？什么取代了它们？

**强回答：**
它们已经饱和：前沿模型在 MMLU 上集中于 88～90% 以上，在 HumanEval 上超过 90%，差异落入 Prompt 措辞噪声范围。它们规模小且公开，容易被污染；重新生成 HumanEval 题目会让分数下降约 39%。测试构造也过于简单：单函数的文档字符串转代码不能预测真实工程能力，这就是同一代模型在 HumanEval 表现出色、SWE-bench 初始解决率却低于 2% 的原因。行业用更难的后继基准（MMLU → MMLU-Pro → HLE）、抗污染时间门控基准（LiveCodeBench、SWE-rebench）、Agent 和仓库级基准（SWE-bench、Terminal-Bench、tau2-bench），以及组件饱和后仍有区分度的综合指数来替代它们。

### Q：为聊天产品选择模型时，如何负责任地使用 LMArena Elo？

**强回答：**
我只把它作为通用聊天偏好的一个信号，绝不把它当作正确性或推理能力指标。我会查看风格控制榜，因为原始 Arena 会奖励更长、格式更好的回答，而不管是否正确；还会查看置信区间，因为前十几个模型在约 15～20 Elo 内统计上接近并列。我也会考虑排行榜幻觉：供应商会私下测试许多变体并只发布最佳结果，因此新进入榜首的结果可能部分来自 Best-of-N 运气。之后我会与客观基准和 Agent 套件交叉验证，最终用自己的偏好数据验证，因为 Arena 的 Prompt 并不是我的用户 Prompt。

---

## 参考资料

- Hendrycks et al. "Measuring Massive Multitask Language Understanding (MMLU)" arXiv:2009.03300
- Wang et al. "MMLU-Pro" arXiv:2406.01574
- Rein et al. "GPQA: A Graduate-Level Google-Proof Q&A Benchmark" arXiv:2311.12022
- "Humanity's Last Exam" arXiv:2501.14249
- "ARC-AGI-2" arXiv:2505.11831 and [ARC Prize leaderboard](https://arcprize.org/leaderboard)
- [Epoch AI FrontierMath](https://epoch.ai/frontiermath) and [benchmarks hub](https://epoch.ai/benchmarks)
- Jimenez et al. "SWE-bench" arXiv:2310.06770 and [swebench.com](https://www.swebench.com/)
- [Scale AI SWE-bench Pro leaderboard](https://labs.scale.com/leaderboard/swe_bench_pro_public)
- "SWE-bench-Live" arXiv:2505.23419 and [SWE-rebench](https://swe-rebench.com/)
- Jain et al. "LiveCodeBench" arXiv:2403.07974
- [Berkeley Function Calling Leaderboard (BFCL)](https://gorilla.cs.berkeley.edu/leaderboard.html)
- [Sierra tau2-bench](https://github.com/sierra-research/tau2-bench)
- "GDPval" arXiv:2510.04374 and [OpenAI GDPval](https://openai.com/index/gdpval/)
- [METR, measuring AI task-completion time horizons](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks)
- "RULER" arXiv:2404.06654 and [NVIDIA/RULER](https://github.com/NVIDIA/RULER)
- "MMMU-Pro" arXiv:2409.02813
- [OpenAI SimpleQA](https://openai.com/index/introducing-simpleqa/) and "SimpleQA Verified" arXiv:2509.07968
- "FACTS Grounding" arXiv:2501.03200
- Singh et al. "The Leaderboard Illusion" arXiv:2504.20879 and the LMArena response
- "Holistic Agent Leaderboard (HAL)" arXiv:2510.11977
- [Artificial Analysis methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking) and [Epoch Capability Index](https://epoch.ai/benchmarks)
- Anthropic, "Quantifying infrastructure noise in agentic coding evals" (Feb 2026)
- Hamel Husain, ["Your AI Product Needs Evals"](https://hamel.dev/blog/posts/evals/) and ["LLM-as-a-Judge"](https://hamel.dev/blog/posts/llm-judge/)

---

*Next: [CI/CD for LLM Applications](../11-infrastructure-and-mlops/02-cicd.md). See also [Research Radar](../RESEARCH-RADAR.md) for the frontier topics beyond the leaderboards.*
