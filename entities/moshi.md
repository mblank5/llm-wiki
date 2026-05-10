---
title: "Moshi"
created: 2026-04-09
updated: 2026-04-09
type: entity
tags: [model, speech-model, full-duplex, open-source, end-to-end]
sources: []
---

# Moshi

Kyutai 实验室于 2024 年 9 月发布的**首个实时全双工语音对话模型**。开创了多流自回归架构范式。

## 基本信息

| 属性 | 值 |
|------|-----|
| arXiv | 2410.00037 |
| 团队 | Kyutai Labs（法国） |
| 发布 | 2024-09-17 |
| 开源 | 是（kyutai/moshiko-pytorch-bf16） |
| 理论延迟 | 160ms |
| 实际延迟 | ~200ms |
| 编解码器 | Mimi（12Hz, 1.1kbps） |

## 架构

三个核心组件：
1. **Helium：** 从零训练的文本 LLM backbone（7B 参数）
2. **Mimi：** 流式神经音频编解码器，结合语义+声学信息，残差量化
3. **多流层级化 token 生成模型：** 分别建模系统语音和用户语音的并行 token 流

关键创新：将 spoken dialogue 视为 speech-to-speech generation，同时建模用户和模型两个音频流，支持重叠语音、打断和插话。

## 意义

- 首个真正意义上的实时全双工语音 LLM
- 开源，推动了全双工语音研究的爆发
- 多流架构成为后续工作的重要参考

## 相关页面

- [[full-duplex-speech-model]] - 全双工语音模型概念
- [[seeduplex]] - 字节 Seed 全双工模型
- [[freeze-omni]] - 冻结 LLM 方案
