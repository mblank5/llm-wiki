---
title: "TIP: Token Importance in On-Policy Distillation"
created: 2026-04-26
updated: 2026-04-26
type: concept
tags: [distillation, on-policy, rl]
sources: [raw/papers/2026/04/2604.14084.md]
---
# TIP: Token Importance in On-Policy Distillation

研究 token 级别重要性在 OPD 中的作用，发现并非所有 token 位置对蒸馏效果贡献相同。

## 定义

TIP 系统分析了 OPD 中不同 token 位置的重要性差异，为**差异化 token 级监督**提供理论基础。

## 核心发现

### Token 级别重要性差异
- **不是所有 token 位置都同等重要**
- 某些 token（如推理关键步骤、决策节点）对蒸馏效果的影响远大于其他 token
- 均匀对所有 token 施加 KL 约束可能浪费计算资源，甚至引入噪声

### 重要性评估方法
- 论文提出了量化 token 级重要度的方法
- 重要性分布呈现显著的**长尾特征**：少数 token 承载了大部分蒸馏信号

### 对 OPD 的启示
- 选择性聚焦重要 token 可提升蒸馏效率
- 与 [[per-token-kl-clipping]] 和 [[entropy-aware-on-policy-distillation]] 的思路互补

## 实验结果
- 论文验证了 token 重要性分布的假设
- 基于重要性的选择性蒸馏可在减少计算量的同时保持性能

## 开放问题
- Token 重要性是否具有跨模型、跨任务的泛化性？
- 如何在训练中动态估计 token 重要性？
- 与 SCOPE 的 per-trajectory routing 如何结合？

## Related
- [[on-policy-distillation]]
- [[per-token-kl-clipping]]
- [[entropy-aware-on-policy-distillation]]
