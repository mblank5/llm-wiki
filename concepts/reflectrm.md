---
title: ReflectRM
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [reward-model, generative, self-reflection, rlhf]
sources: [raw/papers/2026/04/2604.07506.md]
---

# ReflectRM: 自反思增强的生成式 Reward Model

## 核心问题

现有 Generative Reward Models (GRMs) 只关注 outcome-level supervision，忽略了分析过程质量。

## 方法

- 统一生成框架，联合建模 **response preference** 和 **analysis preference**
- 推理时用 self-reflection 识别最可靠的分析，从中导出最终偏好预测
- 训练数据比例: preference:self-reflection = 4:1

## 结果

- Qwen3-4B 上 average accuracy +3.7
- 位置偏差 (positional bias) 改善 +10.2（相比 leading GRMs）

## 意义

- Response preference 和 analysis preference 互相增强
- Self-reflection 作为 reward model 的质量信号是新思路
- 对 RLHF pipeline 中的 RM 环节有直接改进价值

## Related

- [[reinforcement-learning-from-human-feedback]]
- [[llm-post-training-unified-view]]
