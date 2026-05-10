---
title: "Qwen3 语音家族深度解析"
created: 2026-04-15
updated: 2026-04-15
type: query
tags: [model, multimodal, speech-model, architecture, comparison, survey, codec, training]
sources:
  - raw/papers/2025/09/2509.17765.md
  - raw/papers/2026/01/2601.21337.md
  - raw/papers/2026/01/2601.15621.md
  - raw/papers/2023/11/2311.07919.md
  - raw/papers/2026/01/2601.04720.md
---

# Qwen3 语音家族深度解析

## 家族树

```
Qwen3 (基础 LLM)
├── Qwen3-VL (视觉-语言)
│   └── Qwen3-VL-Embedding / Qwen3-VL-Reranker (多模态检索)
└── Qwen3-Omni (text+image+audio+video 统一)
    ├── Qwen3-ASR-1.7B / 0.6B (多语言 ASR)
    ├── Qwen3-ForcedAligner-0.6B (NAR 时间戳对齐)
    └── Qwen3-TTS (双轨 TTS)
```

## 技术传承链

### Audio Encoder: AuT 的演进

1. **Qwen-Audio (2023-11)**: Whisper-based encoder，多任务层级标签训练，30+ 任务
2. **Qwen2.5-Omni (2025-06)**: 过渡版本，block-wise diffusion 语音生成
3. **Qwen3-Omni AuT (2025-09)**: 从头训练 AED 模型，20M 小时，12.5Hz
4. **Qwen3-ASR AuT (2026-01)**: 扩展到 40M 小时，增强 ASR 专项
5. **Qwen3-TTS Tokenizer (2026-01)**: 独立 tokenizer，25Hz/12Hz 双轨

### 语音生成: 从 Diffusion 到 ConvNet

| 版本 | 生成方式 | 解码器 | 延迟 |
|------|---------|--------|------|
| Qwen2.5-Omni | Block-wise AR | DiT | 高 (需等待 block) |
| Qwen3-Omni | Multi-codebook AR + MTP | ConvNet | 234ms |
| Qwen3-TTS (12Hz) | 16层 Multi-codebook | ConvNet | **97ms** |

关键转变: 用 multi-codebook 的表征能力替代复杂的 DiT，换取延迟和算力的大幅降低。

### 训练方法论: RL 进入 ASR

[[qwen3-asr]] 是首个在 ASR 后训练中引入 RL (GSPO) 的工作:
- 50K 条语音（35% 中英 + 35% 多语言 + 30% 功能数据）
- 显著提升噪声鲁棒性和疑难 case 处理
- 与 [[qwen3]] 主系列的后训练 RL (GRPO) 形成方法论呼应

## 竞品定位

| 维度 | Qwen3-Omni | Gemini-2.5-Pro | GPT-4o | Seed-ASR |
|------|-----------|----------------|--------|----------|
| 开源 | 是 | 否 | 否 | 否 |
| 多模态 | text+image+audio+video | text+image+audio+video | text+image+audio+video | audio only |
| ASR | SOTA (开源) | 强 | 强 | 强 |
| 语音生成 | 流式 234ms | - | - | - |
| 语言覆盖 | 119/19/10 | 广 | 广 | 有限 |

## 论文引用矩阵

| 论文 | 引用 | 日期 |
|------|------|------|
| Qwen3-Omni | 119 | 2025-09 |
| Qwen3-VL-Embedding | 26 | 2026-01 |
| Qwen3-TTS | 10 | 2026-01 |
| Qwen3-ASR | 4 | 2026-01 |
| Qwen-Audio | 567 | 2023-11 |

## 关联

- [[qwen3]] — 基础模型
- [[qwen3-omni]] / [[qwen3-asr]] / [[qwen3-tts]] — 各模型详情
- [[omni-modal-llm]] — Omni-Modal LLM 统一概念
- [[full-duplex-speech-model]] — 全双工格局
- [[seeduplex]] — 字节全双工竞品
