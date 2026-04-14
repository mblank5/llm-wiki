---
title: Video Opd
created: 2026-04-06
updated: 2026-04-10
type: concept
tags: [distillation, on-policy, multimodal]
sources: []
---

# Video-OPD

Video-OPD (Video On-Policy Distillation) is an efficient post-training framework for Temporal Video Grounding (TVG) that combines on-policy optimization with dense token-level supervision from a fixed frontier teacher model.

## Core Idea

Video-OPD addresses two key limitations of GRPO-based post-training for TVG:

1. **Sparse reward signals**: GRPO provides only sequence-level rewards, causing poor credit assignment over long temporal horizons.
2. **Prohibitive computational overhead**: GRPO requires multiple on-policy rollouts per training sample for variance reduction, which is expensive for video understanding with long visual contexts.

Video-OPD preserves strict on-policy optimization (trajectories sampled from current student policy) while replacing sparse episode-level rewards with dense token-level supervision via reverse KL divergence against a teacher model.

## Training Pipeline (4 Steps)

| Step | Description |
|------|-------------|
| 1. On-Policy Trajectory Sampling | Student samples trajectory τ=(a_1,...,a_T) ~ π_θ(·|v,q) |
| 2. Teacher Evaluation | Fixed teacher π_tea computes log-probabilities for each student token |
| 3. Dense Token-Level Supervision | Per-token reward r_t = -(log π_θ(a_t|s_t) - log π_tea(a_t|s_t)) |
| 4. Policy Update | Standard policy-gradient with token-level rewards, single rollout per sample |

## Key Advantages over GRPO

| Property | GRPO | Video-OPD |
|----------|------|-----------|
| Optimization | On-policy | On-policy |
| Supervision | Sparse (sequence-level) | Dense (token-level) |
| Rollouts per sample | Multiple (e.g., 8) | Single |
| Credit assignment | Poor for long horizons | Fine-grained per token |
| Convergence | Slow | Substantially faster |
| Computational cost | High | ~20% of GRPO |

## Integration with TVDF

Video-OPD is enhanced by [[tvdf|Teacher-Validated Disagreement Focusing]], a training curriculum that uses ground-truth annotations as validation signals to prioritize teacher-reliable, high-disagreement trajectories.

## Experimental Results

- Outperforms GRPO by average 17% on Charades-TimeLens, ActivityNet-TimeLens, QVHighlights-TimeLens
- Achieves SOTA among open-source models, approaching Gemini-2.5-Flash performance
- Strong generalization to TempCompass, MVBench, Video-MME
- Student consistently matches or surpasses teacher after multi-round training

## Relation to Existing Concepts

- Extends [[on-policy-distillation]] to temporal video grounding with unique challenges of long-horizon temporal reasoning
- Contrasts with [[on-policy-self-distillation|OPSD]]: uses external teacher rather than self-teaching
- Contrasts with [[vold]]: focuses on TVG specifically rather than modality transfer
- Uses reverse KL (mode-seeking) rather than forward KL (mode-covering) for supervision
- Related to [[proximal-policy-distillation|PPD]] but uses simpler policy-gradient without PPO clipping

[src: raw/ingested/2026/02/2602.02994.md]