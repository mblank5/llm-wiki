---
title: Latent Agents — Internalized Multi-Agent Debate (IMAD)
created: 2026-05-02
updated: 2026-05-02
type: concept
tags: [distillation, reasoning, alignment]
sources: [raw/papers/2026/04/2604.24881.md]
---

# Latent Agents — Internalized Multi-Agent Debate (IMAD)

**arXiv:** [2604.24881](https://arxiv.org/abs/2604.24881)
**Authors:** John Seon Keun Yi, Aaron Mueller, Dokyun Lee (Boston University)
**Date:** April 2026

## Overview

IMAD (Internalized Multi-Agent Debate) distills multi-agent debate into a single LLM through a two-stage fine-tuning pipeline. The internalized model matches or exceeds explicit multi-agent debate performance using up to **93% fewer tokens**. Additionally, internalization creates agent-specific subspaces in activation space, enabling activation steering and malicious agent suppression.

## Method: Two-Stage Pipeline

### Stage 1: Debate Structure Learning (SFT)

- Construct multi-agent debate datasets with diverse personas (different perspectives on the same question)
- Train the model via supervised fine-tuning to replicate the debate structure
- The model learns the format of multi-agent interaction but debate remains explicit (generates full transcripts)

### Stage 2: Reinforcement Learning for Internalization

- Apply RL with **dynamic reward scheduling** and **length clipping** to progressively internalize debate
- The model learns to perform the "debate" internally in its latent space rather than generating full transcripts
- **Length clipping** penalizes verbose outputs, encouraging the model to compress debate reasoning
- **Dynamic reward scheduling** balances correctness rewards with efficiency incentives

### Key Insight

The model compresses multi-turn debate reasoning into its internal representations — the "latent agents" are recoverable through activation steering, not collapsed during internalization.

## Mechanistic Analysis: Agent Subspaces

### Steering Vector Extraction

Using **difference-in-means** (Marks & Tegmark, 2023):
$$\vec{v}_i = \frac{1}{|S_i|}\sum_{x \in S_i} h(x) - \frac{1}{|S_{\neg i}|}\sum_{x \in S_{\neg i}} h(x)$$

Where $h(x)$ is the hidden state activation and $S_i$ is the set of examples where agent $i$ is active.

### Key Findings

1. **Agent-specific subspaces exist:** Internalization creates linearly separable directions in activation space corresponding to different agent perspectives
2. **Collaborative structure is preserved:** The debate structure is not collapsed — steering with agent vectors produces agent-specific behaviors
3. **Malicious agent suppression:** By instilling malicious agents through internalized debate, then applying negative steering to suppress them, harmful behaviors are easier to localize and control with smaller reductions in general performance compared to steering base models

## Experimental Results

- IMAD matches or exceeds explicit multi-agent debate across multiple benchmarks
- Token reduction: up to **93% fewer tokens** compared to running explicit debate
- The internalized model retains reasoning quality while achieving single-model inference efficiency

## Implications for Distillation and Alignment

1. **Distillation of reasoning processes:** Multi-agent debate (a computationally expensive reasoning process) can be distilled into efficient single-model inference
2. **Mechanistic interpretability:** The internalized agents form recoverable subspaces, suggesting that distilled models retain structured representations of their training processes
3. **Safety via steering:** Malicious behaviors introduced through internalized debate are easier to localize and suppress via activation steering — distillation may make alignment more tractable

## Related

- [[on-policy-self-distillation]] — Self-distillation for reasoning
- [[knowledge-distillation]] — General knowledge distillation
- [[deepseek-r1-distillation]] — Distillation of reasoning models
- [[reasoning-distillation]] — Reasoning capability distillation
- [[behavioral-self-awareness]] — Model self-awareness and behavioral modeling

## Significance for Our Work

IMAD shows that multi-agent reasoning can be internalized into a single model through post-training. This connects to OPD/GKD in that both involve distilling a more capable (or differently structured) reasoning process into the student model. The agent subspace finding is particularly interesting for MOE models — if different "experts" or "agents" form separable subspaces in activation space, this could inform how we understand and control expert specialization post-distillation.
