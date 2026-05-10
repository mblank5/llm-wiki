---
title: 'V2A-DPO: Video-to-Audio Preference Optimization'
created: 2026-04-27
updated: 2026-04-27
type: concept
tags:
- training
- alignment
- multimodal
- rl
sources:
- raw/papers/2026/03/2603.11089.md
---

# V2A-DPO: Omni-Preference Optimization for Video-to-Audio Generation

## Core Problem

Video-to-Audio generation (V2A) aims to synthesize semantically consistent, temporally aligned audio conditioned on video. Despite rapid progress, prior V2A models have three critical limitations:

1. **Limited style control**: Models are restricted to video-audio pairs seen during training, lacking flexibility for out-of-distribution scenarios
2. **Missing aesthetic quality**: Even when semantically relevant and temporally aligned, generated audio often lacks immersion and aesthetic appeal
3. **Fragmented evaluation**: Existing metrics assess semantic consistency, temporal alignment, and perceptual quality separately, with no comprehensive scoring system

## Technical Solution

V2A-DPO pioneers the adaptation of **Direct Preference Optimization (DPO)** to **flow-based** V2A models with three core innovations:

### 1. AudioScore: Comprehensive Preference Scoring

A multi-dimensional scoring system assessing:
- **Semantic consistency** (ImageBind cosine similarity + CLAP score): Video-audio and text-audio alignment
- **Temporal alignment** (DeSync from Synchformer): Misalignment in seconds between audio and video
- **Perceptual quality** (PANNs-based Inception Score): Audio richness and clarity
- **Speech quality** (PESQ): Human speech category quality

A small MLP (2 Linear layers + ReLU + Softmax) maps the 5-dimensional score vector to 3-class probabilities (Good/Medium/Bad), trained with cross-entropy against human annotations on 2K samples.

### 2. Automated Preference Pair Generation

**Pipeline**:
1. Generate N audio samples per video prompt using pre-trained V2A model
2. Score each with AudioScore → probability vector `p_i`
3. Select "best vs. worst" pair: highest P(Good) as winner, highest P(Bad) as loser

**Dataset**: 50K videos from VGGSound → ~46K auto-generated pairs + 2K human-annotated pairs = **~48K total pairs**

### 3. Curriculum Learning-Empowered DPO

For flow-based generative models, standard DPO can be unstable. V2A-DPO introduces curriculum learning:

1. Compute complexity score for each preference pair
2. Split into "simple" and "complex" subsets
3. Train on simple pairs first, then gradually introduce complex pairs

This staged optimization is tailored for flow matching's unique training dynamics.

### DPO Objective

Standard DPO loss adapted for V2A:
```
L_DPO = -E[log σ(β · (log π_θ(y_w|x)/π_ref(y_w|x) - log π_θ(y_l|x)/π_ref(y_l|x)))]
```

Where `y_w` = winning audio, `y_l` = losing audio, `x` = video + text prompt.

## Experimental Results

Evaluated on VGGSound benchmark with Frieren and MMAudio as base models:

**V2A-DPO vs DDPO vs pre-trained baselines**:
- **IS improvement**: +1.81 absolute (+10.4% relative)
- **IB-score improvement**: +0.86 absolute (+2.6% relative)
- **DeSync reduction**: -0.09 absolute (-20.5% relative)

**DPO-optimized MMAudio achieves state-of-the-art**, surpassing all published V2A models across multiple metrics.

## Comparison with Existing Methods

| Method | Training Paradigm | Preference Data | Scoring System | Curriculum |
|--------|------------------|-----------------|----------------|------------|
| DDPO | RL reward model | None | Single metric | No |
| Standard DPO | Preference pairs | Human only | None | No |
| **V2A-DPO** | **Preference pairs** | **Auto + human (48K)** | **AudioScore (5-dim)** | **Yes** |

## Open Questions

1. **Flow-specific DPO theory**: What are the convergence guarantees of DPO for flow-matching models vs. autoregressive models?

2. **AudioScore generalization**: Does AudioScore trained on VGGSound generalize to other V2A domains (music, ambient sounds)?

3. **Preference diversity**: Does "best vs. worst" selection capture the full preference distribution, or does it oversimplify?

4. **Human-AI score alignment**: How well does AudioScore's automated scoring correlate with diverse human listener preferences?

## See Also

- [[v2a-dpo]] is tightly related to [[avid-benchmark]] — audio-visual consistency evaluation
- [[alignment]] — Alignment techniques for generative models
- [[rl]] — RL-based preference optimization methods
