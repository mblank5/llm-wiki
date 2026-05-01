---
title: "OmniTrace: Generation-Time Attribution in Omni-Modal LLMs"
created: 2026-04-27
updated: 2026-04-27
type: concept
tags: [multimodal, alignment, inference, benchmark]
sources: ["2604.13073"]
---

# OmniTrace: Generation-Time Attribution in Omni-Modal LLMs

## Core Problem

Modern MLLMs generate fluent responses from interleaved text, image, audio, and video inputs, but identifying which input sources support each generated statement remains an open challenge. Existing attribution methods have three critical limitations:

1. **Classification-centric**: Designed for fixed prediction targets (class logits, extractive spans), not open-ended autoregressive generation
2. **Single-modality**: Assume homogeneous inputs, don't handle heterogeneous token types
3. **Post-hoc**: Compute explanations after generation, not during decoding

In decoder-only omni-modal generation, attribution must be:
- **Generation-aware**: Defined per decoding step, not fixed target
- **Omni-modal**: Spanning text, image, audio, video tokens in a unified causal sequence
- **Span-level**: Semantically meaningful units, not noisy token-level scores
- **Model-agnostic**: Plug-and-play with any underlying attribution signal

## Technical Solution

### Problem Formulation

**Input**: `x = (x_1, ..., x_n)` — interleaved multimodal token sequence embedded in a unified token space. Source units `S = {S_1, ..., S_m}` correspond to contiguous input segments (text spans, image regions, audio/video intervals).

**Generation**: Autoregressive decoding `P(y|x) = Π_t P(y_t | x, y_{<t})`

**Attribution signal**: For each decoding step `t`, a token-level score `a_t(i) ≥ 0` measuring influence of token `i` on generating `y_t`. Can be attention weights, gradients, or any model-internal statistic.

**Goal**: Construct mapping `f: C_k → Ŝ_k` from output chunks (phrases/sentences) to source unit subsets that explain them.

### OmniTrace Algorithm

The algorithm operates online during decoding:

1. **Source Curation**: Identify candidate source units from the multimodal input sequence
2. **Token-level Tracing**: For each generated token `y_t`, compute attribution scores `a_t(i)` against all input tokens using the chosen scoring method (attention, gradient, etc.)
3. **Span Aggregation**: Group token-level traces into semantically coherent output spans (phrases/sentences)
4. **Confidence-weighted Selection**: For each span, aggregate source token scores and select the most relevant source units using confidence-weighted, temporally coherent aggregation

### Key Design Properties

- **Signal-agnostic**: Works with attention-based scores, gradient-derived measures (Grad-CAM, Gradient×Input, LRP), or any token alignment estimate
- **No retraining**: Post-hoc framework requiring no model modification or fine-tuning
- **Online operation**: Runs during decoding, no need to wait for complete generation

### Supported Attribution Signals

| Signal Type | Examples | Strengths |
|-------------|----------|-----------|
| Attention-based | Attention rollout, attention flow | Directly from model internals |
| Gradient-based | Grad-CAM, Gradient×Input, LRP | Theoretically grounded |
| Hybrid | Combined attention + gradient | Most robust |

## Experimental Results

Evaluated on Qwen2.5-Omni and MiniCPM-o-4.5 across diverse tasks (759 examples total):

- **Mantis-eval**: Multi-image reasoning
- **MMDialog**: Interleaved image-text summarization
- **CliConSummation**: Clinical summarization
- **MMAU**: Audio reasoning and meeting summarization
- **MISP**: Multimodal meeting summarization
- **Video-MME**: Video question answering

**Key results**:
- Generation-aware span-level attribution produces **more stable and interpretable** explanations than naive self-attribution and embedding-based baselines
- Robust across multiple underlying attribution signals
- Effective across visual, audio, and video tasks

## Comparison with Existing Methods

| Method | Generation-Aware | Omni-Modal | Span-Level | Model-Agnostic |
|--------|------------------|------------|------------|----------------|
| Attention rollout | No | No | No | Yes |
| Grad-CAM | No | No | No | Yes |
| LRP | No | No | No | Yes |
| **OmniTrace** | **Yes** | **Yes** | **Yes** | **Yes** |

## Open Questions

1. **Ground truth for attribution**: How to evaluate attribution quality when human-annotated ground truth source spans are expensive to obtain?

2. **Causal vs. correlational**: Do attribution scores reflect true causal influence or merely statistical correlation?

3. **Cross-modal attribution conflicts**: When multiple modalities provide conflicting evidence, how should attribution be distributed?

4. **Temporal attribution for audio/video**: How to handle cases where the relevant audio/video segment spans a long duration?

## See Also

- [[omni-modal-llm]] — Omni-modal LLM architectures
- [[omni-modality-preference]] — Modality preference analysis
- [[avid-benchmark]] — Audio-visual inconsistency detection
