---
title: "Reverse KL Distillation"
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [distillation, optimization]
sources: []
---

# Reverse KL Distillation

Reverse KL distillation uses the reverse Kullback-Leibler divergence (KL(student || teacher)) instead of the forward direction as the distillation objective. Unlike forward KL, which encourages the student to cover all modes of the teacher distribution, reverse KL encourages the student to be mode-seeking, potentially producing sharper but less diverse outputs. This technique is discussed in the context of [[on-policy-distillation]] and relates to the broader analysis in [[kl-divergence-in-distillation]].

## Related

- [[on-policy-distillation]] — Reverse KL is used in sequence-level on-policy distillation objectives
- [[kl-divergence-in-distillation]] — Broader analysis of KL divergence directions in distillation

## References
