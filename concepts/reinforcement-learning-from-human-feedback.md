---
title: "Reinforcement Learning from Human Feedback"
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [rlhf, rl, alignment]
aliases: [RLHF]
sources: []
---

# Reinforcement Learning from Human Feedback (RLHF)

Reinforcement Learning from Human Feedback (RLHF) is a post-training technique that aligns language models with human preferences by training a reward model on human preference data and then optimizing the language model policy against this reward using reinforcement learning. RLHF is a key component of modern LLM training pipelines, including [[qwen3]], and is related to methods like [[grp-o]] which provide alternatives to traditional RLHF.

## Related

- [[qwen3]] — Qwen3 uses RLHF in its post-training pipeline
- [[grp-o]] — GRPO provides a group-relative alternative to standard RLHF
- [[free-process-rewards]] — Process-level reward signals as an alternative to human feedback

## References

- Ouyang et al. (2022). "Training language models to follow instructions with human feedback." NeurIPS.
