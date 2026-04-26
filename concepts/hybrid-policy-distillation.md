---
title: "Hybrid Policy Distillation for LLMs"
created: 2026-04-26
updated: 2026-04-26
type: concept
tags: [distillation, on-policy, rl, optimization]
sources: [raw/papers/2026/04/2604.20244.md]
---
# Hybrid Policy Distillation for LLMs

混合策略蒸馏方法，结合多种蒸馏策略以平衡不同训练目标。仅有 abstract 可用，全文尚未公开。

## 定义

Hybrid Policy Distillation 提出一种混合策略蒸馏框架，融合多种蒸馏策略（如 KL 约束、reward-weighted、self-distillation）以在不同训练阶段和不同样本上自适应地选择最优蒸馏方式。

## 核心思路

### 混合策略
- 不是单一蒸馏策略，而是**多种策略的组合**
- 可能包括：KL 对齐、reward 加权蒸馏、self-distillation 等
- 根据样本特征或训练阶段**动态切换**蒸馏策略

### 与现有方法的关联
- 与 [[hybrid-distillation-policy-optimization]] (HDPO) 共享"混合"理念
- HDPO 专注于"悬崖 prompt"的特权自蒸馏
- Hybrid Policy Distillation 可能更通用

## 已知信息
- 目前仅有 abstract 可用，全文尚未公开
- 无法获取详细方法、实验设置和结果
- 等待全文发布后补充细节

## 开放问题
- 混合策略的具体组成和选择机制是什么？
- 与 HDPO、SCOPE 等其他混合方法的关系和差异？
- 在不同任务和模型规模上的表现？

## Related
- [[on-policy-distillation]]
- [[hybrid-distillation-policy-optimization]]
- [[on-policy-distillation-survey]]
