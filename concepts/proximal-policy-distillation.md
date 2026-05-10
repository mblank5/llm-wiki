---
title: "Proximal Policy Distillation"
created: 2026-04-06
updated: 2026-04-10
type: concept
tags: ['distillation', 'ppo', 'training']
sources: []
---

     1|# Proximal Policy Distillation (PPD)
     2|
     3|Proximal Policy Distillation (PPD) is a novel policy distillation method that combines student-driven distillation with Proximal Policy Optimization (PPO) to improve sample efficiency and final performance. Unlike traditional policy distillation methods that treat distillation as a pure supervised learning task, PPD integrates environment rewards collected by the student during distillation into the optimization process.
     4|
     5|## Key Properties
     6|
     7|- **Student-Driven Exploration**: The student policy itself acts as the control policy for collecting trajectories, avoiding overfitting to the teacher's limited state-visitation distribution.
     8|
     9|- **PPO Integration**: Replaces the vanilla policy-gradient term in the distillation gradient with the PPO-clip surrogate objective. This includes:
    10|  - Reuse of rollout buffer data over multiple epochs for improved sample efficiency.
    11|  - Importance sampling weights to correct for policy drift.
    12|  - Clipping of both the PPO advantage term and the KL-divergence distillation loss for training stability.
    13|
    14|- **Robustness to Imperfect Teachers**: PPD consistently outperforms baseline methods when distilling from teachers whose parameters have been corrupted with Gaussian noise, often surpassing the corrupted teacher's performance.
    15|
    16|- **Hyperparameter lambda**: A balancing hyperparameter controls the relative weight of the PPO loss versus the distillation loss. Lower values allow the student to potentially outperform the teacher, while higher values speed up initial distillation.
    17|
    18|## Technical Formulation
    19|
    20|The PPD optimization objective is:
    21|
    22|L_PPD = E_{s,a~pi_theta_k} [ L_PPO(s,a,theta) - lambda * KL(pi_teacher(s) || pi_theta(s)) * max(pi_theta(a|s) / pi_theta_k(a|s), 1 - epsilon) ]
    23|
    24|Where L_PPO is the standard PPO-clip loss, lambda is the distillation weight, and epsilon is the clipping parameter.
    25|
    26|## Comparison to Baselines
    27|
    28|PPD was evaluated against:
    29|- **Student-Distill (SD)**: On-policy distillation treated as supervised learning, using the student as the sampling policy.
    30|- **Teacher-Distill (TD)**: Same as SD but using the teacher as the sampling policy.
    31|
    32|PPD showed superior sample efficiency and final test performance across Atari, Mujoco, and Procgen environments, for smaller, same-size, and larger student networks.
    33|
## Context and Related Concepts

- Extends [[policy-distillation]] by integrating reinforcement learning objectives.
- Builds upon [[ppo|Proximal Policy Optimization]].
- Related to works like COSIL, TGRL, and ADVISOR, but differs by applying proximal constraints to both objectives and enabling effective student-driven exploration without dynamic loss balancing.
- Implemented in the sb3-distill library built on [[stable-baselines3]].
- Uses [[per-token-kl-clipping]] for stable token-level training during distillation.

[src: raw/ingested/2024/07/2407.15134.md]