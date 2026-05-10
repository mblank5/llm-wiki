---
title: "Strong to Weak Distillation"
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [distillation, training]
sources: []
---

# Strong-to-Weak Distillation

Strong-to-weak distillation is a paradigm where a larger, more capable "strong" teacher model distills its knowledge into a smaller, less capable "weak" student model. This is the most common distillation direction and is used in models like [[qwen3]] and frameworks like [[generalized-on-policy-distillation]]. The goal is to preserve as much of the strong model's capability as possible in the weaker student, creating efficient models for deployment.

## Related

- [[generalized-on-policy-distillation]] — G-OPD applies strong-to-weak distillation with reward extrapolation
- [[qwen3]] — Qwen3 uses strong-to-weak logits distillation in its training pipeline
- [[knowledge-distillation]] — Foundational concept underlying strong-to-weak transfer

## References
