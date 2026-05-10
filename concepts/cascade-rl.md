---
title: "Cascade Rl"
created: 2026-04-06
updated: 2026-04-10
type: concept
tags: ['rl', 'training', 'alignment']
sources: []
---

     1|# Cascade RL
     2|
     3|Cascade RL is a post-training framework for large language models that orchestrates sequential, domain-wise reinforcement learning training across specialized task domains. Introduced in Nemotron-Cascade 1 and substantially expanded in Nemotron-Cascade 2.
     4|
     5|## Core Properties
     6|
     7|| Property | Description |
     8||----------|-------------|
     9|| Sequential domain training | RL stages applied one after another, each focused on specific capability domain |
    10|| Catastrophic forgetting resistance | Domain-specific RL stages rarely degrade performance from earlier domains |
    11|| Hyperparameter specialization | Each domain can have tailored RL hyperparameters and curriculum |
    12|| Compute efficiency | Task homogeneity within stages yields uniform response lengths and verification times |
    13|
    14|## Cascade RL in Nemotron-Cascade 2
    15|
    16|The ordering of stages:
    17|
    18|1. **IF-RL** (Instruction-Following RL) - establishes foundational instruction adherence
    19|2. **Multi-domain RL** - enhances tool-calling, STEM reasoning, structured output
    20|3. **MOPD** (Multi-domain On-Policy Distillation) - stabilization, recovers regressions
    21|4. **RLHF** - human preference alignment
    22|5. **Long-context RL** - reasoning over massive input sequences
    23|6. **Code RL** - competitive coding problems
    24|7. **SWE RL** - agentic software engineering
    25|
    26|### Ordering Rationale
    27|
    28|- **Mitigating inter-domain interference**: IF-RL first because it can negatively impact human alignment; RLHF later has negligible impact on instruction following
    29|- **Scaling via multi-domain integration**: Groups non-conflicting domains (MCQA, tool calling, structured output)
    30|- **Stabilization through distillation**: MOPD placed after initial RL stages to recover benchmark regressions
    31|
    32|### Training Configuration
    33|
    34|Uses Group Relative Policy Optimization (GRPO) with strict on-policy training. KL divergence term removed entirely, simplifying to REINFORCE with group-normalized rewards and token-level loss.
    35|
    36|Objective:
    37|
    38|J_GRPO(theta) = E_(q,a)~D, {o_i}_i=1^G ~ pi_theta(·|q) [ 1/sum_i |o_i| * sum_i sum_t A_hat_i,t ]
    39|
    40|where A_hat_i,t = (r_i - mean({r_i})) / std({r_i}) for all t.
    41|
    42|## Relation to Existing Concepts
    43|
    44|- Extended by [[multi-domain-on-policy-distillation|MOPD]] for stabilization
    45|- Contrasts with vanilla sequential RL: substantially reduces catastrophic forgetting
    46|- Uses [[grp-o|GRPO]] as underlying RL algorithm
    47|- Related to [[on-policy-distillation]] but applied sequentially across domains
    48|
    49|[src: raw/ingested/2026/03/2603.19220.md]