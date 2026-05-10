---
title: 'AudioKV: KV Cache Eviction for Large Audio-Language Models'
created: 2026-04-27
updated: 2026-04-27
type: concept
tags:
- inference
- speech-model
- architecture
- alignment
sources:
- raw/papers/2026/04/2604.06694.md
---

# AudioKV: KV Cache Eviction in Efficient Large Audio-Language Models

## Core Problem

Large Audio-Language Models (LALMs) have set new benchmarks in speech processing, but their deployment is hindered by the **KV cache memory footprint** during long-context inference. The KV cache grows linearly with audio duration, severely limiting on-device and streaming deployment.

General KV cache compression techniques (SnapKV, AdaKV, etc.) excel in text-only LLMs but **fail in the audio domain** because they overlook the intrinsic **temporal continuity** of acoustic signals.

Two specific failures:
1. **Head-agnostic compression**: Uniformly compressing all attention heads is suboptimal because only a subset of heads captures acoustic information
2. **Temporal clustering**: Raw importance scores cause Top-K selection to concentrate on small token clusters, violating speech's temporal continuity

## Technical Solution

### 1. Audio-Critical Head Identification

**Insight**: Attention heads in LALMs are modality-specialized. Only a small fraction consistently attends to audio tokens.

**Method**:
1. Use WhisperX to get word-level timestamps and confidence scores from ASR
2. Retain high-confidence words (τ = 0.95) as reliable anchors
3. Convert timestamps to audio-token index spans
4. For each attention head, measure overlap between high-attention audio tokens and ground-truth audio spans
5. Compute per-head audio-grounding scores `S_{l,h}`

**Head-aware KV cache allocation**:
```
b_{l,h} = w + r + B_score · S_{l,h} / Σ_{l',h'} S_{l',h'}
```
Where:
- `w` = fixed local window size
- `r` = uniform baseline allocation
- `B_score` = remaining budget distributed proportionally by modality relevance

### 2. Spectral Score Smoothing (SSS)

**Insight**: Speech signals encode information in temporally continuous acoustic representations. Importance scores should be smoothly distributed across the temporal sequence.

**Problem with existing methods**: Top-K selection on raw scores creates dense clusters, violating temporal continuity. Pooling-based smoothing is inherently local.

**SSS Method**:
1. Treat importance scores as a 1D temporal signal
2. Apply **FFT-based global low-pass filter** to suppress high-frequency noise
3. Recover smooth global trends
4. Interpolate filtered signal with original scores using mixing coefficient `α`

```
smoothed_scores = α · FFT_lowpass(original_scores) + (1 - α) · original_scores
```

**Advantages over pooling**:
- Global smoothing over entire importance signal (not local neighborhood)
- Frequency-aware: separates semantic relevance (low-freq) from spurious alignments (high-freq)
- Model-agnostic and computationally efficient (FFT is O(n log n))

### AudioKV Framework

Combines both components:
1. **Offline**: Identify audio-critical heads via ASR-aligned probing
2. **Inference-time**: Apply SSS to importance scores, then allocate head-aware KV budgets

## Experimental Results

Evaluated on Qwen and Gemma series LALMs across ASR and speech translation benchmarks:

**Key result**: At **40% compression ratio** on Qwen3-Omni-30B:
- AudioKV: **0.45% accuracy drop** (near-full accuracy)
- Traditional methods: **Catastrophic degradation** with repetition failures

AudioKV substantially mitigates ASR degradation compared to head-agnostic baselines while maintaining the same cache budget.

## Comparison with Existing Methods

| Method | Head-Aware | Temporal Continuity | Audio-Specific | 40% Compression |
|--------|-----------|---------------------|----------------|-----------------|
| SnapKV | No | Pooling (local) | No | Catastrophic |
| AdaKV | No | Heuristic | No | Catastrophic |
| PyramidKV | Layer-wise | No | No | Degraded |
| **AudioKV** | **Yes** | **FFT (global)** | **Yes** | **0.45% drop** |

## Open Questions

1. **Head stability**: Are audio-critical heads consistent across different tasks, speakers, and languages?

2. **SSS parameter sensitivity**: How to choose the mixing coefficient `α` and cutoff frequency optimally?

3. **Extension to video**: Can similar head-aware + temporal continuity approaches work for video KV cache?

4. **Streaming scenario**: How to adapt AudioKV for true streaming where future context is unavailable for FFT?

## See Also

- [[speech-llm]] — Speech-language model architectures
- [[qwen3-omni]] — Qwen3-Omni model family used in AudioKV experiments
- [[full-duplex-speech-model]] — Full-duplex speech models
