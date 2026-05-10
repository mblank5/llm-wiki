---
title: "Agentic Harness Engineering (AHE)"
created: 2026-05-05
updated: 2026-05-05
type: concept
tags: [agent, agentic-coding, distillation, training, benchmark]
sources: [raw/papers/2026/04/2604.25850.md]
---

# Agentic Harness Engineering (AHE)

## 1. Core Problem Definition (Formal Statement)

Coding agents consist of a base LLM **M** surrounded by a **harness** H — the collection of model-external, editable components: system prompt, tools, middleware, skills, sub-agent configuration, and long-term memory. The harness mediates how M perceives and acts on its environment.

**Formal problem:** Given a fixed base model M and a benchmark D, find the harness H* that maximizes pass@1:

> H* = argmax_H Pass@1(M, H, D)

The challenge is that harness engineering is a **combinatorial optimization problem** with:
- **Heterogeneous action space**: edits span 7 orthogonal component types
- **Voluminous trajectories**: millions of tokens bury actionable signal
- **Attribution difficulty**: hard to trace performance changes to specific edits

The paper asks: *How can an evolution agent jointly and stably evolve all editable components of a coding agent's harness?*

**Key insight**: The bottleneck is **observability**, not agent capability.

## 2. Theoretical Analysis / Method

### 2.1 Three Observability Pillars

**Pillar 1 — Component Observability (NexAU substrate)**

Harness H is decoupled into 7 file-level component types, each at a fixed mount point:

| Component | Role |
|-----------|------|
| System prompt | Shapes work style |
| Tool description | Declares tool interface |
| Tool implementation | Executes tool logic |
| Middleware | Controls context/execution/recovery |
| Skill | Reusable capability packages |
| Sub-agent config | Defines sub-agent behavior |
| Long-term memory | Persists cross-session lessons |

This gives each failure pattern a clean mapping to a single component class. Every edit is a git commit → file-level diffs and rollback for free.

**Pillar 2 — Experience Observability (Agent Debugger)**

Raw rollout trajectories T_t are distilled into a layered evidence corpus via the Agent Debugger framework:

1. **Per-task analysis reports**: Root cause of failure/success for each task
2. **Benchmark-level overview**: Aggregated entry point across all tasks
3. **Original traces**: Available for verification (progressive disclosure)

This converts millions of raw tokens into structured, drill-down-able evidence.

**Pillar 3 — Decision Observability (Change Manifest)**

Every edit ships with a manifest entry containing:
- Failure evidence (which tasks failed)
- Inferred root cause
- Targeted fix
- **Predicted impact**: expected fixes AND at-risk regressions

Each edit becomes a **falsifiable contract** — the next round's task-level deltas verify or revert it.

### 2.2 Algorithm: AHE Outer Loop

```
Algorithm 1: AHE Outer Loop
Input: seed harness H_0, base model M, benchmark D,
       rollouts per task k, max iterations N

H_best ← H_0
for t = 1 to N do
  // Phase 1: Rollout
  T_t ← Rollout(M, H_{t-1}, D, k)

  // Phase 2: Clean trajectories
  T̃_t ← Clean(T_t)    // drop base64, dedup tool output

  // Phase 3: Attribute prior manifest, then rollback
  if t ≥ 2 then
    V_t ← Attribute(C_{t-1}, T_{t-1}, T_t)
    H_{t-1} ← Rollback(H_{t-1}, V_t)
  else
    V_t ← ∅

  // Phase 4: Layered distillation
  R_t ← AgentDebugger(T̃_t)

  // Phase 5: Workspace edits + new manifest
  (H_t, C_t) ← Evolve(H_{t-1}, R_t, V_t)

  // Phase 6: Commit
  Commit(H_t, C_t, t)

  if Pass@1(T_t) > Pass@1(H_best) then
    H_best ← H_t

return H_best
```

**Key properties:**
- k ≥ 2 rollouts per task for stable pass-rate signals
- Attribution runs BEFORE distillation → verdict binds as contract
- Evolve Agent writes only inside harness workspace (read-only: verifier, tracer, LLM config)
- Seed system prompt is non-deletable (prevents shortcuts)

### 2.3 Seed Design

The seed H_0 is deliberately minimal: a single shell-execution tool, no middleware, no skills, no sub-agents. This forces every component AHE adds to earn its place against measured rollouts, avoiding contamination from a pre-fitted harness.

## 3. Complete Experimental Results

### 3.1 Main Results — Terminal-Bench 2 (Table 1)

Pass@1 on Terminal-Bench 2 (89 tasks: 4 easy, 55 medium, 30 hard):

| Method | All | Easy | Medium | Hard |
|--------|-----|------|--------|------|
| opencode | 47.2% | 75.0% | 52.7% | 33.3% |
| terminus-2 | 62.9% | 75.0% | 74.5% | 40.0% |
| Codex-CLI | 71.9% | 75.0% | 80.0% | 56.7% |
| **NexAU seed** | 69.7% | 87.5% | 78.2% | 51.7% |
| ACE | 68.9% | 91.7% | 78.2% | 48.9% |
| TF-GRPO | 72.3% | 100.0% | 79.4% | 55.6% |
| **AHE** | **77.0%** | **100.0%** | **88.2%** | 53.3% |

**Key: AHE lifts pass@1 from 69.7% → 77.0% (+7.3pp), surpassing all human-designed and self-evolving baselines.**

### 3.2 Cross-Benchmark Transfer — SWE-bench-verified (Table 2)

| Repo | NexAU₀ Success | AHE Success | NexAU₀ Tokens | AHE Tokens |
|------|---------------|-------------|---------------|------------|
| All (500) | 75.2% | **75.6%** | 526k | **461k** |
| django (231) | 79.2% | **81.0%** | 527k | 484k |
| sphinx-doc (44) | 68.2% | **70.5%** | 731k | 656k |
| scikit-learn (32) | **93.8%** | 87.5% | 307k | **257k** |

AHE transfers without re-evolution: +12% fewer tokens than seed on aggregate, with the largest gains on the most token-expensive repositories.

### 3.3 Cross-Model Transfer

AHE workspace evolved on GPT-5.4 high, evaluated on 5 alternate bases:

| Base Model | Seed Pass@1 | AHE Pass@1 | Gain |
|------------|-------------|------------|------|
| GPT-5.4 medium | — | — | +2.3pp |
| GPT-5.4 high | 69.7% | 77.0% | +7.3pp |
| GPT-5.4 xhigh | — | — | +2.3pp |
| qwen-3.6-plus | 56.2% | 62.5% | +6.3pp |
| gemini-3.1-flash-lite | 36.5% | 41.6% | +5.1pp |
| deepseek-v4-flash | 51.7% | 61.8% | **+10.1pp** |

All five gains are positive. Larger gains on less-saturated models → AHE encodes coordination patterns that weaker models lean on more heavily.

### 3.4 Component Ablation (Table 3)

Each component swapped individually into the NexAU seed:

| Variant | All | Easy | Medium | Hard |
|---------|-----|------|--------|------|
| NexAU seed | 69.7% | 87.5% | 78.2% | 51.7% |
| + memory only | **75.3%** | 50.0% | **83.6%** | **63.3%** |
| + tool only | 73.0% | 75.0% | 87.3% | 46.7% |
| + middleware only | 71.9% | **100.0%** | 81.8% | 50.0% |
| + system_prompt only | 67.4% | 75.0% | 78.2% | 46.7% |
| **AHE full** | **77.0%** | **100.0%** | **88.2%** | 53.3% |

**Key findings:**
- Tools, middleware, and memory each carry improvement independently
- System prompt alone **regresses** (-2.3pp) — prose-level strategy doesn't transfer
- Components interact non-additively: single-component gains sum to +11.1pp but full AHE is only +7.3pp (redundant verification on hard tasks)
- Memory is the strongest single component, especially on Hard (+11.6pp)

### 3.5 Self-Attribution Analysis (Figure 4)

Cross-iteration precision/recall of the evolve model's self-predictions:

| Metric | Fix Precision | Fix Recall | Regression Precision | Regression Recall |
|--------|--------------|------------|---------------------|-------------------|
| AHE | 33.7% | 51.4% | 11.8% | 11.1% |
| Random baseline | 6.5% | 10.6% | 5.6% | 5.4% |

**Finding**: Fix predictions are ~5× above random (evidence-driven). Regression predictions are only ~2× above random → **regression blindness** is the main limitation.

### 3.6 Training Configuration

| Parameter | Value |
|-----------|-------|
| Base model | GPT-5.4 (high reasoning setting) |
| All role agents | Share same base model (GPT-5.4) |
| Rollouts per task | k = 2 |
| Evolution iterations | 10 |
| Benchmark for evolution | Terminal-Bench 2 (89 tasks) |
| Per-task timeout | 1 hour |
| Total evolution time | ~32 hours |
| Framework | NexAU |

## 4. Comparison with Existing Methods

| Dimension | AHE | ACE | TF-GRPO | Codex-CLI | Human-designed |
|-----------|-----|-----|---------|-----------|----------------|
| **Components edited** | All 7 | Playbook only | Tool sequence only | Fixed | Fixed (manual) |
| **Observability** | 3 pillars | None explicit | Trajectory-level | None | None |
| **Edit falsifiability** | Yes (manifest) | No | No | N/A | N/A |
| **Pass@1 (Terminal-Bench 2)** | **77.0%** | 68.9% | 72.3% | 71.9% | 47.2-71.9% |
| **Transfer to SWE-bench** | ✅ Yes | Regresses | Regesses | N/A | Varies |
| **Cross-model transfer** | ✅ +5.1 to +10.1pp | Not tested | Not tested | No | Limited |
| **Token efficiency** | Improves | -11 to -29% | -21% | Baseline | Varies |

## 5. Critical Analysis

### Strengths
1. **First framework to jointly evolve all 7 harness components** — prior work only optimizes one component type
2. **Falsifiable edit contracts** via change manifest — replaces rationale-driven self-justification with measurable verification
3. **Strong empirical results**: +7.3pp on Terminal-Bench 2, cross-benchmark transfer, cross-model transfer
4. **Attribution granularity**: file-level git diffs localize every gain/loss to specific components
5. **Memory is the strongest component** — confirms that factual harness structure transfers while prose strategy does not

### Weaknesses / Open Questions
1. **Regression blindness**: The evolve agent can justify why an edit should help but cannot reliably predict what it will break (regression precision only 11.8%). This is the clearest limitation.
2. **Non-additive component interactions**: Stacking effective edits can hurt (redundant verification on hard tasks). The optimizer converges to a Medium-heavy trade-off.
3. **Single base model for all roles**: All three agents (Code, Debugger, Evolve) share GPT-5.4. It's unclear if using specialized models for each role would improve further.
4. **Evolution cost**: 32 hours on GPT-5.4. Not cheap, though amortized across future use.
5. **Timeout-budget coupling**: Per-task timeout fitted to GPT-5.4 high; transferring to models with different reasoning depths requires re-tuning.
6. **Only evaluated on coding benchmarks**: Transfer to non-coding agent tasks (e.g., web navigation, multi-modal) is untested.

### Implications for Our Work
- **Harness as a first-class optimization target**: AHE shows that harness structure encodes general engineering experience. This suggests we should treat harness design as a learnable surface, not a manual craft.
- **Observability as the key enabler**: The three-pillar approach (component/experience/decision observability) is a general pattern applicable to any agent self-improvement loop.
- **Falsifiable contracts for agent evolution**: The change manifest pattern could be adopted in our own agent training loops to prevent drift.
- **Memory > Prompt**: The finding that system prompt alone regresses while memory carries the gain suggests we should invest in structured memory over prompt engineering.

## 6. Related

- [[agentic-coding]] — coding agent paradigms and benchmarks
- [[distillation]] — trajectory distillation and knowledge transfer
- [[multi-agent]] — multi-agent system design patterns
- [[benchmark]] — Terminal-Bench, SWE-bench evaluation methodology
- [[training]] — agent training and optimization techniques
