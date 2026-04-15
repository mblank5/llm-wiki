---
title: Omni-R1: 统一生成式多模态推理
created: 2026-04-16
updated: 2026-04-16
type: concept
tags: [multimodal, reasoning, rl, generative, interleaved, visual-reasoning]
sources: [raw/papers/2026/01/2601.09536.md]
---

# Omni-R1: 统一生成式多模态推理

## 核心思想

传统多模态推理是纯文本的（看图→想→输出文字）。Omni-R1 提出了 **生成式多模态推理**：在推理过程中生成中间图像（放大区域、标注框、辅助线、视觉预测），让推理本身变成多模态的。

团队：香港理工大学 + 哈工深 + 中科大（2026-01-14，被引 2 次）。

## 与传统方法的根本区别

```
传统: 视觉输入 → 文本推理链 → 文本答案
Omni-R1: 视觉输入 → 文本+图像交错推理链 → 文本答案
                        ↑
                   生成中间图像辅助推理
```

## Uni-Skills: 四种基本视觉推理操作

| Skill | 功能 | 示例 |
|-------|------|------|
| Grounding | 定位目标区域 | "找到红色三角形" |
| Auxiliary Line | 画辅助线 | 几何题画辅助线 |
| Marking | 标注物体 | 在图中标记关键特征 |
| Visual Prediction | 视觉外推 | 预测旋转后的图形 |

这些 skill 可以组合：先 grounding 再 marking，或画辅助线再做 visual prediction。

## 两阶段训练

### Stage 1: PeSFT (Perception-Aligned SFT)

联合优化两个 loss：

**Cross-Entropy Loss** (L_CE): 标准自回归 loss，学习交错推理格式

**Perception Loss** (L_Pe): 对齐图像 token 的 hidden states 与视觉 codebook
```
L_Pe = 1/|Ω| Σ ||W·h_t - E[c_t]||²
```
- E: frozen 视觉 codebook (K×D)
- h_t: 图像 token 的最后一层 hidden state
- W: 可学习投影矩阵

**总目标**: L_PeSFT = L_CE + λ·L_Pe (λ=1)

Perception Loss 的作用：稳定自回归图像 token 生成，防止图像质量崩塌。

### Stage 2: PeRPO (Perception-Calibrated Relative Policy Optimization)

Group-relative PPO，引入三类 reward：

1. **R_Acc** (Accuracy): 规则匹配最终答案（数值/符号/文本等价）
2. **R_Fmt** (Format): 轨迹格式是否合法（可解析）
3. **R_Pe** (Perception): 中间图像的感知连贯性
   - 用 2D Total Variation on codebook embeddings 衡量
   - 防止 RL 优化牺牲图像质量换取答案正确

**关键**: R_Pe 是本文最重要的创新——传统 RLVR 只看最终答案，不关心中间推理的视觉质量。

## Omni-R1-Zero: 无标注启动

从纯文本推理数据 bootstrap 视觉推理：
1. 取文本 CoT 数据
2. 用 MLLM 为每个推理步骤生成中间可视化
3. 质量过滤后作为训练数据
4. 然后用 PeRPO 优化

**结果**: Omni-R1-Zero 平均性能 **等于甚至超过** 有监督的 Omni-R1！

这意味着：多模态推理的瓶颈不是数据标注，而是推理范式本身。

## Omni-Bench

4 个 Uni-Task 评测基准：
- Math-Geometry（几何推理 + 辅助线）
- Visual-Prediction（视觉外推）
- RefCOCO-Grounding（定位 + 标注）
- MM-Math（多模态数学）

用 GPT judge 做严格的二元正确性判定。

## 实验结果摘要

- Omni-R1 在所有 Uni-Task 上超过 baseline（包括 Qwen2-VL-7B）
- Omni-R1-Zero 在 Math 和 Visual Prediction 上甚至更好
- 消融：PeRPO 的 R_Pe 对视觉质量至关重要，去掉后图像退化但答案有时仍对
- SFT → RL 的两阶段优于纯 SFT

## 与 Wiki 的关联

1. **与 [[pseudo-unification-entropy]] 的呼应**: Omni-R1 通过生成中间图像实现真正的多模态推理（不是伪统一），但图像生成仍然依赖 codebook 对齐（perception loss），说明统一需要显式约束

2. **与 [[omnijigsaw]] 的互补**: 
   - OmniJigsaw: RL 增强多模态理解（不生成中间图像）
   - Omni-R1: RL 增强多模态推理（生成中间图像辅助）
   - 两者都基于 Qwen 系列模型，但走了不同路线

3. **与 [[grpo-rl-training]] 的关系**: PeRPO 是 group-relative PPO 的变体，与 GRPO 思路类似但加入了 perception-calibrated reward

## 开放问题

- 推理时生图的开销（速度 + 计算）
- Uni-Skills 的组合爆炸（4 种 skill 的组合空间）
- Omni-R1-Zero 的 bootstrap 质量上限
- 是否可以用 latent reasoning 替代显式生图？

## Related

- [[omni-modal-llm]]
- [[omnijigsaw]]
- [[grpo-rl-training]]
- [[pseudo-unification-entropy]]
- [[multimodal-latent-reasoning]]
- [[visual-depth-scaling]]
