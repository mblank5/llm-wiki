---
title: Generalized On Policy Distillation
created: 2026-04-06
updated: 2026-04-10
type: concept
tags: ['distillation', 'on-policy', 'training']
sources: []
---

     1|# Generalized On-Policy Distillation (G-OPD)
     2|
     3|Generalized On-Policy Distillation (G-OPD) is a theoretical and practical extension of standard [[on-policy-distillation|OPD]] that reformulates distillation as a dense KL-constrained reinforcement learning problem with two tunable components: a reward scaling factor lambda and a flexible reference model.
     4|
     5|## Core Formulation
     6|
     7|The G-OPD objective is:
     8|
     9|J_G-OPD(theta) = max_theta E_{x~D, y~pi_theta} [ lambda * log(pi*(y|x) / pi_ref(y|x)) - KL(pi_theta(y|x) || pi_ref(y|x)) ]
    10|
    11|Where:
    12|- pi_theta: student policy
    13|- pi*: teacher policy
    14|- pi_ref: reference model (any model, not necessarily student base)
    15|- lambda: reward scaling factor controlling relative weight of reward vs KL regularization
    16|
    17|## Key Variants
    18|
    19|| Lambda Range | Name | Behavior |
    20||-------------|------|----------|
    21|| 0 < lambda < 1 | Reward Interpolation | Student behavior interpolates between reference and teacher |
    22|| lambda = 1 | Standard OPD | Equal weighting of reward and KL |
    23|| lambda > 1 | [[ex-opd|Reward Extrapolation (ExOPD)]] | Student can surpass teacher capability boundary |
    24|
    25|## Reward Correction
    26|
    27|In [[strong-to-weak-distillation]] settings, setting pi_ref = teacher's pre-RL base model (rather than student base) yields more accurate implicit reward signals. This is termed "reward correction" but requires access to teacher's pre-RL checkpoint and incurs higher computational cost.
    28|
    29|## Theoretical Connection
    30|
    31|G-OPD reveals that OPD is a special case of dense RL where:
    32|1. Rewards are dense (token-level) via implicit reward log(pi*/pi_ref)
    33|2. Reward and KL are equally weighted (lambda=1)
    34|3. Reference model choice is arbitrary (does not affect simplified objective)
    35|
    36|## Experimental Findings
    37|
    38|- ExOPD (lambda=1.25) consistently outperforms OPD across math reasoning and code generation
    39|- In multi-teacher distillation, ExOPD produces unified students surpassing all domain teachers
    40|- Reward correction further improves strong-to-weak distillation
    41|- Excessive extrapolation (lambda=1.5) causes instability due to implicit reward hacking
    42|
    43|## Relation to Existing Concepts
    44|
    45|- Generalizes [[on-policy-distillation]] with tunable reward weighting
    46|- Contrasts with [[proximal-policy-distillation|PPD]]: G-OPD uses simple policy gradient, not PPO clipping
    47|- Extends [[video-opd]] and [[vold]] to unified theoretical framework
    48|- Related to implicit reward methods in [[free-process-rewards]]
    49|
    50|[src: raw/ingested/2026/02/2602.12125.md]

## See Also
- [[ex-opd]] — Extended OPD 变体
