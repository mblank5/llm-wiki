---
title: "MGM-Omni"
created: 2026-04-15
updated: 2026-04-15
type: entity
tags: [model, multimodal, speech-model, architecture, streaming, codec]
sources: [raw/papers/2025/09/2509.25131.md]
---

# MGM-Omni

CUHK/JiaLiab 发布的 "Brain-Mouth" 双轨 Omni LLM，专注长音频理解和个性化语音生成。

## 核心架构

- **Brain (MLLM)**: 多模态推理（文本+音频）
- **Mouth (SpeechLM)**: 实时语音合成
- **Dual Audio Encoder**: 通用音频 + 语音编码器

## 关键创新

- **Chunk-based Parallel Decoding**: 缓解文本-语音 token rate 差异，推理加速 3x
- **Zero-shot Voice Cloning**: 流式场景下长时间保持 timbre 一致
- **长音频理解**: 支持 60+ 分钟音频输入
- **数据高效**: 训练数据量显著少于同类

## 性能

- AISHELL CER: 1.8
- DocVQA-Speech: 87.4%
- 长音频处理: 4500s 成功率高
- timbre 稳定性优于开源竞品

## 关联

- [[qwen3-omni]] — 同期双轨架构 (Thinker-Talker)
- [[qwen3-asr]] — ASR 性能对比
- [[speech-llm]] — Speech LLM 概念
- [[full-duplex-speech-model]] — 全双工格局
