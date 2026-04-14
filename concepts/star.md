---
title: STaR
created: 2026-04-15
type: concept
tags: [reasoning, chain-of-thought]
aliases: [Self-Taught Reasoner, STaR]
sources: []
---

# STaR (Self-Taught Reasoner)

STaR (Self-Taught Reasoner) is a method where language models generate their own reasoning traces ([[chain-of-thought]]) to solve problems, then fine-tune on their own successful reasoning. This creates a self-improvement loop that enhances reasoning capabilities without external teacher models. STaR is related to [[on-policy-self-distillation]] in that both approaches leverage the model's own outputs for training, though STaR focuses specifically on reasoning trace generation.

## Related

- [[on-policy-self-distillation]] — Self-distillation shares the self-improvement paradigm with STaR
- [[chain-of-thought]] — STaR generates CoT traces as its core mechanism
- [[reasoning-distillation]] — Broader context of transferring reasoning abilities

## References

- Zelikman et al. (2022). "STaR: Bootstrapping Reasoning With Reasoning." NeurIPS.
