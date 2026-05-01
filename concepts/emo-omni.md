---
title: "EmoOmni: Emotional Understanding in Omni-LLMs"
created: 2026-04-27
updated: 2026-04-27
type: concept
tags: [model, multimodal, alignment, training, architecture]
sources: ["2602.21900"]
---

# EmoOmni: Bridging Emotional Understanding and Expression in Omni-Modal LLMs

## Core Problem

Existing Omni-LLMs struggle with complex real-world emotional scenarios:
1. **Superficial understanding**: Audio and visual cues are often complex, implicit, or conflicting (e.g., cheerful tone + frowning face). Models fail to resolve these conflicts.
2. **Emotional detail loss**: Thinker-Talker architectures rely on implicit emotional control through hidden states. Emotional intent is diluted or lost during transmission from Thinker to Talker.
3. **Data scarcity**: No widely adopted pipeline exists for real-world, emotionally annotated multimodal dialogue data.
4. **Evaluation gap**: Benchmarks focus on task correctness or basic emotion recognition, not emotional intelligence in dialogue context.

## Technical Solution

### EmoOmni Framework

Mimics human affective cognition through a **Perception–Reasoning–Expression causal chain**:

**EmoOmni-Thinker**: Multimodal perception → E-CoT reasoning → Textual response
**EmoOmni-Talker**: E-CoT as explicit emotional instruction → Expressive speech synthesis

### Emotional Chain-of-Thought (E-CoT)

The core innovation is a structured reasoning trajectory with four components:

1. **Multimodal Emotion Perception** (`z_p`): Fine-grained emotional cue extraction from audio and video
   - `P(z_p | M)` where `M` = multimodal features
   - Captures vocal tension, facial expressions, behavioral inconsistencies

2. **Intention Analysis** (`z_a`): Infer user's underlying intention from perceived cues
   - `P(z_a | z_p)`
   - Resolves sarcasm, emotional masking, conflicting signals

3. **Response Strategy Planning** (`z_s`): High-level emotional and pragmatic response plan
   - `P(z_s | z_a)`
   - Abstract control signal decoupling decision-making from surface realization

4. **Textual Response Generation** (`z_t`): Final response conditioned on all reasoning stages
   - `P(z_t | z_p, z_a, z_s)`

**Complete E-CoT**: `Z = {z_p, z_a, z_s, z_t}`

The E-CoT serves dual purpose: (1) explicit reasoning for the Thinker, and (2) explicit emotional instructions for the Talker, ensuring the final speech is semantically and emotionally aligned.

### EmoOmniPipe Data Pipeline

Extracts and annotates emotionally rich dialogues from movies/TV series:
1. Raw video segmentation (20-min chunks, audio/video isolation, denoising via MelBandRoformer)
2. Multimodal annotation (6 dimensions using SOTA models)
3. E-CoT construction (via Gemini 2.5 Pro with contextual history)
4. Quality filtering via GPT-4o

### EmoOmniEval Benchmark

Three evaluation settings:
- **Video-to-Speech (VS)**: End-to-end from input video to generated speech
- **Video-to-Text Response (VT)**: Text generation quality from input video
- **Instruction Following (IF)**: Speech synthesis conditioned on explicit instructions

Each scored 0/1/2 on: Response Content Relevance & Logic, Response Emotional Strategy, Emotion Analysis.

## Experimental Results

**EmoOmni-7B achieves comparable performance with Qwen3Omni-30B-A3B-Thinking** under the same talker, demonstrating that E-CoT and real-world data effectively compensate for parameter scale in affective computing (7B vs 30B).

## Comparison with Existing Methods

| Approach | Emotion Modeling | Data | Reasoning Chain | Expression Control |
|----------|-----------------|------|-----------------|-------------------|
| Tag-based | Single label | Coarse | None | Implicit |
| Prompt-based | Style descriptions | Limited | None | Partial |
| EmoOmni | **Multi-dimensional E-CoT** | **Real-world movies/TV** | **Explicit 4-stage** | **Explicit instruction** |

## Open Questions

1. **Cross-cultural emotions**: How does E-CoT generalize across cultures with different emotional expression norms?

2. **Real-time E-CoT**: Can the multi-stage reasoning be streamlined for low-latency applications?

3. **Conflicting modality resolution**: When audio and video convey opposite emotions, what determines which E-CoT path the model takes?

4. **Talker expressiveness**: How much emotional range can the Talker achieve given E-CoT instructions vs. raw hidden states?

## See Also

- [[omni-modal-llm]] — Omni-modal LLM architectures
- [[u-mind-multimodal]] — Real-time multimodal interaction
- [[full-duplex-speech-model]] — Full-duplex speech models for dialogue
