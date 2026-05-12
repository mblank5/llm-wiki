---
title: EAGLE (Speculative Decoding)
created: 2026-05-12
updated: 2026-05-12
type: concept
tags: [inference, optimization, speculative-decoding, architecture]
sources: []
---

# EAGLE (Speculative Decoding)

## 概述
**EAGLE** 是一种 **外挂模型 (External Draft Model)** 的投机解码技术。它训练一个轻量级的 Draft Model 来“模仿”Target Model 的生成风格，从而并行生成多个候选 token，再由 Target Model 验证。

## 核心机制
-   **架构位置**：独立于 Target Model 之外，是一个单独的小模型。
-   **训练方式**：在 **后训练/微调 (Post-training)** 阶段，收集 Target Model 的 KV Cache 和 Hidden States，训练 Draft Model。EAGLE-3 更是引入了 **SpecBundle** 格式，让 Draft Model 能更高效地利用 Target 的上下文。
-   **推理方式**：
    1.  Target Model 算完 $t$，输出 KV Cache。
    2.  **Eagle Draft Model** 拿着这个 KV Cache，快速生成 $t+1, t+2, t+3$。
    3.  Target Model 并行验证这些 Draft Tokens。
    4.  **回滚机制**：如果 Target 只接受了前 2 个 Draft，框架必须把状态回滚到第 2 步，继续下一轮。

## 版本演进
-   **EAGLE-2**: 引入了更高效的 Draft Model 结构，提升了 Acceptance Rate。
-   **EAGLE-3**: 进一步优化了上下文复用，支持 SpecBundle，在 SGLang 框架中表现优异。

## 优势与劣势
| 维度 | 描述 |
| :--- | :--- |
| **优势** | **高接受率**：Draft Model 是专门训练来“猜”大模型下一步的，通常比 MTP 的接受率更高。 |
| **优势** | **灵活性**：可以针对特定的 Target Model 单独训练 Draft Model，不受 Target 预训练架构限制。 |
| **劣势** | **资源开销**：需要加载额外的模型文件，推理时多加载一个网络，占用额外显存和计算资源。 |

## 代表模型/资源
-   **Llama-3-Eagle**: 针对 Llama-3 训练的 Eagle Speculator。
-   **[[qwen3.5]]**: 目前 **不支持** Eagle3，因为 Qwen3.5 的 Hybrid Linear Attention 状态无法按 token 粒度回滚。
-   **lmsys/SGLang-EAGLE3-Qwen3-Coder-30B-A3B-Instruct-SpecForge**: 针对 Qwen3-Coder 训练的 Eagle3 Speculator。

## 相关概念
-   [[mtp]]: 另一种投机解码方法，原生内置。
-   [[speculative-decoding]]: 投机解码的通用概念。
-   [[sglang]]: 对 EAGLE 支持最好的推理框架之一。
