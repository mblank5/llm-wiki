---
title: 'Chain of Modality: Dynamic Orchestration in Omni-MLLMs'
created: 2026-04-27
updated: 2026-04-27
type: concept
tags:
- architecture
- multimodal
- inference
- alignment
sources:
- raw/papers/2026/04/2604.14520.md
---

# Chain of Modality: Dynamic Orchestration in Omni-MLLMs

## Core Problem

Omni-modal Large Language Models (Omni-MLLMs) promise unified integration of diverse sensory streams, yet a critical performance paradox exists: **unimodal baselines frequently outperform joint multimodal inference**. This perceptual fragility stems from the **static fusion topologies** universally employed by current models.

The paper identifies two structural pathologies in static fusion:

1. **Positional bias (sequential inputs)**: When modalities are concatenated sequentially (e.g., Audio → Visual), visual dominance is largely an artifact of positional bias. Permuting input order causes drastic shifts in attention and performance — the model relies on structural proximity rather than semantic content.

2. **Alignment trap (interleaved formats)**: Models that interleave cross-modal tokens to bridge temporal gaps coerce the model into hallucinating semantic consistency. The enforced physical adjacency leads to elevated false-positive matching rates even when signals are discordant.

## Technical Solution: Chain of Modality (CoM)

CoM transitions multimodal fusion from **passive concatenation** to **dynamic orchestration** by treating modality selection and interaction as modular building blocks.

### Architecture

**Planner**: Adaptively constructs a task-specific modality chain, selecting a sequence of modality-conditioned execution units. Each unit defines both the active modality and its interaction topology:

- **Parallel blocks**: For independent evidence auditing (modalities processed independently, then compared)
- **Sequential anchors**: For causal grounding (one modality provides context for the next)
- **Interleaved sequences**: For fine-grained temporal synchronization (only when temporally aligned)

### Dual Cognitive Pathways

CoM bifurcates reasoning depth based on task complexity:

1. **Plan-Decide (PD) pathway**: For intuitive/perceptual queries. Shortens the chain, bypassing generative reasoning to preserve perceptual fidelity. Training-free.

2. **Plan-Reason-Decide (PRD) pathway**: For complex analytical queries requiring transitive logic. Modality-specific evidence is first analyzed, then synthesized into a grounded decision. Data-efficient SFT on Music-AVQA.

### Training Strategy

- **Training-free mode**: For intuitive tasks, dynamic modality chain construction alone achieves gains
- **Data-efficient SFT**: For analytical tasks, fine-tuning on Music-AVQA with structured reasoning chains

### Key Mechanism Details

The Planner operates by:
1. Analyzing the query's cognitive demand (intuitive vs. analytical)
2. Selecting the modality set (which modalities to activate)
3. Choosing the interaction topology (parallel, sequential, interleaved)
4. Constructing the execution chain as a sequence of modality-conditioned units

## Experimental Results

CoM consistently matches or outperforms specialized models across diverse benchmarks:

- **Music-AVQA**: Fine-grained music perception
- **AV-Odyssey**: Open-domain audio-visual QA
- **DailyOmni**: Daily life multimodal scenarios
- **OmniBench**: Comprehensive omni-modal evaluation
- **WorldSense**: World knowledge multimodal reasoning
- **AV-Counting**: Audio-visual counting tasks
- **AVHBench**: Cross-modal hallucination detection

Key finding: On complement-informative tasks where audio and visual predictions disagree (A ≠ V), CoM significantly reduces "blind trust" failures (ErrorA/ErrorV) compared to Qwen2.5-Omni-7B.

## Comparison with Existing Methods

| Approach | Fusion Topology | Adaptability | Hallucination Handling |
|----------|----------------|--------------|----------------------|
| Sequential concatenation | Static, ordered | None | Positional bias |
| Interleaved fusion | Static, interleaved | None | Alignment trap |
| Specialized models | Task-specific | Poor generalization | Local gains only |
| DPO/RL post-hoc | Static + correction | Symptom only | Treats symptoms |
| **CoM (this work)** | **Dynamic, orchestrated** | **Task-adaptive** | **Root cause fix** |

## Open Questions

1. **Scalability to more modalities**: How does CoM scale beyond tri-modal (text+audio+vision) to include video, sensor data, etc.?

2. **Learned vs. heuristic Planner**: Can the Planner be learned end-to-end rather than using heuristic rules?

3. **Latency overhead**: What is the inference latency cost of dynamic orchestration, and can it be amortized?

4. **Conflict resolution theory**: When modalities genuinely conflict (not just noise), what is the optimal resolution strategy?

## See Also

- [[omni-modal-llm]] — Omni-modal LLM architectures that CoM improves
- [[omni-modality-preference]] — Modality preference analysis in OLLMs
- [[avid-benchmark]] — Audio-visual inconsistency benchmark
