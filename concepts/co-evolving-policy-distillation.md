---
title: Co-Evolving Policy Distillation (CoPD)
created: 2026-05-02
updated: 2026-05-02
type: concept
tags: [distillation, on-policy, rl, rlhf, grpo]
sources: [raw/papers/2026/04/2604.27083.md]
---

# Co-Evolving Policy Distillation (CoPD)

**arXiv:** [2604.27083](https://arxiv.org/abs/2604.27083)
**Authors:** Naibin Gu, Chenxu Yang, Qingyi Si, et al. (中科院信工所 + 京东)
**Date:** April 2026

## Overview

CoPD (Co-Evolving Policy Distillation) proposes a unified training paradigm that addresses capability loss when consolidating multiple expert capabilities into a single model. It identifies two failure modes in existing approaches and introduces parallel expert training with bidirectional on-policy distillation during ongoing RLVR.

## Problem Analysis

### Failure Mode 1: Mixed RLVR — Capability Divergence

Training a single model on mixed-capability data with RLVR exhibits **capability trade-off**: gains in one capability come at the expense of another. Distinct capabilities favor different optimization directions, making it difficult for a single training run to advance all of them simultaneously.

### Failure Mode 2: Static OPD — Behavioral Pattern Gap

The pipeline of first training experts to convergence, then performing OPD to distill them into a student, suffers from:
- Experts trained to convergence **drift outside the effective OPD range**
- Large behavioral pattern gaps between teacher and student reduce distillation efficiency

### Key Finding: Behavioral Consistency Hypothesis

OPD efficiency η increases with teacher-student **top-k overlap** (Oₖ):

$$\eta \propto O_k(\pi_T, \pi_\theta)$$

Empirical finding: post-OPD gain shows strong linear correlation with top-k overlap (r = 0.89, R² = 0.79). As standard RLVR training proceeds, top-k overlap drops and symmetric KL rises, pushing experts into the low-η regime.

## CoPD Method

### Core Idea

Instead of the static pipeline (train experts → distill), CoPD runs **parallel RLVR training** with **bidirectional OPD interleaved** during each expert's ongoing training:

```
Branch A (text RLVR)          Branch B (image RLVR)
    ↓                              ↓
[RLVR steps]                  [RLVR steps]
    ↓         ← OPD →              ↓
[RLVR steps]                  [RLVR steps]
    ↓         ← OPD →              ↓
...                              ...
```

**Key mechanisms:**
1. **Parallel training:** Multiple domain-specific branches train simultaneously from a shared base
2. **Interleaved OPD:** During each branch's RLVR, the other branch serves as teacher
3. **Bidirectional distillation:** Each branch is both teacher and student (mutual teaching)
4. **Behavioral consistency:** Since experts co-evolve (not trained to convergence independently), they maintain sufficient behavioral overlap for effective OPD throughout training

### Why CoPD Works

- **Maintains complementary knowledge:** Experts retain domain-specific capabilities because they never fully converge before distillation
- **Consistent behavioral patterns:** Co-evolving experts stay within the effective OPD range (high Oₖ)
- **Bidirectional signal:** Each branch receives distillation signal from the other, not just one-way teacher→student

## Experimental Results

### Setup
- **Base model:** Qwen3-VL-4B-Instruct
- **Text reasoning:** Polaris-Dataset-53K → evaluated on AIME 2024/2025, HMMT 2025, MATH-500, Minerva Math
- **Image reasoning:** MMFineReason-123K → evaluated on MMMU, MMMU-Pro, MathVista, MathVision, ZeroBench, WeMath, MathVerse
- **Video reasoning (3-branch):** OneThinker + VideoChat-R1 + Video-R1 → evaluated on Video-Holmes, MVBench, MMVU, VideoMathQA

### Key Results (2-branch: text + image)

| Benchmark | Base | Image-Expert | Text-Expert | Mixed RLVR | OPD (V→T) | OPD (T→V) | **CoPD** |
|-----------|------|-------------|-------------|------------|-----------|-----------|----------|
| **Vis. Avg.** | 54.00 | 55.76 | 55.21 | 55.69 | 56.18 | 56.44 | **56.96** |
| **Text Avg.** | 48.45 | 48.27 | 57.27 | 53.45 | 51.73 | 52.82 | **54.27** |

CoPD **outperforms** both mixed RLVR and static OPD, and even surpasses domain-specific experts on their own domains.

### 3-branch Extension (text + image + video)
CoPD scales to 3 branches with similar advantages, demonstrating the model parallel training pattern as a potential new scaling paradigm.

## Relationship to Other Methods

| Method | Training | Distillation | Capability Loss |
|--------|----------|-------------|-----------------|
| Mixed RLVR | Single pool, all data | N/A | Inter-capability divergence |
| Static OPD | Experts → converge → distill | One-way, post-training | Large teacher-student gap |
| MOPD | Multiple experts | One-way | Partial absorption |
| **CoPD** | **Parallel + interleaved** | **Bidirectional, during training** | **Minimized** |

## Related

- [[on-policy-distillation]] — OPD foundation
- [[rlvr]] — RLVR paradigm
- [[grpo-rl-training]] — GRPO as RLVR algorithm
- [[generalized-on-policy-distillation]] — GOPD framework
- [[knowledge-distillation]] — General knowledge distillation

## Significance for Our Work

CoPD directly addresses the OPD training pipeline design problem: when to distill, who distills whom, and how to maintain behavioral consistency. For MOE models where training-inference consistency is a concern, CoPD's parallel branch pattern suggests a new approach — instead of training separate experts then distilling, run parallel RLVR with interleaved OPD to maintain consistent behavioral patterns throughout.
