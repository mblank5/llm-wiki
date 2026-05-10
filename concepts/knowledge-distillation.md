---
title: "Knowledge Distillation"
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [distillation, training]
sources: []
---

# Knowledge Distillation

Knowledge Distillation (KD), introduced by Hinton et al. in 2015, is the foundational technique for transferring knowledge from a large "teacher" model to a smaller "student" model. The student is trained to match the teacher's output distribution (typically via [[kl-divergence-in-distillation]]), preserving much of the teacher's capability at lower computational cost. KD is a core concept referenced throughout the wiki, including in discussions of [[exposure-bias]] and the [[on-policy-distillation-survey]].

## Related

- [[on-policy-distillation-survey]] — Surveys modern distillation methods including on-policy variants
- [[exposure-bias]] — Standard KD suffers from exposure bias when student encounters unseen states
- [[kl-divergence-in-distillation]] — KL divergence as the primary distillation loss
- [[policy-distillation]] — Application of KD to RL policy transfer

## References

- Hinton, Vinyals, & Dean (2015). "Distilling the Knowledge in a Neural Network." arXiv:1503.02531.
