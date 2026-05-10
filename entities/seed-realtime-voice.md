---
title: "Seed Realtime Voice"
created: 2026-04-09
updated: 2026-04-09
type: entity
tags: [model, speech-model, end-to-end, company]
sources: [raw/articles/bytedance-seeduplex-2026-04-09.md]
---

# Seed Realtime Voice

Seeduplex 的前代模型，即豆包 App 此前使用的端到端语音模型。采用半双工（half-duplex）范式。

## 关键特征

- 半双工：严格"你讲我听、我讲你听"轮流机制
- 端到端语音模型（非级联 ASR+LLM+TTS）
- 依赖 VAD 进行机械音频分割
- 无法同时听和说

## 被替代

2026 年 4 月 9 日被 [[seeduplex]] 替代。Seeduplex 在其基础上实现全双工升级：

| 维度 | Seed Realtime Voice | Seeduplex |
|------|-------------------|-----------|
| 范式 | 半双工 | 全双工 |
| 听说 | 轮流 | 同时 |
| 抗干扰 | 依赖前端降噪 | 原生声场理解 |
| 判停 | VAD 驱动 | 语音语义联合 |
| 判停 MOS | baseline | +8% |
| 流畅度 MOS | baseline | +12% |

## 相关页面

- [[seeduplex]]
- [[full-duplex-speech-model]]
