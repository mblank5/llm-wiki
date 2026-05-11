---
title: MTP vs EAGLE
created: 2026-05-12
updated: 2026-05-12
type: comparison
tags: [comparison, inference, optimization]
---

# MTP vs EAGLE

## 概述
MTP (Multi-Token Prediction) 和 EAGLE 都是主流的 **投机解码 (Speculative Decoding)** 技术，旨在通过预测多个 token 来加速 LLM 推理。它们的核心区别在于 **“内生 (Internal)”** 与 **“外挂 (External)”**。

## 核心对比

| 维度 | MTP (Multi-Token Prediction) | EAGLE (Speculative Decoding) |
| :--- | :--- | :--- |
| **本质** | **原生内置** (Native) | **外挂模型** (External Draft Model) |
| **训练阶段** | **预训练 (Pre-training)** | **后训练/微调 (Post-training)** |
| **架构位置** | 嵌入在 Transformer 中间层 | 独立于 Target Model 之外 |
| **计算方式** | 复用前向传播的中间 Hidden States | 复用 Target Model 的 KV Cache |
| **资源开销** | **零额外开销** (权重已包含) | 需加载额外 Draft 模型 (占 VRAM) |
| **接受率** | 中等 (与主模型高度相关) | 高 (专门训练模仿 Target) |
| **灵活性** | 低 (需模型预训练时支持) | 高 (可针对任意 Target 训练) |

## 技术深度
### MTP 的“直觉”
MTP 的核心思想是 **不要只预测下一个 token，让中间层同时预测后面几个 token**。
-   **优势**: 推理时几乎不增加显存，因为不需要加载额外模型。
-   **劣势**: 如果主模型对某段文本“没把握”，MTP Heads 通常也没把握，导致 Acceptance Rate 提升有限。

### EAGLE 的“速记员”
EAGLE 的核心思想是 **训练一个专门的小模型，让它学会“模仿”大模型的生成风格**。
-   **优势**: Draft Model 是专门训练来“猜”大模型下一步的，Acceptance Rate 通常远高于 MTP。
-   **劣势**: 需要额外的模型文件，推理时多加载一个网络，占用额外显存。

## 适用场景
| 场景 | 推荐方案 | 原因 |
| :--- | :--- | :--- |
| **Qwen3.5 27B/35B** | **MTP-1** | 原生支持，零成本，目前唯一稳定方案。 |
| **Llama-3 / Qwen2.5** | **Eagle-3** | 这些模型是标准 Transformer，Eagle 接受率高，加速比可达 2x-3x。 |
| **追求极致吞吐** | **SGLang + Eagle** | 只要模型支持，Eagle 的加速效果通常优于 MTP。 |
| **显存极度受限** | **MTP** | 不需要加载额外的 Eagle 模型权重。 |

## 相关页面
-   [[mtp]]
-   [[eagle-speculative-decoding]]
-   [[qwen3.5]]
