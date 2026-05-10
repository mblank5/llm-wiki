---
title: "Stream-Omni"
created: 2026-04-15
updated: 2026-04-15
type: entity
tags: [model, multimodal, speech-model, architecture, streaming, open-source]
sources: [raw/papers/2025/06/2506.13642.md]
---

# Stream-Omni

ICT/CAS 发布的 text-centric 多模态对齐框架，支持同时视觉理解和语音交互。

## 核心创新: 差异化模态对齐

- **Vision → Text**: Sequence-dimension 拼接（语义互补关系）
- **Speech → Text**: **CTC-based Layer-dimension mapping**（语义一致关系）

这一设计使 Speech 对齐**不需要大量语音数据**，能直接将文本能力迁移到语音。

## 优势

- 同时输出 ASR 转写 + 模型响应（语音交互时）
- 少量语音数据即可训练（vs [[qwen3-omni]] 的 20M 小时）
- 视觉理解: GQA 80.7%, VQA-v2 78.2%
- 语音交互: WER 3.0 (test-clean)

## 与 Qwen3-Omni 对比

| 维度 | Stream-Omni | [[qwen3-omni]] |
|------|------------|----------------|
| 语音对齐 | CTC layer-dimension | 大规模预训练 |
| 数据需求 | 少 | 20M 小时 |
| 视觉+语音 | 统一 | 统一 (更强) |
| 语音生成 | 有限 | 完整流式 |

## 关联

- [[qwen3-omni]] — 更重量级的统一方案
- [[emova]] — 同为 text-centric 对齐
- [[speech-llm]] — Speech LLM 概念
