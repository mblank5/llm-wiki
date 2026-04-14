---
title: LLM Training as Lossy Compression
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [pretraining, information-theory, compression, information-bottleneck]
sources: [raw/papers/2026/04/2604.08348.md]
---

# LLM 训练即有损压缩

## 核心论点

LLM 预训练本质是 **有损压缩** (lossy compression)，训练数据的相关信息被保留，无关信息被丢弃。
模型收敛到 Information Bottleneck bound。

## 两阶段模式

1. **Expansion phase**: 增加输出信息（拟合训练数据）
2. **Compression phase**: 压缩输入信息（泛化/遗忘细节）

这一模式在不同模型规模和架构中一致。

## 关键发现

- 75 个开源模型均接近 Information Bottleneck 理论边界
- Loss 饱和时模型进入 compression phase
- **Post-training 增加偏好信息**（pre-training 建立语义核心，post-training 添加任务偏好）
- 推理/知识 benchmark 性能由最优压缩质量驱动
- 指令遵循性能由 post-training 偏好信息驱动

## 意义

从信息论角度解释了 pre-training 和 post-training 的分工。

## Related

- [[llm-post-training-unified-view]]
- [[knowledge-distillation]]
