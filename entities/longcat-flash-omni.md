---
title: "LongCat-Flash-Omni"
created: 2026-04-27
updated: 2026-04-27
type: entity
tags: [model, architecture, multimodal, speech-model, training, inference, alignment, open-source]
sources: [raw/papers/2025/11/2511.00279.md]
---

# LongCat-Flash-Omni

美团 LongCat 团队发布的全模态开源模型（arXiv 2511.00279，2025-11）。**560B 总参数，27B 激活参数**，在开源模型中达到 SOTA 级别的全模态能力，同时保持强单模态性能。

## 核心参数

- **总参数**：560B（Shortcut-connected MoE，含 zero-computation experts）
- **激活参数**：27B
- **上下文窗口**：128K tokens
- **训练数据**：2.5T+ tokens（多模态预训练）
- **开源**：HuggingFace + GitHub 全开源

## 架构设计

### 整体架构：端到端统一框架

与 Qwen3-Omni 的 Thinker-Talker 双轨不同，LongCat-Flash-Omni 采用**单 LLM Backbone 直接生成 speech tokens** 的架构：

1. **Vision Encoder**：处理图像/视频输入，支持任意宽高比和原生分辨率
2. **Audio Encoder**：将音频转换为特征 token
3. **LLM Backbone (LongCat-Flash)**：核心处理单元，直接生成 text + multi-codebook speech tokens
4. **Audio Decoder**：将 speech tokens 重建为波形（~600M 参数）

所有模块均支持**流式推理**：audio encoder、vision encoder、audio decoder 都是轻量级组件（各约 600M 参数）。

### ScMoE (Shortcut-connected MoE)

继承自 LongCat-Flash 的核心创新：
- **Zero-computation experts**：部分专家网络不参与计算，仅作为信息路由通道
- **Shortcut connection**：跨层直接连接，加速梯度传播和推理
- **效果**：在 560B 总参数下仅激活 27B，实现高效多模态融合

### 多模态融合策略：Early Fusion

- Vision 和 Audio features **chunk-wise interleaved** 后输入 LLM
- 不同于 late fusion（各模态独立编码后再拼接），early fusion 允许模态在 LLM 内部深度交互
- 支持 streaming audio-visual 输入

## 训练策略

### 多阶段渐进式预训练

从简单到复杂逐步引入模态，解决**跨模态异质性**挑战：

1. **Stage 1: Text Pretraining**：纯文本预训练底座
2. **Stage 2: Audio 引入**：逐步加入音频数据
3. **Stage 3: Visual 引入**：加入图像/视频数据
4. **Stage 4: 多模态联合训练**：平衡的多模态数据混合

### 数据管线（2.5T+ tokens）

**音频数据处理流程**：
1. VAD 分割长音频为说话片段
2. 双 ASR 模型交叉验证，过滤不一致片段
3. 多语言强制对齐（Forced Alignment），获取精确时间戳
4. 计算 speech duration / text length 比值，过滤异常（0.5~99.5 百分位）
5. 合并间隔 <10s 的相邻片段

**Speech-Text Interleaved 数据构建**：
- 将音频按标点分割为片段 `(A1,T1), (A2,T2), ...`
- 随机 mask 部分 audio 或 text 成分
- 形成如 `(T1, A2+T2, T3, A4+T4, ...)` 的交错训练样本

### 训练基础设施：模态解耦并行

针对多模态训练的数据和模型异质性，设计了**modality-decoupled parallelism scheme**：
- 文本-only 训练的 **90%+** 吞吐量保持率
- 解决多模态训练中不同模态数据长度差异大的问题

## 后训练与对齐

### 人类在环数据构建

- 针对多轮对话、时间推理、记忆能力构建专用数据
- 128K token 上下文窗口支持长程交互

### 流式交互优化

- 支持 streaming audio/video 输入 + streaming speech 输出
- 严格低延迟约束下的计算效率优化

## 性能表现

### 图像理解（vs Gemini-2.5-Flash / Qwen3-Omni）

| Benchmark | LongCat-Flash-Omni | Gemini-2.5-Flash | Qwen3-Omni |
|-----------|-------------------|-------------------|------------|
| MMBench-EN | 87.5 | 89.3 | 86.8 |
| MathVista | 77.9 | 77.1 | 75.9 |
| MMMU | 70.7 | 76.3 | 69.1 |
| BLINK (多图) | **63.1** | 56.1 | 65.0 |
| MuirBench | **77.1** | 62.1 | 74.6 |
| OCRBench | 84.9 | 85.6 | 85.5 |
| RefCOCO (Grounding) | **93.9** | 74.8 | 91.6 |

**优势领域**：多图理解、Grounding、文档理解。

### 视频理解

| Benchmark | LongCat-Flash-Omni | Gemini-2.5-Pro | Qwen3-VL |
|-----------|-------------------|----------------|----------|
| MVBench | **SOTA** | - | - |
| VideoMME w/ audio | **SOTA (Omni类)** | - | - |
| VideoMME w/o audio | **SOTA** | - | - |
| LongVideoBench | 持平 Gemini-2.5-Pro | - | - |

**关键创新**：dynamic frame sampling + hierarchical token aggregation

### 音频理解

- 在 AudioCaps、Clotho 等基准上达到或超越 Qwen3-Omni
- 支持 74+ 种语言 ASR

### 全模态 Benchmark

| Benchmark | 结果 |
|-----------|------|
| Omni-Bench | **开源 SOTA** |
| WorldSense | **开源 SOTA** |

## 与 Qwen3-Omni 的关键差异

| 维度 | LongCat-Flash-Omni | Qwen3-Omni |
|------|-------------------|------------|
| **架构** | 单 Backbone 直接生成 speech | Thinker-Talker 双轨 |
| **MoE** | ScMoE + zero-computation experts | Dense MoE |
| **参数量** | 560B (27B 激活) | 未公开 |
| **上下文** | 128K | 较短 |
| **开源** | 完全开源 | 部分开源 |
| **训练数据** | 2.5T+ tokens | 未公开 |
| **流式输入** | Chunk-wise interleaved | 双轨输入 |

## 开放问题

1. **560B 参数的高效部署**：尽管激活参数仅 27B，但 560B 总参数的存储和加载仍是挑战
2. **zero-computation experts 的理论理解**：为什么"不计算"的专家能提升性能？
3. **多模态 Scaling Law**：2.5T tokens 是否足够？更大的数据规模能否继续提升？
4. **情感理解**：与 EmoOmni 相比，LongCat 在情感对话上的能力尚未充分评估
5. **OPD 应用**：论文未明确提及 OPD，其 speech-text 交错训练本质上是一种自蒸馏

## Related

- [[qwen3-omni]] — Qwen3-Omni：Thinker-Talker 双轨架构
- [[qwen3-5-omni]] — Qwen3.5-Omni：Hybrid MoE + ARIA
- [[omni-modal-llm]] — Omni-Modal LLM 范式总览
- [[omni-model-evolution-overview]] — Omni 模型技术演进总览
- [[full-duplex-speech-model]] — 全双工语音模型
- [[speech-llm]] — Speech LLM 概念
- [[chain-of-modality]] — 动态模态编排
