---
title: "TTVS: Test-Time Variational Synthesis"
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [rl, test-time, self-evolving, grpo, reasoning]
sources: [raw/papers/2026/04/2604.08468.md]
---

# TTVS: Test-Time Variational Synthesis

## 核心问题

RLVR 依赖可验证的 reward signal，在专业/新领域不可用。
现有 test-time 方法从静态 query set 学习，容易过拟合文本模式。

## 方法

两个协同模块：

1. **Online Variational Synthesis**: 将静态测试查询转化为语义等价的多样化变体流
   - 强制模型学习底层问题逻辑，而非表面模式
   
2. **Test-time Hybrid Exploration**: 平衡 accuracy-driven exploitation 和 consistency-driven exploration

基于 GRPO + self-generated reward（majority voting 产生伪标签）。

## 关键结果

- 仅用无标注 test-time 数据，**超越需要大量标注数据的 supervised RL 方法**
- MATH-500: 47.5%, AIME-2024: 23.3%, GPQA: 26.3%
- 跨 8 个模型架构有效

## 意义

开辟了 **test-time RL** 新范式：不需要标注数据，不需要预定义 reward，模型在推理时持续进化。

## Related

- [[grpo-rl-training]]
- [[llm-post-training-unified-view]]
- [[chain-of-thought]]
