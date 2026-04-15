---
title: Scalable MoE 预训练
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [pretraining, moe, scaling, distributed, supercomputer]
sources: [raw/papers/2026/04/2604.00785.md]
---
# Scalable MoE 预训练

## 核心
在 Aurora 超级计算机上大规模 MoE LLM 预训练的工程实践和 scaling 经验。

## 关键点
- MoE 在超大规模分布式训练中的通信/计算平衡
- Expert parallelism 的实现细节
- 千卡级训练的稳定性技巧

## Related
- [[mixture-of-experts]]
- [[llm-training-as-lossy-compression]]
