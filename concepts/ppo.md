---
title: "Ppo"
created: 2026-04-06
updated: 2026-04-10
type: concept
tags: ['rl', 'training', 'optimization']
sources: []
---

     1|# Proximal Policy Optimization (PPO)
     2|
     3|Proximal Policy Optimization (PPO) is a policy gradient method for reinforcement learning that improves training stability by limiting the size of policy updates via a clipped surrogate objective. It is the foundational RL algorithm extended by [[proximal-policy-distillation]].
     4|
     5|## Key Properties
     6|
     7|- Uses a clipped probability ratio to prevent destructive large policy updates.
     8|- Can reuse samples from a rollout buffer over multiple epochs (sample efficiency).
     9|- Includes an entropy bonus term to encourage exploration.
    10|
    11|[src: raw/ingested/2024/07/2407.15134.md]