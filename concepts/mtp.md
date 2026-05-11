---
title: Multi-Token Prediction (MTP)
created: 2026-05-12
updated: 2026-05-12
type: concept
tags: [inference, optimization, architecture, speculative-decoding]
---

# Multi-Token Prediction (MTP)

## 概述
**MTP (Multi-Token Prediction)** 是一种 **原生内置 (Native)** 的投机解码 (Speculative Decoding) 技术。与外挂的 Draft Model 不同，MTP 将预测头直接嵌入在 Transformer 的中间层中，在预训练阶段就学习预测多个未来的 token。

## 核心机制
-   **架构位置**：在 Transformer 的特定中间层（如第 4、8、12 层）挂载额外的 **MTP Heads**。
-   **训练方式**：在预训练 (Pre-training) 阶段，主 Head 预测 $t+1$，MTP Heads 预测 $t+2, t+3...$。多步预测损失加权回传，强迫中间层具备“前瞻”能力。
    $$ \mathcal{L} = \mathcal{L}_{main} + \sum_{k} \lambda_k \mathcal{L}_{mtp\_head_k} $$
-   **推理方式**：当主 Head 算完 $t$ 时，MTP Heads 已经利用中间层的特征“猜”出了后续 token。这些 Draft Tokens 不需要再走一遍完整的 Transformer 层和昂贵的 `lm_head`，只需轻量级线性投影。

## 优势与劣势
| 维度 | 描述 |
| :--- | :--- |
| **优势** | **零额外开销**：不需要加载额外的 Draft 模型，权重已包含在主模型中。显存占用极低。 |
| **劣势** | **接受率有限**：MTP Heads 与主模型共享参数，如果主模型对某段文本“没把握”，MTP Heads 通常也没把握（相关性太高）。 |
| **劣势** | **架构依赖**：需要模型在预训练时就支持，无法后训练阶段直接添加。 |

## 代表模型
-   **DeepSeek-V3**: 早期大规模应用 MTP 的代表模型。
-   **[[qwen3.5]]**: 原生支持 MTP，但由于 Hybrid Linear Attention 的状态回滚限制，目前推理框架通常只支持 MTP-1。

## 相关概念
-   [[eagle-speculative-decoding]]: 另一种主流的投机解码方法，使用外挂 Draft Model。
-   [[speculative-decoding]]: 投机解码的通用概念。
