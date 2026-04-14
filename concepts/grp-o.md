---
title: GRPO
created: 2026-04-15
type: concept
tags: [grpo, rl, optimization]
aliases: [GRPO, Group Relative Policy Optimization]
sources: []
---

# GRPO (Group Relative Policy Optimization)

GRPO (Group Relative Policy Optimization) is a reinforcement learning training method that optimizes policy by comparing relative rewards within groups of samples, rather than relying on absolute reward values. GRPO is widely adopted in modern LLM post-training and is referenced across multiple wiki pages including [[vold]], [[on-policy-self-distillation]], and [[cascade-rl]]. It is closely related to [[grpo-rl-training]] as a specific training methodology.

## Related

- [[vold]] — VOLD uses GRPO in its vision-language on-policy distillation framework
- [[on-policy-self-distillation]] — Self-distillation methods can incorporate GRPO-style optimization
- [[cascade-rl]] — Cascade RL may leverage GRPO for multi-domain post-training
- [[grpo-rl-training]] — Detailed GRPO-based RL training methodology

## References

- Shao et al. (2024). "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models."
