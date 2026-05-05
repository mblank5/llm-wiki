---
title: "From Skill Text to Skill Structure: The SSL Representation"
created: 2026-05-05
updated: 2026-05-05
type: concept
tags: [safety, evaluation, benchmark, tool-use, alignment]
sources: [raw/papers/2604.24026.md]
---

# From Skill Text to Skill Structure: The SSL Representation

**arXiv**: 2604.24026v4 [cs.CL] | **Date**: 2026-05-04
**Authors**: Qiliang Liang, Hansi Wang, Zhong Liang, Yang Liu (Peking University)
**GitHub**: https://github.com/COOLPKU/SSL

## 1. Core Problem Definition

LLM agents increasingly rely on **reusable skills** — bundles of instructions, control flow, constraints, and callable operations. However, skills are still represented by **text-heavy artifacts** (SKILL.md-style documents) whose machine-usable evidence remains embedded in natural language.

This creates a **representational bottleneck**: semantically distinct properties (invocation interface, execution structure, action/resource-use evidence) are collapsed into a single textual surface, forcing downstream systems to repeatedly re-parse noisy, incomplete text.

## 2. Theoretical Foundation

SSL draws on three classical cognitive linguistic theories from Schank and Abelson:

| Theory | Layer | Analogy |
|--------|-------|---------|
| **Memory Organization Packets** (Schank, 1980) | Scheduling | Goal-oriented organizers for retrieving and contextualizing experience |
| **Script Theory** (Schank & Abelson, 1977) | Structural | Stereotyped activities as ordered scenes with expectations and transitions |
| **Conceptual Dependency** (Schank, 1972) | Logical | Primitive action structures abstracting away from surface wording |

## 3. The SSL Representation

### 3.1 Formal Definition

Given a skill artifact d (e.g., SKILL.md file), SSL maps it into a typed representation:

```
G_d = (r_sch, G_str, G_log, R_cont, R_entry)
```

Where:
- **r_sch** = Scheduling layer (skill-level interface record)
- **G_str** = Structural layer (scene-level directed graph of execution phases)
- **G_log** = Logical layer (logic-step directed graph of atomic actions)
- **R_cont** = Containment relations (scenes → skill, logic steps → scenes)
- **R_entry** = Entry pointers (where traversal begins)

### 3.2 Three Layers

#### Scheduling Layer (r_sch)
Captures **invocation-level signals**: supported intents, input/output contracts, coarse dependencies, control-flow properties. Provides a stable capability record for comparison across a repository without unfolding full structure.

#### Structural Layer (G_str)
Nodes = **scenes** (coherent execution phases: preparation, acquisition, reasoning, action, verification, recovery). Edges = phase-level transitions. Motivated by Script Theory — groups low-level operations into stereotyped stages.

#### Logical Layer (G_log)
Nodes = **logic steps** (atomic actions). Edges = micro-level transitions. Each atomic action selects an `act_type` from a closed primitive inventory, recording arguments, effects, and resource boundaries as typed evidence.

### 3.3 Design Goals
- **Compact**: Preserves evidence for skill management while avoiding open-ended attributes
- **Typed**: Uses restricted vocabularies so normalized outputs remain comparable
- **Grounded**: Fields strictly summarize evidence present in the source artifact (no inference of hidden behavior)

### 3.4 LLM-based Normalizer

Implemented with **DeepSeek-V3.2** (Liu et al., 2025). The normalizer:
1. Extracts the skill-level record (scheduling layer)
2. Decomposes the document into scenes (structural layer)
3. Expands each scene into source-grounded logic steps (logical layer)
4. Validates the resulting graph (structural well-formedness, identifier consistency, allowed enum values, containment links, entry pointers)

**Human audit**: 83% of audited SSL outputs judged to be supported by corresponding source artifacts (100 skills sampled).

## 4. Experimental Results

### 4.1 Skill Discovery

**Setup**: 6,184 public skills as retrieval candidate pool; 431 intent-level queries. All methods use Qwen3-Embedding-0.6B with FAISS inner-product index.

**Table 1: Skill Discovery Performance**

| Group | Method | MRR@50 | NDCG@5 | NDCG@10 | Recall@10 |
|-------|--------|--------|--------|---------|-----------|
| **Baselines** | Desc_only | 0.588 | 0.608 | 0.626 | 0.761 |
| | Full SKILL.md | 0.645 | 0.655 | 0.682 | 0.821 |
| | Source Outline | 0.592 | 0.615 | 0.634 | 0.787 |
| | Desc + Source Outline | 0.649 | 0.670 | 0.689 | 0.833 |
| **SSL-Shallow** | Desc + SSL-Shallow | 0.716 | 0.730 | 0.752 | 0.879 |
| | Full SKILL.md + SSL-Shallow | 0.664 | 0.688 | 0.706 | 0.847 |
| **SSL-Sched** | Desc + SSL-Sched | 0.694 | 0.716 | 0.733 | 0.868 |
| | Full SKILL.md + SSL-Sched | 0.676 | 0.694 | 0.715 | 0.849 |
| **SSL-Rich** | **Desc + SSL-Rich** | **0.729** | **0.748** | **0.770** | **0.905** |
| | Full SKILL.md + SSL-Rich | 0.681 | 0.705 | 0.720 | 0.856 |

**Key findings**:
- Desc + SSL-Rich improves MRR@50 from 0.649 → 0.729 (+12.3%) over strongest non-SSL baseline
- SSL-Shallow already provides strong gain; SSL-Rich adds scene-level and interface-level signals
- Full-document inputs remain weaker even when augmented with SSL (concise structure > verbose text)
- 95% CI for MRR@50 improvement: [0.051, 0.111]

### 4.2 Risk Assessment

**Setup**: 252 gold-labeled skills with six binary risk dimensions. Fixed judge: DeepSeek-V3.2.

**Risk dimensions**: Data Exfiltration, Destructive Behavior, Privilege Escalation, Covert Execution, Resource Abuse, Credential Access

**Table 2: Per-Dimension F1 Scores**

| Threat Dimension | Desc | Full MD | SSL-Sh. | Full SSL | MD + SSL |
|-----------------|------|---------|---------|----------|----------|
| Data Exfiltration | 0.280 | 0.511 | 0.272 | 0.651 | **0.699** |
| Destructive Behaviors | 0.162 | 0.371 | 0.147 | 0.403 | **0.439** |
| Privilege Escalation | 0.364 | 0.381 | 0.381 | 0.348 | **0.455** |
| Covert Execution | 0.083 | 0.222 | 0.042 | 0.083 | **0.264** |
| Resource Abuse | 0.132 | 0.271 | 0.133 | 0.323 | **0.419** |
| Credential Access | 0.391 | 0.695 | 0.286 | 0.722 | **0.780** |
| **Macro F1** | 0.235 | 0.409 | 0.210 | 0.422 | **0.509** |

**Table 3: Aggregate Risk Assessment**

| Input | Macro Acc. | Macro Prec. | Macro Rec. | Macro F1 |
|-------|-----------|-------------|------------|----------|
| Desc Only | 0.714 | 0.823 | 0.148 | 0.235 |
| Full SKILL.md | 0.765 | 0.828 | 0.283 | 0.409 |
| SSL-Shallow | 0.709 | 0.783 | 0.129 | 0.210 |
| Full SSL | 0.778 | 0.841 | 0.315 | 0.422 |
| **MD + SSL** | **0.801** | **0.884** | **0.382** | **0.509** |

**Key findings**:
- Full SKILL.md + SSL improves macro F1 from 0.409 → 0.509 (+24.4%) over full text alone
- Largest gains on data exfiltration, credential access, and resource abuse
- SSL alone slightly outperforms full-document baseline; the main benefit comes from **combining** structured evidence with source context
- 95% CI for macro-F1 improvement: [0.051, 0.152]

## 5. Training Configuration

- **Normalizer**: DeepSeek-V3.2
- **Embedding model**: Qwen3-Embedding-0.6B
- **Retrieval index**: FAISS inner-product over L2-normalized embeddings
- **Risk judge**: DeepSeek-V3.2 (fixed across all representation variants)
- **Skill corpus**: 6,184 public skills
- **Skill Discovery queries**: 431 intent-level queries
- **Risk Assessment labels**: 252 skills × 6 dimensions, labeled by Gemini-3.1-pro-preview + Claude-Sonnet-4.5 + GPT-5 majority voting

## 6. Comparison with Existing Methods

| Method | Skill Discovery MRR@50 | Risk Assessment Macro F1 |
|--------|----------------------|-------------------------|
| Desc_only | 0.588 | 0.235 |
| Full SKILL.md | 0.645 | 0.409 |
| Source Outline | 0.592 | — |
| SSL-Shallow | 0.716 | 0.210 |
| SSL-Sched | 0.694 | — |
| SSL-Rich | **0.729** | — |
| Full SSL | — | 0.422 |
| **MD + SSL** | — | **0.509** |

SSL consistently outperforms text-only baselines. The best results come from combining SSL structure with source document context.

## 7. Critical Analysis

**Strengths**:
- First structured representation specifically designed for agent skill artifacts
- Grounded in classical cognitive linguistic theory (Schank & Abelson)
- Evaluated on two distinct downstream tasks with consistent improvements
- Large-scale evaluation (6,184 skills, 431 queries, 252 risk-labeled skills)
- Open-source release (GitHub: COOLPKU/SSL)
- Human audit validates normalizer fidelity (83% source-grounded)

**Weaknesses**:
- **Static only**: SSL is extracted from static artifacts; cannot determine dynamic actions (downloaded payloads, constructed commands, conditional resource access)
- **Normalizer dependence**: SSL quality depends on LLM-based normalization, which may omit facts, over-regularize, or map ambiguous behavior into coarse enums
- **Limited evaluation scope**: Only evaluates pre-execution skill management (discovery + risk); does not evaluate actual skill use during planning, execution, or monitoring
- **Model-mediated labels**: Risk labels come from multi-model voting, not expert security audit
- **No runtime evaluation**: Does not test whether SSL actually helps agents use skills better

**Open Questions**:
- Can SSL be extended with runtime traces for dynamic analysis?
- How does SSL quality degrade for obfuscated or adversarial skills?
- Can SSL graphs be linked into repository-level skill graphs for composition?
- Would SSL help agents during actual skill execution (not just pre-execution management)?

## Related

- [[skill-orchestration]] — Agent skill routing and selection
- [[agent-safety]] — Safety considerations for tool-using agents
- [[agent-memory-system]] — Memory systems for LLM agents
- [[tool-use]] — Tool use and function calling in LLMs
- [[prompt-injection]] — Security risks from retrieved content
