---
title: Dual Policy Distillation
created: 2026-04-06
updated: 2026-04-10
type: concept
tags: ['distillation', 'training']
sources: []
---

     1|# Dual Policy Distillation (DPD)
     2|
     3|Dual Policy Distillation (DPD) is a student-student framework in reinforcement learning where two policies operate on the same environment and extract knowledge from each other to enhance learning, without requiring a pre-trained expert teacher model. Proposed by Lai et al. (2020).
     4|
     5|## Core Idea
     6|
     7|Unlike traditional [[policy-distillation]] which transfers knowledge from a teacher to a student, DPD involves two simultaneously trained student policies (π_θ and π_φ) with different initializations. Each policy iteratively optimizes its own RL objective and a distillation objective that regresses to the other peer policy.
     8|
     9|## Key Theoretical Foundation
    10|
    11|### Hypothetical Hybrid Policy
    12|
    13|A hypothetical hybrid policy π_hypo is defined that selectively follows the policy with higher value at each state:
    14|
    15|π_hypo(·|s) = π_φ(·|s) if V^π_φ(s) > V^π(s), else π(·|s)
    16|
    17|**Proposition 1**: This hybrid policy guarantees policy improvement: V^π_hypo(s) ≥ V^π(s) and V^π_hypo(s) ≥ V^π_φ(s) for all states s.
    18|
    19|### Disadvantageous Policy Distillation
    20|
    21|**Proposition 2**: Distilling from π_hypo is equivalent to minimizing:
    22|
    23|J = E_{s~π_φ}[D(π(·|s), π_φ(·|s)) * 1(ξ^π_φ(s) > 0)]
    24|
    25|where ξ^π_φ(s) = V^π_φ(s) - V^π(s) is the advantage of the peer policy. This prioritizes distillation at states where the current policy is disadvantaged.
    26|
    27|In practice, a softened weighted objective is used:
    28|
    29|J^w_π_θ(θ) = E_{s~π_φ}[D(π_θ(·|s), π_φ(·|s)) * exp(α * ξ^π_φ(s))]
    30|
    31|where α controls confidence level based on value estimation accuracy.
    32|
    33|## Connection to Value Iteration
    34|
    35|Distilling at disadvantage states pushes policy values towards optimal values, analogous to value iteration's max operation. For states where V^π_φ(s) > V^π(s), we have V^π*(s) ≥ V^π_φ(s) > V^π(s), so adopting π_φ's actions moves π closer to optimal.
    36|
    37|## Algorithm
    38|
    39|Alternating update: (1) Update π_θ via RL objective, (2) Update π_θ via distillation using mini-batch from π_φ's buffer, (3) Repeat for π_φ.
    40|
    41|## Experimental Results
    42|
    43|Evaluated with DDPG and PPO on Swimmer-v2, HalfCheetah-v2, Walker2d-v2, Humanoid-v2:
    44|
    45|- DPD outperforms vanilla DDPG/PPO by 10-15% in 3 of 4 tasks at half the timesteps
    46|- Two learners show complementary Q-values (supporting hybrid policy hypothesis)
    47|- Learners converge to similar policies over time (supporting similar visitation frequency assumption)
    48|
    49|## Relation to Existing Concepts
    50|
    51|- Extends [[policy-distillation]] to collaborative student-student setting
    52|- Contrasts with [[proximal-policy-distillation|PPD]]: DPD uses peer policies instead of expert teacher; PPD uses PPO clipping
    53|- Related to collaborative learning in cognitive psychology
    54|- Differs from multi-agent RL: two learners in independent single-agent environments
    55|
    56|[src: raw/ingested/2020/06/2006.04061.md]