---
title: AudioKV: 音频大模型 KV Cache 驱逐
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [inference, kv-cache, audio, efficiency, long-context]
sources: [raw/papers/2026/04/2604.06694.md]
---

# AudioKV: 音频 LLM 的 KV Cache 驱逐策略

## 核心问题

Large Audio-Language Models 在长音频推理时 KV cache 占用巨大。

## 方法

针对音频 token 的 KV cache eviction 策略，在保持质量的同时降低显存占用。

## 意义

长音频推理（如 40 分钟音频）的工程优化，与 [[qwen3-omni]] 的长音频处理能力相关。

## Related

- [[qwen3-omni]]
- [[qwen3-asr]]
