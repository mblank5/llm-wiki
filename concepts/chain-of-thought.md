---
title: "Chain of Thought"
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [reasoning, chain-of-thought]
sources: []
---

# Chain of Thought

Chain-of-Thought (CoT) reasoning is a prompting technique where language models generate intermediate reasoning steps before producing a final answer. CoT prompting dramatically improves performance on complex reasoning tasks and underpins modern reasoning models like those in [[qwen3]]. It is foundational to techniques like [[star]] (Self-Taught Reasoner) and plays a central role in [[reasoning-distillation]].

## Related

- [[qwen3]] — Qwen3 supports thinking/non-thinking mode toggling, leveraging CoT reasoning
- [[star]] — Self-Taught Reasoner generates its own CoT traces for self-improvement
- [[reasoning-distillation]] — Transferring CoT reasoning abilities from teacher to student models
- [[thinking-budget]] — Compute allocation for extended CoT reasoning

## References

- Wei et al. (2022). "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models." NeurIPS.
