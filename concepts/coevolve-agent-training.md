---
title: "CoEvolve: Training LLM Agents via Agent-Data Mutual Evolution"
created: 2026-05-01
updated: 2026-05-01
type: concept
tags: [agent, rl, training, data]
sources: [raw/papers/2026/04/2604.15840.md]
---

# CoEvolve: Agent-Data Mutual Evolution

**Agent 与训练数据共同进化** —— 闭环反馈驱动的 Agent RL 训练框架，通过遗忘/边界/稀少信号自动发现弱点并合成新任务。

## Overview

当前 LLM Agent 的 RL 训练依赖静态数据分布（人工标注轨迹或离线合成数据），无法适应 Agent 行为的动态变化，导致对复杂环境交互的覆盖不足。

**CoEvolve** 提出 Agent-数据共同进化框架：
1. 从 rollout 轨迹提取反馈信号（遗忘、边界、稀少）
2. 利用信号引导 LLM 合成针对性任务
3. 通过环境交互验证并更新训练分布

核心循环：Agent 训练 → 提取弱点信号 → 引导重探索 → 任务抽象验证 → 更新数据分布

## Key Contribution / 核心创新

### 1. 三种反馈信号

**Forgetting Signal (遗忘信号)**：
```
触发条件: ∃ s_i ∈ H_recent s.t. s_i ≥ 0.5 AND s_now < 0.5
```
Agent 之前成功但现在失败的任务。

**Boundary Signal (边界信号)**：
同一次训练迭代中，同一任务的 K 个 rollout 同时包含成功和失败轨迹。Agent 在决策边界上不稳定。

**Rare Signal (稀少信号)**：
任务在当前训练分布中出现频率极低，导致探索不足。

### 2. 信号驱动的任务合成

从信号标注的轨迹出发：
1. 按任务分组交互三元组 (action-observation pairs)
2. LLM 抽象为任务级规范 (intent + query + solution)
3. 环境执行验证任务有效性
4. 通过验证的任务加入训练集 D_t

### 3. GRPO 训练目标

```
J(θ) = (1/Σ|τ_k|) Σ_k Σ_t CLIP(r_{k,t}(θ), Â_k, ε)
       - β · D_KL[π_θ || π_ref]
```

在 GRPO 基础上加入闭环数据进化。

## Experimental Results

### 主结果

| Backbone | AppWorld TestN (TGC) | BFCL-V3 |
|---|---|---|
| Qwen2.5-7B Zero-shot | 1.19 | 13.50 |
| Qwen2.5-7B + GRPO | 26.78 | 56.00 |
| **Qwen2.5-7B + CoEvolve** | **27.98** | **61.50** |
| Qwen3-4B Zero-shot | 16.67 | 26.50 |
| Qwen3-4B + GRPO | 28.57 | 58.00 |
| **Qwen3-4B + CoEvolve** | **35.71** | **63.00** |
| Qwen3-30B-A3B Zero-shot | 31.55 | 43.50 |
| Qwen3-30B-A3B + GRPO | 48.81 | 64.00 |
| **Qwen3-30B-A3B + CoEvolve** | **54.76** | **67.00** |

### 关键数字

- 绝对提升：Qwen2.5-7B +19.43%, Qwen3-4B +15.58%, Qwen3-30B-A3B +18.14%
- 超越 GPT-4 on BFCL (63.00 vs 54.00)
- 超越 Gemini-2.5-Flash on BFCL (63.00 vs 41.50)
- AppWorld Challenge split: +23.21 / +21.43 (TGC/SGC) for Qwen3-30B-A3B

### 消融实验 (Qwen3-4B)

| 阶段 | AppWorld | BFCL | Avg |
|------|----------|------|-----|
| Zero-shot baseline | 16.67 | 26.50 | 21.59 |
| + Synthetic Data | 28.57 | 58.00 | 43.29 |
| + Random Exploration | 30.36 | 60.50 | 45.43 |
| + Feedback (CoEvolve) | **35.71** | **63.00** | **49.36** |

### 信号消融
- 去掉遗忘信号：49.36 → 45.18 (最大降幅)
- 去掉稀少信号：49.36 → 47.21
- 去掉边界信号：49.36 → 47.17
- 信号分布：边界信号最多 (AppWorld 51.4%, BFCL 45.5%)

### 效率
- 反馈阶段仅占总训练时间 ~10%
- AppWorld: +22.92% 相对提升 for ~10% 额外计算

## Relation to Existing Work

- 与 [[ragegen-multi-turn-rl-agents]] 互补：CoEvolve 关注数据进化，而非多轮交互策略
- 区别于 [[agent-r1-end-to-end-rl]]：不依赖端到端 RL，而是在 GRPO 基础上加闭环数据进化
- 超越 [[ml-agent-autonomous-ml]] 的静态数据方法：反馈驱动的自适应数据生成
- 与 ReAct/Reflexion 不同：不是 prompting 策略，而是训练时数据分布优化
- 跨域迁移：AppWorld 训练 → BFCL zero-shot 从 26.50 提升到 45.00

## Related

- [[ragegen-multi-turn-rl-agents]]
- [[agent-r1-end-to-end-rl]]
- [[ml-agent-autonomous-ml]]
