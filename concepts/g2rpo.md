---
title: "Gaussian GRPO (G2RPO)"
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [rl, grpo, post-training, multimodal, reward-shaping]
sources: [raw/papers/2026/04/2604.08539.md]
---

# G2RPO: Gaussian GRPO

## 核心问题

GRPO 在多模态多任务 RL 中存在 **reward topology 方差极大** 的问题：
- 不同视觉任务的 reward 分布差异巨大（OCR vs 空间推理 vs 数学）
- 线性 advantage normalization 无法消除任务间的梯度不公平
- Heavy-tail outliers 导致训练不稳定

## 方法

用 **1D Optimal Transport** 替换标准线性 scaling，强制 advantage 分布 → N(0,1)：
- 非线性 distributional matching
- 理论保证 inter-task gradient equity
- 对 heavy-tail outliers 鲁棒
- 正负 reward 对称更新

### 两个 Task-level Shaping 机制

1. **Response Length Shaping**: 
   - 复杂查询 → 激发长推理链
   - 简单查询 → 强制直接输出（强化 grounding）
   
2. **Entropy Shaping**:
   - 紧密约束探索区域
   - 防止 entropy collapse 和 explosion

## 实验结果

基于 Qwen3-Omni-30B-A3B 训练，18 个 benchmark：
- DocVQA: 96.7%
- OCRBench: 911
- InfoVQA: 86.4%
- 超越 Qwen3-VL-Instruct 和其他开源/闭源 baseline

## 与标准 GRPO 的区别

| 维度 | GRPO | G2RPO |
|------|------|-------|
| Advantage normalization | Linear (z-score) | Non-linear (Optimal Transport → Gaussian) |
| Task fairness | No guarantee | Inter-task gradient equity |
| Outlier robustness | Weak | Strong |
| Symmetric updates | Not guaranteed | Yes (N(0,1)) |

## Related

- [[grpo-rl-training]]
- [[llm-post-training-unified-view]]
- [[omni-modal-llm]]
- [[qwen3-omni]]
