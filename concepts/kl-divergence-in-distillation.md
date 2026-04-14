---
title: KL Divergence in Distillation
created: 2026-04-15
type: concept
tags: [distillation, optimization]
sources: []
---

# KL Divergence in Distillation

KL (Kullback-Leibler) divergence plays a central role in knowledge distillation as the primary loss function measuring the discrepancy between teacher and student output distributions. The [[on-policy-distillation-survey]] frames distillation methods through the lens of f-divergence measures, with KL divergence being the most commonly used instance. The choice between forward KL, [[reverse-kl-distillation]], and other f-divergences fundamentally shapes the bias-variance tradeoff in distilled models.

## Related

- [[on-policy-distillation-survey]] — Comprehensive survey analyzing KL divergence's role across distillation methods
- [[reverse-kl-distillation]] — Alternative divergence direction with different properties
- [[knowledge-distillation]] — Foundational concept where KL divergence is the standard loss

## References
