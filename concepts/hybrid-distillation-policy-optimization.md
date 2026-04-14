---
title: Hybrid Distillation Policy Optimization
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: ['distillation', 'on-policy', 'rl', 'training']
sources: ['raw/papers/2026/03/2603.23871.md']
---

# Hybrid Distillation Policy Optimization (HDPO)

Hybrid Distillation Policy Optimization via Privileged Self-Distillation (HDPO) augments standard RL training with a privileged self-distillation mechanism targeting "cliff prompts" — prompts where all student rollouts fail. The teacher and student share weights and differ only in their input conditioning. HDPO proves that using R=1 filtered privileged generation recovers the optimal KL-regularized RL policy.

## Overview

In RL fine-tuning, some prompts are "cliffs": the student generates N rollouts and every single one fails, yielding zero reward signal. Standard GRPO/PPO has no gradient signal for these prompts. HDPO solves this by using a privileged self-distillation setup: the same model acts as both teacher and student, with the teacher receiving additional privileged input (e.g., the ground-truth answer or solution hint) that the student does not see.

## Core Mechanism

1. **Cliff Prompt Detection**: After generating N rollouts per prompt, identify prompts where all N rollouts receive zero reward (all incorrect). These are cliff prompts.

2. **Privileged Self-Distillation**: For cliff prompts only:
   - **Teacher**: Same model, but conditioned on privileged information (ground-truth answer appended to the prompt).
   - **Student**: Same model, conditioned on the original prompt only.
   - Since teacher and student share weights, no separate teacher model is needed — only the input differs.

3. **R=1 Filtered Generation**: The teacher generates a single privileged completion (R=1), which is filtered for correctness. HDPO proves this filtered privileged generation recovers the optimal KL-regularized RL policy under standard assumptions.

4. **Loss Combination**: Standard RL loss (GRPO/PPO) on non-cliff prompts + distillation loss (reverse KL) on cliff prompts, using the privileged teacher logits as the target.

## Key Results

On OpenMathInstruct-2:

| Metric | Improvement |
|--------|------------|
| pass@4 | +0.8–1.1% |
| pass@8 | +0.4–1.7% |

The improvements are modest in absolute terms but consistent, and come at negligible additional compute cost since the teacher is the same model with different input.

## Relationships

- Self-distillation variant of [[on-policy-distillation|OPD]]: no external teacher needed.
- Related to [[sample-routed-policy-optimization|SRPO]]'s sample routing idea: HDPO routes cliff prompts to distillation and non-cliff prompts to standard RL.
- Extends [[on-policy-self-distillation|OPSD]] by adding privileged conditioning for teacher logits.
- Theoretical connection to KL-regularized RL, similar to the analysis in [[generalized-on-policy-distillation|G-OPD]].

## See Also

- [[on-policy-distillation]]
- [[sample-routed-policy-optimization]]
- [[on-policy-self-distillation]]
- [[generalized-on-policy-distillation]]

[src: raw/papers/2026/03/2603.23871.md]
