---
title: Qwen3-Omni
created: 2026-04-15
updated: 2026-04-15
type: entity
tags: [model, multimodal, speech-model, architecture, open-source, streaming, codec]
sources: [raw/papers/2025/09/2509.17765.md]
---

# Qwen3-Omni

阿里 Qwen 团队 2025-09 发布的统一多模态模型，首次实现 text/image/audio/video 全模态 SOTA 且无单模态退化。

## 核心架构: Thinker-Talker MoE

| 模块 | 架构 | 参数 | 功能 |
|------|------|------|------|
| Audio Encoder (AuT) | Attention Encoder-Decoder | 650M | 从 20M 小时音频从头训练，12.5Hz token rate |
| Vision Encoder | SigLIP2-So400M | 540M | 复用 Qwen3-VL |
| Thinker | MoE Transformer | 30B-A3B | 文本生成，支持流式 |
| Talker | MoE Transformer | 3B-A0.3B | 流式语音 token 生成 |
| MTP | Dense Transformer | 80M | 多 codebook 残差预测 |
| Code2Wav | Causal ConvNet | 200M | 轻量级波形合成 |

### 关键设计决策

1. **Thinker-Talker 解耦**: Talker 不再消费 Thinker 的文本表示，仅依赖音频/视觉多模态特征。原因：
   - 文本上离散 token 和 embedding 信息等价
   - 多模态条件对语音翻译等场景必要
   - 允许外部模块（RAG、function calling、安全过滤）介入 Thinker 文本输出

2. **Multi-codebook AR 生成**: Talker 每步生成一个 codec frame，MTP 模块预测剩余残差 codebook。替代了 Qwen2.5-Omni 的 block-wise diffusion。

3. **TM-RoPE**: Time-aligned Multimodal RoPE，将位置编码分解为 temporal/height/width 三维度，temporal/height/width 分别分配 24/20/20 个旋转角度，改善长序列外推。

4. **Streaming 设计**: Chunked prefilling + MoE 架构 → Thinker 和 Talker 异步 prefilling，左上下文 multi-codebook 生成，ConvNet 实现即时波形输出。

## 性能指标

- **端到端首包延迟**: 234ms (Audio) / 547ms (Video)，单并发
- **36 个音频基准**: 开源 SOTA 32 个，总体 SOTA 22 个
- **超越**: Gemini-2.5-Pro, Seed-ASR, GPT-4o-Transcribe
- **语言支持**: 文本 119 语言，语音理解 19 语言，语音生成 10 语言
- **最长音频**: 40 分钟

## 三阶段预训练

1. **Stage 1**: 基础 encoder 对齐（音频/视觉/文本）
2. **Stage 2**: 大规模多模态数据暴露
3. **Stage 3**: 扩展序列长度，长上下文能力

## Post-training

- Thinker: 分阶段 modality-aware SFT + 蒸馏
- Talker: 高质量、上下文感知、可控语音生成训练

## 变体

- **Qwen3-Omni-30B-A3B**: 基础版
- **Qwen3-Omni-30B-A3B-Thinking**: 增强跨模态推理
- **Qwen3-Omni-30B-A3B-Captioner**: 通用音频标注，低幻觉

全部 Apache 2.0 开源。

## 关联

- [[qwen3]] — Qwen3 基础 LLM 系列
- [[qwen3-asr]] — 基于本模型的 ASR 专项模型
- [[qwen3-tts]] — 基于本模型架构的 TTS 模型
- [[full-duplex-speech-model]] — 全双工语音模型竞品格局
- [[emova]] — 同期竞品：EMOVA 情感语音助手
- [[salmonn-omni]] — 同期竞品：codec-free 全双工
- [[speech-llm]] — Speech LLM 概念
