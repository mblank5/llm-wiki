---
title: ReaLM-Retrieve — Adaptive Retrieval for Large Reasoning Models
created: 2026-05-05
updated: 2026-05-05
type: concept
tags:
- retrieval
- reasoning
- agent
- inference
- benchmark
sources:
- raw/papers/2026/04/2604.26649.md
---

# ReaLM-Retrieve: When to Retrieve During Reasoning

## Core Problem Definition

Large reasoning models (LRMs) like DeepSeek-R1 and OpenAI o1 generate extended chains of thought spanning **12,000-25,000 tokens**, yet their integration with retrieval-augmented generation (RAG) is fundamentally misaligned.

**The temporal mismatch**: Current RAG pipelines optimize for providing context *before* reasoning begins ("retrieve-then-generate"). But reasoning models encounter knowledge gaps *during* multi-step inference chains — gaps that cannot be anticipated at query time.

**Three incompatibilities with existing iterative retrieval**:
1. **Granularity mismatch**: Token-level (FLARE) or sentence-level (IRCoT) vs. reasoning-step granularity
2. **Signal unavailability**: Token probability methods (FLARE) require logits unavailable from completion-only models (o1)
3. **Efficiency collapse**: Fixed-interval retrieval (IRCoT) adds 2-5s per call, prohibitive for 12K-25K token chains

**Formal Statement**: Given query q, document collection D, reasoning model generating chain R = (r_1, ..., r_n) where each r_i is a reasoning step (logical unit spanning multiple sentences), learn an intervention policy π that at each step decides:
- Retrieve decision: a^ret_i ∈ {0,1}
- Query formulation: q_i = f(q, r_{1:i})
- Context integration: c_i = g(r_{1:i}, R_i)

Objective: max_π E_{q~Q}[Acc(a_π, a*) - λ · Cost(π)]

## Method: ReaLM-Retrieve Three Components

### Component 1: Step-Level Uncertainty Detection (RSUS)

**Reasoning Step Uncertainty Score** — a composite of three signals:

```
RSUS(r_i) = α · U_verb(r_i) + β · U_ent(r_i) + γ · U_cons(r_i)
```

with learned weights (α, β, γ) = (0.40, 0.35, 0.25) maximizing correlation (r=0.72) with downstream retrieval benefit.

**U_verb — Verbalized Uncertainty**: Prompt at step boundaries: "Rate your confidence that the current conclusion is factually correct (0-100)". Normalized to [0,1]. For completion-only models: 2-layer MLP proxy trained on SBERT embedding + surface features (hedge phrases, named entities), achieving 0.71 AUROC vs 0.83 for true verbalized confidence.

**U_ent — Entity-based Entropy**: Extract named entities from r_i, compute retrieval score entropy across candidate documents:
```
U_ent(r_i) = -Σ_{e∈Ent(r_i)} p(e|D) log p(e|D)
```
High entropy = entities with ambiguous/sparse corpus coverage. Uses BM25 scores from top-100 documents per entity.

**U_cons — Consistency Signal**: Sample k=3 alternative continuations at critical steps (identified by discourse markers), measure agreement. Disagreement indicates reasoning uncertainty.

**Overhead**: RSUS adds only 8% to reasoning inference vs 500-2000% for semantic entropy.

### Component 2: Reasoning Step Segmentation

Lightweight classifier (3-layer transformer encoder, hidden dim 256, 4 attention heads) operating on 128-token sliding windows with 64-token stride. Predicts boundary probability from:
1. Discourse markers ("therefore", "however", "this means")
2. Logical connectives indicating inference completion
3. Topic shifts via embedding similarity
4. Punctuation and formatting patterns

**Training**: 2,847 human-annotated reasoning traces from DeepSeek-R1 on NaturalQuestions. Inter-annotator agreement κ=0.78. Trained 10 epochs, lr=5×10^{-5}, batch size 32. Achieves 94.2% F1 on held-out test (N=412 traces). Average segment: 127 tokens vs 23 for sentence-level.

**Generalization**: On out-of-domain benchmarks, boundary F1 degrades modestly (1.5-3.0 points): MuSiQue 91.4%, HotpotQA 92.7%, 2WikiMultiHopQA 91.2%.

### Component 3: Learned Retrieval Intervention Policy

Modeled as contextual bandit with state s_i = (q, r_{1:i}, RSUS(r_i), h_i) where h_i encodes retrieval history.

```
a^ret_i = 1[π_θ(s_i) > τ]    (τ = 0.65)
q_i = QueryGen(s_i) if a^ret_i = 1
```

**Policy architecture**: Lightweight transformer encoder processing concatenation of query embedding, current reasoning step embedding, RSUS features, and retrieval history. Outputs retrieval probability + query representation.

**Training**: REINFORCE with reward R = F1(a_π, a*) - λ_1 · n_ret - λ_2 · t_latency. QueryGen receives gradients via same reward signal. Curriculum learning: start with high λ (penalize retrieval), gradually decrease.

**QueryGen**: Single-layer transformer decoder (hidden dim 512, 8 heads) cross-attending to current reasoning step. Queries formulated as information needs ("What is [entity]'s relationship to [concept]?") outperform direct reasoning-step queries.

### Efficient Retrieval Integration

**Implicit compression**: Attention-weighted importance scores for retrieved passages, retain only sentences exceeding threshold τ_rel=0.45. Reduces context expansion by 73% while preserving 96% of retrieval utility.

**Speculative caching**: After first retrieval, speculatively retrieve documents for likely next-step queries based on entities in retrieved content. 37% hit rate eliminates retrieval latency entirely for those calls.

**KV-cache preservation**: For open-weight models, preserves cached key-value states for unchanged context portions. Reduces time-to-first-token after retrieval by 2.1x.

**Combined effect**: 3.2x per-call efficiency improvement (0.66s vs 2.10s naive), enabling 1.33x lower end-to-end latency than IRCoT.

## Experimental Results

### Main Results (Multi-hop QA)

**DeepSeek-R1-Distill-Qwen-32B**:

| Method | MuSiQue F1 | MuSiQue Calls | HotpotQA F1 | HotpotQA Calls | 2WikiMHQA F1 | 2WikiMHQA Calls | Avg F1 |
|--------|-----------|--------------|------------|---------------|-------------|----------------|--------|
| No Retrieval | 48.7 | 0.0 | 51.2 | 0.0 | 47.3 | 0.0 | 49.1 |
| Single RAG | 59.4 | 1.0 | 62.8 | 1.0 | 60.1 | 1.0 | 60.8 |
| IRCoT | 65.4 | 3.4 | 67.9 | 4.1 | 66.2 | 3.8 | 66.5 |
| FLARE* | 62.3 | 2.8 | 65.4 | 3.2 | 63.7 | 2.9 | 63.8 |
| Self-RAG† | 61.9 | 2.1 | 66.3 | 2.4 | 64.5 | 2.2 | 64.2 |
| Search-R1 | 66.8 | 2.4 | 69.2 | 2.7 | 67.4 | 2.5 | 67.8 |
| **ReaLM-Retrieve** | **71.2** | **1.8** | **71.8** | **1.9** | **69.7** | **1.7** | **70.9** |

All ReaLM-Retrieve improvements significant at p<0.01 (paired bootstrap, 10K iterations, Bonferroni corrected).

**DeepSeek-R1-671B**:

| Method | MuSiQue F1 | Calls | HotpotQA F1 | Calls | Avg F1 |
|--------|-----------|------|------------|------|--------|
| Search-R1 | 73.4 | 2.6 | 75.2 | 2.8 | 74.1 |
| **ReaLM-Retrieve** | **77.8** | **1.9** | **78.4** | **2.0** | **77.6** |

4.4% absolute improvement over Search-R1 (p<0.01).

### Statistical Significance (R1-32B)

| Dataset | ΔF1 vs IRCoT | 95% CI | ΔF1 vs Search-R1 | 95% CI |
|---------|-------------|--------|-----------------|--------|
| MuSiQue | +5.8 | [4.2, 7.4] | +4.4 | [2.9, 5.9] |
| HotpotQA | +3.9 | [2.4, 5.4] | +2.6 | [1.2, 4.0] |
| 2WikiMHQA | +3.5 | [2.1, 4.9] | +2.3 | [0.9, 3.7] |

### Efficiency Analysis (MuSiQue, R1-32B)

| Method | Calls | Latency (s) | Per-Call (s) | Tokens | F1/Call |
|--------|-------|-------------|-------------|--------|---------|
| No Retrieval | 0.0 | 12.4 | – | 8,432 | – |
| Single RAG | 1.0 | 13.2 | 0.80 | 9,156 | 59.4 |
| Naive Interleave | 4.2 | 21.2 | 2.10 | 12,847 | 14.9 |
| IRCoT | 3.4 | 18.7 | 1.85 | 11,284 | 19.2 |
| FLARE | 2.8 | 16.9 | 1.61 | 10,647 | 22.3 |
| Search-R1 | 2.4 | 15.8 | 1.42 | 10,102 | 27.8 |
| **ReaLM-Retrieve** | **1.8** | **14.1** | **0.66** | **9,489** | **39.6** |

Cost savings vs IRCoT: 16% (conservative, output-token only at $2.19/1M tokens).

### Ablation Study (MuSiQue, R1-32B)

| Configuration | F1 | Calls | ΔF1 |
|--------------|-----|-------|-----|
| Full ReaLM-Retrieve | 71.2±0.6 | 1.8±0.1 | – |
| **Uncertainty ablation** | | | |
| w/o U_verb | 68.4±0.8 | 2.1±0.2 | -2.8** |
| w/o U_ent | 69.1±0.7 | 1.9±0.1 | -2.1** |
| w/o U_cons | 70.3±0.5 | 1.8±0.1 | -0.9* |
| RSUS → Random | 62.7±1.2 | 1.8±0.1 | -8.5** |
| **Policy ablation** | | | |
| Fixed threshold τ | 68.9±0.9 | 2.4±0.2 | -2.3** |
| w/o Query formulation | 69.4±0.6 | 1.8±0.1 | -1.8** |
| w/o Retrieval history | 69.8±0.7 | 2.0±0.1 | -1.4* |
| **Integration ablation** | | | |
| w/o Implicit compression | 70.8±0.5 | 1.8±0.1 | -0.4 |
| w/o Speculative cache | 71.0±0.6 | 1.8±0.1 | -0.2 |
| w/o KV preservation | 70.9±0.5 | 1.8±0.1 | -0.3 |

Key finding: **Verbalized uncertainty contributes most** (-2.8% F1 when removed). Random triggering degrades by 8.5%, proving *when* to retrieve matters enormously.

### Performance by Question Complexity

| Hops | ReaLM-Retrieve F1 | IRCoT F1 | ΔF1 |
|------|------------------|---------|-----|
| 2-hop | 72.1 | 68.9 | +3.2 |
| 3-hop | 69.4 | 63.6 | +5.8 |
| 4-hop | 66.2 | 57.8 | +8.4 |

Advantage increases with complexity: step-level uncertainty detection provides most value on longer reasoning chains.

## Training/Implementation Configuration

- **Hardware**: 8× NVIDIA A100 80GB GPUs
- **Reasoning inference**: vLLM with tensor parallelism
- **Retrieval**: ColBERTv2 with PLAID engine, WARP optimizations (171ms avg latency)
- **Policy training**: 50,000 steps, lr=10^{-4}, batch size 64, curriculum-decreasing λ_1 from 0.5 to 0.1
- **RSUS weights**: (α, β, γ) = (0.40, 0.35, 0.25) via grid search on validation split
- **Compression threshold**: τ_rel = 0.45 (retains 27% of content, preserves 96% utility)
- **Retrieval threshold**: τ = 0.65 (balances precision 0.72 / recall 0.81)
- **Statistical testing**: Paired bootstrap (10K iterations), Bonferroni correction, 3 seeds (42, 123, 456)

## Comparison with Related Approaches

| Method | Granularity | Black-box Compatible | RL Training | Step-Level Uncertainty | Efficiency Optimized |
|--------|-----------|---------------------|-------------|----------------------|---------------------|
| Single RAG | Query | ✅ | ❌ | ❌ | N/A |
| IRCoT | Sentence | ✅ | ❌ | ❌ | ❌ |
| FLARE | Token | ❌ (needs logits) | ❌ | ❌ | ❌ |
| DRAGIN | Token | ❌ (needs attention) | ❌ | ❌ | ❌ |
| Self-RAG | Sentence | ❌ (needs fine-tuning) | ❌ | Partial | ❌ |
| Search-R1 | Step | ✅ | ✅ | ❌ | Partial |
| **ReaLM-Retrieve** | **Reasoning step** | **✅** | **✅** | **✅ RSUS** | **✅ 3.2x** |

## Critical Analysis

### Strengths
1. **Principled problem formulation**: Clearly identifies the temporal mismatch between RAG and reasoning models
2. **RSUS is elegant**: Three complementary uncertainty signals (verbalized, entity-entropy, consistency) with only 8% overhead vs 500-2000% for semantic entropy
3. **Strong empirical results**: +10.1% F1 with 47% fewer retrieval calls — establishes new Pareto frontier
4. **Comprehensive ablation**: Each component's contribution isolated, random triggering degrades 8.5% — proves the method works
5. **Scales with model capability**: Results improve from R1-32B (71.2%) to R1-671B (77.8%)
6. **Well-engineered**: KV-cache preservation, speculative caching, implicit compression — practical deployment considerations

### Weaknesses / Questions
1. **Step segmentation dependency**: The classifier (94.2% F1 in-domain, ~91% OOD) introduces a failure mode — mis-segmented steps propagate errors through RSUS
2. **Verbalized confidence quality**: The proxy for completion-only models achieves 0.71 AUROC vs 0.83 for true verbalized confidence — a significant gap
3. **Limited to multi-hop QA**: Evaluation only on MuSiQue, HotpotQA, 2Wiki. Generalization to other reasoning tasks (math, coding, planning) unknown.
4. **No comparison to concurrent "Dynamic Search-R1"**: The paper mentions it as orthogonal but doesn't experiment with combining adaptive timing + adaptive depth.
5. **Fixed k=3 for consistency sampling**: No ablation on the number of alternative continuations sampled.
6. **QueryGen is simple**: Single-layer transformer decoder — more sophisticated query formulation might yield further gains.

### Implications for Our Work
- **Step-level uncertainty detection** is directly applicable to agent reasoning: knowing *when* an agent needs to retrieve vs. reason from memory is crucial
- The **RSUS triple-signal approach** (self-report + entity coverage + consistency) is a practical uncertainty quantification method for black-box models
- **Speculative caching** (37% hit rate) is a general technique applicable to any agent system with predictable query patterns
- The **granularity insight** (reasoning-step > sentence > token) suggests agent memory retrieval should operate at decision-boundary granularity
- For [[retrieval]] systems, this work demonstrates that fewer, better-timed retrievals outperform frequent fixed-interval ones

## Related

- [[retrieval]] — Retrieval-augmented generation
- [[reasoning]] — Chain-of-thought and multi-step reasoning
- [[agent]] — AI agent architectures
- [[inference]] — Inference optimization techniques
