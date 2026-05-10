---
title: "Freeze-Omni"
created: 2026-04-09
updated: 2026-04-09
type: entity
tags: [model, speech-model, end-to-end, company]
sources: []
---

# Freeze-Omni

腾讯团队于 2024 年 11 月发布的语音对话模型，核心创新是**保持 LLM 参数冻结**的同时实现 speech-to-speech 对话和 duplex 能力。

## 基本信息

| 属性 | 值 |
|------|-----|
| arXiv | 2411.00774 |
| 团队 | 腾讯 |
| 发布 | 2024-11-01 |
| 训练资源 | 8 GPU + 60,000 多轮文本 QA 数据 |

## 架构

- **语音输入模态：** 外接编码器，三阶段训练
- **语音输出模态：** 外接解码器
- **LLM backbone：** 参数完全冻结
- **Duplex 能力：** 通过多任务训练实现

## 核心优势

1. **避免灾难性遗忘：** LLM 参数不动，文本能力不退化
2. **训练高效：** 仅需 ASR/TTS 配对数据 + 少量多轮 QA
3. **智能保持：** 语音模态的智能水平与文本模态一致
4. **低延迟：** 端到端 spoken response

## 相关页面

- [[full-duplex-speech-model]]
- [[moshi]]
- [[llama-omni]]
- [[seeduplex]]
