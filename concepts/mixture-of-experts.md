---
title: "Mixture of Experts"
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [architecture, model]
aliases: [MoE]
sources: []
---

# Mixture of Experts (MoE)

Mixture of Experts (MoE) is a neural network architecture that routes tokens to different "expert" sub-networks, enabling larger model capacity without proportionally increasing compute per forward pass. MoE architectures are used in models like [[qwen3]] and [[composer2]], where they provide efficient scaling for large language models by activating only a subset of parameters per token.

## Related

- [[qwen3]] — Qwen3 uses MoE architecture in its larger model variants
- [[composer2]] — Composer 2 is built on a MoE architecture (1.04T/32B)

## References
