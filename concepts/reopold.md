---
title: "Reopold"
created: 2026-04-06
updated: 2026-04-10
type: concept
tags: ['distillation', 'on-policy', 'reasoning']
sources: []
---

     1|# Reopold (Relaxed On-Policy Distillation)
     2|
     3|Reopold is a framework for stabilizing and improving on-policy distillation of reasoning capabilities to compact language models. It addresses fundamental optimization instabilities inherited from reinforcement learning when using reverse KL divergence as the distillation objective.
     4|
     5|## Core Insight
     6|
     7|On-policy distillation with reverse KL (RKL) is theoretically equivalent to policy gradient optimization where the token-level log-likelihood ratio between teacher and student acts as a reward signal. This equivalence allows diagnosis of optimization failures through RL lens.
     8|
     9|## Three Optimization Challenges Addressed
    10|
    11|| Challenge | Cause | Reopold Solution |
    12||-----------|-------|------------------|
    13|| Heavy-tailed negative rewards | Student samples tokens with near-zero teacher probability | Mixture-based reward clipping (Eq. 7) |
    14|| Near-zero reward inefficiency | Most tokens have aligned student-teacher distributions | Entropy-guided token-level dynamic sampling |
    15|| Entropy collapse | Aggressive negative penalties eliminate exploration | Exploration-to-refinement multi-stage training |
    16|
    17|## Technical Components
    18|
    19|### 1. Mixture-Based Reward Clipping
    20|
    21|Uses convex combination bound to derive principled clipping floor:
    22|
    23|R_hat = max(sg(R), log(lambda)/(1-lambda))
    24|
    25|Unlike PPO's rho-clipping which constrains policy updates, this clips the reward signal itself to prevent gradient explosion from extreme negative values.
    26|
    27|### 2. Entropy-Guided Dynamic Sampling
    28|
    29|Filters gradient computation to high-entropy tokens only (top beta percentile), where student-teacher divergence is maximal and learning signal is strongest. Low-entropy tokens provide vanishing gradients.
    30|
    31|### 3. Multi-Stage Training
    32|
    33|- **Exploration phase** (first T_switch steps): Masks strongly negative rewards to prevent entropy collapse, mimicking SFT dynamics
    34|- **Refinement phase**: Switches to entropy-based masking to focus on critical branching points
    35|
    36|## Experimental Results
    37|
    38|| Task | Key Finding |
    39||------|-------------|
    40|| Math reasoning (1.5B student) | 6.7-12x sample efficiency vs RL; outperforms RKL by 4.96% avg |
    41|| Visual reasoning (3B student) | 3.32x inference speedup vs 32B teacher; matches accuracy |
    42|| Agentic tool-use | Outperforms GRPO with complex rewards using simple distillation signal |
    43|
    44|## Relation to Existing Concepts
    45|
    46|- Extends [[on-policy-distillation]] with RL-aware stabilization
    47|- Contrasts with [[generalized-on-policy-distillation|G-OPD]]: Reopold clips rewards rather than scaling them
    48|- More aggressive filtering than [[video-opd]] or [[vold]]
    49|- Unlike [[on-policy-self-distillation|OPSD]], requires external teacher
    50|- Uses stop-gradient as control variate, similar to [[proximal-policy-distillation|PPD]] but without PPO clipping
    51|
    52|[src: raw/ingested/2026/03/2603.11137.md]