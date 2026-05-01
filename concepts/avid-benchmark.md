---
title: "AVID: Audio-Visual Inconsistency Benchmark"
created: 2026-04-27
updated: 2026-04-27
type: concept
tags: [benchmark, multimodal, architecture]
sources: ["2604.13593"]
---

# AVID: Audio-Visual Inconsistency Understanding Benchmark

## Core Problem

Omni-modal LLMs excel at temporally aligned tasks (captioning, QA) but struggle to perceive **cross-modal conflicts** — a fundamental human capability critical for trustworthy AI. Existing benchmarks have two major limitations:

1. **Positive-only bias in grounding benchmarks**: AVE, UnAV-100, LongVALE focus exclusively on localizing temporally aligned positive events, assuming visual and auditory streams are always congruent.

2. **Artifact-oriented bias in deepfake datasets**: FakeAVCeleb, LAV-DF, AV-Deepfake1M++ can be solved by exploiting uni-modal artifacts (visual blending defects, unnatural audio frequencies) without genuinely understanding cross-modal correlations. Also limited to extremely short durations.

No benchmark systematically evaluates audio-visual inconsistency understanding in **long-form video contexts**.

## Technical Solution

### AVID Construction Pipeline

**Stage 1: Temporal Segmentation and Classification**
Videos are segmented and classified into three categories:
- **Active Speaker**: Person speaking on camera
- **Voiceover**: Off-screen narrator
- **Scenic**: Environmental/natural sounds

**Stage 2: Agent-Driven Strategy Planning**
A strategy agent analyzes segment content and recommends appropriate inconsistency types to inject.

**Stage 3: Controlled Inconsistency Injection**
Five specialized injectors introduce diverse audio-visual conflicts while preserving original visual content and video duration:

1. **Audio replacement**: Swap audio with semantically mismatched audio
2. **Speaker mismatch**: Replace speaker's voice with different voice
3. **Temporal misalignment**: Shift audio relative to video
4. **Content conflict**: Add audio describing different visual content
5. **Emotional incongruence**: Audio emotion doesn't match visual emotion

### Dataset Statistics

- **11.2K full videos** (avg. 235.5s), 3:1 ratio of inconsistent to fully consistent
- **39.4K annotated inconsistency events** with precise temporal boundaries
- **78.7K segment clips** (avg. 14.8s), balanced positive-to-negative ratio (1:1)
- **8 fine-grained inconsistency categories** across 3 segment classes
- All samples annotated with detailed causal explanations

### Evaluation Tasks

**Segment-level** (78.7K clips):
- Inconsistency detection (binary)
- Category classification (8 classes)
- Fine-grained reasoning about the conflict

**Full-video level** (11.2K videos):
- Inconsistency detection
- Temporal grounding (locate when inconsistency occurs)
- Dense reasoning across multiple events

## Experimental Results

Comprehensive evaluation of state-of-the-art omni-models reveals significant limitations in temporal grounding and reasoning.

**AVID-Qwen** (Qwen3-Omni fine-tuned on AVID):
- **2.8× higher BLEU-4** in segment reasoning vs. base model
- **mIoU: 36.1%** vs. 26.2% for best competing model (temporal grounding)
- **SODA-m: 7.47** vs. 6.15 for best competing model (holistic understanding)

## Comparison with Existing Benchmarks

| Benchmark | Video Form | A/V Inconsistency | # Categories | Reasoning | Long-form |
|-----------|-----------|-------------------|--------------|-----------|-----------|
| AVE | Segment (10s) | No | — | No | No |
| UnAV-100 | Full (42s) | No | — | No | Partial |
| FakeAVCeleb | Segment (7.8s) | Yes | 3 | No | No |
| LongVALE | Full (235s) | No | — | No | Yes |
| **AVID** | **Full (235s) + Segment** | **Yes** | **8** | **Yes** | **Yes** |

## Open Questions

1. **Generalization to real-world inconsistencies**: How well do models trained on injected inconsistencies generalize to naturally occurring audio-visual conflicts?

2. **Causal reasoning depth**: Can models go beyond detecting inconsistency to explaining WHY the modalities conflict?

3. **Multimodal inconsistency types**: How to handle cases where inconsistency is subtle and requires domain knowledge (e.g., anachronistic sounds in historical footage)?

4. **Real-time detection**: Can inconsistency detection be made efficient enough for real-time video monitoring applications?

## See Also

- [[omni-modal-llm]] — Omni-modal LLM architectures
- [[omni-modality-preference]] — Modality preference understanding
- [[omnitrace-attribution]] — Attribution methods for multimodal generation
