---
title: Sample Routed Policy Optimization
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: ['distillation', 'on-policy', 'grpo', 'rl', 'training']
sources: ['raw/papers/2026/04/2604.02288.md']
---

# Sample-Routed Policy Optimization (SRPO)

Sample-Routed Policy Optimization (SRPO) is a unified on-policy post-training framework that dynamically routes correct samples to GRPO-style reward-aligned reinforcement and failed samples to SDPO's (Self-Distillation Policy Optimization) targeted logit-level correction. It uses entropy-aware dynamic weighting to balance the two objectives, directly unifying [[generalized-on-policy-distillation|G-OPD]], [[on-policy-distillation|OPD]], and GRPO paradigms into a single training loop.

## Overview

SRPO addresses a fundamental tension in LLM post-training: reinforcement learning methods like GRPO excel when rollouts produce correct answers (providing clean reward signal), but waste compute on failed rollouts. Conversely, distillation methods like OPD can extract useful learning signal from failed samples via teacher logit guidance, but ignore reward information from correct samples. SRPO routes each sample to the objective best suited to it.

## Core Mechanism

1. **Sample Routing**: After generating rollouts for a prompt, SRPO checks correctness against a verifier/reward model:
   - **Correct samples** → routed to GRPO's advantage-based reinforcement objective, which reinforces the entire trajectory proportional to its reward advantage.
   - **Failed samples** → routed to SDPO's logit-level distillation objective, which aligns student logits with teacher logits token-by-token, providing fine-grained correction signal even when the trajectory is incorrect.

2. **Entropy-Aware Dynamic Weighting**: A gating mechanism modulates the relative weight of the GRPO and SDPO branches based on the current policy entropy:
   - High entropy (early training, exploratory phase) → increase GRPO weight to encourage diverse exploration.
   - Low entropy (late training, exploitative phase) → increase SDPO weight to refine via distillation.
   - This prevents mode collapse and maintains training stability across phases.

3. **Unified On-Policy Loop**: Both objectives operate on the same batch of student-generated rollouts. No separate teacher data generation or offline distillation phase is needed. The framework is fully on-policy.

## Key Results

Evaluated on Qwen3-8B across five benchmarks:

| Metric | SRPO vs GRPO | SRPO vs SDPO |
|--------|-------------|-------------|
| Five-benchmark average | +3.4% | +6.3% |
| Compute cost | Down 17.2% | — |

SRPO achieves both higher performance and lower compute than either constituent method alone, demonstrating the complementary value of routing.

## Relationships

- Directly unifies [[generalized-on-policy-distillation|G-OPD]] (theoretical framework for reward-scaled OPD) and [[on-policy-distillation|OPD]] (the distillation branch) with GRPO (the RL branch).
- Extends [[proximal-policy-distillation|PPD]]'s idea of combining RL and distillation, but with sample-level routing rather than fixed loss weighting.
- Complementary to [[cascade-rl|Cascade RL]]: where Cascade RL chains multiple training stages, SRPO unifies two objectives in a single stage.
- Related to [[entropy-aware-on-policy-distillation|Entropy-Aware OPD]]'s entropy-based adaptive mechanisms.

## See Also

- [[on-policy-distillation]]
- [[generalized-on-policy-distillation]]
- [[proximal-policy-distillation]]
- [[cascade-rl]]
- [[entropy-aware-on-policy-distillation]]
- [[hybrid-distillation-policy-optimization|HDPO]] — related hybrid approach combining distillation and policy optimization

[src: raw/papers/2026/04/2604.02288.md]
