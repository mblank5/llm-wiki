---
title: Entropy Aware On Policy Distillation
created: 2026-04-06
updated: 2026-04-10
type: concept
tags: ['distillation', 'on-policy', 'training']
sources: []
---

     1|# Entropy-Aware On-Policy Distillation (EOPD)
     2|
     3|Entropy-Aware On-Policy Distillation (EOPD) is a distillation framework for language models that dynamically adapts the training objective based on the teacher model's token-level entropy. It addresses diversity degradation and training instability inherent in standard on-policy distillation (OPD) that relies solely on reverse KL divergence.
     4|
     5|## Core Idea
     6|
     7|Reverse KL is mode-seeking, causing diversity collapse and unstable gradients when the teacher distribution has high entropy (multiple plausible outputs). Forward KL is mode-covering, preserving uncertainty but computationally expensive and inefficient for low-entropy regions.
     8|
     9|EOPD combines both:
    10|
    11|- **Low teacher entropy**: Use reverse KL for efficient, stable learning on confident predictions.
    12|- **High teacher entropy**: Add forward KL to preserve diversity and transfer the teacher's uncertainty.
    13|
    14|## Objective
    15|
    16|The token-level objective is:
    17|
    18|L_t^EOPD(theta;c_t) = L_t^OPD(theta;c_t) + I[H_t^te > tau] * L_t^FKL(theta;c_t)
    19|
    20|Where H_t^te is the teacher's token-level entropy, tau is a threshold hyperparameter, L_t^OPD is the clipped reverse KL loss, and L_t^FKL is the forward KL divergence.
    21|
    22|The forward KL is approximated over the teacher's top-k tokens for computational efficiency.
    23|
    24|## Key Findings
    25|
    26|- Standard OPD retains only 6.8% of high-entropy tokens vs. 18.5% in the teacher.
    27|- EOPD improves Pass@8 accuracy by +1.37 (0.6B), +2.39 (1.7B), +5.05 (4B) on math reasoning benchmarks.
    28|- EOPD outperforms entropy bonus and advantage shaping baselines.
    29|- The method is robust across a range of tau values, with optimal performance at tau=0.8.
    30|
## Relation to Existing Concepts

- Extends [[on-policy-distillation]] by adding entropy-aware forward KL.
- Contrasts with [[on-policy-self-distillation|OPSD]]: uses external teacher, not self-teaching.
- Contrasts with [[video-opd]]: focuses on text reasoning, not video grounding.
- Related to [[policy-distillation]] and [[proximal-policy-distillation|PPD]], but specifically addresses token-level entropy dynamics.
- See [[token-level-entropy-analysis]] for detailed analysis of token-level entropy patterns in distillation.

[src: raw/ingested/2026/03/2603.07079.md]