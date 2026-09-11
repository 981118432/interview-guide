# Model Taxonomy

This chapter provides a comprehensive guide to the model landscape as of **August 2026**, covering model families, capabilities, and selection criteria for production systems.

> **Last verified: August 15, 2026.** The model landscape evolves rapidly. Always cross-check with provider pricing pages and release notes.
>
> **August 2026 headline:** Most of the month's releases were post-training refreshes or derivatives rather than new pretraining runs, and no US frontier lab shipped a new flagship base model. The action moved to prices, licenses, and access control. The clear exception is Alibaba's Qwen3.8-Max, a genuinely new 2.4T base whose weights landed August 12. **Claude Sonnet 5's introductory $2/$10 per 1M became the permanent price on August 10**, and the scheduled September 1 rise to $3/$15 was canceled, making Sonnet 5 permanently cheaper than the Sonnet 4.6 it replaced. Running the other way, **DeepSeek raises V4 prices 3x to 12x effective August 16 at 16:00 UTC**, moving to peak and off-peak billing (off-peak is exactly half peak, and peak covers only 01:00-04:00 and 06:00-10:00 UTC). That ends its run as the unambiguous cheap option. **OpenAI shipped GPT-5.6-Cyber** (August 10, $12.50/$75 per 1M) behind a new two-tier Daybreak Blue and Daybreak Red access program, the most concrete production example yet of capability-tiered gating. **Google released Gemini 3.7 Flash** (August 13) at half price through year-end, and **SpaceXAI released Grok 4.6** (August 12) with a 500K context. On open weights the licensing picture split: **Alibaba's Qwen3.8-Max** (August 12, 2.4T/95B active) shipped under a bespoke commercially gated license while its **Qwen3.8-27B** sibling (August 14) shipped plain Apache 2.0, **Meta returned to open weights with Muse Glimmer** (August 10, 30B, Apache 2.0), and **Z.ai withheld GLM-5.3's weights** pending safety evaluation after cyber capability grew faster than expected. **Claude Opus 4.1 retired on August 5**, closing out the last $15/$75 Opus tier. Benchmark figures throughout this section are largely vendor-reported; confirm on independent leaderboards.
>
> **July 2026 headline:** Anthropic shipped a full generation refresh: **Claude Sonnet 5** (June 30, `claude-sonnet-5`, new default everywhere, introductory $2/$10 per 1M through August 31 then $3/$15) and **Claude Opus 5** (July 24, `claude-opus-5`, unchanged $5/$25 with an optional Fast mode at $10/$50 about 2.5x faster). **Claude Fable 5 was restored globally July 1** after the export-control suspension, with a new jailbreak-specific cybersecurity classifier; Mythos 5 returned only to roughly 100 US critical-infrastructure organizations via Project Glasswing. **GPT-5.6 (Sol, Terra, Luna) reached general availability July 9**, and on July 30 OpenAI cut Luna 80% to $0.20/$1.20 and Terra 20% to $2/$12 (Sol stays $5/$30). The open-weight frontier had its strongest month ever: **Moonshot Kimi K3** (July 16, weights July 27) is the largest open-weight model to date at 2.8T total / 104B active with a 1M context, and **Thinking Machines Lab** debuted **Inkling** (July 15, 975B / 41B active, open weights), the leading US open-weights model. Google shipped **Gemini 3.6 Flash**, **3.5 Flash-Lite**, and a government-gated **3.5 Flash Cyber** (July 21) while delaying Gemini 3.5 Pro. **Meta Muse Spark 1.1** (July 9) arrived with Meta's first paid self-serve model API ($1.25/$4.25 per 1M). Black Forest Labs announced **FLUX 3** (July 23), a unified image, video, audio, and action model, in gated early access. Benchmark figures across these launches are largely vendor-reported; confirm on independent leaderboards.
>
> **June 2026 headline:** Anthropic released **Claude Fable 5** (June 9, `claude-fable-5`, $10/$50 per 1M, 1M context), its most capable widely released model: a Mythos-class model made safe for general availability, with an Opus 4.8 fallback safeguard on sensitive topics. **Claude Mythos 5** ships the same day as the unrestricted variant for Project Glasswing partners, succeeding Mythos Preview at less than half its price.
>
> **June 10-26 update:** A dense second wave of June launches followed. **Google DeepMind DiffusionGemma** (June 10, Apache 2.0) is Google DeepMind's first open-weight text-diffusion model: a 26B Mixture-of-Experts (~4B active) that denoises blocks of tokens in parallel for roughly 4x faster generation on a single H100, trading some quality versus standard Gemma 4. **Gemini 3.5 Live Translate** (June 9, built on Gemini 3 Pro) added real-time speech-to-speech translation across 70+ languages in public preview via the Gemini Live API and AI Studio. **Cohere North Mini Code 1.0** (June 9, Apache 2.0) is Cohere's first open coding model, a 30B / 3B-active MoE that runs on one H100. **Moonshot Kimi K2.7 Code** (June 12, Modified MIT) tunes K2.6 for long-horizon software work (1T / 32B-active MoE, roughly 30% fewer thinking tokens). **Z.ai GLM-5.2** (coding-plan access June 13, open weights under MIT June 16-17) is a 744B / 40B-active MoE with a 1M context that reports SWE-Bench Pro 62.1, ahead of GPT-5.5 on that benchmark, at roughly $1.40 / $4.40 per 1M. **xAI Grok Imagine Video 1.5** reached general availability June 16 (image-to-video with synchronized audio, $0.080 per second of video), and **Grok 4.3** arrived on Amazon Bedrock June 15 ($1.25 / $2.50 per 1M, xAI's first model there). Alibaba's official Qwen Cloud changelog lists a June snapshot adding vision to **Qwen 3.7-Max** (text-only at its May launch), though some independent coverage attributes that vision update to Qwen 3.7-Plus instead, so verify before relying on it. Separately, on June 12 Anthropic suspended access to Claude Fable 5 and Claude Mythos 5 following a US export-control directive, with Mythos 5 later cleared for a limited set of US institutions. Then on June 26, OpenAI previewed **GPT-5.6** (Sol, Terra, and Luna), its next-generation line, in a limited release to a small set of US-government-approved partners over dual-use cybersecurity concerns, echoing the Anthropic restriction; Sol claims a new Terminal-Bench 2.1 record and Terra targets GPT-5.5-level quality at about half the cost. Coding scores here are largely vendor-reported; confirm on independent leaderboards.
>
> **May 2026 recap:** Anthropic Claude Opus 4.8 (May 28, same $5/$25 price as Opus 4.7; Dynamic Workflows research preview with hundreds of parallel subagents; fast mode at $10/$50 is 3x cheaper than the Opus 4.7 fast mode); OpenAI GPT-5.5 (April 23) and GPT-5.5 Instant (May 5, default in ChatGPT); Claude Opus 4.7 (April 16, GA on Bedrock/Vertex/Foundry); Google Gemma 4 (April 2, Apache 2.0) and Gemini 3.2 Flash (quiet rollout May 5); DeepSeek V4 Pro and V4 Flash (April 24; 75% V4 Pro discount made **permanent** May 22, new list price $0.435/$0.87 per 1M from June 1); Moonshot Kimi K2.6 (April 20, 1T MoE / 32B active); Alibaba Qwen 3.6 Plus / 3.6-35B-A3B / 3.6 Max-Preview; Mistral Medium 3.5 (April 29, unified chat/reasoning/coding/vision); Meta Muse Spark (April 8, first closed-weight Meta model); Llama 4 Behemoth release paused through fall 2026 amid capability concerns. SWE-bench Verified published leaders before the Fable 5 launch: Claude Mythos Preview 93.9%, GPT-5.5 88.7%, Claude Opus 4.8 88.6%; ARC-AGI-2 leader: GPT-5.5 at 85.0%. Anthropic describes Fable 5 as state of the art on nearly all tested benchmarks; standard numeric scores were not in the launch post, so verify on the leaderboards.

## Table of Contents

- [Model Categories](#model-categories)
- [Frontier Models (May 2026)](#frontier-models)
- [Reasoning Models](#reasoning-models)
- [Open Source Models](#open-source-models)
- [Specialized Models](#specialized-models)
- [Embedding Models](#embedding-models)
- [Model Selection Framework & Semantic Routing](#model-selection-framework)
- [Sovereign AI & Data Residency](#sovereign-ai-and-data-residency)
- [Capability Comparison](#capability-comparison)
- [Interview Questions](#interview-questions)
- [References](#references)

---

## Model Categories

### By Capability Level (April 2026 Reality)

| Tier | Characteristics | Examples | Use Case |
|------|-----------------|----------|----------|
| **Frontier** | State-of-the-art reasoning, agentic mastery | Claude Fable 5, Claude Opus 4.8, GPT-5.5, Gemini 3.1 Pro, Grok 4.3 | Complex reasoning, coding, production agents |
| **Fast/Efficient** | Sub-200ms, cost-optimized | Gemini 3.1 Flash, GPT-5.5-mini, Claude Haiku 4.5, DeepSeek V4 Flash | High-volume streaming, UI, real-time |
| **Battle-Tested** | Mature, widely-deployed, stable | Claude Sonnet 4.6, GPT-5.5 Instant, Gemini 3.1 Pro | Enterprise production workloads |
| **Small/Edge** | Private, edge, specialized | Llama 4 Scout, Mistral Small 4, Phi-4 | Local privacy, on-device, MoE-efficient |
| **Reasoning-Heavy** | Extended internal CoT | Claude Opus 4.8 (thinking), GPT-5.5 reasoning, Gemini 3.1 Pro Deep Think, DeepSeek-R1 | Math, code debug, multi-step logic |

### By Reasoning Mode (2025–2026)

| Mode | Capability | Models | Use Case |
|------|------------|--------|----------|
| **Standard** | Fast, intuitive response | GPT-5.5-mini, Claude Sonnet 4.6 | Chat, simple extraction |
| **Extended Thinking** | Internal scratchpad CoT before output | Claude Opus 4.8, GPT-5.5 reasoning, DeepSeek-R1 | Math, code debugging, planning |
| **Hybrid** | User-controllable reasoning depth | Claude Opus 4.8, GPT-5.5 | Variable complexity tasks |

---

## Frontier Models (June 2026)

### Claude Opus 5 (Anthropic) - July 2026 NEW

| Attribute | Value |
|-----------|-------|
| Model ID | `claude-opus-5` |
| Context Window | 1M tokens (default and max; 128K max output) |
| Input / Output Cost | $5.00 / $25.00 per 1M (unchanged from Opus 4.8) |
| Fast mode | $10.00 / $50.00 per 1M, about 2.5x faster |
| Benchmarks | Anthropic's launch post, reporting the pre-release benchmark it called Frontier-Bench v0.1 (since renamed Terminal-Bench 3.0): 43.3% at max effort vs GPT-5.6 Sol's 34.4%, Fable 5's 33.7%, and Opus 4.8's 18.7%. Within 0.5% of Fable 5 on CursorBench 3.2 at about half the cost per task; roughly 3x the next-best model on ARC-AGI 3. Vendor-reported. |
| Released | July 24, 2026 (Claude API, Claude Code, Claude Cowork; new default on Claude Max) |

**What it is:** The Opus line's generational successor at unchanged pricing, aimed at long-horizon agentic coding and computer use. Beta features include mid-conversation tool changes and automatic fallback routing. The dual-price Fast mode continues the pattern Opus 4.8 introduced: one model, two latency tiers.

**Best for:** Agentic coding and computer-use workloads where Fable 5's ceiling is not needed; the price-performance flagship of the Claude line as of late July 2026.

### Claude Sonnet 5 (Anthropic) - July 2026 NEW

| Attribute | Value |
|-----------|-------|
| Model ID | `claude-sonnet-5` |
| Context Window | 1M tokens per third-party coverage (not stated in the launch post) |
| Input / Output Cost | $2.00 / $10.00 per 1M (permanent since August 10, 2026) |
| Cache / Batch | Cache write $2.50 per 1M (5 min) or $4.00 (1 hr); cache hit $0.20; Batch API $1.00 / $5.00 |
| Positioning | The most agentic Sonnet yet: planning, browser and terminal tool use, autonomous operation approaching Opus 4.8 at lower cost |
| Safety posture | Cyber safeguards on by default; deliberately reduced cybersecurity capability relative to Opus-class models |
| Released | June 30, 2026 (default model across consumer and developer products same day) |

**What it is:** The new production workhorse, replacing Sonnet 4.6 as the default. On August 10, 2026 Anthropic made the introductory $2/$10 rate permanent and canceled the September 1 increase to $3/$15, so Sonnet 5 is permanently cheaper than the Sonnet 4.6 it succeeds (still $3/$15). Cost models built on the reversion assumption should be revised down.

**Best for:** Production agent fleets, coding at scale, and the default tier in cost-aware routing stacks.

### Claude Fable 5 (Anthropic) - June 2026 NEW

| Attribute | Value |
|-----------|-------|
| Model ID | `claude-fable-5` |
| Context Window | 1M tokens (Opus 4.7 tokenizer; roughly 30% more tokens than pre-4.7 models for the same text) |
| Max Output | 128K tokens |
| Input Cost | $10.00 / 1M tokens |
| Output Cost | $50.00 / 1M tokens |
| Thinking | Adaptive thinking, always on (no separate extended-thinking toggle) |
| Multimodal | Text + Vision (new state of the art on vision tasks per Anthropic) |
| Benchmarks | State of the art on nearly all tested benchmarks per Anthropic; highest frontier score on Cognition's FrontierCode, highest on the Hebbia Finance Benchmark, ViBench, and CursorBench. Standard numeric scores (SWE-bench, GPQA) were not published in the launch post. |
| Released | June 9, 2026 (GA on Claude API, Claude Platform on AWS, Amazon Bedrock, Vertex AI, Microsoft Foundry) |

**What it is:** A Mythos-class model made safe for general availability. Until now the Mythos line (SWE-bench Verified 93.9% on Mythos Preview) was restricted to ~11 Project Glasswing partners over dual-use cybersecurity concerns. Fable 5 brings that capability tier to everyone by pairing it with conservative safeguards.

**The Opus 4.8 fallback safeguard:** When Fable 5's classifiers detect a request in one of three categories (offensive cyber techniques, bioweapon-adjacent biology and chemistry, or attempts to distill the model), the response is silently delegated to **Claude Opus 4.8** and the user is informed. Anthropic says this triggers in under 5% of sessions and is deliberately tuned conservative, so some harmless requests get caught. Architecturally this is a production example of **model-tier routing as a safety control**, not just a cost control.

**Best for:** The most demanding reasoning, long-horizon agentic work, vision-heavy tasks, and workloads where capability ceiling matters more than unit cost. Anthropic reports it sustains autonomous operation longer than any previous Claude model.

**Considerations:** 2x the per-token price of Opus 4.8 ($10/$50 vs $5/$25), so route only ceiling-bound work to it. Mythos-class traffic carries a 30-day data retention requirement (not used for training; access-logged; deleted after 30 days in almost all cases), which matters for compliance reviews. On subscription plans it was included at no extra cost June 9-22, then moved to usage credits. There is no Fable-tier fast mode or published cache/batch discount at launch; check the pricing page.

### Claude Mythos 5 (Anthropic) - RESTRICTED ACCESS

| Attribute | Value |
|-----------|-------|
| Model ID | `claude-mythos-5` |
| Status | Limited availability: Project Glasswing partners and select biology researchers |
| Relationship | Same underlying model as Fable 5 with safeguards lifted in some areas |
| Pricing | $10 / $50 per 1M (less than half of Mythos Preview) |
| Released | June 9, 2026 |

**Why it matters:** Succeeds Claude Mythos Preview at comparable or somewhat stronger capability and much lower price. The Fable/Mythos split formalizes a two-track release pattern: one safeguarded general release, one unrestricted release for vetted defenders.

### Claude Opus 4.8 (Anthropic) - May 2026

| Attribute | Value |
|-----------|-------|
| Context Window | 1M tokens (standard pricing across the full window) |
| Input Cost | $5.00 / 1M tokens (same as 4.7) |
| Output Cost | $25.00 / 1M tokens (same as 4.7) |
| Cache: 5m write | $6.25 / 1M tokens |
| Cache: 1h write | $10.00 / 1M tokens |
| Cache: hit / refresh | $0.50 / 1M tokens |
| Batch API | $2.50 / $12.50 per 1M (50% discount) |
| Fast mode (research preview) | $10 / $50 per 1M (about 2.5x faster; 3x cheaper than the Opus 4.7 fast mode which was $30 / $150) |
| Extended Thinking | Native, adaptive mode |
| Multimodal | Text + Higher-resolution Vision |
| SWE-bench Verified | 88.6% |
| SWE-Bench Pro | 69.2% (up from 64.3% on Opus 4.7) |
| Terminal-Bench 2.1 | 74.6% (GPT-5.5 still leads at 78.2%) |
| GDPval-AA | 1890 Elo (up from 1753 on Opus 4.7) |
| OSWorld-Verified | 82.3% |
| Online-Mind2Web | 84% |
| Released | May 28, 2026 (GA on Claude API, AWS Bedrock, Vertex AI) |

**Best for:** Long-running autonomous coding work in Claude Code, codebase-scale migrations, agentic workflows that need parallel subagents, and workloads where the alignment and honesty gains matter.

**Key features over Opus 4.7:**
- **Dynamic Workflows** (research preview): Claude plans the work and runs hundreds of parallel subagents in a single Claude Code session, verifies their outputs, and reports back. Suited for codebase-scale migrations across hundreds of thousands of lines.
- **Mid-task system messages**: The Messages API now accepts system messages mid-conversation, useful for steering long agent runs without ending the session.
- **Optional fast mode** at roughly 2.5x speed for $10 / $50 per 1M, priced 3x lower than the Opus 4.7 fast mode.
- **Effort-control toggle** in `claude.ai` and Cowork lets users tune reasoning depth per turn.
- **Expanded Claude Code rate limits**.

**Considerations:** Tokenizer is the same one introduced in Opus 4.7 (up to 35% more tokens than the pre-4.7 tokenizer for the same fixed text). GPT-5.5 still holds the SWE-Bench Verified leaderboard at 88.7% and leads Terminal-Bench 2.1 at 78.2%. GPQA Diamond slipped 0.6 pts versus Opus 4.7. Anthropic's tokenizer change means token counts and bills for the same text are not directly comparable to pre-4.7 models. There was no Claude Sonnet 4.8; the line jumped to **Claude Sonnet 5** on June 30, 2026, which replaced Sonnet 4.6 as the production workhorse.

> [!NOTE]
> **Retired August 5, 2026:** `claude-opus-4-1-20250805` was removed from the Claude API, closing out the last $15/$75 per 1M Opus tier. Every first-party Anthropic Opus SKU is now $5/$25 (or $10/$50 in Fast mode). The model remains available on Amazon Bedrock and Google Cloud, which set their own retirement schedules, so code pinned to that ID fails on the first-party API while still working on the partner clouds.

### Claude Opus 4.7 (Anthropic)

| Attribute | Value |
|-----------|-------|
| Context Window | 1M tokens |
| Max Output | 128K tokens |
| Input Cost | $5.00 / 1M tokens (same as 4.6) |
| Output Cost | $25.00 / 1M tokens (same as 4.6) |
| Extended Thinking | Native, Adaptive mode |
| Multimodal | Text + Higher-resolution Vision |
| SWE-bench Verified (Adaptive) | 87.6% (May 13, 2026) |
| Released | April 16, 2026 (GA on API, Bedrock, Vertex, Microsoft Foundry) |

**Best for:** Autonomous coding agents (powers Claude Code), multi-file refactors, complex reasoning. Same pricing as 4.6 - straight upgrade for most workloads.
**Considerations:** Use Sonnet 4.6 for cost-sensitive workloads; Opus 4.7 mainly for tasks requiring peak coding/agentic quality.

### Claude Mythos Preview (Anthropic) - SUCCEEDED BY MYTHOS 5

| Attribute | Value |
|-----------|-------|
| Status | Restricted research preview, Project Glasswing partners only (~11 orgs: AWS, Apple, Cisco, Google, Microsoft, NVIDIA, Palo Alto, etc.) |
| Reason for restriction | Dual-use cybersecurity capabilities |
| SWE-bench Verified | 93.9% (May 13, 2026; the published SOTA before the Fable 5 / Mythos 5 launch) |
| Released | April 7, 2026 (restricted partner preview); succeeded by Claude Mythos 5 on June 9, 2026 at less than half the price |

**Best for:** Historical reference. Its capability tier reached general availability as Claude Fable 5 on June 9, 2026; new Glasswing work should target Mythos 5.

### Claude Opus 4.6 (Anthropic)

| Attribute | Value |
|-----------|-------|
| Context Window | 1M tokens |
| Max Output | 128K tokens |
| Input Cost | $5.00 / 1M tokens |
| Output Cost | $25.00 / 1M tokens |
| Extended Thinking | Native adaptive thinking (configurable budget_tokens) |
| Multimodal | Text + Vision |
| Highlights | Most capable Anthropic model; exceptional coding and reasoning |
| Released | February 2026 |

**Best for:** Most complex reasoning, autonomous software engineering, agentic workflows.
**Considerations:** Premium pricing; use Sonnet 4.6 for tasks that don't need peak capability.

### Claude Sonnet 4.6 (Anthropic)

| Attribute | Value |
|-----------|-------|
| Context Window | 1M tokens |
| Input Cost | $3.00 / 1M tokens |
| Output Cost | $15.00 / 1M tokens |
| Extended Thinking | Supported |
| Multimodal | Text + Vision |
| Highlights | Handles tasks previously requiring Opus tier; best cost/quality balance |
| Released | February 2026 |

**Best for:** Production coding agents (powers Claude Code), complex reasoning at scale.
**Considerations:** Now covers most Opus-level tasks at lower cost. Strong default for most workloads.

### GPT-5.4 (OpenAI)

| Attribute | Value |
|-----------|-------|
| Context Window | 272K tokens (standard); extended available |
| Input Cost | $2.50 / 1M tokens |
| Output Cost | $15.00 / 1M tokens |
| Multimodal | Text, Vision, native computer use |
| Highlights | Built-in computer-use capabilities; 33% fewer factual errors vs GPT-5.2; combines coding + agentic strengths |
| Released | March 2026 |

**Best for:** Agentic workflows with computer use, coding, professional tasks.
**Considerations:** Long-context pricing doubles at 272K+ tokens.

### GPT-5.4-mini (OpenAI)

| Attribute | Value |
|-----------|-------|
| Context Window | 272K tokens |
| Input Cost | $0.75 / 1M tokens |
| Output Cost | $4.50 / 1M tokens |
| Highlights | Best cost/performance for high-volume GPT-5 tier workloads |
| Released | March 2026 |

**Best for:** High-volume API calls, cost-optimized reasoning, production chatbots.

### GPT-5.4 Pro (OpenAI)

| Attribute | Value |
|-----------|-------|
| Context Window | 272K tokens |
| Input Cost | $30.00 / 1M tokens |
| Output Cost | $180.00 / 1M tokens |
| Highlights | Maximum reasoning power; premium tier for hardest tasks |
| Released | March 2026 |

**Best for:** Competition-level math, complex multi-step reasoning.
**Considerations:** Very expensive; use standard GPT-5.4 or mini for volume.

### GPT-5.6 Sol / Terra / Luna (OpenAI) - GA July 9, 2026

| Attribute | Value |
|-----------|-------|
| Variants | Sol (flagship), Terra (balanced), Luna (fast, low cost) |
| Context Window | 1M tokens (all three); 128K max output; knowledge cutoff February 16, 2026 |
| Sol pricing | $5.00 / $30.00 per 1M |
| Terra pricing | $2.00 / $12.00 per 1M (cut 20% from $2.50/$15 on July 30) |
| Luna pricing | $0.20 / $1.20 per 1M (cut 80% from $1/$6 on July 30) |
| Reasoning | "max" reasoning effort plus an "ultra" mode that uses subagents to accelerate complex work |
| API features at GA | Programmatic tool calling, multi-agent support, explicit prompt-cache breakpoints |
| Benchmarks | Sol: 53.6 on Agents' Last Exam (13.1 points ahead of Claude Fable 5) and a Terminal-Bench 2.1 record. Claude Fable 5 still leads SWE-Bench Pro (80 vs Sol's 64.6), a benchmark OpenAI publicly disputes. Vendor-reported. |
| Released | Limited preview June 26, 2026; general availability July 9, 2026 |

**What it is:** OpenAI's next-generation flagship line, shipped for the first time as three models. The June 26 preview was gated at the request of the US government over dual-use cybersecurity capability; GA followed a 13-day review. The three-tier structure plus the steep July 30 cuts (Luna at $0.20/$1.20 is priced against open-weight competition) reset the routing math for anyone doing tiered model selection.

**Best for:** Sol for frontier agentic work and cybersecurity-adjacent coding; Terra as the GPT-5.5-class production default at roughly half GPT-5.5's price; Luna for high-volume classification, extraction, and routing tiers.

### GPT-5.6-Cyber (OpenAI) - August 2026 NEW (restricted)

| Attribute | Value |
|-----------|-------|
| Model ID | `gpt-5.6-cyber` |
| Context Window | 400K total (272K max input, 128K max output) |
| Input / Output Cost | $12.50 / $75.00 per 1M; cached input $1.25 |
| Access | Daybreak Red tier only, with identity verification, legal attestations, and approved use cases. Responses API only. Hardware security keys become mandatory on individual Daybreak accounts from September 1, 2026 |
| Refusal posture | Trained for a lower refusal rate on dual-use security work: 95.0% completion on OpenAI's internal Advanced Cybersecurity Completion Rate eval versus 1.5% for GPT-5.6 Sol |
| Released | August 10, 2026 (the Daybreak Blue and Red tier split appears in the API changelog dated August 7) |

**What it is:** A cybersecurity model built on GPT-5.6 Sol, shipped alongside a split of the Daybreak program into two tiers. **Daybreak Blue** gives approved defenders access to general-purpose frontier models for vulnerability discovery, secure code review, detection engineering, and incident response. **Daybreak Red** is separately approved and gates `gpt-5.6-cyber` for vulnerability reproduction, exploit validation, penetration testing, and red teaming.

**Why it matters architecturally:** This is the clearest production instance of capability-tiered gating to date. A model that is deliberately *more* permissive than the frontier default, priced at 2.5x Sol, restricted to a single API surface, and fenced behind identity verification plus mandatory hardware 2FA is a reference design for how labs are operationalizing dual-use access. Compare with Anthropic's Fable 5 and Mythos 5 split and Google's Gemini 3.5 Flash Cyber: three labs, three variations on the same tiering pattern.

### GPT-5.5 (OpenAI) - May 2026 NEW

| Attribute | Value |
|-----------|-------|
| Context Window | 1M tokens |
| Input Cost | $5.00 / 1M tokens |
| Output Cost | $30.00 / 1M tokens |
| Multimodal | Text, Image, Audio, Video |
| ARC-AGI-2 | 85.0% (May 13, 2026 - leader) |
| Released | April 23, 2026 |

**Best for:** Highest-quality multimodal workloads; current ARC-AGI-2 leader. Pitched as "new class of intelligence for real work" - replaces GPT-5.4 for top-tier reasoning + multimodal.
**Considerations:** ~2× the input cost of GPT-5.4 ($2.50 → $5.00) and ~2× output ($15 → $30). Use GPT-5.5 Instant for chat workloads where the price isn't justified.

### GPT-5.5 Instant (OpenAI) - May 2026 NEW

| Attribute | Value |
|-----------|-------|
| Status | Default in ChatGPT and `chat-latest` in API since May 5, 2026 |
| Hallucination Reduction | 52.5% fewer on high-stakes prompts (medicine/law/finance) vs GPT-5.3 Instant |
| AIME 2025 | 81.2% (up from 65.4% on GPT-5.3 Instant) |
| Response Length | ~30% fewer words/lines than predecessor |
| Released | May 5, 2026 |

**Best for:** Default ChatGPT-equivalent workloads, instant chat, high-stakes domains where hallucination reduction matters.
**Considerations:** Replaces GPT-5.3 Instant as the chat default. GPT-5.2-chat-latest and GPT-5.3-chat-latest deprecated May 8, 2026.

### GPT-Realtime-2, Translate, Whisper (OpenAI) - May 2026 NEW

| Attribute | Value |
|-----------|-------|
| Capability | Realtime voice with GPT-5-class reasoning |
| Translate Coverage | 70+ input → 13 output languages |
| Pricing | $32 / $64 per 1M audio tokens (input/output) |
| Released | May 7, 2026 |

**Best for:** Real-time voice agents, multilingual translation, voice-first products. Realtime API Beta was removed May 12, 2026 - Realtime-2 is the supported path.

### Gemini 3.1 Pro (Google)

| Attribute | Value |
|-----------|-------|
| Context Window | 1M tokens |
| Input Cost | $2.00 / 1M tokens (standard); $4.00 (200K+) |
| Output Cost | $12.00 / 1M tokens (standard); $18.00 (200K+) |
| Multimodal | Native: Text, Vision, Audio, Video |
| Highlights | State-of-the-art Google reasoning; powerful agentic and coding capabilities |
| Released | February 2026 |

**Best for:** Complex reasoning, multimodal analysis, long-context workloads.
**Considerations:** Replaced Gemini 3 Pro Preview. Gemini 2.5 Pro/Flash deprecated June 2026.

### Gemini 3.1 Flash (Google)

| Attribute | Value |
|-----------|-------|
| Context Window | 1M tokens |
| Input Cost | $0.10 / 1M tokens |
| Output Cost | $3.00 / 1M tokens |
| Multimodal | Native: Text, Vision, Audio, Video |
| Highlights | Fastest Google model; best price/performance for high-volume |
| Released | March 2026 |

**Best for:** Real-time multimodal apps, high-volume pipelines, long-context RAG.

### Gemini 3.2 Flash (Google) - May 2026 NEW

| Attribute | Value |
|-----------|-------|
| Status | Quiet rollout in iOS Gemini app and Google AI Studio May 5, 2026 (no formal announcement yet) |
| Released | May 5, 2026 |

**Best for:** Likely successor to 3.1 Flash for high-volume workloads. Treat as preview - pricing and full capability disclosure pending official launch.

### Gemini Deep Research / Deep Research Max (Google) - May 2026 NEW

| Attribute | Value |
|-----------|-------|
| Built on | Gemini 3.1 Pro |
| Capabilities | MCP support; native chart/infographic generation; extended test-time compute; async background workflows |
| Released | April 21, 2026 |

**Best for:** Research agents, document synthesis, long-running async workflows. The MCP support makes it the first Google research-agent product with first-class tool integration.

### Gemini Robotics-ER 1.6 (Google DeepMind) - May 2026 NEW

| Attribute | Value |
|-----------|-------|
| Domain | Physical robotics, embodied reasoning |
| New capability | Reading gauges/sight glasses |
| Deployment | Boston Dynamics Spot |
| Released | April 14, 2026 |

**Best for:** Robotics applications requiring vision-language grounding for physical actions. Available via Gemini API and AI Studio.

### Gemini 3.7 Flash (Google) - August 2026 NEW

| Attribute | Value |
|-----------|-------|
| Model ID | `gemini-3.7-flash` |
| Context Window | 1,048,576 tokens in / 65,536 out |
| Input / Output Cost | $0.75 / $3.75 per 1M through December 31, 2026, then $1.50 / $7.50. Context caching $0.075 per 1M; Batch $0.375 / $1.875 |
| Multimodal | Text, image, audio, video; first Gemini model with agentic video processing on by default |
| Knowledge cutoff | March 2026 |
| Released | August 13, 2026 (GA) |

**What it is:** Google's workhorse tier, built on Gemini 3.6 Flash with what the model card describes as algorithmic improvements to the reasoning foundation rather than a new pretraining run. Customizable thinking configurations trade quality against cost and latency per request. Google-reported gains over 3.6 Flash include FrontierCode 1.1 Main 43.6% versus 34.4% and WebDev Arena Elo 1588 versus 1538.

**Considerations:** The half-price introductory rate expires December 31, 2026 and then doubles, so run cost models against the January 2027 numbers before committing to volume. Gemini 3.5 Pro still has not shipped as of mid-August; `gemini-3.1-pro-preview` remains Google's top Pro-tier entry.

### Grok 4.6 (SpaceXAI) - August 2026 NEW

| Attribute | Value |
|-----------|-------|
| Model ID | `grok-4.6` |
| Context Window | 500K tokens |
| Input / Output Cost | $2.00 / $6.00 per 1M below a 200K prompt; $4.00 / $12.00 at or above 200K. Cached input $0.50 |
| Reasoning | Effort settings low, medium, high (default), xhigh |
| Knowledge cutoff | February 1, 2026 |
| Released | August 12, 2026 |

**What it is:** SpaceXAI's frontier model, focused on long-running agents and interactive visual work. Artificial Analysis Intelligence Index 61, up from 56 for Grok 4.5 High.

**Two traps worth knowing.** The higher long-prompt rate applies to *all* tokens in the request once the prompt reaches 200K, not just the tokens past the threshold. And cached input got more expensive than Grok 4.5 ($0.50 versus $0.30 per 1M), so cache-heavy agent loops do not automatically get cheaper on the upgrade. Note the vendor name: xAI completed a rebrand to SpaceXAI, so current docs and release notes use the new name.

### Grok 4 (xAI)

| Attribute | Value |
|-----------|-------|
| Context Window | 256K tokens |
| Input Cost | $3.00 / 1M tokens |
| Output Cost | $15.00 / 1M tokens |
| Highlights | Native tool use and real-time search; competitive reasoning |
| Released | July 2025 (Grok 4.20 beta: February 2026) |

**Best for:** Live web research, reasoning-heavy tasks, real-time X/web integration.
**Considerations:** Grok 4.1 Fast available at $0.20/$0.50 for high-volume.

### Model Comparison: Frontier Tier (June 2026)

| Model | Reasoning | Coding | Context | Agentic | Cost |
|-------|-----------|--------|---------|---------|------|
| Claude Fable 5 | ★★★★★ | ★★★★★ | ★★★★★ | ★★★★★ | $$$$$ |
| Claude Mythos 5 (restricted) | ★★★★★ | ★★★★★ | ★★★★★ | ★★★★★ | $$$$$ |
| Claude Opus 4.8 | ★★★★★ | ★★★★★ | ★★★★★ | ★★★★★ | $$$$ |
| Claude Opus 4.7 | ★★★★★ | ★★★★★ | ★★★★★ | ★★★★★ | $$$$ |
| GPT-5.5 | ★★★★★ | ★★★★★ | ★★★★★ | ★★★★★ | $$$$ |
| Claude Opus 4.6 | ★★★★★ | ★★★★★ | ★★★★★ | ★★★★★ | $$$$ |
| GPT-5.4 | ★★★★★ | ★★★★★ | ★★★★ | ★★★★★ | $$$ |
| Claude Sonnet 4.6 | ★★★★★ | ★★★★★ | ★★★★★ | ★★★★★ | $$$ |
| Gemini 3.1 Pro | ★★★★★ | ★★★★ | ★★★★★ | ★★★★ | $$ |
| Grok 4 | ★★★★ | ★★★★ | ★★★★ | ★★★★ | $$$ |
| GPT-5.4-mini | ★★★★ | ★★★★ | ★★★★ | ★★★ | $ |
| Gemini 3.1 Flash | ★★★ | ★★★ | ★★★★★ | ★★★ | $ |
| GPT-5.5 Instant | ★★★★ | ★★★★ | ★★★★ | ★★★★ | $$ |

### Production Heritage & Maturity

While frontier models lead on benchmarks, many enterprise systems rely on **battle-tested** models:

| Model Family | Production Since | Maturity Note |
|--------------|------------------|---------------|
| **GPT-4o** | May 2024 | Most mature ecosystem; lowest latency variance; highest rate limits. |
| **Claude 3.5 Sonnet / 3.7 Sonnet** | June 2024 | Gold standard for tool-use reliability and structured output. |
| **Gemini 2.5 Pro** | March 2025 | Proven at scale; stable long-context. Being deprecated June 2026 in favor of 3.x. |
| **o1 / o3** | Sept 2024 | Well-understood reasoning model failure modes; o3 superseded o1. |

**Why stay on "older" frontier models?**
1. **Consistency**: New models have "release-window" latency spikes and behavior shifts.
2. **Cost Efficiency**: Previous generation is often 50-80% cheaper after a new release.
3. **Guardrail Tuning**: Security and moderation layers are more refined.

---

## Open Source Models

### Llama 4 Family (Meta) -- NEW April 2026

| Model | Parameters | Context | Architecture | Notes |
|-------|------------|---------|--------------|-------|
| Llama 4 Scout | 17B active / 16 experts (MoE) | 10M | Sparse MoE | Industry-leading 10M context; fits single H100; beats Gemma 3, Gemini 2.0 Flash-Lite |
| Llama 4 Maverick | 17B active / 128 experts (MoE) | 1M | Sparse MoE | Beats GPT-4o and Gemini 2.0 Flash; comparable to DeepSeek V3 at half active params |
| Llama 4 Behemoth | ~288B active (est.) | - | Dense MoE | Still training; outperforms GPT-4.5, Gemini 2.0 Pro on STEM benchmarks |

**Strengths:**
- First Llama generation with Mixture-of-Experts architecture
- Natively multimodal from the ground up (text, image, video input)
- Open weights on Hugging Face; available via Meta AI on WhatsApp, Messenger, Instagram
- Scout's 10M token context window is industry-leading for open models

### Llama 3.x Family (Meta) -- Previous Generation

| Model | Parameters | Context | License | Notes |
|-------|------------|---------|---------|-------|
| Llama 3.3 70B | 70B | 128K | Llama 3.3 | Still widely deployed; strong general model |
| Llama 3.1 405B | 405B | 128K | Llama 3.1 | Largest dense Meta model; being superseded by Llama 4 |

**Note:** Llama 3.x remains widely used in production, but Llama 4 Scout/Maverick offer superior performance with lower active parameter counts thanks to MoE.

### DeepSeek Family

| Model | Parameters | Context | Status | Notes |
|-------|------------|---------|--------|-------|
| **DeepSeek V4 Pro** | 1.6T total / 49B active (MoE) | 1M | GA | Previewed April 24, 2026. Uses ~27% compute / 10% memory of V3.2 at 1M tokens. SWE-bench Verified 80.6%. NIST CAISI evaluation (May 2026) places it ~8 months behind US frontier (Elo ~800). Open weights on Hugging Face. **API: $0.435 / $0.87 per 1M input/output (75% discount made permanent May 22, 2026, effective June 1).** Cache-hit input $0.003625/M. |
| **DeepSeek V4 Flash** | 284B total / 13B active (MoE) | 1M | GA | Smaller-active variant for high-throughput workloads. **API: $0.14 / $0.28 per 1M (cache-hit $0.0028/M).** Cheapest frontier-class 1M-context API as of May 2026. |
| DeepSeek-V3.2 | 671B (MoE) | 128K | Frontier | General-purpose; 98% cache-hit discount ($0.28/$0.42 per 1M base). Largely superseded by V4 Flash for new builds. |
| DeepSeek-V3 | 671B (MoE, 37B active) | 128K | Frontier | GPT-4o level at a fraction of training cost; open weights. |
| DeepSeek-R1 | 671B (MoE) | 128K | Reasoning | Matches o1 on math/code; first open-source reasoning model. |
| DeepSeek-R1-Distill | 7B–70B | - | Reasoning | Distilled to smaller models; cost-efficient reasoning. |

**Key May 2026 context**: DeepSeek V4 Pro (released April 24, with the 75% promotional discount made permanent on May 22) closed the gap with US frontier models on multiple benchmarks at a fraction of the cost. At $0.435 / $0.87 per 1M, V4 Pro is roughly 10x cheaper than Claude Opus 4.7 ($5 / $25) and 5-10x cheaper than GPT-5.5 ($5 / $30) for comparable tasks. V4 Flash drops the floor further to $0.14 / $0.28 per 1M with the same 1M context window. The 98% cache-hit discount on both makes V4 the dominant choice for high-volume RAG and classification workloads where prompts are cache-friendly. DeepSeek R2 (reasoning successor to R1) remains delayed per reports about Huawei Ascend training challenges.

### Moonshot Kimi Family - May 2026 NEW

| Model | Parameters | Context | Notes |
|-------|------------|---------|-------|
| **Kimi K3** | 2.8T total / 104B active (MoE) | 1M | July 16, 2026 NEW (open weights July 27). Largest open-weight model to date. Always-on thinking, multimodal. $3 / $15 per 1M ($0.30 cached input). Artificial Analysis Intelligence Index 57.1, third overall at launch behind Fable 5 and GPT-5.6 Sol; first open model to top WebDev Arena. Moonshot's flagship, superseding K2.7 Code. |
| **Kimi K2.6** | 1T total / 32B active (MoE) | - | Released April 20, 2026. Modified MIT license. Native video input; Agent Swarm scaling to 300 sub-agents and 4,000 coordinated steps. Ties GPT-5.5 on SWE-Bench Pro (58.6%); SWE-bench Verified ~80.2%. |
| **Kimi K2.7 Code** | 1T total / 32B active (MoE) | 256K | June 12, 2026 NEW. Coding-focused build on K2.6 (Modified MIT) with a MoonViT vision encoder. Reports about +21.8% over K2.6 on Moonshot's own Kimi Code Bench v2 with roughly 30% fewer thinking tokens (vendor benchmark). API about $0.95 / $4.00 per 1M. |
| Kimi K2-Thinking-0905 | - | - | First model to hit 100% on AIME 2025 (reasoning variant). |

**Best for:** Long-horizon agent workloads, video understanding, open-weight agent stack alternative to closed frontier.

### Alibaba Qwen 3.x Family - May 2026 NEW

| Model | Parameters | License | Notes |
|-------|------------|---------|-------|
| **Qwen3.8-Max** | 2.4T total / 95B active MoE | Qwen3.8-Max License (gated) | August 12, 2026. 262K context native, extensible to ~1,010,000. Open weights under a bespoke license, not Apache: attribution required above 100M MAU or $20M monthly revenue, and a separate paid license is required for Model-as-a-Service or AI-assistant businesses above $50M aggregate revenue. The open checkpoint is text-input-only; the API version is multimodal. |
| **Qwen3.8-27B** | 27B dense | Apache 2.0 | August 14, 2026. The more permissive *and* more modality-complete artifact: accepts image and video input where the open Max checkpoint does not. 262K context, extensible to ~1M. Dense rather than MoE, which makes it the practical single-GPU option. |
| **Qwen 3.6 Max-Preview** | ~1T MoE | Commercial preview | Released ~April 20–27, 2026. 262K context. Tops six coding benchmarks per Alibaba. |
| **Qwen 3.6-Plus** | - | - | Released April 2, 2026. Enhanced coding. |
| **Qwen 3.6-35B-A3B** | 35B / 3B active MoE | Apache 2.0 | Released April 16, 2026. Open-weight workhorse. |
| Qwen2.5-Coder-32B | 32B | Apache 2.0 | Previous-generation open coding leader. |
| Qwen2.5-72B | 72B | Apache 2.0 | Previous-generation multilingual leader. |
| Qwen2.5-7B | 7B | Apache 2.0 | Efficient self-hosted option. |

### Mistral Family

| Model | Parameters | Context | Notes |
|-------|------------|---------|-------|
| **Mistral Medium 3.5** | 128B dense | 256K | May 2026 NEW. Released April 29, 2026. Merges Magistral (reasoning) + Pixtral (vision) + Devstral 2 (coding) into one model. 77.6% on SWE-Bench Verified. $1.50/M input tokens. |
| **Voxtral TTS** | 4B open-weights | streaming | May 2026 NEW (March 23 release, CC BY-NC 4.0). 70ms latency, 9 languages, 3-second voice cloning. |
| Mistral Large 3 | 675B (MoE, 41B active) | 256K | Sparse MoE; parity with best open-weight models; #2 OSS non-reasoning on LMArena. |
| Mistral Small 4 | - | 256K | Hybrid instruct/reasoning/coding; released March 2026. |
| Mistral 3 (14B/8B/3B) | 3B–14B | - | Unified family: multilingual, multimodal, Apache 2.0. |
| Mixtral 8x22B | 141B (MoE) | - | Previous gen; still viable for throughput. |

### Google Gemma Family - May 2026 NEW

| Model | Parameters | Context | License | Notes |
|-------|------------|---------|---------|-------|
| **Gemma 4 (31B dense)** | 31B | 256K | Apache 2.0 | Released April 2, 2026. 140+ languages; native vision/audio; function calling. |
| **Gemma 4 (26B-A4B MoE)** | 26B / 4B active | 256K | Apache 2.0 | Sparse MoE variant. |
| **Gemma 4 E4B** | 8B | 256K | Apache 2.0 | Edge-suitable. |
| **Gemma 4 E2B** | 5.1B / 2.3B active | 256K | Apache 2.0 | Smallest variant; mobile/embedded. |
| **DiffusionGemma (26B-A4B MoE)** | 26B / ~4B active | 256K | Apache 2.0 | June 10, 2026 NEW. Google DeepMind's first open-weight text-diffusion model; denoises blocks of tokens in parallel for roughly 4x faster generation (1000+ tokens/sec on one H100). Lower quality than standard Gemma 4; aimed at low-latency and in-line editing. |

### Zhipu / Z.ai GLM Family - June 2026 NEW

| Model | Parameters | Context | License | Notes |
|-------|------------|---------|---------|-------|
| **GLM-5.3** | Post-trained on the same 744B / 40B-active base as GLM-5.2 | 1M | Weights withheld at launch | August 14, 2026 via the GLM Coding Plan. The entire gain comes from extended post-training rather than a new pretraining run, a useful datapoint on where capability now comes from. Z.ai says cyber capability grew faster than anticipated as post-training scaled, claims a CyberGym lead, and staged the open-weight release pending safety evaluation, targeting roughly two weeks out (around August 28, 2026). |
| **GLM-5.2** | 744B total / 40B active (MoE) | 1M | MIT | Coding-plan access June 13, 2026; open weights June 16-17. Built for long-horizon agentic coding and tool use. Reports SWE-Bench Pro 62.1 (ahead of GPT-5.5 at 58.6 on that benchmark) and a long-horizon coding score near the closed frontier; figures are vendor-reported. API roughly $1.40 / $4.40 per 1M; weights on Hugging Face. |

**Best for:** Open-weight agentic coding and long-horizon tool use where a 1M context and a permissive license matter. Verify benchmark claims on independent leaderboards.

### Thinking Machines Inkling - July 2026 NEW

| Model | Parameters | Context | License | Notes |
|-------|------------|---------|---------|-------|
| **Inkling** | 975B total / 41B active (MoE) | 1M (64K or 256K via the lab's Tinker API) | Open weights | Released July 15, 2026: Thinking Machines Lab's first public model, pretrained on 45T tokens of text, image, audio, and video. SWE-Bench Verified 77.6%; the leading US open-weights model per Artificial Analysis, with safety scores the lab reports as aligning with frontier models. NVFP4 checkpoint optimized for NVIDIA Blackwell. |
| Inkling-Small (preview) | 276B total / 12B active | - | Open weights | Announced alongside Inkling for lower cost and latency. |

**Why it matters:** A brand-new US lab shipping the leading American open-weights model, positioned explicitly as a fine-tuning foundation. Until July the open frontier was dominated by Chinese labs; Kimi K3 and Inkling landing in the same week is the strongest open-weights month on record.

### Meta Muse Spark (Closed Weights) - May 2026 STRATEGIC SHIFT

| Attribute | Value |
|-----------|-------|
| License | **Closed weights** - first proprietary model from Meta Superintelligence Labs |
| Capabilities | Multimodal reasoning with Instant / Thinking / Contemplating modes |
| Released | April 8, 2026 |

**Strategic significance:** Meta's first non-open model since the original Llama era. Signals that frontier-quality work may require a closed-development feedback loop. Llama 4 Behemoth release was simultaneously paused through fall 2026 amid capability concerns. The open-vs-closed equilibrium is now two-tier: frontier closed lags 6–12 months ahead; open weights catch up via distillation, RL, and ecosystem iteration.

**July 2026 update:** **Muse Spark 1.1** shipped July 9 alongside the public preview of the **Meta Model API**, Meta's first self-serve paid API: OpenAI-compatible, $1.25 / $4.25 per 1M, roughly a quarter of rival flagship rates. Vendor-reported benchmarks lead on scaled tool use (MCP Atlas 88.1) and professional tool use (JobBench 54.7). Meta charging for API access completes the pivot away from open-weight Llama; there is no Llama 5, and Behemoth remains shelved.

**August 2026 update:** **Muse Glimmer** (August 10) is Meta's first open-weight release since Llama 4 and, at Apache 2.0, its most permissive license ever for an open model. It is a 30B dense multimodal model aimed at always-on local agent work (local coding agents, function calling, LLM-as-a-judge), with a 131,072-token context; quantized to 4-bit it fits under 20GB and runs on a single 24GB consumer GPU. **Muse Spark 1.2** and **Muse Code**, a terminal coding agent, shipped alongside it, notable for a `muse-spark-1.2-contributor` tier priced at $0.10 / $0.20 per 1M (against $1.25 / $4.25 standard) in exchange for permission to train on your prompts and completions. Data-for-discount as an explicit, published API tier is new, and worth a policy decision before anyone enables it.

---

### The August 2026 Open-Weight Licensing Split

August was the month open weights stopped meaning one thing. Three postures now coexist, and the license is as much a design input as the benchmark:

| Model | Released | Size | License posture | What the license actually does |
|-------|----------|------|-----------------|-------------------------------|
| **Qwen3.8-Max** (Alibaba) | Aug 12 | 2.4T / 95B active | Bespoke, commercially gated | Free use, modification, and resale, but attribution is required above 100M MAU or $20M monthly revenue, and a separate paid license is required to run a Model-as-a-Service or AI-assistant business above $50M aggregate revenue |
| **Qwen3.8-27B** (Alibaba) | Aug 14 | 27B dense | Apache 2.0 | No conditions. The smaller sibling is both more permissive and more modality-complete than the flagship |
| **Muse Glimmer** (Meta) | Aug 10 | 30B dense | Apache 2.0 | No conditions; Meta's most permissive open license to date |
| **Tencent Hy3** | Global Aug 5 (model Jul 6) | 295B / 21B active | Apache 2.0 | Fully permissive with no geographic carve-outs, reversing the April preview's restrictive license that excluded the EU, UK, and South Korea |
| **Ling-3.0-flash / tiny** (Ant Group) | Aug 5 / Aug 11 | 124B / 5.1B active; 7.9B / 1.3B active | MIT | No conditions |
| **Nemotron 3.5 Lightning** (NVIDIA) | Aug 11 | 30B / 3B active | OpenMDW-1.1 | Linux Foundation license, free for commercial use |
| **GLM-5.3** (Z.ai) | Aug 14 | 744B base | Weights withheld | Open release deliberately staged pending safety evaluation after cyber capability grew faster than expected; Z.ai gave a target of roughly two weeks (around August 28, 2026) |

Two things follow for anyone building on open weights. First, **read the license before the model card**: a gated license can make a "open" flagship unusable for exactly the SaaS business you were planning, while its smaller sibling is unencumbered. Second, **withholding is now a legitimate outcome**: a lab can ship a model commercially and hold the weights on safety grounds. Z.ai did publish a target date, so treat it as a dated plan rather than an open-ended promise, and do not build a roadmap on weights that have not shipped.

### Small and On-Device Models - August 2026

| Model | Size | Context | License | Notes |
|-------|------|---------|---------|-------|
| **Ling-3.0-tiny** (Ant Group) | 7.9B / 1.3B active | 256K | MIT | Genuinely laptop-class agentic model: roughly 8.3 GiB peak memory at 8K context, 86-90 tok/s on an M4 Pro MacBook at FP8 |
| **LFM2.5-2.6B** (Liquid AI) | 2.6B | 128K | Open weights | Built for on-device tool calling and multi-step planning rather than chat; under 2.5 GB memory, runs down to a Raspberry Pi |
| **LFM2.5-VL-3B** (Liquid AI) | 3B | - | Open weights | On-device vision-language model for screen understanding and GUI grounding (August 12) |
| **Shieldstral 1.0** (Mistral) | 3B | 32K | Apache 2.0 | Policy-adaptive **multimodal** safety classifier (text and image, 12 languages): moderation policies are supplied in natural language at inference time, so a policy change needs no retraining. Runs on one 16GB GPU |
| **Muse Glimmer** (Meta) | 30B dense | 131K | Apache 2.0 | Under 20GB at 4-bit; targets always-on local agents |

The pattern worth noting: the small-model tier stopped competing on chat quality and started competing on **tool calling, planning, and screen grounding**, which are the capabilities a local agent actually needs.

---

## Specialized Models

### Coding Mastery (June 2026)

| Model | Specialization | Why it wins |
|-------|----------------|-------------|
| **Claude Fable 5** | Capability ceiling | Mythos-class coding now generally available; highest frontier score on Cognition's FrontierCode and SOTA on CursorBench per Anthropic; 2x Opus 4.8 price |
| **GPT-5.5** | Single-shot coding leader (published) | SWE-bench Verified 88.7%; Terminal-Bench 2.1 78.2% |
| **Claude Opus 4.8** | Long-running agentic coding | SWE-bench Verified 88.6%; SWE-Bench Pro 69.2%; Dynamic Workflows with parallel subagents in Claude Code |
| **Claude Opus 4.7** | Predecessor flagship coding | SWE-bench Verified 87.6%; SWE-Bench Pro 64.3% |
| **Claude Sonnet 4.6** | Workhorse coding | Powers Claude Code at lower cost; 1M context |
| **Llama 4 Maverick** | Open-source coding | Open weights; competitive on coding benchmarks |
| **Qwen 3.6 Coder / Qwen2.5-Coder-32B** | Self-hosted coding | Best price-to-performance for self-hosted IDEs |
| **DeepSeek V4 Pro / R1-Distill-70B** | Open reasoning + code | Best open reasoning at 70B; V4 Pro is open-weight 1.6T/49B-active MoE |
| **Z.ai GLM-5.2** | Open agentic coding | June 2026; 744B / 40B-active MoE, 1M context, MIT; reports SWE-Bench Pro 62.1 ahead of GPT-5.5 on that benchmark (vendor-reported); about $1.40 / $4.40 per 1M |
| **Kimi K2.7 Code** | Open long-horizon coding | June 2026; 1T / 32B-active MoE, Modified MIT; tuned from K2.6 for software work with fewer thinking tokens |
| **Cohere North Mini Code 1.0** | Open lightweight coding | June 2026; 30B / 3B-active MoE on a single H100, Apache 2.0; Cohere's first open coding model |

### Reasoning & Math

| Model | Approach | Best For |
|-------|----------|----------|
| **Claude Fable 5** | Always-on adaptive thinking at the Mythos capability tier | The hardest reasoning problems where ceiling beats cost |
| **Claude Opus 4.8 (thinking)** | Adaptive thinking with parallel subagents | Software planning, codebase-scale work, agentic reasoning |
| **GPT-5.5 reasoning** | Maximum-compute reasoning | Competition math (AIME 2025 81.2% on Instant), ARC-AGI-2 85.0% leader |
| **Gemini 3.1 Pro Deep Think** | Sustained chain-of-thought | Scientific reasoning, GPQA Diamond leader |
| **DeepSeek-R1** | RL-based thinking | Open-source logical inference, competitive math |
| **Grok 4.3 (DeepSearch)** | Web-grounded reasoning | Research tasks needing live information |

### Long Context (1M+)

| Model | Window | Recall Performance |
|-------|--------|-------------------|
| **Llama 4 Scout** | 10M | Industry-leading open-weight context window |
| **Gemini 3.1 Pro / Flash** | 1M | Best quality at 1M context; proven at scale |
| **Claude Fable 5** | 1M | Anthropic reports improved long-context performance with persistent memory across long sessions |
| **Claude Opus 4.8 / 4.7 / Sonnet 4.6** | 1M | Full 1M at standard pricing; reliable recall |
| **Llama 4 Maverick** | 1M | Open-weight 1M context with MoE efficiency |

---

## Embedding Models

### API Embedding Models (May 2026)

| Model | Dimensions | Max Tokens | MTEB Score | Cost/1M |
|-------|------------|------------|------------|---------|
| OpenAI text-embedding-3-large | 3072 | 8191 | 64.6 | $0.13 |
| OpenAI text-embedding-3-small | 1536 | 8191 | 62.3 | $0.02 |
| Voyage-3 | 1024 | 32000 | 67.8 | $0.06 |
| Cohere embed-v3 | 1024 | 512 | 66.4 | $0.10 |
| Google text-embedding-004 | 768 | 2048 | 66.1 | $0.025 |

### Open Source Embedding Models

| Model | Dimensions | Max Tokens | MTEB | Notes |
|-------|------------|------------|------|-------|
| BGE-large-en-v1.5 | 1024 | 512 | 63.9 | Instruction-tuned |
| E5-mistral-7b-instruct | 4096 | 32768 | 66.6 | Strong with instructions |
| Nomic-embed-text-v1.5 | 768 | 8192 | 62.3 | Long context, open |
| GTE-Qwen2-7B | 3584 | 32K | 72.1 | State-of-the-art open embedding |

### Embedding Selection Guide

| Requirement | Recommended | Why |
|-------------|-------------|-----|
| Best quality | Voyage-3 or text-embedding-3-large | Highest MTEB |
| Cost-efficient | text-embedding-3-small | $0.02/1M |
| Self-hosted | GTE-Qwen2-7B | Best open MTEB |
| Long documents | Nomic or Voyage-3 | 8K+ context |
| Multilingual | Cohere embed-v3 | Built for multilingual |

---

## Model Selection Framework

### Decision Tree

```
What is your primary constraint?

├── Cost → Use smaller model, consider open source
│   ├── Very cost sensitive → DeepSeek V4 Flash, GPT-5.5-mini, Claude Haiku 4.5, Gemini 3.1 Flash
│   └── Moderate budget → Claude Sonnet 4.6, GPT-5.5 Instant, DeepSeek V4 Pro
│
├── Quality + Reasoning → Use frontier models
│   ├── Highest reasoning → Claude Fable 5, Claude Opus 4.8 (thinking), GPT-5.5 reasoning, Gemini 3.1 Pro Deep Think
│   └── Coding + reasoning → Claude Opus 4.8 with Dynamic Workflows, Claude Sonnet 4.6 (Extended Thinking), GPT-5.5
│
├── Latency → Use fast models
│   ├── <100ms response → Gemini 3.1 Flash, GPT-5.5-mini
│   └── <500ms response → Claude Haiku 4.5, Claude Opus 4.8 fast mode, Grok 4.1 Fast
│
├── Self-hosting → Use open models
│   ├── Maximum capability → Llama 4 Maverick, DeepSeek-V3
│   ├── Good balance → Llama 4 Scout, Llama 3.3 70B, Qwen2.5-72B
│   └── Edge/mobile → Mistral 3 3B, Phi-4
│
└── Privacy → Self-host or use on-prem
    └── Choose open models with appropriate license
```

### Semantic Routing

Static decision trees are being replaced by **Semantic Routers**:
- **How it works**: A small, fast embedding model vectorises the query. If it matches a "known easy" cluster, route to a cheap model (Gemini 3.1 Flash, DeepSeek V4 Flash, Claude Haiku 4.5). If it hits an "agentic/logic" cluster, route to Claude Opus 4.8 or GPT-5.5 with reasoning.
- **Benefit**: Automates cost-optimization without hardcoded rules.
- **Implementation**: Tools like `semantic-router` (Python) or custom Weaviate/Pinecone classifiers.

---

## Sovereign AI and Data Residency

**The 2026 Regulatory Reality:**
Enterprises must comply with GDPR (EU), DPDPA (India), Saudi Arabia PDPL, and sectoral rules. "Sovereign AI" is now a product category.

| Solution | Provider | Use Case |
|----------|----------|----------|
| **Azure Government/Sovereign** | Microsoft | Dedicated infra in 40+ regions; approved for US Gov/EU NIS2 |
| **AWS Sovereign Cloud** | Amazon | Physically isolated VPCs; GDPR-safe EU regions |
| **Google Distributed Cloud** | Google | Air-gapped on-prem Gemini deployment |
| **Private Llama 4 / 3.3** | Meta (self-host) | Maximum data sovereignty; open weights (Llama 4 MoE or 3.3 dense) |
| **DeepSeek (self-host)** | DeepSeek (open) | Open weights; no data leaves your infra |
| **Mistral Large 3 (self-host)** | Mistral (Apache 2.0) | 675B MoE; open weights; strong multilingual |

**Tradeoff**: Sovereign clouds carry a **20-30% premium** over standard global regions but are mandatory for finance and government.

### Cost Comparison at Scale (May 2026)

Assume 1M requests/day, 1K input + 500 output tokens:

| Model | Input Cost/Day | Output Cost/Day | Total/Month |
|-------|----------------|-----------------|-------------|
| Claude Sonnet 4.6 | $3,000 | $7,500 | $315,000 |
| GPT-5.4 | $2,500 | $7,500 | $300,000 |
| Gemini 3.1 Pro | $2,000 | $6,000 | $240,000 |
| GPT-5.4-mini | $750 | $2,250 | $90,000 |
| Gemini 3.1 Flash | $100 | $1,500 | $48,000 |
| Self-hosted Llama 4 Scout* | - | - | ~$15,000 |
| Self-hosted Llama 3.3 70B* | - | - | ~$50,000 |

*Self-hosted Llama 4 Scout fits on a single H100; Llama 3.3 70B assumes 4x H100 GPUs

---

## Capability Comparison

### Benchmark Performance (May 2026)

| Model | MMLU | HumanEval | SWE-bench Verified | Notes |
|-------|------|-----------|--------------------|-------|
| **Claude Opus 4.6** | - | - | - | Top-tier across reasoning and coding; specific scores check latest |
| **GPT-5.4** | - | - | - | 33% fewer factual errors vs GPT-5.2; strong coding + agentic |
| **Claude Sonnet 4.6** | - | - | - | Approaches Opus-level on many tasks |
| **Gemini 3.1 Pro** | - | - | - | State-of-the-art Google reasoning |
| **Grok 4** | - | - | - | Competitive reasoning; real-time web integration |
| **Llama 4 Maverick** | - | - | - | Beats GPT-4o, Gemini 2.0 Flash on reported benchmarks |
| **DeepSeek-R1** | 90.8 | 92.6 | 49.2% | First open-source reasoning model; math/code strong |

*Source: Respective technical reports and LMSYS Chatbot Arena / LMArena, April 2026. Benchmark scores for newest models (Opus 4.6, GPT-5.4, Gemini 3.1) are evolving rapidly -- always verify with current leaderboards.*

### Task-Specific Recommendations (May 2026)

| Task | Recommended Models | Why |
|------|--------------------|-----|
| **Autonomous Coding Agent** | Claude Sonnet 4.6 / Opus 4.6 | Powers Claude Code; 1M context; top tool reliability |
| **Complex Reasoning** | GPT-5.4 Pro, Claude Opus 4.6 (thinking), DeepSeek-R1 | Maximum reasoning power |
| **Agentic Computer Use** | GPT-5.4 | First general-purpose model with native computer-use capabilities |
| **High-Volume API** | Gemini 3.1 Flash, GPT-5.4-mini | Lowest cost per token in class |
| **Long Context RAG** | Gemini 3.1 Pro/Flash (1M), Claude Sonnet 4.6 (1M) | Verified long-range recall |
| **Ultra-Long Context** | Llama 4 Scout (10M) | Industry-leading 10M context; open weights |
| **Multimodal Real-time** | Gemini 3.1 Flash | Real-time audio/video/text native |
| **Private Production** | Llama 4 Maverick, Llama 3.3 70B, Qwen2.5-72B | High capability with local control |
| **Open-source Coding** | Llama 4 Maverick, Qwen2.5-Coder-32B | Open weights, strong coding benchmarks |
| **Creative/Chat** | GPT-5.4 | Strong conversation quality and instruction following |

---

## Interview Questions

### Q: How would you select a model for a production RAG system?

**Strong answer:**
I evaluate across these dimensions:

**1. Quality requirements:**
- Test on representative queries from the actual domain
- Measure answer correctness, hallucination rate, citation accuracy

**2. Cost analysis:**
```
Monthly cost = requests/day × 30 × avg_tokens × rate
```
Always calculate for top 2-3 candidates.

**3. Latency requirements:**
- If <200ms TTFT needed: Gemini 3.1 Flash, Claude Haiku 4.5, GPT-5.4-mini
- If quality is paramount: Accept 2-3s with Claude Opus 4.6 or GPT-5.4

**4. Operational requirements:**
- Self-hosting: Llama 4 Scout/Maverick, DeepSeek-V3
- Compliance / data residency: Azure Sovereign or self-hosted

**5. Practical selection:**
- Start with Claude Sonnet 4.6 or GPT-5.4 for prototyping
- A/B test Gemini 3.1 Flash for 80% of queries (cost)
- Keep frontier on hard queries via semantic routing

### Q: Explain the tradeoffs between proprietary and open source models.

**Strong answer:**
| Factor | Proprietary (OpenAI, Anthropic) | Open Source (Llama, DeepSeek) |
|--------|--------------------------------|-----------------------------|
| Quality | Generally higher (slightly) | Catching up rapidly |
| Cost | Per-token pricing | Compute + ops |
| Control | Limited | Full |
| Privacy | Data goes to provider | Stays on-prem |
| Updates | Automatic | Manual |
| Customization | Limited fine-tuning | Full fine-tuning |
| Ops overhead | None | Significant |

**Key insight (2026)**: DeepSeek-V3/R1 and now Llama 4 have changed this conversation -- open models match or beat GPT-4o on many benchmarks. With Llama 4 Maverick matching DeepSeek V3 on reasoning at half the active parameters, the gap is narrower than ever.

### Q: What is the difference between GPT-5.4 Pro and Claude Opus 4.6's Extended Thinking?

**Strong answer:**
Both use internal chain-of-thought, but the mechanics differ:

- **GPT-5.4 Pro**: OpenAI's maximum-compute reasoning tier ($30/$180 per 1M tokens). Allocates high compute to reasoning. Internal thoughts are not exposed. Successor to the o3 line.
- **Claude Opus 4.6 Adaptive Thinking**: Returns thinking tokens in a separate `<thinking>` block. Configurable `budget_tokens`. You can inspect the reasoning chain for debugging. Full 1M context with 128K max output.

**Production choice**: For debugging and trust-building, Claude's visible thinking is more transparent. For maximum raw reasoning power on math/competition tasks, GPT-5.4 Pro leads. For cost-effective reasoning, Claude Sonnet 4.6 or GPT-5.4-mini are strong choices.

---

## References

- Anthropic: https://platform.claude.com/docs/en/about-claude/models/overview
- OpenAI Platform: https://developers.openai.com/api/docs/models
- Google AI: https://ai.google.dev/gemini-api/docs/models
- Meta Llama: https://www.llama.com/
- DeepSeek: https://api-docs.deepseek.com/
- xAI Grok: https://docs.x.ai/developers/models
- Mistral AI: https://docs.mistral.ai/models/
- LMArena Leaderboard: https://lmarena.ai/
- Hugging Face Open LLM Leaderboard: https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard

---

*Next: [Capability Assessment](02-capability-assessment.md)*
