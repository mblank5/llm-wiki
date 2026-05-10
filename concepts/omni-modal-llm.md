---
title: "Omni-Modal LLM"
created: 2026-04-15
updated: 2026-04-16
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
  - raw/papers/2026/04/2604.10708.md
  - raw/papers/2026/04/2604.10949.md
  - raw/papers/2026/04/2604.08209.md
  - raw/papers/2026/01/2601.09536.md
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

### 方案 5: Frozen MLLM + Diffusion 合成 (新增)

| 模型 | 理解模块 | 生成模块 | 特点 |
|------|---------|---------|------|
| [[audio-omni]] | Qwen2.5-Omni-3B (frozen) | DiT + Rectified Flow | 理解+生成+编辑统一 |

优势: 充分利用 frozen MLLM 的语义能力，编辑能力原生支持。
劣势: 不能帧级流式，延迟高（需完整 ODE 求解）。

## 语音生成路线竞争 (2026 最新)

```
路线 A: Multi-codebook AR + ConvNet (实时交互)
├── Qwen3-Omni (234ms), Qwen3-TTS 12Hz (97ms)
├── 帧级自回归，可流式
└── 适用: 实时对话、语音助手

路线 B: Frozen MLLM + DiT / Rectified Flow (创作工具)
├── Audio-Omni (7.9B, 3.05B 可训)
├── 整体合成 + 双流条件注入
└── 适用: 音频创作、编辑、跨语言控制
```

判断: 两条路线解决不同问题，短期内不会一方取代另一方。
- 路线 A 追求"边想边说"的实时性
- 路线 B 追求"想清楚再做"的高质量+可编辑

## 关键技术维度

### Audio Encoder

| 方案 | 训练数据 | Token Rate | 特色 |
|------|---------|-----------|------|
| [[qwen3-omni]] AuT | 20M 小时 | 12.5 Hz | 从头训练，ASR+音频理解多任务 |
| [[qwen3-asr]] AuT | 40M 小时 | 12.5 Hz | 专门 ASR 优化，动态注意力窗口 |
| Qwen-Audio | 多任务 | - | 30+ 任务，层级标签避免干扰 |
| Whisper | 680K 小时 | - | OpenAI，广泛使用 |
| [[whisper-aut]] | Whisper 微调 | - | 领域适配，小数据高效 |

### Speech Codec / Tokenizer

| 方案 | Codebook 数 | Frame Rate | 延迟 |
|------|-----------|-----------|------|
| [[qwen3-omni]] Multi-codebook | 多层 RVQ | 12.5 Hz | 234ms |
| [[qwen3-tts]] 25Hz | Single | 25 Hz | ~200ms |
| [[qwen3-tts]] 12Hz | 16层 | 12.5 Hz | **97ms** |
| [[salmonn-omni]] | 无 (codec-free) | - | - |
| [[emova]] S2U | 共享 codebook | - | - |

## Pseudo-Unification: 统一的幻觉 (新增)

[[pseudo-unification-entropy]] 用信息论熵探测揭示了关键问题：

**参数共享 ≠ 信息流统一**。表面上"统一"的 UMM 存在双重分歧：

1. **Modality-Asymmetric Encoding**: 视觉和语言走不同熵轨迹（大模型对视觉过早压缩）
2. **Pattern-Split Response**: 文本生成高熵（创造），图像生成低熵（保真），两个模态的生成范式根本不同

**对 Omni 模型的启示**:
- Qwen3-Omni 的 Thinker-Talker 解耦是否也引入了 pattern-split？
- Audio-Omni 的 frozen MLLM + DiT 解耦，信息流是否真正统一？
- 真正的统一需要 contextual prediction 式的共享编码-生成逻辑（如 Harmon 模型）

**只有信息流一致，才不是伪统一。**

## RL 后训练在 Omni 上的进展 (新增)

| 方法 | 基座模型 | RL 策略 | 提升 |
|------|---------|--------|------|
| [[omnijigsaw]] | Qwen3-Omni-30B-A3B | 自监督时间重排 + GRPO | AoTBench +4.02%, MLVU +4.38% |
| [[g2rpo]] | Qwen3-Omni-30B-A3B | Gaussian OT advantage | 18 benchmark 全面提升 |
| [[omni-r1]] | Qwen2-VL | PeRPO (perception-calibrated RL) | 生成式多模态推理 |
| [[qwen3-asr]] | Qwen3-ASR-1.7B | GSPO | ASR 鲁棒性显著提升 |

**趋势**: RL 后训练从文本/视觉扩展到音频/多模态，perception-calibrated reward 成为关键创新。

## 生成式多模态推理 (新增)

[[omni-r1]] 开辟了新范式：推理过程中生成中间图像（放大、标注、辅助线）。

- 传统: 视觉输入 → 文本推理 → 文本答案
- Omni-R1: 视觉输入 → 文本+图像交错推理 → 文本答案
- Omni-R1-Zero: 从纯文本数据 bootstrap，无多模态标注也能达到同等效果

## 性能对比矩阵 (2024-2026)

| 模型 | 视觉-语言 | ASR (WER) | TTS 质量 | 音频编辑 | 全双工 | 延迟 | 参数 | 开源 |
|------|---------|-----------|---------|---------|--------|------|------|------|
| [[qwen3-omni]] 30B | SOTA | SOTA | 优秀 | - | 半双工 | 234ms | 30B+ | Apache 2.0 |
| [[qwen3-asr]] 1.7B | - | SOTA | - | - | - | 92ms | 2B | Apache 2.0 |
| [[audio-omni]] 7.9B | 良好(frozen) | - | WER 1.77 | SOTA | 否 | 高 | 7.9B | 即将开源 |
| [[emova]] 7B | SOTA | 2.9-5.8 | 优秀 | - | 否 | - | 7B | 部分 |
| [[salmonn-omni]] | 否 | 优秀 | 良好 | - | **是** | - | - | 即将 |
| [[mgm-omni]] | 良好 | 1.8 CER | 优秀 | - | 否 | ~300ms | - | GitHub |
| [[speech-omni-lite]] | 保持 | 良好 | 良好 | - | 否 | 1346ms | 8B | - |

## 关键趋势

1. **MoE 成为标配**: [[qwen3-omni]] 和 [[mgm-omni]] 均采用 MoE 提升并发效率
2. **Codec 进化**: 从 block-wise diffusion → multi-codebook AR + ConvNet，延迟大幅降低
3. **数据规模**: Audio encoder 从百万小时级别提升到 2000 万+ 小时
4. **全双工探索**: [[salmonn-omni]] 的 codec-free 方案是一条新路
5. **模块化/插件化**: [[speech-omni-lite]] 证明数千小时即可给 VL 模型加语音能力
6. **RL for Omni**: GRPO/GSPO 从文本 RLVR 扩展到音频/多模态 RL 后训练
7. **生成式推理**: [[omni-r1]] 证明推理过程本身可以是多模态的
8. **统一性的信息论审视**: [[pseudo-unification-entropy]] 揭示"参数共享 ≠ 信息统一"
9. **双路线并行**: 实时交互 (AR+ConvNet) vs 创作编辑 (Frozen MLLM+DiT) 各自深耕

## 开放问题

- 全双工 + 多模态理解 + 生成能否统一？(当前多为取舍)
- Codec-free vs Codec-based 最终谁胜出？
- 语音数据 scaling law 边界在哪？
- 端侧部署 (sub-1B) 的能力天花板？
- Omni 模型的"无退化"在信息论层面是否成立？(需要熵探测验证)
- 生成式推理 (Omni-R1) 的开销能否通过 latent reasoning 降低？

## 关联

- [[speech-llm]] — Speech LLM 更广泛概念
- [[full-duplex-speech-model]] — 全双工专项
- [[qwen3]] — Qwen3 基础模型系列
- [[qwen3-omni]] / [[qwen3-asr]] / [[qwen3-tts]] — Qwen3 语音家族
- [[audio-omni]] — 音频理解+生成+编辑统一框架
- [[omnijigsaw]] — Omni 模型 RL 后训练
- [[omni-r1]] — 生成式多模态推理
- [[pseudo-unification-entropy]] — 信息论审视统一性
- [[g2rpo]] — Gaussian GRPO for multimodal RL
