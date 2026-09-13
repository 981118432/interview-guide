# OCR 与版面分析

传统 OCR（Tesseract、专用引擎）已经基本被**原生多模态 LLM**（Gemini 3.1 Pro、GPT-5.5、Claude Sonnet 4.6、Claude Opus 4.7）取代。我们不再只是“读取字符”，而是在“理解版面”。

## 目录

- [转变：传统 OCR 与视觉 LLM](#shift)
- [视觉 LLM 版面提取](#layout-extraction)
- [阅读顺序与逻辑结构](#reading-order)
- [处理低质量扫描和手写内容](#quality)
- [成本与延迟权衡](#tradeoffs)
- [面试问题](#interview-questions)
- [参考资料](#references)

---

## 转变：传统 OCR 与视觉 LLM

| 特性 | 传统 OCR（Tesseract/AWS Textract） | 视觉 LLM（Gemini 3.1 Pro、GPT-5.5、Claude Opus 4.7） |
|---------|-------------------------------------------|--------------------------------------------------------|
| **主要机制** | 字符识别 | 视觉 Token 理解 |
| **逻辑** | 点和线分析 | 语义上下文 |
| **阅读顺序** | 简单的从上到下 | 感知多列和复杂版面 |
| **手写内容** | 较差 | 出色（人类水平） |
| **输出** | 文本块 + 边界框 | 结构化 Markdown/JSON |

---

## 视觉 LLM 版面提取

标准工作流是**截图转 Markdown**。
1. **栅格化**：把 PDF 页面转换为图像。
2. **视觉 Prompt**：要求视觉模型“将下面页面转录为 GitHub 风格 Markdown，并保留表格和标题”。
3. **结构化恢复**：利用模型的空间感知能力重建逻辑层级。

---

## 阅读顺序与逻辑结构

> [!IMPORTANT]
> 朴素 RAG 的常见失败是把一个段落从一栏截断到另一栏。
> 视觉 LLM 可以通过“看见”栏间空白来解决这个问题，并正确排列文本顺序；基于规则的解析器则可能直接横向读过两栏。

---

## 处理低质量扫描

现代多模态模型能够稳健处理：
- **倾斜/旋转**：在视觉注意力层自动纠正。
- **透印**：模型使用语义上下文“忽略”页面背面的文字。
- **手写注释**：可以提取到单独的 `annotations` JSON 字段。

---

## 成本与延迟权衡

| 模型层级 | 使用场景 | 延迟 | 成本（1K 页） |
|------------|---------|---------|-----------------|
| **Gemini 3.1 Flash** | 高吞吐批处理 | 1-2s / 页 | $1-3 |
| **GPT-5.5 / Claude Sonnet 4.6** | 高精度/法律 | 3-5s / 页 | $8-18 |
| **本地（Llama 4 Vision）** | PII 敏感/本地部署 | <1s / 页 | 仅基础设施 |

---

## 面试问题

### Q：既然有视觉 LLM，为什么还会使用 AWS Textract 或 Azure AI Search（OCR）？

**强回答：**
**严格的空间元数据和合规性**。如果应用需要每个词的精确像素级边界框（例如法律文档脱敏工具），专用 OCR 引擎通常更精确、更便宜。此外 OCR 引擎是**确定性的**：不会“幻觉”出不存在的词。在对“版面理解”要求不高、但需要 100% 字符准确率的高风险文档处理场景中，传统引擎仍然适合放在混合流水线里。

### Q：如何高效处理一份 500 页的 PDF？

**强回答：**
我们使用**并行 Map-Reduce** 模式。
1. **Map**：启动 50 个并行 Worker（使用 AWS Lambda 或 Modal），每个 Worker 处理 10 页。每个 Worker 调用快速视觉模型（如 Gemini 3 Flash）获得 Markdown。
2. **Consolidate**：中央 Agent 审查 Markdown 片段，确保标题连续。
3. **Cache**：把生成的 Markdown 存入向量数据库。
这会把顺序处理的 30 分钟缩短到 20 秒以内。

---

## 参考资料
- Google DeepMind：《Gemini 2.0: Understanding Multi-column Documents》（2025）
- OpenAI：《Vision Models for Document Understanding》（2025）
- Tesseract v6：《The Integration of Hybrid Transformer OCR》（2025）
