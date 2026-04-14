---
title: Exposure Bias
created: 2026-04-06
updated: 2026-04-10
type: concept
tags: ['training', 'distillation']
sources: []
---

     1|# Exposure Bias in LLMs
     2|
     3|**Exposure bias** is the critical train-test mismatch between training and inference in autoregressive language models. During training, the student conditions on ground-truth tokens from a fixed dataset. During inference, it must condition on its own previous outputs — which may be erroneous.
     4|
     5|## The Problem
     6|
     7|Off-policy distillation trains students on data from an expert distribution p_data. At inference, the student samples from its own policy p_theta. Errors at early positions propagate through the entire remaining sequence, and the student has no gradient information about how to behave in these self-induced off-distribution states.
     8|
     9|## Formal Error Bounds
    10|
    11|**Pure behavior cloning (off-policy):** Error compounds as O(T^2) where T is sequence length
    12|**With expert feedback on learner states (on-policy/DAgger):** Error bounds improve to O(T)
    13|
    14|The DAgger algorithm (Ross et al., 2011) provides the theoretical foundation: querying an expert on the learner's own visited states prevents catastrophic error accumulation.
    15|
    16|## Connection to OPD
    17|
    18|On-Policy Distillation directly addresses exposure bias by:
    19|1. Letting the student sample from its own policy p_theta
    20|2. Soliciting teacher feedback on these self-generated trajectories
    21|3. Using the teacher signal as supervision for states the student actually visits
    22|
    23|Gudibande et al. (2023) demonstrated empirically that off-policy distilled students degrade sharply on tasks requiring sustained multi-step generation — the very tasks most vulnerable to exposure bias.
    24|
    25|## Mitigation Approaches
    26|
    27|- **Mixture sampling** (GKD): Mix student-sampled and teacher-sampled trajectories during training
    28|- **On-policy feedback**: Teacher provides distributions, rewards, or preferences on student-generated sequences
    29|- **Self-play**: Student learns to distinguish its own errors from correct outputs (but saturates)
    30|- **Curriculum learning**: Gradually increase student autonomy during training
    31|
    32|## See Also
    33|- [[on-policy-distillation-survey]]
    34|- [[knowledge-distillation]]
    35|- [[interactive-imitation-learning]]
    36|
    37|> [!note] Practical Impact
    38|> DeepSeek-R1's success in transferring reasoning from 671B to 1.5B-70B parameter students demonstrates that exposure bias can be overcome — but R1 used off-policy distillation with carefully designed CoT targets. On-policy methods are the next step for further improvement.
    39|> [src: raw/ingested/2026/04/2604.00626.md]
    40|