---
title: "Are Complicated Loss Functions Necessary for Teaching LLMs to Reason?"
created: 2026-05-01
updated: 2026-05-01
type: concept
tags: [rl, grpo, training, reasoning]
sources: [raw/papers/2026/03/2603.18756.md]
---

# Are Complicated Loss Functions Necessary for Teaching LLMs to Reason?

**复杂损失函数是否必要？** —— 系统性拆解 GRPO 组件，提出简化变体 RGRA 在 17/27 基准上超越 GRPO。

## Overview

GRPO (Group Relative Policy Optimization) 是当前 LLM 后训练的主流 RL 算法，结合了 group-relative advantage estimation、PPO-style clipping 和 KL regularization。本文系统性分析 GRPO 的每个组件是否必要，提出核心发现：

1. **负反馈不可或缺**：仅用正优势训练 (GRPO-pos) 会导致训练崩溃
2. **PPO-style clipping 不必要**：去掉 clipping 和 policy ratio 不损害性能
3. **Advantage estimation 至关重要**：直接用原始 reward 的 REINFORCE 也会崩溃

基于此提出 **RGRA (REINFORCE with Group Relative Advantage)**：保留 group-relative advantage 但去掉 PPO-style 约束，在 17/27 任务上超越 GRPO。

## Key Contribution / 核心创新

### RGRA: REINFORCE with Group Relative Advantage

去掉 policy ratio 和 clipping，简化为经典 REINFORCE + group advantage：

```
∇_θ J_RGRA(θ) = E[1/G Σ_i 1/|o_i| Σ_t {
    ∇_θ log π_θ(o_{i,t}|q, o_{i,<t}) * Â_{i,t}
    - β ∇_θ D_KL[π_θ || π_ref]
}]
```

关键简化：无 `r_{i,t} = π_θ/π_θ_old` ratio，无 `clip(r, 1-ε, 1+ε)` 约束。

### GRPO 组件消融分析

| 变体 | 描述 | 稳定性 | 性能 |
|------|------|--------|------|
| GRPO | 完整 (ratio + clip + advantage) | 稳定 | 基线 |
| GRPO-pos | 仅正优势 (负反馈设为0) | **崩溃** | 显著下降 |
| RGRA | 去掉 ratio/clip，保留 advantage | 稳定 | **超越 GRPO** |
| REINFORCE | 去掉 advantage，直接 reward | **崩溃** | 差 |
| RAFT | 拒绝采样 + SFT | 不稳定 | 中等 |

## Experimental Results

### Math-English Benchmarks (Avg)

| Model | Base | GRPO | RGRA | GRPO-pos | RAFT |
|-------|------|------|------|----------|------|
| Qwen2.5-0.5B | 19.8 | 25.6 | **26.5** | 17.0 | 8.7 |
| Qwen2.5-1.5B | 32.8 | 37.3 | **38.3** | 35.7 | 36.0 |
| Llama3.2-1.0B | 13.4 | **20.1** | 20.2 | 19.8 | 19.0 |

### Chinese Math Benchmarks (Avg)

| Model | Base | GRPO | RGRA | GRPO-pos |
|-------|------|------|------|----------|
| Qwen2.5-0.5B | 38.5 | 51.4 | **55.1** | 41.4 |
| Qwen2.5-1.5B | 51.9 | **65.7** | 69.3 (CMATH+CN-MS) | 65.3 |

### Key Numbers
- RGRA 在 27 个对比中 17 个超越 GRPO
- GRPO-pos 在 0.5B 模型上 20 步内训练崩溃
- RGRA 保持训练稳定性和推理行为涌现
- 0.5B + GRPO-pos: GSM8K 从 41.5 降到 35.6（崩溃）
- 0.5B + RGRA: GSM8K 从 41.5 升到 53.1

## Relation to Existing Work

- 直接简化 [[grpo]]：去掉 PPO-style clipping 不损失性能
- 与 [[ppo]] 形成对比：PPO 的 clipping 在 LLM 后训练场景中可能不必要
- 对 [[faithful-grpo]] 和 [[rl-post-training-scaling-laws]] 的启示：更简单的损失函数可能更高效
- 呼应 Ahmadian et al. (2024) "Back to Basics"：REINFORCE-style 优化在 LLM 中同样有效
- 实验基于 Qwen2.5 和 Llama3.2，模型规模较小 (0.5B-1.5B)

## Related

- [[grpo]]
- [[ppo]]
- [[faithful-grpo]]
- [[rl-post-training-scaling-laws]]
