---
title: Qwen3
created: 2026-04-06
updated: 2026-04-10
type: entity
tags: [model, architecture, open-source]
sources: [raw/papers/2025/05/2505.09388.md]
---

# Qwen3

Qwen3 is the latest series of open-weight large language models (LLMs) from the Qwen model family, released under Apache 2.0. It includes both dense and Mixture-of-Experts (MoE) architectures with parameter scales ranging from 0.6B to 235B.

## Key Innovations

- **Thinking Mode and Non-Thinking Mode Integration**: A unified framework allowing dynamic switching between complex multi-step reasoning and rapid context-driven responses within a single model, eliminating the need for separate chat-optimized and reasoning models.
- **Thinking Budget**: A mechanism enabling users to allocate computational resources adaptively during inference, balancing latency and performance.
- **Strong-to-Weak Distillation**: Leveraging knowledge from flagship models to efficiently build smaller-scale models with highly competitive performance.
- **Expanded Multilingual Support**: Pre-trained on 36 trillion tokens covering 119 languages and dialects (up from 29 in Qwen2.5).

## Model Variants

### Dense Models
| Model | Parameters | Context Length |
|-------|------------|---------------|
| Qwen3-0.6B | 0.6B | 32K |
| Qwen3-1.7B | 1.7B | 32K |
| Qwen3-4B | 4B | 128K |
| Qwen3-8B | 8B | 128K |
| Qwen3-14B | 14B | 128K |
| Qwen3-32B | 32B | 128K |

### MoE Models
| Model | Total Params | Activated Params | Context Length |
|-------|-------------|-----------------|---------------|
| Qwen3-30B-A3B | 30B | 3B | 128K |
| Qwen3-235B-A22B | 235B | 22B | 128K |

## Architecture

Based on Qwen2.5 architecture with Grouped Query Attention (GQA), SwiGLU, Rotary Positional Embeddings (RoPE), and RMSNorm with pre-normalization. QKV-bias is removed and QK-Norm is introduced for training stability. MoE models use fine-grained expert segmentation with 128 total experts, 8 activated per token, and no shared experts.

## Training Pipeline

### Pre-training (3 stages)
1. General Stage: 30T+ tokens, 4K sequence length, 119 languages
2. Reasoning Stage: 5T tokens with increased STEM/coding/reasoning data
3. Long Context Stage: Extended to 32K context using ABF RoPE, YARN, and Dual Chunk Attention

### Post-training (4 stages for flagship)
1. Long-CoT Cold Start
2. Reasoning RL (GRPO)
3. Thinking Mode Fusion (SFT)
4. General-domain RL

Smaller models use Strong-to-Weak Distillation instead of full 4-stage training.

## Performance Highlights (Post-trained)

Qwen3-235B-A22B achieves:
- AIME'24: 85.7, AIME'25: 81.5
- LiveCodeBench v5: 70.7
- CodeForces: 2056
- BFCL v3: 70.8

Outperforms DeepSeek-V3 Base on 14/15 benchmarks with 1/3 total parameters.

## Related Concepts

- [[mixture-of-experts]]
- [[thinking-budget]]
- [[strong-to-weak-distillation]]
- [[chain-of-thought]]
- [[reinforcement-learning-from-human-feedback|RLHF]] (related, though Qwen3 uses GRPO)
- [[on-policy-distillation]]
- [[generalized-on-policy-distillation]]
- [[opd-vs-sft]] — comparison of OPD versus SFT approaches as used in Qwen3
- [[qwen3-opd-usage]] — detailed analysis of how Qwen3 applies on-policy distillation
- [[qwen3-tech-overview]] — comprehensive technical overview of the Qwen3 family
- [[qwen3-voice-family-deep-dive]] — deep dive into Qwen3 voice and speech models

[src: raw/ingested/2025/05/2505.09388.md]