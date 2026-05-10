---
title: "Multimodal Latent Reasoning via Predictive Embeddings"
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [multimodal, reasoning, latent, embedding, continuous]
sources: [raw/papers/2026/04/2604.08065.md]
---
# Multimodal Latent Reasoning

## 核心思路
推理不一定要在 token 空间进行——可以在连续 embedding 空间做"潜在推理"。

## 方法
- Predictive embedding: 在 latent space 预测下一步推理状态
- 跳过显式 token 生成，用 embedding 直接推进推理
- 可在推理时增加计算量而不增加输出长度

## 意义
- 与 [[thinking-budget]] 互补：不同于 token-level CoT，latent reasoning 更高效
- 与 [[silent-thought]] 的"think-while-listening"理念类似，但更系统化

## Related
- [[thinking-budget]]
- [[silent-thought]]
- [[chain-of-thought]]
