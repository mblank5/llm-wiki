---
title: RL-Guided Synthetic Data Generation
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [synthetic-data, rl, privacy, data-generation]
sources: [raw/papers/2026/04/2604.07884.md]
---
# RL-Guided Synthetic Data Generation

## 核心
用强化学习引导合成数据生成过程，在保护隐私的同时最大化下游任务效用。

## 方法
- 将数据生成建模为 RL 问题
- Reward = 下游任务性能 + 隐私保护程度
- 生成器自动学习最优的数据合成策略

## 意义
RL 不仅用于模型后训练，还可以用于数据工程——合成数据生成本身也可以 RL 化。

## Related
- [[blendfusion]]
- [[optimsyn]]
- [[grpo-rl-training]]
