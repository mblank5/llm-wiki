---
title: SUPERNOVA: 自然指令 RL 激发通用推理
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [rl, reasoning, natural-instructions, generalization]
sources: [raw/papers/2026/04/2604.08477.md]
---
# SUPERNOVA

## 核心方法
在自然语言指令上用 RL 训练，激发 LLM 的通用推理能力——不需要专门的数学/代码推理数据。

## 与 RLVR 的区别
- RLVR 依赖可验证 reward（数学、代码有明确对错）
- SUPERNOVA 在更广泛的自然语言任务上做 RL，用 LLM judge 做 reward
- 目标是通用推理能力，而非特定领域

## Related
- [[llm-post-training-unified-view]]
- [[g2rpo]]
- [[reflectrm]]
