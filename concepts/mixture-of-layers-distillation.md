---
title: "Mixture-of-Layers Distillation with Stepwise Attention on Key Information"
created: 2026-05-01
updated: 2026-05-01
type: concept
tags: [distillation, mixture-of-experts, reasoning]
sources: [raw/papers/2026/04/2604.15701.md]
---

# Mixture-of-Layers Distillation with Stepwise Attention (MoLSAKI)

**逐步注意力蒸馏 + 混合层对齐** —— 首次将教师模型的逐步注意力模式迁移至学生模型，通过 MoL 动态层映射突破蒸馏中的架构差异限制。

## Overview

现有 CoT (Chain-of-Thought) 蒸馏方法主要迁移教师模型生成的推理文本，但忽略了教师在推理过程中对关键信息的 **动态注意力变化**。本文发现：

1. 语言模型在推理过程中对关键 token（如数学推理中的数字 token）展现出 **渐进式注意力转移**
2. 这种逐步注意力模式隐式编码了推理的关键线索
3. 传统方法未能将此模式迁移给学生模型

基于此提出 **MoLSAKI** 框架：
- 提取并迁移教师模型对关键 token 的逐步注意力
- 设计 Mixture-of-Layers (MoL) 模块实现自适应层对齐
- 不要求 teacher-student 共享 tokenizer 或词表

## Key Contribution / 核心创新

### 1. Stepwise Attention on Critical Tokens

对教师模型第 l 层的 self-attention 矩阵 I^t_l，提取推理步骤集合 M_1 中每个步骤对关键 token 集合 M_2 的聚合注意力：

```
A^t_l = Σ_{i∈K, j∈P} I^t_l[i,j]  (K ∈ M_1, P ∈ M_2)
```

其中 A^t_l ∈ R^{|M_1| × |M_2|}，|M_1| 为推理步骤数，|M_2| 为关键 token 数。

### 2. Mixture-of-Layers (MoL) 自适应层对齐

**教师端**：基于逐步注意力梯度加权，中间层权重最大：
```
G(A^t_l) = mean column gradient of A^t_l
p^t = softmax([G(A^t_1), ..., G(A^t_{L1})], τ_1)
```

**学生端**：可学习路由机制：
```
h_l = Σ_i RMSNorm(V_l)[i,:]
H = concat(h_1, ..., h_{L2})
p^s = softmax(WH + b, τ_2)
```

### 3. 总损失函数

```
L = α·L_pre + (1-α)·L_exp + β·L_att
```

- L_pre: 答案预测损失
- L_exp: 推理生成损失
- L_att: 逐步注意力 KL 散度损失

## Experimental Results

### 主实验结果 (Accuracy %)

| Teacher → Student | SVAMP (ID) | SingleEq (OOD) | AsDiv (OOD) | GSM8K (OOD) | CSQA (ID) |
|---|---|---|---|---|---|
| Llama3-8B → GPT2-Large | | | | | |
| Vanilla Finetune | 10.0 | 12.1 | 9.2 | 4.2 | 16.7 |
| DSS | 48.0 | 36.1 | 30.3 | 12.4 | 19.1 |
| MMIloss | 47.0 | 37.9 | 30.7 | 12.5 | 19.4 |
| **MoLSAKI** | **49.5** | **39.8** | **32.2** | **15.1** | **21.0** |
| Qwen2.5-32B → TinyLlama-1.1B | | | | | |
| Vanilla Finetune | 14.5 | 21.4 | 14.3 | 6.7 | 17.8 |
| DSS | 59.5 | 48.1 | 33.5 | 13.8 | 28.9 |
| MMIloss | 64.5 | 48.1 | 42.6 | 14.0 | 25.8 |
| **MoLSAKI** | **68.5** | **51.8** | **43.3** | **16.9** | **30.3** |

### 关键数字
- 相对基线平均提升：7.5% (GPT2-Large), 11.3% (TinyLlama)
- MoL 自适应层对齐 (37.5 avg) 显著优于最优单层映射 (35.8 avg)
- 跨模型配置下 MoLSAKI 一致优于基线 (5.1% 和 7.9% 相对提升)
- 支持异构蒸馏：可用 PaLM-540B 生成 rationale + Llama3-8B 提取注意力

### 超参数设置
- β (注意力损失权重) = 1.0
- τ_1 (教师温度) = 0.1, τ_2 (学生温度) = 0.5
- α = 0.5

## Relation to Existing Work

- 区别于传统 [[mixture-of-experts]] 的 MoE 路由：MoL 路由的是层而非专家
- 创新的 [[reasoning-distillation]] 方法：首次关注逐步注意力而非仅文本
- 与 [[strong-to-weak-distillation]] 一致：大模型 → 小模型推理能力迁移
- 突破 [[knowledge-distillation]] 的层对齐限制：MoL 动态加权替代固定层映射
- 不要求 teacher-student 共享 tokenizer，增强了实用性

## Related

- [[mixture-of-experts]]
- [[reasoning-distillation]]
- [[strong-to-weak-distillation]]
- [[knowledge-distillation]]
