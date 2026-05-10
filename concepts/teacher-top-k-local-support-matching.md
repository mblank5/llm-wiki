---
title: "Teacher Top-K Local Support Matching"
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [distillation, optimization]
sources: []
---

# Teacher Top-K Local Support Matching

Teacher top-k local support matching is a technique used in knowledge distillation where the student is trained to match not just the full output distribution of the teacher, but specifically the top-k highest-probability tokens at each position. This provides more focused training signal and can improve distillation efficiency by concentrating learning on the most important tokens. The technique is discussed in the context of [[on-policy-distillation]].

## Related

- [[on-policy-distillation]] — Teacher top-k matching is applied within on-policy distillation frameworks

## References
