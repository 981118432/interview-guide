# AI System Design Interview Preparation

Interview prep for senior and staff AI engineering roles: 128 system design questions, answer frameworks with a worked mock-interview transcript, common pitfalls, nine whiteboard exercises, behavioral prep, a quick-answer FAQ, and August 2026 hiring trends.

> **What's new (August 2026):** the question bank gained six August-2026 questions (rebuilding cost models after the first major inference price increase, capability-tiered access control, coding-agent supply-chain defense after the Shai-Hulud worm, reviewing agent plugins, securing a multi-tenant MCP server on the stateless spec, and shipping synthetic-content provenance now that EU and California transparency rules are enforceable) and now runs continuously Q1-Q128.

## Before You Start

This folder assumes you already write production code and know LLM basics (tokens, context windows, embeddings, what RAG is). If those are shaky, spend a week in [01-foundations](../01-foundations/) and the [Courses guide](../COURSES.md) first; interview prep on top of missing fundamentals produces fluent-sounding wrong answers, which is the worst possible outcome in a senior loop.

The files in this folder are designed to be read in order. Each builds on the last: questions teach the surface area, frameworks teach how to structure answers, pitfalls teach what kills offers, exercises rehearse the motion, behavioral covers the staff-level signal, and job-market trends cover the current hiring landscape.

## Read in Order

```mermaid
flowchart TD
    A[Start prep] --> B{Time available}
    B -->|2 weeks| C[01 Question Bank]
    B -->|1 week| D[02 Answer Frameworks]
    B -->|3 days| E[03 Common Pitfalls]
    C --> F[02 Answer Frameworks]
    D --> G[04 Whiteboard Exercises]
    F --> G
    E --> G
    G --> H[05 Behavioral]
    H --> I[06 Job Market Trends 2026]
    I --> J[Interview day]
```

## Role-Specific Prep Paths

```mermaid
mindmap
  root((Role Prep))
    AI Engineer IC
      Question Bank Q1 to Q49
      Answer Frameworks
      Whiteboard exercises
    Staff or Principal
      Advanced sets Q50 to Q128
      Behavioral STAR-L
      Eval and memory exercises
    Applied Scientist
      Model Selection questions
      Evaluation questions
      Optimization questions
    PM or TPM for AI
      Common Pitfalls
      Job Market Trends 2026
      Answer Frameworks
```

## Files in This Folder

| File | Purpose |
|------|---------|
| [01-question-bank.md](01-question-bank.md) | 128 real interview questions (Q1-Q128, continuously numbered) grouped by topic, with model answers and follow-ups (through August 2026). |
| [02-answer-frameworks.md](02-answer-frameworks.md) | Five structured answer frameworks (SPIDER, ETA, tradeoff, debugging, STAR-L) plus a worked 45-minute SPIDER mock-interview transcript. |
| [03-common-pitfalls.md](03-common-pitfalls.md) | Patterns that kill staff-level offers: hand-waving on tradeoffs, missing observability, ignoring failure modes. |
| [04-whiteboard-exercises.md](04-whiteboard-exercises.md) | Nine system design exercises with worked solutions, including evaluation pipeline design and agent memory. The closest simulation of a real loop. |
| [05-behavioral-for-ai-roles.md](05-behavioral-for-ai-roles.md) | Behavioral prep for AI-specific scenarios with six worked STAR-L examples, compensation and leveling questions, and an out-loud practice guide. |
| [06-job-market-trends-2026.md](06-job-market-trends-2026.md) | Role taxonomy, comp ranges, interview process patterns, and emerging titles (FDE, AI Eval Engineer, AI Reliability Engineer, MCP Engineer). |
| [07-faq.md](07-faq.md) | Short, direct answers to the most-asked questions about AI engineering, RAG, agents, models, eval, inference, memory, and security. Useful for quick reference and for newcomers to the field. |

## Companion Resources

- [Role Transition Guide](../TRANSITION_GUIDE.md) for prepping from backend, frontend, QA, PM, or EM into AI.
- [Recommended Courses](../COURSES.md) for foundational learning before interview prep.
- [Glossary](../GLOSSARY.md) for quick term definitions during prep.
- [Case Studies](../16-case-studies/) for production architectures that map directly to whiteboard prompts.

## Key Takeaways

- The files are designed to be read in order; jumping straight to questions without absorbing answer frameworks leaves answers unstructured.
- Whiteboard exercises (file 04) are the closest simulation to real interviews; do at least three before any loop.
- Behavioral prep (file 05) is what separates staff candidates from senior candidates; do not skip it.
- The August 2026 job market chapter (file 06) is a moat: candidates who know the hiring landscape can ask better questions and tailor stories.
- Recheck this folder monthly; new question batches are added as hiring trends shift.
