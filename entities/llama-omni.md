---
title: "LLaMA-Omni"
created: 2026-04-09
updated: 2026-04-09
type: entity
tags: [model, speech-model, end-to-end, open-source]
sources: []
---

# LLaMA-Omni

中科院团队基于 LLaMA-3.1-8B 构建的语音交互模型，发表于 ICLR 2025。

## 基本信息

| 属性 | 值 |
|------|-----|
| arXiv | 2409.06666 |
| 团队 | 中科院（CAS） |
| 发布 | 2024-09-10 |
| 会议 | ICLR 2025 |
| 底座 | LLaMA-3.1-8B-Instruct |

## 架构

- 语音编码器 + LLM + 语音解码器
- 流式语音输出
- 低延迟推理

## 贡献

- 早期探索如何基于开源 LLM 构建语音交互模型
- 验证了 speech adapter 方案的可行性
- ICLR 2025 接收，影响力较大

## 相关页面

- [[full-duplex-speech-model]]
- [[freeze-omni]]
- [[moshi]]
