---
title: On Policy Distillation Survey
created: 2026-04-06
updated: 2026-04-10
type: concept
tags: ['distillation', 'on-policy', 'survey']
sources: []
---

     1|# On-Policy Distillation (OPD) - Survey
     2|
     3|A comprehensive taxonomy and unified framework for On-Policy Distillation of LLMs. OPD addresses the fundamental **exposure bias** problem — the train-test mismatch where students trained on static teacher-generated data fail when generating autoregressively at inference time.
     4|
     5|## Core Concept
     6|
     7|**Off-policy distillation** (traditional): Student trains on fixed teacher data y ~ p_data, but at inference generates from its own policy y ~ p_theta. Error compounds O(epsilon * T^2).
     8|
     9|**On-policy distillation** (OPD): Student generates its own trajectories and receives teacher feedback on self-generated outputs. Grounded in interactive imitation learning (DAgger). Error reduced to O(epsilon * T).
    10|
    11|## Three-Dimensional Taxonomy
    12|
    13|| Dimension | Categories |
    14||-----------|------------|
    15|| **Feedback Signal** | Logit-based (white-box distributions), Outcome-based (scalar rewards, preferences), Self-play |
    16|| **Teacher Access** | White-box (full logit access), Black-box (generated outputs only), Self-distillation (teacher-free) |
    17|| **Loss Granularity** | Token-level, Sequence-level, Hybrid/Adaptive |
    18|
    19|## Key White-Box Methods
    20|
    21|- **GKD** (Agarwal et al., 2024): Unified OPD with mixture sampling between student and teacher sequences
    22|- **MiniLLM** (Gu et al., 2024): Minimizes Reverse KL to avoid mode-covering pathology of Forward KL
    23|- **DistiLLM** (Ko et al., 2024): Skewed KL objectives with student-teacher mixture for stability
    24|- **Proximal Policy Distillation** (2407.15134): Clipped policy gradients for stable OPD
    25|
    26|## Black-Box / Self-Play
    27|
    28|- **Self-Play** (SPIN): Student distinguishes its own generations from references — but **saturates** (echo chamber effect)
    29|- **Breaking the ceiling**: Privileged information, reasoning compression, or reward-free alignment
    30|- **Black-box OPD** (GAD, Lion): Operate with only top-k teacher generations
    31|
    32|## Reasoning Distillation
    33|
    34|- Chain-of-Thought distillation is the dominant post-DeepSeek-R1 paradigm
    35|- DeepSeek-R1: Massive success transferring 671B MoE teacher reasoning into 1.5B-70B dense students via off-policy distillation
    36|- On-policy methods can further improve on R1-distilled students
    37|
    38|## Open Problems
    39|
    40|- Distillation scaling laws
    41|- Teacher calibration and uncertainty-aware distillation
    42|- Dynamic curriculum distillation
    43|- Latent space distillation for vocabulary mismatch
    44|- Agent-level distillation (multi-turn, state-dependent)
    45|- Multimodal OPD
    46|- Closing the distillation-RL loop
    47|
    48|## See Also
    49|- [[exposure-bias]]
    50|- [[knowledge-distillation]]
    51|- [[kl-divergence-in-distillation]]
    52|- [[self-play-limitations]]
    53|- [[reasoning-distillation]]
    54|- [[deepseek-r1-distillation]]
    55|
    56|> [!note] Survey Scope
    57|> This is the first dedicated comprehensive treatment of OPD for LLMs, providing a unified f-divergence framework over on-policy samples. Previous surveys treated off-policy and on-policy as interchangeable variants rather than fundamentally distinct paradigms.
    58|> [src: raw/ingested/2026/04/2604.00626.md]
    59|