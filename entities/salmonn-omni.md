---
title: "SALMONN-omni"
created: 2026-04-15
updated: 2026-04-15
type: entity
tags: [model, speech-model, architecture, full-duplex, streaming, open-source]
sources: [raw/papers/2024/11/2411.18138.md]
---

# SALMONN-omni

Tsinghua 提出的 **Codec-free** 全双工语音理解与生成模型。

## 核心创新

1. **Codec-free 架构**: 不使用语音 codec（量化 token），直接用 embedding 处理输入/输出语音
2. **Thinking 机制**: `<start_speak>` / `<end_speak>` token 管理对话状态
3. **全双工**: 能同时听自己生成的语音和背景声音
4. **异步文本/语音生成**: 依赖 embedding 而非 codec

## 能力

- 流式语音识别
- 语音增强
- 口语问答
- Turn-taking / Barge-in / Echo Cancellation

## 与其他模型对比

| 维度 | SALMONN-omni | [[qwen3-omni]] | [[emova]] |
|------|-------------|----------------|-----------|
| Codec | **无 (embedding-based)** | Multi-codebook AR | S2U 分离 |
| 全双工 | 是 | 半双工(Thinker-Talker) | 否 |
| 延迟 | 未公布 | 234ms | 未公布 |
| 视觉 | 否 | 是 | 是 |

## 关联

- [[qwen3-omni]] — 主流 multi-codebook 方案
- [[emova]] — 同期 omni-modal
- [[full-duplex-speech-model]] — 全双工格局
- [[speech-llm]] — Speech LLM 概念
