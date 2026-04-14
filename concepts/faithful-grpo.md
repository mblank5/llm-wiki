---
title: Faithful GRPO
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [rl, grpo, vision, spatial-reasoning, faithfulness]
sources: [raw/papers/2026/04/2604.08476.md]
---

# Faithful GRPO: 约束策略优化下的视觉空间推理

## 核心问题

RLVR 训练的 VLM 在视觉空间推理上存在 **accuracy-faithfulness 矛盾**：
- Accuracy 提升（答对更多题）
- Faithfulness 下降（推理过程与视觉输入不一致，模型"猜对"而非"看对"）

## 方法

在 GRPO 基础上引入约束，确保 RL 增益来自真实的视觉 grounding：
- 限制策略更新不偏离视觉证据
- 对空间推理任务增加 faithfulness reward 信号

## 意义

揭示了 RLVR 的一个潜在陷阱：模型可能在 reward hacking（通过统计偏差答对），
而非真正理解视觉内容。对多模态 RL 后训练有重要警示。

## Related

- [[grpo-rl-training]]
- [[g2rpo]]
- [[llm-post-training-unified-view]]
