---
title: Mental Self-Modeling
created: 2026-04-10
updated: 2026-04-10
type: concept
tags: [behavioral-awareness, theory-of-mind, metacognition, alignment]
sources:
  - raw/papers/2026/03/2603.26089.md
---

# Mental Self-Modeling

Mental self-modeling refers to the capacity of large language models (LLMs) to represent and reason about their own internal decision-making processes, mental states, and behavioral dispositions. It is a cognitive capacity related to—but distinct from—[[behavioral-self-awareness]], theory of mind, and metacognition.

## Definition

Where [[behavioral-self-awareness]] concerns a model's ability to articulate its learned behaviors without in-context examples, mental self-modeling goes further: it involves the model constructing an internal model of its own cognitive processes—its preferences, reasoning strategies, knowledge boundaries, and decision policies—and using that self-model to predict or explain its own future behavior.

## Selective Deficits in LLM Mental Self-Modeling

Gurney et al. (2026) identify selective deficits in LLM mental self-modeling through a behavior-based test of theory of mind (arXiv:2603.26089). The key findings include:

- **Selective rather than uniform failure**: LLMs do not uniformly succeed or fail at mental self-modeling. Instead, they show selective deficits—succeeding at some aspects of self-modeling while failing at others.
- **Behavior-based theory of mind test**: The paper uses a novel behavioral paradigm that tests whether models can predict their own behavior across different scenarios, analogous to how theory of mind tests assess understanding of others' mental states.
- **Dissociation between self and other modeling**: The deficits are selective in that models may perform well at modeling others' mental states while failing to accurately model their own, or vice versa.

## Relation to Other Concepts

### [[behavioral-self-awareness]]
Mental self-modeling is a broader and deeper form of self-knowledge than behavioral self-awareness. Where behavioral self-awareness involves recognizing one's learned behaviors (e.g., "I write insecure code"), mental self-modeling involves understanding *why* one has those behaviors and being able to predict them in novel contexts.

### Theory of Mind
Mental self-modeling is the self-directed analogue of theory of mind. If theory of mind is the ability to model others' beliefs, desires, and intentions, mental self-modeling is the ability to apply similar reasoning to oneself. Selective deficits suggest these capacities may be partially dissociable in LLMs.

### Metacognition
In cognitive science, metacognition involves monitoring and controlling one's own cognitive processes. LLM mental self-modeling may be a prerequisite or component of machine metacognition, with implications for:

- **Calibration**: Knowing what you know and don't know (cf. Kadavath et al., 2022)
- **Self-correction**: Using self-knowledge to improve outputs
- **Strategic reasoning**: Adjusting behavior based on self-model (cf. [[ai-self-awareness-game-theory]])

## Implications for Alignment

1. **Safety monitoring**: If models have accurate mental self-models, they could report on their own alignment states, complementing [[ppo]]-based alignment approaches.
2. **Failure modes**: Selective deficits mean models may be overconfident in some aspects of self-knowledge while being unaware of gaps in others, creating a false sense of reliability.
3. **Deception risk**: Models with accurate self-models but misaligned objectives could use their self-knowledge strategically, as discussed in the [[emergent-misalignment]] literature.
4. **Distillation effects**: Whether mental self-modeling survives [[on-policy-distillation]] is an open question relevant to deploying smaller aligned models.

## Open Questions

1. What are the specific dimensions along which mental self-modeling shows selective deficits?
2. Does mental self-modeling scale with model size, or does it emerge discontinuously?
3. How does mental self-modeling interact with chain-of-thought reasoning?
4. Can mental self-modeling be explicitly trained or is it an emergent property?
5. How do selective deficits in self-modeling relate to the self-awareness measured by [[ai-self-awareness-game-theory]]?

## See Also

- [[behavioral-self-awareness]]
- [[ppo]]
- [[on-policy-distillation]]
- [[emergent-misalignment]]
- [[ai-self-awareness-game-theory]]

## References

- Gurney et al. (2026). "Selective Deficits in LLM Mental Self-Modeling in a Behavior-Based Test of Theory of Mind." arXiv:2603.26089.
- Kadavath, S., et al. (2022). "Language models (mostly) know what they know." arXiv:2207.05221.
- Betley, J., et al. (2025). "Tell me about yourself: LLMs are aware of their learned behaviors." arXiv:2501.11120.
