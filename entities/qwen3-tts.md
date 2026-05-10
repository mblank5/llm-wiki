---
title: "Qwen3-TTS"
created: 2026-04-15
updated: 2026-04-15
type: entity
tags: [model, speech-model, open-source, codec, streaming, architecture]
sources: [raw/papers/2026/01/2601.15621.md]
---

# Qwen3-TTS

阿里 Qwen 团队 2026-01 发布的多语言、可控、流式 TTS 模型家族。基于 Qwen3 LLM 系列。

## 双轨架构

### Tokenizer 方案

| 方案 | Token Rate | Codebook | 解码器 | 首包延迟 | 定位 |
|------|-----------|----------|--------|---------|------|
| Qwen-TTS-Tokenizer-25Hz | 25 Hz | Single-codebook | Block-wise DiT | ~200ms | 高质量、语义保真 |
| Qwen-TTS-Tokenizer-12Hz | 12.5 Hz | 16层 Multi-codebook | Causal ConvNet | **97ms** | 超低延迟流式 |

### 核心创新

- **Semantic-Acoustic 分离**: 12Hz 版本用语义优先编码 + 声学细节分离，实现极端低码率
- **Dual-track LM**: 同一模型支持两种 tokenizer 方案切换
- **自然语言控制**: 支持描述式语音风格控制（情绪、音调等）
- **3秒语音克隆**: SOTA 级 zero-shot voice cloning

## 性能

- **训练数据**: 500 万+ 小时，10 种语言
- **Voice Cloning WER**: Seed-TTS 基准上最低
- **跨语言鲁棒性**: 中→韩等跨语言场景稳定
- **流式生成**: 全程支持实时流式合成

Apache 2.0 开源（模型 + 两种 tokenizer）。

## 关联

- [[qwen3-omni]] — 共享架构思想的姊妹模型
- [[qwen3-asr]] — ASR 姊妹模型
- [[seed-tts]] — 竞品：Seed-TTS
- [[speech-llm]] — Speech LLM 概念
