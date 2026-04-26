---
title: "Qwen3.5-Omni"
created: 2026-04-26
updated: 2026-04-26
type: entity
tags: [model, architecture, multimodal, speech-model, training, on-policy, distillation]
sources: [raw/papers/2026/04/2604.15804.md]
---

# Qwen3.5-Omni

Qwen Team 发布的最新 Omni 模型（arxiv 2604.15804，2026-04-17/21），Qwen-Omni 家族的重大演进。相比 [[qwen3-omni]]，在规模、对齐、实时交互上有全面升级。

## 关键参数

- **规模**：数千亿参数（Hybrid MoE 架构）
- **上下文长度**：256k tokens
- **音频理解**：支持 10+ 小时连续音频
- **视频理解**：400 秒 720P（1 FPS）
- **多语言**：文本 201 种语言/方言，语音输入 74 种语言 + 39 种中文方言，语音输出 29 种语言 + 7 种中文方言
- **变体**：Qwen3.5-Omni-Plus 和 Qwen3.5-Omni-Flash

## 架构：Thinker-Talker

延续 [[qwen3-omni]] 的 Thinker-Talker 双轨架构，但有重大改进：

### 核心改进

1. **Hybrid MoE  backbone**：Thinker 和 Talker 均采用 Hybrid Attention Mixture-of-Experts 设计，提升扩展性，平衡多模态理解和生成的容量与效率
2. **统一多模态输入**：音频和视频 interleaved 输入，显式插入 timestamp 提升时间感知（替代 TMRoPE）
3. **ARIA (Adaptive Rate Interleave Alignment)**：替代 Qwen3-Omni 的 dual-track Talker input，动态对齐 text 和 speech units 后再 interleaving，解决 tokenizer 速率不匹配导致的跳词、错读、数字渲染模糊等问题
4. **RVQ-based speech representation**：继承自 Qwen3-Omni，大幅提升推理效率
5. **Chunk-wise streaming**：Thinker 分块流式输入 + Talker 流式设计，实现超低延迟端到端对话

### 延迟指标

| 指标 | Plus | Flash |
|------|------|-------|
| First-Packet Latency (Audio) | 435ms | 235ms |
| First-Packet Latency (Video) | 651ms | 426ms |

### AuT 音频编码器

- 从头训练的 Transformer-based attention-encoder-decoder
- 40M 小时音频-文本对训练（Qwen3-ASR 生成）
- 4 层 Conv2D 下采样 16 倍 → 6.25Hz token rate
- 支持 20+ 种语言，中:英:多语言 = 3.5:3.5:3
- Dynamic attention window size training

## 预训练（三阶段）

1. **Encoder Alignment (S1)**：LLM 参数来自 Qwen3.5 锁定，单独训练 vision encoder（来自 Qwen3.5）和 audio encoder（AuT），先训 adapter 再训 encoder
2. **General Stage (S2)**：~4T tokens，全参数训练，32,768 seq length
   - 文本 0.92T、音频 1.99T、图像 0.95T、视频 0.14T、视频-音频 0.29T
3. **Long Context (S3)**：seq length 提升至 262,144，增加长音频/长视频数据比例

### Temporal Positioning 改进

Qwen3-Omni 用 TMRoPE 做时间感知，但有两个问题：
- 长音频/视频导致位置 ID 过大过稀疏
- 需要多帧率均匀采样数据，成本高

Qwen3.5-Omni 改用 **显式 timestamp**：在视频/音视频 temporal patch 前插入秒级格式化文本字符串，音频随机间隔插入 timestamp。

## 后训练

### Thinker（三阶段）

1. **Specialist Distillation**：从 Qwen3.5 基座独立 SFT + RL 训练各领域 teacher（文本、视觉、音频），再蒸馏到统一模型
2. **[[on-policy-distillation]]**（OPD）：用 text-conditioned 高质量 response 作为 audio-conditioned query 的蒸馏目标，缩小音频/文本输入下的响应质量差距
3. **Interaction-Aligned RL**：针对多轮对话中的语言切换、persona 不一致、长上下文指令跟随退化问题，用 RL 优化交互质量

### Talker（四阶段）

1. **General**：20M+ 小时多语言语音数据 + 多模态上下文
2. **Long-Context**：数据质量分层 + CPT，扩展到 64k context
3. **RL**：DPO（多语言偏好对）+ GSPO（rule-based rewards）
4. **Speaker Fine-tuning**：voice cloning 和个性化语音生成

## 性能亮点

### ASR（FLEURS test）
- Qwen3.5-Omni-Plus：平均 WER 6.6%，超越 Gemini-3.1 Pro（7.3%）和 GPT-4o-Transcribe（10.4%）
- 粤语 2.2% vs Gemini 6.3%（大幅领先）
- Qwen3.5-Omni-Flash：WER 10.8%，粤语 3.1% vs Gemini-3-Flash 10.8%

### 翻译（FLEURS）
- Plus en2xx BLEU 33.8 vs Gemini 31.8，zh2xx 21.4 vs 19.6
- 粤语翻译大幅领先（+15.6 BLEU in xx2zh）

### 综合
- Qwen3.5-Omni-Plus：215 项音频/音视频子任务 SOTA
- 关键音频任务超越 Gemini-3.1 Pro，综合音视频理解持平

## 与 Qwen3-Omni 的关键差异

| 维度 | Qwen3-Omni | Qwen3.5-Omni |
|------|------------|--------------|
| 架构 | Dense | **Hybrid MoE** |
| 上下文 | 较短 | **256k** |
| Talker 输入 | Dual-track | **ARIA 动态对齐** |
| 时间感知 | TMRoPE | **显式 timestamp** |
| 多语言 | 较少 | **74 种语言 + 39 种方言** |
| 后训练 | 标准 | **Specialist Distillation + OPD + Interaction RL** |

## 开放问题

- MoE 架构下的训推一致性问题（routing 在训练/推理时是否一致？）
- ARIA 机制的更多技术细节尚未公开
- Flash vs Plus 的具体参数规模差异
- OPD 在 audio-text cross-modal 蒸馏中的具体损失函数设计

## Related

- [[qwen3-omni]] — 前代 Qwen3-Omni，Thinker-Talker 架构起源
- [[qwen3-asr]] — Qwen3-ASR，Qwen3.5-Omni AuT 训练数据由其生成
- [[qwen3]] — Qwen3 系列 LLM 基座
- [[omni-modal-llm]] — Omni-Modal LLM 范式总览
- [[on-policy-distillation]] — OPD 在 Qwen3.5-Omni 后训练中的关键角色
- [[omnijigsaw]] — Qwen3-Omni 的 RL 后训练技术（时间重排）
