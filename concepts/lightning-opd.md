---
title: "Lightning OPD: Offline On-Policy Distillation"
created: 2026-04-26
updated: 2026-04-26
type: concept
tags: [distillation, on-policy, rl, optimization]
sources: [raw/papers/2026/04/2604.13010.md]
---
# Lightning OPD: Offline On-Policy Distillation

NVIDIA 团队（Song Han, Han Cai）提出的离线 OPD 变体，通过预计算 teacher log-probabilities 消除实时推理开销，实现 4 倍加速。

## 定义

Lightning OPD 将标准 OPD 中的在线 teacher 推理替换为**预计算的 teacher log-probabilities**，在 SFT rollouts 上离线蒸馏，无需 live teacher server。

## 核心发现

### Teacher Consistency 条件
- **SFT teacher 和 OPD teacher 必须是同一模型**
- 违反 teacher consistency 会导致**不可约的梯度偏差**（irreducible gradient bias）
- 偏差使训练收敛到**次优固定点**（suboptimal fixed point）
- 这是之前 OPD 文献中未被系统认识的关键约束

### Lightning OPD 方法
- 预计算 teacher log-probabilities over SFT rollouts
- 训练阶段无需 teacher 模型参与，消除实时推理开销
- **理论证明**：在 teacher consistency 下，Lightning OPD 与标准 OPD 有相同的最优点

### 计算优势
- 消除实时 teacher forward pass 的开销
- 支持离线数据预处理和缓存

## 实验结果
- **Qwen3-8B-Base + Lightning OPD → AIME 2024: 69.9%**
- 仅 **30 GPU hours** 训练
- 相比标准 OPD 实现 **4 倍 speedup**
- 保持相同最优解（teacher consistency 条件下）

## 开放问题
- Teacher consistency 条件是否过于严格？部分不一致是否可容忍？
- 预计算 log-probabilities 在多轮 self-improvement 场景下如何迭代更新？
- Lightning OPD 能否应用于 teacher-student 不同架构的场景？

## Related
- [[on-policy-distillation]]
- [[on-policy-distillation-survey]]
- [[reasoning-distillation]]
