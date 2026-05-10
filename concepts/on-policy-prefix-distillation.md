---
title: "On Policy Prefix Distillation"
created: 2026-04-06
updated: 2026-04-10
type: concept
tags: ['distillation', 'on-policy', 'training']
sources: []
---

     1|# On-Policy Prefix Distillation (OPPD)
     2|
     3|On-Policy Prefix Distillation (OPPD) is a computationally efficient variant of [[on-policy-distillation|OPD]] that applies the distillation objective exclusively to the **prefix** of student-generated outputs, terminating sampling early during distillation.
     4|
     5|## Motivation
     6|
     7|Standard [[on-policy-distillation|OPD]] requires expensive on-the-fly sampling of full student trajectories during training, especially costly for long responses. Analysis shows that training signals in OPD are **concentrated in the prefix** of each output, and even a short teacher-generated prefix can significantly guide the student toward the correct answer.
     8|
     9|## Core Mechanism
    10|
    11|| Step | Description |
    12||------|-------------|
    13|| 1 | Student samples partial trajectory (prefix) τ_prefix = (a_1,...,a_k) ~ π_θ(·|x), where k << T (full length) |
    14|| 2 | Teacher π_tea computes log-probabilities for each prefix token |
    15|| 3 | Distillation loss applied only to prefix tokens: L = sum_{t=1}^k KL(π_tea(·|s_t) || π_θ(·|s_t)) |
    16|| 4 | Sampling terminated after prefix; no full rollout needed |
    17|
    18|## Key Advantages
    19|
    20|| Property | Full OPD | OPPD (Ours) |
    21||----------|----------|-------------|
    22|| Optimization | On-policy | On-policy |
    23|| Supervision scope | Full output | Prefix only |
    24|| Sampling cost | Full trajectory | Early termination |
    25|| Training FLOP | Baseline | 2×–47× reduction |
    26|| Performance | Baseline | Matched |
    27|
    28|## Experimental Validation
    29|
    30|- Matches full [[on-policy-distillation|OPD]] performance on AI-for-Math and out-of-domain benchmarks
    31|- 2×–47× FLOP reduction depending on response length and prefix ratio
    32|- Effective across diverse task types including mathematical reasoning
    33|
    34|## Relation to Existing Concepts
    35|
    36|- Direct optimization of [[on-policy-distillation|OPD]] with computational efficiency focus
    37|- Contrasts with [[video-opd]]: OPPD uses prefix truncation, Video-OPD uses dense token supervision over full outputs
    38|- Contrasts with [[on-policy-self-distillation|OPSD]]: OPPD uses external teacher, OPSD is self-teaching
    39|- Orthogonal to [[generalized-on-policy-distillation|G-OPD]]: OPPD can be combined with reward scaling variants
    40|- Related to early-exiting strategies in [[model-distillation]]
    41|
    42|[src: raw/ingested/2026/02/2602.15260.md]