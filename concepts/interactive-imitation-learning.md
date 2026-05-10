---
title: "Interactive Imitation Learning"
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [rl, training]
sources: []
---

# Interactive Imitation Learning

Interactive Imitation Learning extends standard [[imitation-learning]] by allowing the learner to query the expert interactively during training, rather than learning only from a fixed dataset of demonstrations. This addresses the [[exposure-bias]] problem by ensuring the learner receives guidance on states it actually encounters during rollout, similar to how on-policy methods in distillation address distribution mismatch.

## Related

- [[exposure-bias]] — Interactive IL directly addresses exposure bias by querying experts on learner-visited states
- [[imitation-learning]] — Broader imitation learning paradigm
- [[on-policy-distillation]] — OPD similarly addresses distribution mismatch through on-policy rollouts

## References
