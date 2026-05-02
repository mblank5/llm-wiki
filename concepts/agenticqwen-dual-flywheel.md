---
title: AgenticQwen — Dual Data Flywheels for Small Agentic Models
created: 2026-05-02
updated: 2026-05-02
type: concept
tags: [training, fine-tuning, tool-use, rl]
sources: [raw/papers/2026/04/2604.21590.md]
---

# AgenticQwen — Dual Data Flywheels for Small Agentic Models

**arXiv:** [2604.21590](https://arxiv.org/abs/2604.21590)
**Authors:** Yuanjie Lyu, Chengyu Wang, Haonan Zheng, et al. (Alibaba Group)
**Date:** April 2026

## Overview

AgenticQwen trains small language models to act as agents with multi-step reasoning and tool use in industrial settings. The key innovation is a **dual data flywheel** system that automatically generates increasingly challenging synthetic data for RL training, closing the gap with much larger models on search and data analysis tasks.

## Dual Data Flywheels

### Flywheel 1: Reasoning Data Flywheel

Generates increasingly difficult reasoning tasks by learning from errors:

1. **Self-instruct expansion (structural diversity):** Generate diverse reasoning templates from seed tasks
2. **Persona injection (contextual diversity):** Inject different reasoning personas to create diverse solution paths
3. **Multi-model consistency filtering:** Only keep tasks where multiple models agree on the answer (quality control)

The key loop: errors from current model → harder tasks generated to address weaknesses → model improves on those weaknesses.

### Flywheel 2: Agentic Data Flywheel

Expands linear workflows into multi-branch behavior trees that reflect real-world decision complexity:

1. **Phase 1 — Linear task initialization:** Start with simple linear tool-use workflows
2. **Phase 2 — Behavior tree expansion:** Expand linear workflows into branching decision trees
3. **Phase 3 — Branch-to-task inversion:** Convert decision branches into new standalone tasks
4. **Phase 4 — Adversarial mock-user intervention:** Introduce adversarial user strategies to test robustness

**Synthetic data validation:** Each generated task is validated for correctness and difficulty before inclusion.

## Training Framework

### Multi-Round RL Training

Combines **reasoning RL** (internal reasoning capability) with **agentic RL** (external tool-use capability):

- Both flywheels run iteratively, generating harder data as the model improves
- RL training on synthetic data + limited open-source data
- Multiple rounds of training with progressively harder data

### Model Family

The AgenticQwen family includes models of various sizes, with checkpoints released on HuggingFace.

## Experimental Results

### Benchmarks
- Strong performance on multiple agentic benchmarks (BFCL-V4 for web search and memory)
- In industrial agent system, closes gap with much larger models on search and data analysis tasks

### Industrial Application
- Deployed in enterprise data analytics agent system
- Small AgenticQwen models compete with larger models on search and data analysis under strict cost/latency constraints

## Related

- [[tool-use]] — Tool use in LLM agents
- [[agentic-coding]] — Agentic coding systems
- [[less-is-more-agentic]] — Efficient agentic approaches
- [[knowledge-distillation]] — Knowledge distillation techniques
- [[rl-post-training-scaling-laws]] — RL scaling laws

## Significance for Our Work

AgenticQwen demonstrates that small models can achieve competitive agentic performance through careful synthetic data generation and multi-round RL training. The dual flywheel approach (reasoning + agentic) is relevant for our work on OPD — the data generation pipeline could be combined with distillation to produce high-quality student data. The behavior tree expansion (Phase 2 of the agentic flywheel) is particularly interesting as a method for generating complex multi-step training data that tests the limits of small models.
