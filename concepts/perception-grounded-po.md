---
title: Perception-Grounded Policy Optimization for VLMs
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [rl, vlm, perception, policy-optimization, vision]
sources: [raw/papers/2026/04/2604.01840.md]
---
# Perception-Grounded Policy Optimization

## 核心问题
VLM 的 RL 训练中，不是所有 token 都平等——视觉感知相关的 token 应该获得不同的优化策略。

## 方法
- 区分"感知 token"（需要看图）和"推理 token"（纯语言推理）
- 对感知 token 施加更强的视觉 grounding 约束
- Per-token 级别的 policy 优化

## 意义
与 [[faithful-grpo]] 互补，都关注 RLVR 中视觉/推理的平衡，但角度不同：
- Faithful GRPO: 全局 faithfulness 约束
- 本文: token 级别的感知区分

## Related
- [[faithful-grpo]]
- [[g2rpo]]
- [[omni-modal-llm]]
