#!/usr/bin/env python3
"""Build a dependency-free local reader for the interview-prep Markdown files."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).parent
PROJECT_ROOT = ROOT.parent
OUTPUT = ROOT / "reader.html"

SECTION_META = {
    "00-interview-prep": "00 · 面试准备",
    "01-foundations": "01 · 基础知识",
    "02-model-landscape": "02 · 模型版图",
    "03-training-and-adaptation": "03 · 训练与适配",
}

DOC_META = {
    "README.md": {
        "label": "阅读地图",
        "title_zh": "AI 系统设计面试准备",
        "summary": "这组资料按“题库 → 答题框架 → 常见陷阱 → 白板练习 → 行为面试 → 市场趋势 → FAQ”的顺序组织。建议先用阅读地图了解路径，再根据面试时间选择重点。",
        "detail": "这篇 README 是整个目录的导航。它说明了每篇资料的用途、推荐阅读顺序和不同岗位的准备路径。对于你的目标岗位，建议优先阅读题库、答题框架、白板练习和行为面试；其中 RAG、Agent、MCP、评测、可观测性和成本控制可以结合 AliceFeed Copilot 的真实经历来准备。",
    },
    "01-question-bank.md": {
        "label": "128 道系统设计题",
        "title_zh": "AI 系统设计面试题库",
        "summary": "覆盖 RAG、Agent、模型选择、推理优化、评测、MLOps、安全和系统设计场景。重点不是背答案，而是掌握需求澄清、架构拆解、权衡和验证的表达顺序。",
        "detail": "题库从生产 RAG 管线开始，逐步扩展到 Agent、MCP、多智能体、模型路由、KV Cache、批处理、量化、LLM 评测、可观测性、限流、安全和多租户。每道题通常包含面试官关注点、强回答应覆盖的内容、示例回答和追问。学习时可以先用中文概要建立知识地图，再挑选与你经历最相关的问题深入准备，例如混合检索、RRF、上下文压缩、Tool Calling、Agent 循环控制、RAGAS 和 Langfuse。",
    },
    "02-answer-frameworks.md": {
        "label": "答题框架",
        "title_zh": "AI 系统设计答题框架",
        "summary": "提供 SPIDER、ETA、Trade-off、Debugging 和 STAR-L 五种框架，帮助你把零散知识组织成结构化、可追问的面试回答。",
        "detail": "SPIDER 用于系统设计：先澄清范围，再确定优先级，画出初始架构，深入关键路径，补充评测与可观测性，最后讨论可靠性和规模。ETA 用于解释概念：先用简单语言说明，再补充技术细节，最后落到应用场景与权衡。Trade-off 用于比较方案，Debugging 用于定位线上问题，STAR-L 用于行为面试。你的回答可以把这些框架和真实项目结合起来：先说明金融问答场景，再讲 RAG、Tool Calling、上下文压缩和 Langfuse，最后用 RAGAS 或回归测试说明如何验证效果。",
    },
    "03-common-pitfalls.md": {
        "label": "常见陷阱",
        "title_zh": "AI 系统设计面试常见陷阱",
        "summary": "总结会让高级候选人失分的模式：跳过数据管道、只谈模型、不谈评测和成本、忽视多租户与故障降级，以及表达缺少结构。",
        "detail": "这篇资料把失分点分成架构、技术知识、沟通、面试策略和 AI 特有问题几类。核心提醒是：不要把 AI 系统描述成一个模型调用；必须覆盖数据处理、检索、生成、评测、监控、权限、安全和失败兜底。回答时要主动说清楚假设、指标和权衡，避免把理解过的原理包装成独立负责的生产经验。对于你的面试准备尤其要注意区分“我主导实现”“我参与建设”和“我理解原理但还需要深入”的边界。",
    },
    "04-whiteboard-exercises.md": {
        "label": "9 个白板练习",
        "title_zh": "AI 系统设计白板练习",
        "summary": "通过企业 RAG、客服机器人、代码审查、文档处理、实时审核、多租户平台、语义搜索、评测流水线和 Agent 记忆等场景模拟完整面试。",
        "detail": "白板练习要求你在有限时间内完成从需求澄清到架构落图。每个练习都强调关键组件、数据流、容量估算、延迟、可靠性、评测和安全。建议每次先口述目标和非目标，再画最小可行架构，最后主动挑一个关键链路深入。对你来说，企业 RAG、评测流水线、Agent 记忆和多租户 AI 平台最值得优先练习，因为它们能直接连接到金融数据问答、RRF 检索、RAGAS、上下文压缩和调用链路观测等经历。",
    },
    "05-behavioral-for-ai-roles.md": {
        "label": "行为面试",
        "title_zh": "AI 岗位行为面试",
        "summary": "围绕模糊需求、预期管理、失败复盘、跨团队协作、责任 AI、技术决策和影响力，提供 STAR-L 示例与练习清单。",
        "detail": "AI 岗位的行为面试不仅考察做过什么，还考察你如何在不确定性中做判断。资料建议使用 STAR-L：背景、任务、行动、结果、学习。准备故事时可以优先选择真实且能体现影响力的经历，例如搭建 Agent 框架、限制模型调用循环、建设上下文压缩 Middleware、接入 Langfuse、使用测评集和 RAGAS 做回归验证，以及带领转档小组协调任务。数据不确定时要明确口径，不能为了让故事更漂亮而补造数字。",
    },
    "06-job-market-trends-2026.md": {
        "label": "2026 岗位趋势",
        "title_zh": "2026 年 AI 就业市场趋势",
        "summary": "介绍 AI 岗位从单一模型开发转向应用工程、评测、可靠性、安全、MCP 和 Forward Deployed Engineer 等细分方向的变化。",
        "detail": "这篇资料从岗位名称、技能层级、招聘要求、薪酬、地区、面试流程和新兴岗位几个角度描述 2026 年市场。对你的定位而言，最有价值的不是记住具体公司或薪资数字，而是理解“AI 应用生产化”正在成为独立能力：包括 Agent 编排、RAG、Tool Calling、评测、可观测性、成本和安全。阅读时要结合自己的 Java 后端基础、Python Agent 开发经验和金融业务背景，形成清晰的岗位叙事。",
    },
    "07-faq.md": {
        "label": "快速 FAQ",
        "title_zh": "AI 工程、RAG 与 Agent 快速问答",
        "summary": "用短答案覆盖 AI 工程、RAG、Agent、模型、评测、推理、记忆和安全等高频问题，适合复习前快速扫一遍。",
        "detail": "FAQ 适合作为复习索引，不适合替代深入学习。它把常见概念压缩成可快速回忆的答案，例如 RAG 与微调的区别、混合检索、GraphRAG、上下文工程、MCP、Agentic RAG、LLM-as-judge、RAGAS、vLLM、提示词注入和 Agent 沙箱。遇到与你项目相关的问题，建议从 FAQ 先恢复答案骨架，再回到题库或白板练习补充架构、指标和故障处理细节。",
    },
}


HTML_TEMPLATE = r'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI System Design Interview Prep</title>
  <style>
    :root { color-scheme: light; --ink:#1d2733; --muted:#718096; --line:#e6e9ee; --brand:#2563eb; --paper:#fff; --bg:#f5f7fb; }
    * { box-sizing:border-box; }
    body { margin:0; color:var(--ink); background:var(--bg); font:15px/1.7 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif; }
    .app { display:grid; grid-template-columns:280px minmax(0,1fr); min-height:100vh; }
    aside { padding:24px 16px; background:#111827; color:#dbe5f2; }
    aside h1 { margin:0 8px 6px; font-size:18px; color:#fff; }
    aside p { margin:0 8px 20px; color:#9fb0c5; font-size:13px; }
    .doc-list { display:grid; gap:12px; }
    .section { display:grid; gap:4px; }
    .section-title { padding:6px 8px 3px; color:#8fa5bf; font-size:11px; font-weight:800; letter-spacing:.08em; text-transform:uppercase; }
    .section-docs { display:grid; gap:3px; }
    .doc-list button { border:0; border-radius:8px; padding:9px 10px; text-align:left; background:transparent; color:#c9d5e4; cursor:pointer; font:inherit; }
    .doc-list button:hover,.doc-list button.active { background:#263650; color:#fff; }
    .doc-list .doc-name { display:block; font-size:13px; }
    .doc-list .doc-file { display:block; margin-top:1px; color:#8195ad; font-size:10px; }
    main { min-width:0; padding:32px clamp(18px,4vw,56px); }
    .topbar { display:flex; align-items:flex-start; justify-content:space-between; gap:20px; margin-bottom:20px; }
    .eyebrow { margin:0 0 4px; color:var(--brand); font-size:13px; font-weight:700; }
    h2 { margin:0; font-size:30px; line-height:1.25; }
    .hint { color:var(--muted); font-size:13px; }
    .tabs { display:flex; gap:8px; margin:18px 0 0; border-bottom:1px solid var(--line); }
    .tabs button { padding:10px 14px; border:0; border-bottom:2px solid transparent; background:transparent; color:var(--muted); cursor:pointer; font:inherit; }
    .tabs button.active { border-bottom-color:var(--brand); color:var(--brand); font-weight:700; }
    .panel { max-width:980px; padding:28px 0 60px; }
    .summary { margin-bottom:22px; padding:16px 18px; border-left:4px solid var(--brand); border-radius:6px; background:#eef5ff; }
    .detail { white-space:pre-wrap; }
    .markdown h1 { font-size:30px; margin:0 0 20px; }
    .markdown h2 { margin:30px 0 10px; font-size:24px; }
    .markdown h3 { margin:24px 0 8px; font-size:19px; }
    .markdown p { margin:10px 0; }
    .markdown ul,.markdown ol { padding-left:28px; }
    .markdown li { margin:4px 0; }
    .markdown blockquote { margin:16px 0; padding:10px 16px; border-left:4px solid #cbd5e1; color:#526174; background:#f8fafc; }
    .markdown pre { overflow:auto; padding:14px 16px; border-radius:8px; background:#111827; color:#e5e7eb; font:13px/1.6 ui-monospace,SFMono-Regular,Menlo,monospace; }
    .markdown code { padding:2px 5px; border-radius:4px; background:#eef2f7; font:13px ui-monospace,SFMono-Regular,Menlo,monospace; }
    .markdown pre code { padding:0; background:transparent; }
    .markdown table { width:100%; border-collapse:collapse; display:block; overflow:auto; }
    .markdown th,.markdown td { min-width:120px; padding:8px 10px; border:1px solid var(--line); text-align:left; vertical-align:top; }
    .markdown th { background:#f8fafc; }
    .markdown a { color:var(--brand); }
    @media (max-width:760px) { .app { display:block; } aside { padding:16px; } .doc-list { display:flex; overflow:auto; } .doc-list button { white-space:nowrap; } main { padding:24px 16px; } h2 { font-size:24px; } }
  </style>
</head>
<body>
<div class="app">
  <aside>
    <h1>AI 面试资料阅读器</h1>
    <p>00-interview-prep · 本地实验版</p>
    <div id="doc-list" class="doc-list"></div>
  </aside>
  <main>
    <div class="topbar">
      <div><p id="eyebrow" class="eyebrow"></p><h2 id="title"></h2></div>
      <div class="hint">双击 reader.html 即可打开</div>
    </div>
    <div id="tabs" class="tabs"></div>
    <section id="panel" class="panel"></section>
  </main>
</div>
<script>
const documents = __DOCUMENTS__;
const modes = [
  { id: 'english', label: '英文详情' },
  { id: 'chinese', label: '中文详情' },
  { id: 'summary', label: '中文概要' },
];
let current = 0;
let mode = 'english';

function escapeHtml(value) { return value.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function inline(value) {
  let result = escapeHtml(value);
  result = result.replace(/`([^`]+)`/g, '<code>$1</code>');
  result = result.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noreferrer">$1</a>');
  result = result.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  result = result.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  return result;
}
function renderMarkdown(source) {
  const lines = source.replace(/\r/g, '').split('\n');
  let html = '', inCode = false, code = [], list = null, table = false;
  const closeList = () => { if (list) { html += `</${list}>`; list = null; } };
  const closeTable = () => { if (table) { html += '</tbody></table>'; table = false; } };
  for (const line of lines) {
    if (line.startsWith('```')) { if (inCode) { html += `<pre><code>${escapeHtml(code.join('\n'))}</code></pre>`; code = []; inCode = false; } else { closeList(); closeTable(); inCode = true; } continue; }
    if (inCode) { code.push(line); continue; }
    if (/^\s*\|.*\|\s*$/.test(line)) {
      const cells = line.trim().replace(/^\||\|$/g, '').split('|').map(x => x.trim());
      if (/^\s*[-:]+\s*$/.test(cells[0] || '')) continue;
      closeList();
      if (!table) { html += '<table><thead><tr>' + cells.map(x => `<th>${inline(x)}</th>`).join('') + '</tr></thead><tbody>'; table = true; }
      else html += '<tr>' + cells.map(x => `<td>${inline(x)}</td>`).join('') + '</tr>';
      continue;
    }
    closeTable();
    const heading = line.match(/^(#{1,3})\s+(.*)$/);
    if (heading) { closeList(); const level = heading[1].length; html += `<h${level}>${inline(heading[2])}</h${level}>`; continue; }
    const bullet = line.match(/^\s*[-*+]\s+(.*)$/);
    const numbered = line.match(/^\s*\d+\.\s+(.*)$/);
    if (bullet || numbered) { const wanted = numbered ? 'ol' : 'ul'; if (list !== wanted) { closeList(); html += `<${wanted}>`; list = wanted; } html += `<li>${inline((bullet || numbered)[1])}</li>`; continue; }
    if (/^>\s?/.test(line)) { closeList(); html += `<blockquote>${inline(line.replace(/^>\s?/, ''))}</blockquote>`; continue; }
    closeList();
    if (line.trim()) html += `<p>${inline(line)}</p>`;
  }
  closeList(); closeTable(); if (inCode) html += `<pre><code>${escapeHtml(code.join('\n'))}</code></pre>`;
  return html;
}
function render() {
  const doc = documents[current];
  document.getElementById('eyebrow').textContent = doc.label;
  document.getElementById('title').textContent = doc.title_zh;
  const sections = [...new Map(documents.map((item, index) => [item.section_id, { id: item.section_id, label: item.section_label, items: [] }])).values()];
  documents.forEach((item, index) => sections.find(section => section.id === item.section_id).items.push({ item, index }));
  document.getElementById('doc-list').innerHTML = sections.map(section => `<div class="section"><div class="section-title">${section.label}</div><div class="section-docs">${section.items.map(({item, index}) => `<button class="${index === current ? 'active' : ''}" data-doc="${index}"><span class="doc-name">${item.label}</span><span class="doc-file">${item.filename}</span></button>`).join('')}</div></div>`).join('');
  document.querySelectorAll('[data-doc]').forEach(button => button.onclick = () => { current = Number(button.dataset.doc); mode = 'english'; render(); });
  document.getElementById('tabs').innerHTML = modes.map(item => `<button class="${item.id === mode ? 'active' : ''}" data-mode="${item.id}">${item.label}</button>`).join('');
  document.querySelectorAll('[data-mode]').forEach(button => button.onclick = () => { mode = button.dataset.mode; render(); });
  const panel = document.getElementById('panel');
  if (mode === 'english') panel.innerHTML = `<div class="markdown">${renderMarkdown(doc.content)}</div>`;
  if (mode === 'chinese') panel.innerHTML = `<div class="markdown"><div class="summary"><strong>中文学习提示</strong><br>${doc.summary}</div>${renderMarkdown(doc.content_zh || doc.detail)}</div>`;
  if (mode === 'summary') panel.innerHTML = `<div class="markdown">${renderMarkdown(doc.summary_content || `## 中文概要\n\n${doc.summary}\n\n建议：先阅读本概要，再切换到英文详情定位原文，最后用中文详情整理自己的面试表达。`)}</div>`;
}
render();
</script>
</body>
</html>
'''


def build() -> None:
    documents = []
    for filename, meta in DOC_META.items():
        source_path = ROOT / filename
        content = source_path.read_text(encoding="utf-8")
        zh_path = source_path.with_suffix(".zh.md")
        summary_path = source_path.with_suffix(".summary.md")
        content_zh = zh_path.read_text(encoding="utf-8") if zh_path.exists() else ""
        summary_content = summary_path.read_text(encoding="utf-8") if summary_path.exists() else ""
        documents.append({"filename": filename, "section_id": "00-interview-prep", "section_label": SECTION_META["00-interview-prep"], **meta, "content": content, "content_zh": content_zh, "summary_content": summary_content})

    for section_id, section_label in SECTION_META.items():
        if section_id == "00-interview-prep":
            continue
        for source_path in sorted((PROJECT_ROOT / section_id).glob("*.md")):
            if source_path.name.endswith(".zh.md") or source_path.name.endswith(".summary.md"):
                continue
            content = source_path.read_text(encoding="utf-8")
            zh_path = source_path.with_suffix(".zh.md")
            summary_path = source_path.with_suffix(".summary.md")
            content_zh = zh_path.read_text(encoding="utf-8") if zh_path.exists() else ""
            summary_content = summary_path.read_text(encoding="utf-8") if summary_path.exists() else ""
            title_zh = next((line[2:].strip() for line in content_zh.splitlines() if line.startswith("# ")), source_path.stem)
            label = source_path.stem.replace("-", " ")
            documents.append({
                "filename": f"{section_id}/{source_path.name}",
                "section_id": section_id,
                "section_label": section_label,
                "label": label,
                "title_zh": title_zh,
                "summary": summary_content.splitlines()[2] if len(summary_content.splitlines()) > 2 else f"{title_zh}的中文学习内容。",
                "detail": "",
                "content": content,
                "content_zh": content_zh,
                "summary_content": summary_content,
            })
    payload = json.dumps(documents, ensure_ascii=False).replace("</", "<\\/")
    OUTPUT.write_text(HTML_TEMPLATE.replace("__DOCUMENTS__", payload), encoding="utf-8")
    print(f"Built {OUTPUT} with {len(documents)} documents.")


if __name__ == "__main__":
    build()
