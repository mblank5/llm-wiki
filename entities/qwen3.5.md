---
title: Qwen3.5
created: 2026-05-12
updated: 2026-05-12
type: entity
tags: [model, architecture, open-source, inference]
---

# Qwen3.5

## 概述
**Qwen3.5** 是阿里巴巴通义千问团队发布的下一代基础模型系列。首个开源权重模型为 **Qwen3.5-397B-A17B**。

## 架构创新
-   **Hybrid Linear Attention**: 融合了 Gated Delta Networks (线性注意力) 和标准 Transformer Attention。
-   **MoE (Mixture of Experts)**: 采用稀疏混合专家架构，提升计算效率。
-   **原生多模态**: 支持原生视觉语言理解。

## 推理优化支持
### MTP (Multi-Token Prediction)
-   **支持状态**: **原生内置**。Qwen3.5 在预训练时引入了 MTP Heads。
-   **当前限制**: 由于 Hybrid Linear Attention 的 `conv_states` 和 `recurrent_states` 是全局累积的，**没有 `sequence_length` 维度**，无法像传统 KV Cache 那样按 token 切片回滚。
-   **框架支持**:
    -   **vLLM**: 目前仅支持 `MTP-1` (`num_speculative_tokens=1`)。提升约 15-20% 吞吐。
    -   **SGLang**: 正在适配中。

### EAGLE (Speculative Decoding)
-   **支持状态**: **目前不支持**。
-   **原因**: Eagle 依赖 Draft Model 生成草稿后，Target Model 进行验证和状态回滚。Qwen3.5 的 Linear Attention 状态目前无法支持这种选择性回滚操作。
-   **社区进展**: SpecForge (sgl-project/SpecForge) 正在开发 Qwen3.5 的 EAGLE3/DFlash 训练适配，但尚未发布可用模型。

## 性能表现
-   **vLLM + MTP-1**: 吞吐量提升约 15-20%。
-   **SGLang + Eagle3 (Qwen3-Coder)**: 在 DGX Spark 上可达 ~60 tok/s (+38%)。

## 相关模型
-   [[qwen3]]: 上一代模型，支持 Eagle3。
-   [[qwen3-coder]]: 代码专用模型，已有 Eagle3 Speculator 可用。

## 相关技术
-   [[mtp]]
-   [[eagle-speculative-decoding]]
-   [[hybrid-linear-attention]]
