---
title: On Policy Distillation
created: 2026-04-06
updated: 2026-04-15
type: concept
tags: ['distillation', 'on-policy', 'training']
sources: []
---

     1|# On-Policy Distillation (OPD)
     2|
     3|On-policy distillation (OPD) is a post-training method for large language models (LLMs) that evaluates teacher feedback on student-generated rollouts rather than fixed teacher traces. This makes OPD attractive for long-horizon reasoning and agentic post-training, where the student quickly reaches prefixes that are rare or absent in fixed teacher traces [src: raw/ingested/2026/03/2603.25562.md].
     4|
     5|## Core Tradeoff: Bias vs Variance
     6|
     7|The central tradeoff in OPD is between sequence-level coupling and token-level approximation:
     8|
     9|| Estimator | Bias | Variance Scaling | Description |
    10||-----------|------|------------------|-------------|
    11|| Sequence-level reverse-KL | Unbiased | O(T^4) | Full trajectory reward coupling |
    12|| Token-level OPD | Biased | O(T^2) | Immediate reward only |
    13|| Discounted return-to-go (gamma) | Interpolated | Between O(T^2) and O(T^4) | Tunable coupling |
    14|
    15|Token-level OPD removes future-reward coupling terms, making it biased relative to the sequence-level objective but with much tighter worst-case variance bounds. This matters significantly in long-horizon LLM post-training [src: raw/ingested/2026/03/2603.25562.md].
    16|
    17|## Failure Modes of Sampled-Token OPD
    18|
    19|The commonly implemented sampled-token variant has three distinct failure modes:
    20|
    21|1. **Imbalanced one-token signal**: Updates driven by single sampled token log-ratio; most tokens receive negative rewards, positive signal concentrated on small subset. Training becomes sensitive to locally favorable tokens like fillers or hesitation markers [src: raw/ingested/2026/03/2603.25562.md].
    22|
    23|2. **Unreliable teacher guidance on student prefixes**: When rollouts enter prefixes common for student but atypical for teacher, teacher may assign high probability to plausible-looking tokens even when trajectory has deviated. Associated with repetition loops, self-resetting reasoning, malformed continuations. Teacher-student log-probability gaps widen at later positions [src: raw/ingested/2026/03/2603.25562.md].
    24|
    25|3. **Tokenizer and special-token mismatch**: Different tokenizations cause same raw text to be segmented differently. One-token comparison confuses semantic disagreement with tokenization artifacts [src: raw/ingested/2026/03/2603.25562.md].
    26|
## Related
- [[ex-opd]] — Extended/Extrapolated OPD 变体 Methods

- [[reopold|Reopold]]: RL-aware stabilization of OPD with reward clipping and entropy-guided sampling
- [[video-opd|Video-OPD]]: OPD for temporal video grounding with dense token-level supervision
- [[on-policy-self-distillation|OPSD]]: Self-teaching variant without external teacher
- [[on-policy-self-distillation-reasoning-compression|OPSDC]]: Self-distillation variant for reasoning compression
- [[on-policy-prefix-distillation|OPPD]]: Prefix-only distillation for computational efficiency
- [[proximal-policy-distillation|PPD]]: Integrates PPO with distillation objectives
- [[dual-policy-distillation|DPD]]: Dual-policy variant of on-policy distillation
- [[sample-routed-policy-optimization|SRPO]]: Routes correct samples to GRPO reinforcement, failed samples to SDPO distillation; entropy-aware dynamic weighting
- [[hybrid-distillation-policy-optimization|HDPO]]: Recent hybrid approach combining distillation and policy optimization
- [[rl-aware-distillation|RLAD]]: Selective imitation during RL — distills from teacher only when it improves current policy update; uses Trust Region Ratio Distillation (TRRD)
    34|
## See Also

- [[teacher-top-k-local-support-matching]]
- [[reverse-kl-distillation]]
- [[x-opd]]
- [[vold]]
- [[speech-llm]]
- [[full-duplex-speech-model]]
- [[opd-tokenizer-requirement]] — tokenizer and special-token mismatch in OPD
- [[opd-vs-sft]] — comparison of OPD with supervised fine-tuning
- [[per-token-kl-clipping]] — per-token KL clipping technique for training stability
- [[qwen3-opd-usage]] — how Qwen3 applies OPD in practice
- [[token-level-entropy-analysis]] — token-level entropy analysis for distillation
    39|
    40|[src: raw/ingested/2026/03/2603.25562.md]