---
title: "PARM: Pipeline-Adapted Reward Model"
created: 2026-05-01
updated: 2026-05-01
type: concept
tags:
  - reward-model
  - pipeline
  - alignment
sources:
  - raw/papers/2026/04/2604.18327.md
---

# PARM: 流水线自适应奖励模型

PARM 提出面向多阶段 LLM 流水线的自适应奖励模型训练方法，利用流水线最终执行反馈自动构建偏好数据，无需人工标注即可训练出有效的阶段级奖励模型。

## Overview

现有奖励模型研究主要聚焦于单阶段文本生成任务（如 Best-of-N、Beam Search、MCTS）。然而，实际应用中 LLM 越来越多地作为流水线 (pipeline) 中的模块使用——例如，将组合优化问题分解为"问题建模"和"代码求解"两个阶段。当奖励模型用于指导多阶段流水线时，会出现**奖励不一致**问题：某阶段的奖励分数高，但最终流水线输出质量差。

PARM (Pipeline-Adapted Reward Model) 通过 Pipeline-Adapted Training (PAT) 解决此问题：利用流水线末端的任务级验证反馈作为监督信号，自动构建阶段级偏好数据集来训练奖励模型，使各阶段奖励与最终执行结果对齐。

## Key Contribution

### Pipeline Framework (两阶段实例化)

给定优化问题 $P$，流水线包含:

1. **建模阶段**: 建模生成器 $\text{LLM}_F$ 采样 $N_F$ 个候选公式 $\{F_i\}_{i=1}^{N_F}$，由建模奖励模型 $\text{RM}_F$ 评分并选最优
2. **求解阶段**: 求解生成器 $\text{LLM}_S$ 基于选中公式生成 $N_S$ 个候选解，由求解奖励模型 $\text{RM}_S$ 评分并选最优

关键: 各阶段奖励模型不是独立训练的，而是通过 PAT 方法利用**端到端执行反馈**进行自适应。

### Pipeline-Adapted Training (PAT)

PAT 的核心流程:

1. 运行流水线收集候选输出及其执行结果
2. 对于建模阶段: 如果某公式至少产生一个通过验证的解，标记为正样本；否则为负样本
3. 对于求解阶段: 直接使用执行结果（正确/错误）作为标签
4. 基于自动收集的偏好数据，用 DPO 训练各阶段奖励模型

### 扩展性分析

- 推理复杂度: $O(k \cdot N)$（贪心逐阶段选择），避免了 $O(N^k)$ 的组合爆炸
- 训练数据构建: 随阶段数增加，早期阶段的正标签依赖于后续阶段的成功，数据成本增长

## Experimental Results

### 优化任务基准

6 个数据集涵盖从高中到本科级别的 MILP/LP/NLP 优化问题:

| 数据集 | 规模 | 类型 |
|--------|------|------|
| IndustryOR | 100 | 工业 LP/MILP/非线性规划 |
| ComplexOR | 19 | 供应链/调度/物流 |
| NL4Opt | 100 | 线性规划文字题 |
| NLP4LP | 65 | 设施选址/网络流/调度 |
| Mamo Easy | 100 | 高中 MILP |
| Mamo Complex | 100 | 本科 LP/MILP |

### 模型配置

| 系列 | 建模器 | 求解器 |
|------|--------|--------|
| Qwen | Qwen2.5-Math-7B-Instruct | Qwen2.5-Coder-7B-Instruct |
| DeepSeek | deepseek-math-7b-instruct | deepseek-coder-7b-instruct-v1.5 |

奖励模型: Skywork-RM, Qwen-PRM 等

### 关键发现

- PARM 在求解准确率 (Solving Accuracy, SA) 和执行率 (Execution Rate, ER) 上均**优于直接使用 GPT-4o 和 DeepSeek-v3 的单模型基线**
- 自动训练的奖励模型**无需人工标注**即可有效指导流水线
- Self-debugging 机制进一步提升性能
- GSM8K 跨域实验验证了方法的泛化潜力

## Related

- [[free-process-rewards]] — 免标注过程奖励方法与 PARM 的自动数据构建理念一致
- [[ppo]] — PARM 可与 PPO 等 RL 算法结合用于流水线优化
- [[reinforcement-learning-from-human-feedback]] — RLHF 在多阶段流水线中的扩展
