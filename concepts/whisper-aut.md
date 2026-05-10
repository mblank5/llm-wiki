---
title: "Whisper-AuT: Domain-Adapted Audio Encoder"
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [audio, encoder, domain-adaptation, efficient-training]
sources: [raw/papers/2026/04/2604.10438.md]
---
# Whisper-AuT: Domain-Adapted Audio Encoder

## 核心
基于 Whisper 的领域适配音频编码器，用于高效 Audio-LLM 训练。

## 与 Qwen3-Omni AuT 的关系
- Qwen3-Omni 的 AuT 是从头训练的（2000 万小时）
- Whisper-AuT 基于 Whisper 做领域适配，数据量更小但效率更高
- 两种路线各有优劣

## Related
- [[qwen3-omni]]
- [[speech-llm]]
