---
title: "Per Token Kl Clipping"
created: 2026-04-06
updated: 2026-04-10
type: concept
tags: ['distillation', 'optimization']
sources: []
---

     1|# Per-Token Pointwise KL Clipping
     2|
     3|A stabilization technique used in [[on-policy-self-distillation]] to prevent stylistic tokens from dominating the training signal.
     4|
     5|## Problem
     6|
     7|Per-token KL divergence is highly skewed: stylistic tokens (e.g., "let", "therefore", "first") exhibit much higher divergence than mathematically meaningful tokens. This imbalance causes training instability and performance collapse.
     8|
     9|## Solution
    10|
    11|Clip vocabulary-level divergence contributions pointwise:
    12|
    13|- For f-divergence D_f(p_T||p_S), at position n and vocabulary entry v:
    14|  - l_n,v^(f) = p_T(v|·) * f(p_S(v|·)/p_T(v|·))
    15|- Clipped divergence: D_clip^(f) = (1/|ŷ|) sum_n sum_v min(l_n,v^(f), tau)
    16|
    17|## Effect
    18|
    19|- Prevents performance degradation during rapid OPSD convergence (within 100 steps).
    20|- Preserves learning signal on math tokens while suppressing noise from style tokens.
    21|
    22|[src: raw/ingested/2026/01/2601.18734.md]

## Related

- [[on-policy-self-distillation]] — Source setting where per-token clipping is used.
- [[kl-divergence-in-distillation]] — KL objective stabilized by clipping.
- [[on-policy-distillation]] — Broader distillation family.
