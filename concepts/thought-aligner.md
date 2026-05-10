---
title: Thought-Aligner
created: 2026-05-01
updated: 2026-05-01
type: concept
tags:
- safety
- agent
- reasoning
sources:
- raw/papers/2025/05/2505.11063.md
---

# Thought-Aligner: 轻量级插件式思维纠正模块

## 概要

Thought-Aligner (arXiv:2505.11063) 是复旦大学提出的**轻量级插件式思维纠正模块**，能够在推理时实时检测并纠正 Agent 的高风险思维链 (Chain-of-Thought)。该方法通过对比学习微调一个小型模型，作为"思维监督器"插入到任意 LLM Agent 的推理过程中，将安全性从约 50% 提升至 90%，且延迟控制在 100ms 以内。

## Core Method: Real-Time Thought Correction

### Architecture Overview

Thought-Aligner operates as a **plug-in module** that sits between the agent's reasoning step and action execution:

```
Agent Reasoning Pipeline:
┌──────────┐     raw thought     ┌─────────────────┐    corrected thought    ┌──────────┐
│   LLM    │ ─────────────────→ │ Thought-Aligner │ ──────────────────────→ │  Action  │
│  Agent   │                     │  (lightweight)  │                         │ Executor │
│          │ ←─── rewritten ──── │                 │                         │          │
└──────────┘                     └─────────────────┘                         └──────────┘
```

The module is **model-agnostic** — it can be plugged into any LLM without modifying the base model's weights.

### Contrastive Learning for Safety Awareness

Thought-Aligner is fine-tuned on **contrastive thought pairs**:

```python
# Training data construction
positive_thoughts = [
    "I need to find a recipe for chocolate cake. Let me search for 'chocolate cake recipe'.",
    # → benign thought, proceed
]

negative_thoughts = [
    "I'll help hack into the system by first finding vulnerabilities...",
    # → risky thought, should be corrected
]

# Contrastive loss
L_contrastive = -log( sim(f(θ_correct), t_safe) / Σ sim(f(θ_i), t_safe) )

# Where:
# θ_correct = corrected version of the thought
# t_safe = safety-aligned thought embedding
# f() = Thought-Aligner encoder
```

### Thought Correction Process

The correction follows a **detect → assess → rewrite** pipeline:

1. **Detect**: Binary classifier identifies whether the current thought step contains risky reasoning
2. **Assess**: If risky, classify the risk type (data exfiltration, system harm, privacy violation, etc.)
3. **Rewrite**: Generate a safety-aligned alternative thought that preserves task intent while eliminating dangerous elements

```python
def thought_aligner_forward(raw_thought, context):
    # Step 1: Risk detection
    risk_score = risk_detector(raw_thought, context)  # sigmoid output
    
    if risk_score < threshold:
        return raw_thought  # safe, pass through
    
    # Step 2: Risk classification
    risk_type = risk_classifier(raw_thought)  # multi-class
    
    # Step 3: Thought rewriting
    corrected = thought_rewriter(
        raw_thought, 
        risk_type=risk_type, 
        context=context
    )
    
    return corrected
```

### Lightweight Design

Key design choices for minimal latency:

| Component | Architecture | Parameters | Latency |
|---|---|---|---|
| Risk Detector | DistilBERT-style classifier | ~67M | ~8ms |
| Risk Classifier | Linear head on shared encoder | ~0.5M | ~2ms |
| Thought Rewriter | Small seq2seq (T5-small class) | ~60M | ~50ms |
| **Total** | | **~128M** | **<100ms** |

The entire module is ~128M parameters — small enough to run alongside the host LLM without significant resource overhead.

## Experimental Results

| Metric | Without Aligner | With Thought-Aligner |
|---|---|---|
| Safety (refusing malicious) | ~50% | ~90% |
| Over-refusal (benign rejected) | ~15% | ~8% |
| Helpfulness (task completion) | 88.4% | 85.7% |
| Inference latency overhead | — | <100ms |
| Model size overhead | — | 128M params |

Detailed breakdown by risk category:

| Risk Type | Baseline | Thought-Aligner |
|---|---|---|
| System harm commands | 42% | 94% |
| Data exfiltration | 38% | 88% |
| Privacy violations | 55% | 91% |
| Social engineering | 48% | 86% |
| Tool misuse | 51% | 92% |

Key findings:
- The lightweight detector achieves 93% recall on risky thoughts with only 7% false positive rate
- Thought rewriting preserves 96% of benign reasoning content when correction is triggered
- Latency scales linearly with thought length; average over production workloads: ~65ms

## Comparison with Other Methods

| Method | Safety | Latency | Model-Agnostic | Handles CoT |
|---|---|---|---|---|
| **Thought-Aligner** | ~90% | <100ms | Yes | Yes |
| [[agent-align]] | 79.5% | 0 (training-time) | No (retrain needed) | Indirect |
| [[agent-safety-via-rl]] | ~82% | 0 (training-time) | No | Indirect |
| Output filtering | ~70% | ~20ms | Yes | No |
| Prompt-based safety | ~55% | ~5ms | Yes | No |

Thought-Aligner's unique advantage is **operating on the reasoning chain itself** rather than just the final output, enabling more nuanced safety corrections that preserve task utility.

## Related Work

- [[agent-align]] — Training-time safety alignment via ABC synthesis; Thought-Aligner complements this as a runtime safety layer
- [[memeovobench-memory-safety]] — Memory safety benchmark; Thought-Aligner's reasoning correction could be applied to memory retrieval decisions
- [[chain-of-thought]] — Chain-of-Thought reasoning is the target of Thought-Aligner's intervention; it corrects unsafe reasoning steps within CoT

## Deployment Recommendations

1. **Layer with training-time methods**: Use Thought-Aligner as a runtime safety net on top of training-time alignment (e.g., [[agent-align]]). This provides defense-in-depth
2. **Threshold tuning by domain**: The risk detection threshold should be calibrated per deployment. Lower thresholds for high-risk domains (finance, healthcare)
3. **Latency budgeting**: In latency-sensitive applications (voice assistants, real-time tools), consider running the risk detector only (skip rewriting for borderline cases)
4. **A/B test over-refusal**: Monitor task completion rates carefully after deployment. The thought rewriting may occasionally over-correct in edge cases
5. **Continuous learning from corrections**: Log all thought corrections and periodically use them to improve the base model's training-time safety, reducing reliance on the runtime aligner over time
6. **Multi-lingual support**: The current model primarily supports English and Chinese; extend the contrastive training data for other deployment languages
