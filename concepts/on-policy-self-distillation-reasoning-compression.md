---
title: On-Policy Self-Distillation for Reasoning Compression
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: ['distillation', 'on-policy', 'self-distillation', 'training']
sources: ['raw/papers/2026/03/2603.05433.md']
---

# On-Policy Self-Distillation for Reasoning Compression (OPSDC)

On-Policy Self-Distillation for Reasoning Compression (OPSDC) is a training method that compresses LLM reasoning traces by conditioning the same model on a "be concise" instruction to generate teacher logits, then training the student (unconditioned) to minimize per-token reverse KL divergence on its own rollouts. No ground-truth answers are needed.

## Overview

LLM reasoning models (e.g., chain-of-thought) often produce verbose traces with unnecessary deliberation. OPSDC compresses these traces by teaching the model to produce shorter, equally accurate reasoning. The key insight: the same model can serve as its own teacher by conditioning it differently — with a conciseness instruction for teacher logits, without it for student rollouts.

## Core Mechanism

1. **Dual Conditioning**: The same model is used twice:
   - **Teacher mode**: Conditioned on "be concise" instruction prepended to the prompt. Produces logits pi_teacher(y|x, "be concise").
   - **Student mode**: Standard prompting without the conciseness instruction. Generates rollouts pi_student(y|x).

2. **On-Policy Rollouts**: The student generates rollouts from its own policy (on-policy). No offline teacher traces are needed.

3. **Per-Token Reverse KL Minimization**: At each token position in the student's rollout, minimize KL(pi_student || pi_teacher). This encourages the student to match the teacher's more compact token distribution.

4. **No Ground Truth Needed**: Since the objective is self-consistency (match the concise version of yourself), no external ground-truth answers or solutions are required. The model learns to self-compress.

## Key Results

| Model | Token Reduction | Accuracy Gain (MATH-500) |
|-------|----------------|--------------------------|
| Qwen3-8B | 57% | +9–16 pts |
| Qwen3-14B | 59% | +9–16 pts |

OPSDC achieves substantial compression (over half the tokens removed) while actually *improving* accuracy, suggesting that verbose reasoning traces contain noise that self-distillation filters out.

## Relationships

- Self-distillation variant of [[on-policy-distillation|OPD]]: the teacher is the same model with different conditioning.
- Related to [[on-policy-self-distillation|OPSD]] but specifically targets reasoning compression rather than general capability transfer.
- Complementary to [[sample-routed-policy-optimization|SRPO]]: OPSDC shows that self-conditioning can serve as the "teacher" signal, while SRPO uses an external teacher for failed samples.
- The per-token reverse KL objective connects to the theoretical framework in [[generalized-on-policy-distillation|G-OPD]].

## See Also

- [[on-policy-distillation]]
- [[on-policy-self-distillation]]
- [[sample-routed-policy-optimization]]
- [[generalized-on-policy-distillation]]

[src: raw/papers/2026/03/2603.05433.md]
