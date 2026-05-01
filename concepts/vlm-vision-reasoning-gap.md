---
title: "Do Vision-Language Models Truly Perform Vision Reasoning?"
created: 2026-05-01
updated: 2026-05-01
type: concept
tags:
  - multimodal
  - vision
  - reasoning
sources:
  - arxiv: "2604.16256"
  - url: "https://arxiv.org/abs/2604.16256"
  - date: 2026-04-17
---

# VLM 是否真正执行了视觉推理? ——模态差距的严格研究

**概要**: 本文通过构建 CrossMath 基准——一个支持 text-only / image-only / image+text 三种严格等价输入格式的多模态推理数据集——系统性地揭示了 VLM 在视觉推理上的根本不足。实验发现 SOTA VLM 在文本输入下表现优异，但加入视觉数据后性能反而下降。通过 SFT+GRPO 后训练可有效缓解此差距。

## Overview

现代 VLM 建立在视觉编码器 + 跨模态投影器 + 预训练文本解码器的标准化管道之上。尽管在多模态基准上表现亮眼，但一个核心问题悬而未决：这些模型是真正在进行视觉推理，还是仅仅利用文本骨干的推理能力？现有基准要么只评估表面级视觉识别，要么视觉和文本输入纠缠在一起无法分离模态贡献。

## Key Contributions

1. **CrossMath 基准**: 基于二维交叉数学方程网格的多模态推理数据集，满足三个核心原则：
   - **视觉优先**: 求解需要空间几何理解和多步逻辑推导
   - **难度分层**: Easy / Medium / Hard 三级，通过网格大小、缺失方程数和算子复杂度控制
   - **严格跨模态等价**: 每个问题提供 text-only（Markdown 表）、image-only（网格图）和 image+text 三种格式，确保任务相关信息完全一致

2. **模态差距的系统性揭示**: 对 SOTA VLM 的广泛评估发现一致性现象——文本输入表现最佳，加入视觉数据后性能下降，纯视觉输入表现最差。例如 Qwen3.5-Plus 的 Macro Accuracy 从 text-only 的 92.80% 降至 image-only 的 12.40%。

3. **有效的后训练方案**: 使用 image-only 数据进行 SFT + GRPO 后训练：
   - SFT 将 Micro Accuracy 从 23.25% 提升至 59.52%（image-only）
   - GRPO 进一步提升至 62.33%，并在外部视觉数学任务上展现鲁棒泛化

4. **关键发现**:
   - 视觉推理失败主要不是感知错误——OCR 错误率极低，问题在于结构化推理
   - 推理深度是核心瓶颈——随逻辑跳数增加，准确率急剧下降
   - 后训练虽大幅提升但仍未完全闭合模态差距，暗示架构层面的根本限制

## Experimental Results

- **测试集**: 250 核心 CrossMath 实例（4 种视觉风格扩展至 1000 评测样本）+ 5000 训练样本
- **Zero-shot 结果**: 所有模型在 text-only >> image+text >> image-only 的趋势一致
- **后训练**: Qwen3.5-9B-SFT+GRPO 在 image-only 的 Macro Acc 从 3.20% 升至 50.40%，text-only 从 44.00% 升至 76.40%
- **泛化**: 后训练在外部视觉数学基准上也取得一致提升

## Related

- [[visual-depth-scaling]] — CrossMath 的推理深度分析直接关联视觉推理的规模效应
- [[chain-of-thought]] — CrossMath 提供逐步推理标注，支持对 CoT 质量的细粒度评估
- [[omni-r1]] — 统一多模态推理模型需要解决本文揭示的视觉-文本推理差距
