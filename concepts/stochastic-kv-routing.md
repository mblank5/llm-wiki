---
title: "Stochastic KV Routing: Random Cross-Layer Attention for Depth-Wise Cache Sharing"
created: 2026-05-05
updated: 2026-05-05
type: concept
tags: [inference, memory, architecture, training]
sources: ["arxiv:2604.22782"]
---

# Stochastic KV Routing (R-CLA)

## Core Problem Definition

**Formal Statement.** During autoregressive inference, a Transformer with $L$ layers stores a KV cache of size:

$$M = L \times (T + t) \times S$$

where $T$ is the prompt length, $t$ is the number of generated tokens, and $S$ is the per-layer KV state size. For Llama-2-7B, a single token's KV cache is ~512 KB — a 100,000x expansion from the 2-4 byte token representation. Caching the context of a single book consumes more memory than the model weights themselves.

**Prior work** focuses on *temporal* eviction (dropping tokens along the time axis). This paper argues the *depth* dimension offers an orthogonal and robust optimization avenue.

**Key hypothesis:** Full per-layer caching is redundant. Layers exhibit high inter-layer redundancy, and a model can be trained to function with shared KV states across layers.

**Challenge:** Existing cross-layer attention (CLA) methods either require separate encoders (XC-Cache), multiple forward passes (Layer-Condensed), or are post-hoc (MiniCache). None provide a practical, efficient training scheme.

## Method

### Cross-Layer Attention (CLA)

In standard self-attention, layer $l$ computes:
$$\text{Output}_l = \text{Attn}(Q_l, K_l, V_l)$$

In CLA, layer $l$ attends to the KV states of a *preceding* layer $l' < l$:
$$\text{Output}_l = \text{Attn}(Q_l, K_{l'}, V_{l'}) \quad \text{where } l' \leq l$$

When $l' < l$, the model reuses the cache of a previous layer, eliminating the need to store a unique cache for layer $l$.

### Random Cross-Layer Attention (R-CLA)

**Training procedure.** For each forward pass of layer $l$:
- With probability $p$: perform standard self-attention ($l' = l$)
- With probability $1-p$: attend to KV states of a randomly chosen preceding layer $l' \sim \text{Uniform}(\{1, \ldots, l-1\})$

This stochastic process forces the query projection $Q_l$ to learn to interact with a wide variety of key/value distributions from different layers. The model becomes invariant to the source of KV states.

**Inference.** A fixed deterministic cache sharing strategy $\mathcal{S} \subseteq \{1, \ldots, L\}$ is employed. For any layer $l$, the cache mapping is:

$$\mu(l) = \begin{cases} l & \text{if } l \in \mathcal{S} \\ \max\{j \in \mathcal{S} : j < l\} & \text{otherwise} \end{cases}$$

**Key property:** The same model can deploy across different hardware environments by simply changing $\mathcal{S}$. High-end: $\mathcal{S} = \{1,\ldots,L\}$ (full cache). Edge: $\mathcal{S} = \{1, 5, 9, \ldots\}$ (sparse cache). No retraining needed.

### Cache Sharing Strategies

Examples:
- **Every 4th layer**: $\mathcal{S} = \{4, 8, 12, \ldots\}$ → 75% memory reduction
- **Groups of 2-3**: $\mathcal{S} = \{1, 3, 6, 8, \ldots\}$ → 50-67% memory reduction
- **Single cache**: $\mathcal{S} = \{1\}$ → maximum compression (not evaluated)

### Algorithm

```
Algorithm: R-CLA Training
for each layer l = 1 to L do
    Compute Q_l from input
    Sample b ~ Bernoulli(p)
    if b = 1 then
        Use own KV states (K_l, V_l)     # self-attention
    else
        Sample l' ~ Uniform({1,...,l-1})
        Use KV states from layer l'        # cross-layer attention
    end if
    Output_l = Attn(Q_l, K_{l'}, V_{l'})
end for
```

```
Algorithm: R-CLA Inference (Deterministic)
Given cache strategy S
for each layer l = 1 to L do
    Compute Q_l from input
    if l ∈ S then
        Load own KV states (K_l, V_l)
        Update cache for layer l
    else
        Load KV states from μ(l) = max{j ∈ S : j < l}
    end if
    Output_l = Attn(Q_l, K_{μ(l)}, V_{μ(l)})
end for
```

## Training Configuration

### Pre-training
| Parameter | Value |
|-----------|-------|
| Architecture | Qwen-1.7B-style decoder-only Transformer |
| Context length | 2,048 tokens |
| Optimizer | AdamW ($\beta_1=0.9, \beta_2=0.95$) |
| Training tokens | Fixed budget (equal across all runs) |
| R-CLA probability $p$ | 0.5 (default), up to 0.75 |
| Baseline comparison | Shallower Transformers with same cache footprint |

### Fine-tuning (QA tasks)
| Parameter | Value |
|-----------|-------|
| Models | Llama-3.1-8B, Mistral-7B, Qwen3-8B |
| R-CLA probability $p$ | 0.6 |
| Cache retention levels | 100%, 50%, 25% |
| Tasks | HotpotQA, MSMarco |

## Experimental Results

### Pre-training Stability

Training loss with R-CLA ($p=0.75$) is 2.46 vs. 2.46 for standard training ($p=0$) — less than 2% degradation despite 75% of attention operations being redirected to preceding layers. Training dynamics remain stable (see Appendix A).

### Cache Size vs. Performance (Figure 2, 3)

R-CLA models maintain performance much better than base models as cache retention decreases. At 25% retention, R-CLA models retain most of their full-cache performance while base models degrade severely.

### Deeper Models with Shared Cache vs. Shallower Models (Figure 5)

R-CLA models (28-layer with depth-wise cache sharing) consistently outperform shallower Transformers with the same cache footprint. This shows that cache sharing preserves the benefit of depth — deeper models with shared cache beat shallower models with full cache.

### QA Fine-tuning Results (Table 2)

**HotpotQA (F1 scores):**

| Model | Retention | Base | R-CLA | Δ% |
|-------|-----------|------|-------|-----|
| Llama-3.1-8B | 100% | 0.203 | 0.306 | +51.1% |
| Llama-3.1-8B | 50% | 0.171 | 0.305 | +78.7% |
| Llama-3.1-8B | 25% | 0.080 | 0.237 | +196.2% |
| Mistral-7B | 100% | 0.215 | 0.242 | +12.4% |
| Mistral-7B | 50% | 0.162 | 0.211 | +30.0% |
| Mistral-7B | 25% | 0.031 | 0.162 | +421.3% |
| Qwen3-8B | 100% | 0.233 | 0.357 | +53.1% |
| Qwen3-8B | 50% | 0.085 | 0.314 | +267.8% |
| Qwen3-8B | 25% | 0.011 | 0.098 | +826.6% |

**MSMarco (F1 scores):**

| Model | Retention | Base | R-CLA | Δ% |
|-------|-----------|------|-------|-----|
| Llama-3.1-8B | 100% | 0.301 | 0.318 | +5.6% |
| Llama-3.1-8B | 50% | 0.226 | 0.324 | +43.2% |
| Mistral-7B | 100% | 0.310 | 0.316 | +1.7% |
| Mistral-7B | 50% | 0.236 | 0.300 | +26.9% |
| Qwen3-8B | 100% | 0.291 | 0.329 | +13.0% |
| Qwen3-8B | 50% | 0.112 | 0.227 | +102.4% |

**Key finding:** The benefits of R-CLA are most dramatic at low cache retention rates. At 25% retention, R-CLA provides 200-800% relative improvement. Even at 100% retention, R-CLA often *improves* over baseline (regularization effect).

## Comparison with Existing Methods

| Method | Approach | Training | TTFT Impact | Memory Reduction |
|--------|----------|----------|-------------|-----------------|
| H2O | Attention-based eviction | None | None | ~30% |
| SnapKV | Importance scoring | None | None | ~40% |
| PyramidKV | Layer-varying budget | None | None | ~50% |
| XC-Cache | Shared cache + encoder | Requires encoder | High | ~50% |
| Layer-Condensed | Single shared cache | Multiple passes | Very high | ~75% |
| MiniCache | Post-hoc merging | None | None | ~30% |
| KVSharer | SVD-based sharing | None | None | ~30% |
| **R-CLA** | **Random cross-layer attention** | **Single training run** | **None** | **50-75%** |

## Critical Analysis

### Strengths
1. **Simplicity**: The training procedure is remarkably simple — just randomize the KV source during training. No auxiliary losses, no extra networks.
2. **Flexibility**: One model supports arbitrary cache sharing strategies at deployment time. This is a major practical advantage for serving across heterogeneous hardware.
3. **No TTFT penalty**: Unlike XC-Cache (requires encoder forward pass) or Layer-Condensed (multiple passes), R-CLA has no time-to-first-token overhead.
4. **Regularization effect**: R-CLA often *improves* full-cache performance, suggesting the stochastic training acts as a regularizer.
5. **Orthogonal to temporal methods**: Can be combined with H2O, SnapKV, etc. for compounded gains.
6. **Strong empirical results**: 50-75% memory reduction with *improved* performance is exceptional.

### Weaknesses and Open Questions
1. **Training cost**: Requires training from scratch or fine-tuning. Cannot be applied to existing pretrained models without additional training.
2. **Probability tuning**: The optimal $p$ value may vary by model architecture and task. The paper uses $p=0.5$ or $p=0.6$ but doesn't provide a systematic study.
3. **Layer grouping constraints**: The paper doesn't explore whether certain layer groupings are better than others. Is uniform spacing optimal?
4. **Long-context behavior**: Evaluation is at 2048 context length. Behavior at 32K+ contexts (where KV cache pressure is most severe) is untested.
5. **Causal masking interaction**: How does R-CLA interact with causal masking during autoregressive generation? The paper doesn't discuss this in detail.
6. **Multi-head attention**: All heads in a layer share the same KV source during R-CLA. Per-head randomization might provide finer control.

### Implications for Our Work
- **For [[inference]] optimization**: R-CLA is one of the most practical KV cache reduction methods — no TTFT penalty, flexible deployment
- **For [[agent]] systems**: Long-running agents with extensive context would benefit from 50-75% memory reduction
- **For [[memory]] systems**: The depth-wise sharing idea could inspire memory-efficient agent architectures
- **For serving infrastructure**: The single-model-multiple-strategies property is ideal for multi-tenant serving

## Related
- [[inference]] — Inference optimization techniques
- [[memory]] — Memory systems for agents
- [[agent]] — Agent architecture and design
- [[audio-kv-cache]] — KV cache optimization for audio models
