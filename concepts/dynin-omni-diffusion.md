---
title: "Dynin-Omni: Diffusion-Based Omnimodal Foundation Model"
created: 2026-04-27
updated: 2026-04-27
type: concept
tags: [model, architecture, multimodal, training]
sources: ["2604.00007"]
---

# Dynin-Omni: Diffusion-Based Omnimodal Foundation Model

## Core Problem

Most unified understanding-generation models are built on **autoregressive (AR)** or AR-dominated designs. AR models impose strict causal ordering that is fundamentally mismatched with non-sequential modalities like images. Current alternatives have limitations:

- **Hybrid/compositional designs** (AR + diffusion generators): Fragment generation across separate modules, creating orchestration bottlenecks and hindering deep cross-modal integration
- **Pure AR unified models**: Sacrifice textual reasoning for richer multimodal modeling
- **Masked diffusion models**: Confined to vision-language, not scaled to true omnimodal (text+image+speech+video)

## Technical Solution

Dynin-Omni is the **first open-source 8B-scale masked-diffusion foundation model** that natively unifies omnimodal understanding and generation in a single architecture.

### Architecture

**Masked Diffusion Backbone**: All tasks (understanding and generation across text, image, speech, video) are formulated as **masked diffusion over a shared discrete token space**. The model performs iterative token prediction under bidirectional context — predicting multiple masked tokens simultaneously while attending to both past and future context.

**Key properties over AR**:
- **Bidirectional attention**: Can refine outputs globally across modalities
- **Parallel token refinement**: Multiple tokens predicted per step (not one-by-one)
- **Non-causal generation**: No forced left-to-right ordering for images/speech

**Modality detokenizers**: Lightweight modality-specific decoders convert discrete tokens back to continuous signals (images, audio) without delegating to separate generative experts.

### Multi-Stage Training Paradigm

Unlike naive joint training, Dynin-Omni decouples modality expansion from capability scaling:

1. **Modality alignment**: Align new modalities (image, speech, video) into the shared backbone representation space
2. **Modality-disentangled model merging**: Merge modality-specific models while preserving prior semantic consistency and extending vocabulary capacity
3. **Capability scaling**: Scale advanced reasoning and generation abilities

### Scheduled Padding Learning

Supports **flexible-length generation** under masked diffusion without degrading global semantic coherence. This addresses a key challenge in diffusion-based generation where fixed-length masks are the norm.

### Key Formulas

**Masked diffusion objective**: Given a sequence `x` with masked positions `M`, the model predicts:
```
P(x_M | x_\M) — predict masked tokens from unmasked context
```

**Iterative refinement**: At each denoising step, a subset of masked tokens is predicted, then the mask is updated:
```
x_M^(t) = Predict(x^(t-1), mask^(t-1))
mask^(t) = UpdateMask(mask^(t-1), x_M^(t))
```

## Experimental Results

Evaluated across **19 multimodal benchmarks**:

| Benchmark | Score | Task |
|-----------|-------|------|
| GSM8K | 87.6 | Mathematical reasoning |
| MME-P | 1733.6 | Multimodal perception |
| VideoMME | 61.4 | Video understanding |
| GenEval | 0.87 | Image generation |
| LibriSpeech (WER) | 2.1 | Speech recognition |

**Competitive with modality-specific experts** while using a single unified backbone. Outperforms Show-o2, HyperCLOVAX-8B-Omni, and NExT-OMNI. Improvements of up to +6.2% on reasoning tasks and +10.1% on video understanding.

## Comparison with Existing Methods

| Model | Architecture | Omni-Modal | Unified Backbone | Open Source |
|-------|-------------|------------|------------------|-------------|
| Show-o2 | AR + FM | Partial | No | Yes |
| HyperCLOVAX-8B-Omni | AR + Diff. | Yes | No | Yes |
| NExT-OMNI | Discrete FM | Yes | Yes | Yes |
| **Dynin-Omni** | **Masked Diffusion** | **Yes** | **Yes** | **Yes** |

## Open Questions

1. **Diffusion steps vs. quality**: How does the number of denoising steps affect generation quality across different modalities?

2. **Reasoning preservation**: Does masked diffusion maintain the chain-of-thought reasoning capabilities of AR models?

3. **Training stability**: How to stabilize joint training across very heterogeneous data distributions?

4. **Tokenization trade-offs**: What is the optimal discrete token representation for each modality?

## See Also

- [[omni-modal-llm]] — Omni-modal LLM landscape
- [[qwen3-omni]] — Qwen3-Omni (AR-based comparison point)
- [[u-mind-multimodal]] — Another unified multimodal generation system
