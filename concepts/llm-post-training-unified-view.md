---
title: LLM Post-Training: A Unified View of Off-Policy and On-Policy Learning
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [post-training, survey, rlhf, distillation, on-policy, off-policy]
sources: [raw/papers/2026/04/2604.07941.md]
---

# LLM Post-Training 统一视角

## 核心论点

LLM 后训练的本质是 **结构化的行为干预** (structured intervention on model behavior)，而非孤立的方法选择。论文提出按 trajectory provenance（轨迹来源）组织整个后训练领域。

## 统一框架

### 两条主线

1. **Off-policy Learning**: 在外部提供的轨迹上学习（SFT、DPO、蒸馏）
2. **On-policy Learning**: 在学习者自己生成的轨迹上学习（RLHF、RLVR、on-policy distillation）

### 三种功能角色

1. **Support Expansion (支持扩展)**: 让模型触及新的有用行为
   - SFT 可以充当此角色（当监督数据超出模型当前能力时）
   
2. **Policy Reshaping (策略重塑)**: 在已有行为范围内改善质量
   - Preference-based methods 多为 off-policy reshaping
   - On-policy RL 在 learner-generated states 上改善行为
   
3. **Behavioral Consolidation (行为巩固)**: 跨阶段/模型迁移保持行为
   - Distillation 最好理解为此角色，而非仅仅是压缩

## 对各范式的解读

| 方法 | 轨迹来源 | 功能角色 |
|------|---------|---------|
| SFT | Off-policy | Support expansion 或 Policy reshaping |
| DPO | Off-policy | Policy reshaping |
| RLHF/PPO | On-policy | Policy reshaping (+ support expansion under strong guidance) |
| RLVR | On-policy | Policy reshaping (verifiable rewards) |
| Distillation | 混合 | Behavioral consolidation |
| Hybrid pipelines | 混合 | 多角色协调组合 |

## 关键洞察

- SFT 的角色取决于 **监督数据与模型当前能力的对齐程度**
- 简单任务：SFT = policy reshaping；新能力：SFT = support expansion
- Hybrid pipeline 的必要性来自不同阶段解决不同瓶颈
- **On-policy RL 的局限**: 评估器可靠性和外部行为导入有限
- **Progress 越来越依赖协调的系统设计**，而非单一目标函数

## 与 Wiki 内容的关联

- 为 [[on-policy-distillation]] 提供了理论统一框架
- 与 [[grpo-rl-training]] 的 RL 范式形成互补
- [[strong-to-weak-distillation]] 是 behavioral consolidation 的典型实例
- [[qwen3-omni]] 的 Thinker post-training（SFT → distillation → GSPO）正是 hybrid pipeline

## Related

- [[on-policy-distillation]]
- [[grpo-rl-training]]
- [[strong-to-weak-distillation]]
- [[qwen3-omni]]
- [[reinforcement-learning-from-human-feedback]]
