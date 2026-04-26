---
title: "Self-Distilled RLVR: On-Policy Distillation for RL with Verifiable Rewards"
created: 2026-04-26
updated: 2026-04-26
type: concept
tags: [distillation, on-policy, rl, grpo]
sources: [raw/papers/2026/04/2604.03128.md]
---
# Self-Distilled RLVR

将 OPD 与 RLVR（Reinforcement Learning with Verifiable Rewards）结合，用大模型 teacher 为采样轨迹提供密集细粒度信号。

## 定义

Self-Distilled RLVR 融合 on-policy distillation 与 RLVR 范式，利用强 teacher 模型对采样轨迹提供 **dense fine-grained signals**，弥补 binary reward 的稀疏性。

## 核心方法

### OPD + RLVR 融合
- RLVR 依赖 verifiable rewards（如数学题正确/错误），信号稀疏
- 引入大模型 teacher 对每个采样轨迹提供**细粒度的过程级反馈**
- 在 student rollout 过程中，teacher 对每个 token 或每个推理步骤提供密集监督

### Dense Fine-Grained Signals
- Teacher 评估 sampled trajectories 的中间推理步骤
- 提供比 binary reward 更丰富的 learning signal
- 结合 KL 约束防止分布偏移过大

### 与标准 RLVR 的对比
- RLVR：sparse binary rewards（仅最终答案）
- Self-Distilled RLVR：dense token/step-level rewards（中间过程也受监督）

## 实验结果
- 在推理任务上显著优于纯 RLVR
- 训练效率提升，因为密集信号减少了无效探索
- 与 [[self-distillation-zero]] 共享"将 binary 转 dense"的核心思路

## 开放问题
- Teacher 提供的细粒度信号是否可能引入偏差（teacher 也可能犯错）？
- 在数学/代码等 verifiable domain 之外是否有效？
- 与 GRPO 的组内相对奖励如何结合？

## Related
- [[on-policy-distillation]]
- [[reasoning-distillation]]
- [[self-distillation-zero]]
