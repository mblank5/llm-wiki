---
title: "On Policy Self Distillation"
created: 2026-04-06
updated: 2026-04-10
type: concept
tags: ['distillation', 'on-policy', 'reasoning']
sources: []
---

     1|# On-Policy Self-Distillation (OPSD)
     2|
     3|On-Policy Self-Distillation (OPSD) is a post-training framework for large language models (LLMs) on reasoning tasks where a single model acts as both teacher and student. The teacher policy conditions on privileged information (ground-truth solution y*), while the student policy conditions only on the problem x. Training minimizes per-token divergence between teacher and student distributions over student-generated rollouts.
     4|
     5|## Core Mechanism
     6|
     7|- **Student Policy**: p_S(·|x) = p_theta(·|x) — sees only problem.
     8|- **Teacher Policy**: p_T(·|x,y*) = p_theta(·|x,y*) — sees problem and ground-truth solution.
     9|- **On-Policy Sampling**: Student generates response ŷ ~ p_S(·|x).
    10|- **Dense Token-Level Supervision**: At each position n, compute divergence D(p_T(·|x,y*,ŷ_<n) || p_S(·|x,ŷ_<n)).
    11|- **Loss**: L_OPSD = E_(x,y*)~S [ E_ŷ~p_S [ sum_n D(...) ] ]
    12|
    13|## Key Innovations
    14|
    15|| Feature | Description |
    16||---------|-------------|
    17|| Self-Teaching | No external teacher model required |
    18|| Dense Feedback | Per-token supervision vs. sequence-level RL rewards |
    19|| On-Policy | Mitigates distribution mismatch |
    20|| Per-Token Pointwise KL Clipping | Stabilizes training by limiting dominance of stylistic tokens |
    21|| Forward KL Preferred | Forward KL outperforms reverse KL and JSD empirically |
    22|
    23|## Advantages over Alternatives
    24|
    25|| Method | On-Policy | Dense Signal | No External Teacher | Low Sampling Cost |
    26||--------|-----------|-------------|---------------------|-------------------|
    27|| SFT | ✗ | ✓ | ✓ | ✓ |
    28|| GRPO | ✓ | ✗ | ✓ | ✗ |
    29|| On-Policy Distillation | ✓ | ✓ | ✗ | ✓ |
    30|| **OPSD (Ours)** | **✓** | **✓** | **✓** | **✓** |
    31|
    32|## Experimental Findings
    33|
    34|- OPSD matches or exceeds GRPO on AIME24, AIME25, HMMT25 with 10x fewer tokens.
    35|- Student: Thinking Mode off; Teacher: Thinking Mode on — maximizes KL on math tokens.
    36|- Generation length 1024 sufficient; longer sequences don't consistently improve.
    37|- Full-vocabulary logit distillation outperforms sampled-token policy gradient.
    38|- SFT degrades performance due to concise solution style reducing test-time reasoning length.
    39|
## Relation to Existing Concepts

- Extends [[on-policy-distillation]] by eliminating need for separate teacher.
- Contrasts with [[star|STaR]]: OPSD provides token-level dense rewards vs. STaR's sequence-level binary rewards.
- Related to [[policy-distillation]] and [[model-distillation]], adapted for autoregressive LLMs.
- Uses [[grp-o|GRPO]] as baseline comparison.
- Related to [[on-policy-self-distillation-reasoning-compression|OPSDC]]: a self-distillation variant targeting reasoning compression.

[src: raw/ingested/2026/01/2601.18734.md]