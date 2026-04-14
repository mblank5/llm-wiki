---
title: Omni-Modal LLM
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [model, multimodal, speech-model, architecture, comparison, survey]
sources:
  - raw/papers/2025/09/2509.17765.md
  - raw/papers/2026/01/2601.21337.md
  - raw/papers/2024/09/2409.18042.md
  - raw/papers/2024/11/2411.18138.md
  - raw/papers/2025/06/2506.13642.md
  - raw/papers/2025/09/2509.25131.md
  - raw/papers/2026/01/2601.10323.md
  - raw/papers/2026/03/2603.09627.md
---

# Omni-Modal LLM

统一处理 text + vision + audio + speech 输入/输出的大语言模型范式。代表模型: GPT-4o, [[qwen3-omni]], [[emova]] 等。

## 架构方案对比

### 方案 1: Thinker-Talker 双轨 (主流)

| 模型 | Thinker | Talker/生成 | Codec | 流式延迟 |
|------|---------|------------|-------|---------|
| [[qwen3-omni]] | MoE 30B-A3B | MoE 3B + MTP + ConvNet | Multi-codebook RVQ | 234ms |
| [[mgm-omni]] | MLLM | SpeechLM | Token-based | ~300ms |

优势: 解耦推理与生成，可独立优化。Talker 可利用 Thinker 的高层表示。
劣势: 需要两个模块的协调训练。

### 方案 2: Codec-free Embedding 方案

| 模型 | 方法 | 特点 |
|------|------|------|
| [[salmonn-omni]] | Embedding-based | 无量化损失，全双工 |
| Stream-Omni | CTC layer mapping | 极少语音数据 |

优势: 避免量化损失，数据需求低。
劣势: 生成质量可能受限，工业部署成熟度低。

### 方案 3: Text-centric 统一对齐

| 模型 | 对齐方式 | 特点 |
|------|---------|------|
| [[emova]] | S2U + text bridge | 语义-声学分离 |
| Stream-Omni | CTC mapping | 差异化对齐 |

优势: 不需要三模态数据。
劣势: 能力上限受文本模态约束。

### 方案 4: 轻量插件式扩展

| 模型 | 方法 | 特点 |
|------|------|------|
| [[speech-omni-lite]] | 冻结 VL backbone + speech projector | 极低成本 |
| Speech-Omni-Lite | QTATS 数据构造 | 数千小时即可 |

优势: 不损害原有 VL 能力，可迁移。
劣势: 性能天花板受限于 backbone。

## 关键技术维度

### Audio Encoder

| 方案 | 训练数据 | Token Rate | 特色 |
|------|---------|-----------|------|
| [[qwen3-omni]] AuT | 20M 小时 | 12.5 Hz | 从头训练，ASR+音频理解多任务 |
| [[qwen3-asr]] AuT | 40M 小时 | 12.5 Hz | 专门 ASR 优化，动态注意力窗口 |
| Qwen-Audio | 多任务 | - | 30+ 任务，层级标签避免干扰 |
| Whisper | 680K 小时 | - | OpenAI，广泛使用 |

### Speech Codec / Tokenizer

| 方案 | Codebook 数 | Frame Rate | 延迟 |
|------|-----------|-----------|------|
| [[qwen3-omni]] Multi-codebook | 多层 RVQ | 12.5 Hz | 234ms |
| [[qwen3-tts]] 25Hz | Single | 25 Hz | ~200ms |
| [[qwen3-tts]] 12Hz | 16层 | 12.5 Hz | **97ms** |
| [[salmonn-omni]] | 无 (codec-free) | - | - |
| [[emova]] S2U | 共享 codebook | - | - |

### 语音生成方式

| 方式 | 模型 | 解码器 | 优劣 |
|------|------|--------|------|
| Multi-codebook AR | [[qwen3-omni]] | ConvNet | 高质量，可流式 |
| Block-wise Diffusion | Qwen2.5-Omni | DiT | 高质量，延迟高 |
| Embedding 直接生成 | [[salmonn-omni]] | Synthesizer | 无量化，但质量待验证 |
| Discrete Token + De-tokenizer | [[speech-omni-lite]] | CA-DiT | 轻量，可迁移 |

## 性能对比矩阵 (2024-2026)

| 模型 | 视觉-语言 | ASR (WER) | TTS 质量 | 全双工 | 延迟 | 参数 | 开源 |
|------|---------|-----------|---------|--------|------|------|------|
| [[qwen3-omni]] 30B | SOTA | SOTA | 优秀 | 半双工 | 234ms | 30B+ | Apache 2.0 |
| [[qwen3-asr]] 1.7B | - | SOTA | - | - | 92ms TTFT | 2B | Apache 2.0 |
| [[emova]] 7B | SOTA | 2.9-5.8 | 优秀 | 否 | - | 7B | 部分 |
| [[salmonn-omni]] | 否 | 优秀 | 良好 | **是** | - | - | 即将 |
| [[mgm-omni]] | 良好 | 1.8 CER | 优秀 | 否 | ~300ms | - | GitHub |
| Stream-Omni | SOTA | 3.0 | - | 否 | - | - | GitHub |
| [[speech-omni-lite]] | 保持 | 良好 | 良好 | 否 | 1346ms | 8B | - |
| ROMA | 良好 | - | - | 主动式 | - | - | - |

## 关键趋势

1. **MoE 成为标配**: [[qwen3-omni]] 和 [[mgm-omni]] 均采用 MoE 提升并发效率
2. **Codec 进化**: 从 block-wise diffusion → multi-codebook AR + ConvNet，延迟大幅降低
3. **数据规模**: Audio encoder 从百万小时级别提升到 2000 万+ 小时
4. **全双工探索**: [[salmonn-omni]] 的 codec-free 方案是一条新路
5. **模块化/插件化**: [[speech-omni-lite]] 证明数千小时即可给 VL 模型加语音能力
6. **RL for ASR**: [[qwen3-asr]] 用 GSPO (类似 GRPO) 做后训练，显著提升鲁棒性

## 开放问题

- 全双工 + 多模态理解 + 生成能否统一？(当前多为取舍)
- Codec-free vs Codec-based 最终谁胜出？
- 语音数据 scaling law 边界在哪？
- 端侧部署 (sub-1B) 的能力天花板？

## 关联

- [[speech-llm]] — Speech LLM 更广泛概念
- [[full-duplex-speech-model]] — 全双工专项
- [[qwen3]] — Qwen3 基础模型系列
- [[qwen3-omni]] / [[qwen3-asr]] / [[qwen3-tts]] — Qwen3 语音家族
