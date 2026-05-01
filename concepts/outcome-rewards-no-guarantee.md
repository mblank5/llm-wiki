---
title: "Outcome Rewards Do Not Guarantee Verifiable or Causally Important Reasoning"
created: 2026-05-01
updated: 2026-05-01
type: concept
tags: [rl, rlvr, reasoning, reward-model]
sources: [raw/papers/2026/04/2604.22074.md]
---

# Outcome Rewards Do Not Guarantee Verifiable or Causally Important Reasoning

**Outcome Reward 不保证推理链可验证或因果重要** —— 对 RLVR 后训练根本性质的系统性质疑与改进方案。

## Overview

RLVR (Reinforcement Learning from Verifiable Rewards) 已成为 LLM 后训练的标准范式，其核心假设是：outcome-based reward 能引导模型产生有意义的推理链。本文从根本上质疑这一假设，提出两个互补指标来衡量推理链质量：

1. **Causal Importance of Reasoning (CIR)**: 推理链是否真正因果地影响了最终答案
2. **Sufficiency of Reasoning (SR)**: 推理链是否足够自洽，使外部验证者仅凭推理链即可推导出答案

通过对 Qwen2.5 系列 (1.5B/3B/7B) 和 Llama3.2-3B 在 40 个 ReasoningGym 任务上的实验，作者发现 RLVR 虽然提升任务准确率，但 **不保证** CIR 或 SR 的提升：40 个任务中 19 个 CIR 下降，17 个 SR 下降。

## Key Contribution / 核心创新

### CIR: Causal Importance of Reasoning

对问题 q、推理链 t=(t_1,...,t_T) 和答案 y，定义前缀截断后模型预测分布的变化：

```
CIR = (1/T) * Σ_{k=1}^{T} JS(Bernoulli(p_k) || Bernoulli(p_T))
```

其中 p_k = p_φ(y|q, t_{1:k})，p_T = p_φ(y|q, t_{1:T})。CIR=0 意味着 y⊥t|q，即答案完全独立于推理链。

### SR: Sufficiency of Reasoning

通过验证者模型 θ 预测答案分布，比较有无问题的条件预测：

```
SR(q,t) = 1 if ŷ(q,t') = ŷ(t'), 0 otherwise
```

其中 t' 是去除显式答案后的推理链。SR=1 意味着推理链本身足以推导答案。

### 三个核心发现 (R1-R3)

**R1: RLVR 不保证 CIR/SR 提升**
- 40 个任务中 19 个 CIR 下降，17 个 SR 下降
- 仅在准确率提升 >50 分的任务上可靠提升 CIR/SR
- 低 CIR/SR 任务上，去掉推理链训练效果相似（平均准确率差仅 -0.053）

**R2: SFT 可修复低 CIR/SR**
- 少量专家推理轨迹 SFT (2-512 条) 即可大幅提升 CIR 和 SR
- SFT-before-RL 策略有效：先教会模型如何推理，再用 RLVR 优化

**R3: 辅助奖励可联合优化**
- 将 CIR/SR 作为辅助奖励加入 RLVR，可在保持准确率的同时提升 CIR/SR
- 无需专家轨迹数据

## Experimental Results

| Finding | Quantitative Result |
|---------|-------------------|
| CIR 下降任务比例 | 19/40 tasks |
| SR 下降任务比例 | 17/40 tasks |
| CIR-SR 与准确率不相关 | Spearman ρ=0.17, p=0.31 |
| SR 与准确率弱相关 | ρ=0.57, p=0.0001 |
| 低 CIR/SR 下推理 vs 无推理差 | ΔAcc = -0.053 |
| SFT 2 样本 CIR 提升 | 从 ≈0.05 → ≈0.25 |
| 初始-最终 CIR 相关 | Spearman ρ=0.40 |
| 初始-最终 SR 相关 | Spearman ρ=0.62 |

## Relation to Existing Work

- 与 [[free-process-rewards]] 互补：本文指出 outcome reward 的根本局限，而 process reward 是一种解决方案
- 直接挑战 [[self-distilled-rlvr]] 的假设基础：推理链质量不能被 outcome reward 隐式保证
- 对 [[rl-post-training-scaling-laws]] 的补充：scaling laws 关注准确率，本文提醒推理质量可能不随 scaling 提升
- 与 TRACE (Wang et al. 2025) 并行工作：CIR 类似但用于推理链质量评估而非 reward hacking 检测
- 呼应 Lanham et al. (2023) 的 faithfulness 发现：更高性能不代表更忠实的推理

## Related

- [[free-process-rewards]]
- [[self-distilled-rlvr]]
- [[rl-post-training-scaling-laws]]
- [[grpo]]
