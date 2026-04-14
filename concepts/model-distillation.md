---
title: Model Distillation
created: 2026-04-06
updated: 2026-04-10
type: concept
tags: ['distillation', 'training']
sources: []
---

     1|# Model Distillation
     2|
     3|Model distillation is a supervised learning technique for compressing knowledge from a large, complex model (or ensemble) into a smaller, faster model. The core idea is to train the student model not on the original hard labels, but on the softened output probabilities (logits) produced by the teacher model. This transfers richer information about class similarities and decision boundaries.
     4|
     5|## Key Properties
     6|
     7|- Proposed by Bucila et al. (2006) for ensemble compression.
     8|
     9|- Formalized by Hinton et al. (2014) using a temperature-scaled softmax to create 'soft targets'.
    10|
    11|- Enables training shallow networks to mimic deep networks (Ba and Caruana, 2014).
    12|
## Relation to Policy Distillation

Standard distillation operates on classification outputs (probability distributions). [[policy-distillation]] extends this to reinforcement learning, where the teacher outputs are real-valued, unbounded Q-values rather than probabilities. This requires careful handling of scale and the use of a sharpening (low temperature) softmax instead of a softening one.

[[dual-policy-distillation|Dual-Policy Distillation]] is a related approach that uses on-policy rollouts with a dual-policy setup for knowledge transfer.

[src: raw/ingested/2015/11/1511.06295.md]