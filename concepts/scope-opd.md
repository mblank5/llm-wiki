---
title: "SCOPE: Signal-Calibrated On-Policy Distillation Enhancement"
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [on-policy-distillation, adaptive-weighting, dual-path, reasoning]
sources: [raw/papers/2026/04/2604.10688.md]
---
# SCOPE: Signal-Calibrated OPD

## 核心改进
标准 OPD 对所有 rollout 统一应用 KL 监督，忽略了轨迹间信号质量的根本差异。SCOPE 按 **轨迹正确性** 路由到两条互补监督路径。

## 双路径框架

### 路径 1: 错误轨迹 → Teacher-Perplexity-Weighted KL
- 优先 teacher 展现真正纠正能力的样本
- 降权 teacher 也不确定的（不可靠指导）

### 路径 2: 正确轨迹 → Student-Perplexity-Weighted MLE
- 聚焦 student 低置信度样本（能力边界）
- 避免过度强化已掌握的内容

### Group-level Normalization
两组都按 prompt 组内做自适应权重标定，解决不同 prompt 难度方差。

## 结果
6 个推理 benchmark：
- Avg@32 相对提升 **11.42%**
- Pass@32 相对提升 **7.30%**
- AIME25 和 OlympiadBench 上尤其突出

## 与 Wiki 的关联
直接改进 [[on-policy-distillation]] 基础方法，与 [[entropy-aware-on-policy-distillation]] 的"动态 divergence"思路互补，但更精细（per-trajectory routing vs global entropy）。

## Related
- [[on-policy-distillation]]
- [[entropy-aware-on-policy-distillation]]
- [[llm-post-training-unified-view]]
