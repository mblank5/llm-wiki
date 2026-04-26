---
title: "The Illusion of Certainty: Decoupling Capability and Calibration in OPD"
created: 2026-04-26
updated: 2026-04-26
type: concept
tags: [distillation, on-policy, rl, alignment]
sources: [raw/papers/2026/04/2604.16830.md]
---
# The Illusion of Certainty: Decoupling Capability and Calibration in OPD

Salesforce AI Research 发现 OPD 会导致严重过置信（overconfidence），提出 CaOPD 解耦能力与校准。

## 定义

该论文揭示了 OPD 中的一个关键缺陷：**能力提升伴随着校准退化**，并提出了校准感知的 OPD 变体 CaOPD。

## 核心发现

### Scaling Law of Miscalibration
- OPD 提高 accuracy 但导致**严重 overconfidence**
- 存在系统性的 scaling law：模型越大、蒸馏越强，校准退化越严重

### 根因：信息不对称
- Teacher 拥有 **privileged context**（如验证过程、中间推理步骤）
- 部署时模型只有 **deployment-time 信息**
- Teacher-conditioned success 不是有效的 deployment-time confidence 目标
- **理论证明**了这一信息不对称的根本性

### CaOPD: Calibration-Aware OPD
- 用 **student-grounded empirical confidence** 替代 self-reported confidence
- 在蒸馏过程中显式优化校准目标
- 实现 Pareto-optimal calibration + competitive capability

## 实验结果
- CaOPD 在多个 benchmark 上实现**校准-能力的 Pareto 最优**
- 保持与标准 OPD 竞争性的 accuracy
- 显著改善置信度估计的可靠性

## 开放问题
- CaOPD 的计算开销如何？
- 是否适用于 self-distillation 场景（student=teacher）？
- 校准退化是否会随训练步数累积？

## Related
- [[on-policy-distillation]]
- [[kl-divergence-in-distillation]]
- [[on-policy-self-distillation]]
