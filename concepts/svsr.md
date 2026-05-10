---
title: "SVSR: 多模态推理的自验证自修正"
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [multimodal, reasoning, self-verification, self-rectification]
sources: [raw/papers/2026/04/2604.10228.md]
---
# SVSR: Self-Verification and Self-Rectification

## 核心范式
多模态推理的两阶段自我改进：
1. **Self-Verification**: 模型验证自己的推理过程是否与视觉证据一致
2. **Self-Rectification**: 发现不一致后自动修正

## 与 SAVeR 的关系
- [[saver-faithful-reasoning]] 关注 agent 的 belief 审计
- SVSR 关注多模态推理中的视觉-语言一致性
- 两者都体现了"推理后验证"的新范式

## Related
- [[saver-faithful-reasoning]]
- [[perception-grounded-po]]
- [[chain-of-thought]]
