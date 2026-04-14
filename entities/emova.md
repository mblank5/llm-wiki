---
title: EMOVA
created: 2026-04-15
updated: 2026-04-15
type: entity
tags: [model, multimodal, speech-model, architecture, open-source, codec]
sources: [raw/papers/2024/09/2409.18042.md]
---

# EMOVA (EMotionally Omni-present Voice Assistant)

CVPR 2025，HKUST/SenseTime 联合发布的端到端 Omni-modal LLM，首个同时在视觉-语言和语音基准上达到 SOTA 的模型。

## 核心创新

1. **Semantic-Acoustic 分离 tokenizer (S2U)**:
   - 将语音分离为语义单元（内容）和声学风格（情绪/音调）
   - 共享 codebook，在无标注 + 语音-文本对数据上训练
   - 最少数据即可将语音集成到 LLM

2. **Text-centric 对齐**:
   - 以文本为桥梁对齐视觉和语音
   - 无需三模态训练数据
   - 惊人发现: omni-modal 对齐反而**增强**了视觉-语言和语音能力

3. **Lightweight Style Module**: 轻量级情绪/音调控制模块

## 关键结果

- 同时在 VLM 和 Speech 基准 SOTA（首次）
- WER/CER: 2.9-5.8（显著优于同期 omni 模型）
- 支持情绪丰富的实时语音对话
- 7B 参数

## 局限

- 无全双工建模
- 无直接 unit-to-unit 语音生成
- 视觉生成能力有限

## 关联

- [[qwen3-omni]] — 同为 omni-modal，规模更大
- [[salmonn-omni]] — 同期 codec-free 方案
- [[speech-llm]] — Speech LLM 概念
- [[full-duplex-speech-model]] — 全双工模型格局
