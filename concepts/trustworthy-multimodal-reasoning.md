---
title: "The Expense of Seeing: Trustworthy Multimodal Reasoning Within Monolithic Paradigm"
created: 2026-05-01
updated: 2026-05-01
type: concept
tags:
  - multimodal
  - reasoning
  - trustworthiness
sources:
  - arxiv: "2604.20665"
  - url: "https://arxiv.org/abs/2604.20665"
  - date: 2026-04-22
---

# "看见"的代价: 在单体范式中实现可信多模态推理

**概要**: 本文系统性地挑战了当前 VLM（视觉-语言模型）忠实整合视觉与文本信息的假设。通过提出 Modality Translation Protocol 和三个量化指标（ToS / CoS / FoS），揭示了 SOTA VLM 在视觉推理中的功能性盲区。文章进一步提出 Divergence Law of Multimodal Scaling 假说和 Semantic Sufficiency Criterion（SSC），为可信多模态推理奠定理论基础。

## Overview

当前主流 VLM 架构（Vision Encoder-Projector-LLM）被广泛认为能原生整合视觉和文本信息进行推理。然而，SOTA 模型经常表现出功能性盲区——利用强大的语言先验绕过严重的视觉表征瓶颈，而非从视觉输入中提取有根据的知识。现有评估方法（如 Multimodal Gain / Leakage）基于数据消融，无法区分数据集偏差与架构缺陷。

## Key Contributions

1. **Modality Translation Protocol**: 替代数据消融的新方法论。保持语义载荷不变，仅翻译模态形式，定义三种调制：
   - S_full: 标准 VLM（视觉 + 文本）
   - S_SymT: 符号文本天花板（将图像替换为穷尽的符号文本）
   - S_SymV: 符号视觉（将文本渲染为图像内文字，强制通过视觉管道读取）

2. **三个核心指标**:
   - **ToS (Toll of Seeing)**: S_SymT − S_full，量化视觉处理造成的系统性能惩罚
   - **CoS (Curse of Seeing)**: S_SymT − S_SymV，揭示跨模态处理的非对称惩罚
   - **FoS (Fallacy of Seeing)**: S_full − S_SymV，精确定位瓶颈源头——正值指向视觉编码缺陷，负值指向跨模态投影头缺陷

3. **Semantic Sufficiency Criterion (SSC)**: 当 max(ToS, CoS, |FoS|) = 0 时，模型被认为忠实整合了多模态信息。SSC 作为诊断约束而非即时目标。

4. **Divergence Law of Multimodal Scaling**: 提出随着 LLM 骨干网络规模增长，视觉知识瓶颈的惩罚反而加剧——因为语言推理能力增长远超视觉投影头的信息带宽，导致 ToS 随参数规模扩大而增长。

5. **路线图**: 提出三支柱方案——Semantic Equivalence Engineering (SEE)、SSC 作为训练目标函数、以及 Faithful Monolithic Paradigm 架构设计。

## Experimental Results

本文为理论/框架论文，通过三个高风险领域案例研究验证了诊断工具的有效性：
- **金融时序分析**: 若 S_SymT = 95% 但 S_full = 60%，直接暴露视觉编码瓶颈
- **可信医疗诊断**: 若 S_SymT 正确但 S_full 产生幻觉诊断，暴露灾难性跨模态覆盖
- **分子图挖掘**: FoS 信号精确定位编码器 vs 投影头缺陷

## Related

- [[visual-depth-scaling]] — Divergence Law 与视觉推理能力的规模缩放规律直接相关
- [[omni-r1]] — 统一多模态推理模型同样面临视觉-文本整合的信任问题
- [[chain-of-thought]] — 可信推理需要模型在视觉和文本空间中产生可靠的推理链
