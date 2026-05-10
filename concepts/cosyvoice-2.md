---
title: "CosyVoice 2"
created: 2026-05-01
updated: 2026-05-01
type: concept
tags: [speech-model, model, open-source, streaming]
sources: [raw/papers/2024/12/2412.10117.md]
---

# CosyVoice 2

CosyVoice 2 是阿里 FunAudioLLM 团队于 2024 年 12 月发布的**可扩展流式语音合成模型**（arXiv 2412.10117）。相比 [[cosyvoice]] 一代，核心改进集中在四个方面：FSQ 替换 VQ 提升码本利用率、直接用预训练 LLM 作为文本-语音 LM 骨干、统一流式/非流式合成的单模型框架、以及增强的指令控制能力。

代码开源：https://github.com/FunAudioLLM/CosyVoice
Demo：https://funaudiollm.github.io/cosyvoice2

## 系统架构

CosyVoice 2 延续了前代"语义-声学解耦建模"的设计哲学，生成流程分为三个阶段：

1. **有监督语义 Tokenizer**（SenseVoice-Large + FSQ）→ 提取离散语义 token
2. **Text-Speech LM**（预训练 Qwen2.5-0.5B）→ 自回归生成语义 token
3. **Chunk-aware CFM** → 语义 token → Mel 频谱图 → Vocoder → 波形

```
Text + prompt audio → Tokenizer → semantic tokens (FSQ)
    → Pre-trained LLM → speech token sequence
    → Chunk-aware causal CFM (conditioned on speaker emb + ref speech)
    → Mel spectrogram → HiFiGAN vocoder → waveform
```

相比一代的四大架构变化：

| 变化 | CosyVoice (v1) | CosyVoice 2 |
|------|----------------|-------------|
| Tokenizer 量化 | Vector Quantization (VQ) | **Finite Scalar Quantization (FSQ)** |
| Text-Speech LM | 从头训练的自定义 LM + Text Encoder + Speaker Embedding | **预训练 Qwen2.5-0.5B**，去掉 Text Encoder 和 Speaker Embedding |
| Flow Matching | 离线非因果 CFM | **Chunk-aware 因果 CFM**，支持流式/非流式 |
| 推理模式 | 仅非流式 | **统一单模型**支持流式 + 非流式 |

## 1. 有监督语义 Speech Tokenizer（FSQ）

### FSQ（Finite Scalar Quantization）

**核心创新**：用 FSQ 替换传统 VQ，解决码本崩溃（codebook collapse）问题。

**数学流程**：
1. 输入语音 X → Encoder₁（6 层 Transformer + RoPE）→ 中间表征 H
2. **降维投影**：Proj_down(H) → D 维低秩空间
3. **标量量化**：ROUND 操作，每维量化到 [-K, K] 范围内的整数
4. **升维投影**：Proj_up(ȲH) → 恢复原始维度 H̃
5. **索引计算**：将量化低秩向量 ȳhᵢ 映射为 (2K+1)^D-ary 系统下的整数 token μᵢ
6. H̃ → Encoder₂ + ASR Decoder → 文本 token 后验概率

训练时使用 **Straight-Through Estimation** 近似 FSQ 模块和 Encoder₁ 的梯度。

### 码本利用率对比

| 方法 | 码本大小 | 利用率 | C.V. EN WER | C.V. CN WER | Fluers EN WER | Fluers CN WER |
|------|---------|--------|------------|------------|--------------|--------------|
| VQ | 4,096 | 23% (963/4096) | 18.26 | 11.56 | 7.65 | 5.03 |
| **FSQ** | **6,561** | **100%** | **10.67** | **7.29** | **6.58** | **4.43** |

FSQ 的 6,561 码本（对应 levels=[9,9,9,9] 或类似配置）实现 **100% 利用率**，显著优于 VQ 的 23%。

### 说话人信息解耦

t-SNE 可视化表明：量化前 Encoder₁ 输出对不同说话人有明显分布差异，量化后分布几乎不可区分。SID（说话人识别）训练中使用量化 token 的特征提取器**无法收敛**，证明 FSQ 成功将说话人身份信息从语义表征中解耦。

### 关键参数

- **Token 速率**：25 Hz（每秒 25 个 speech token）
- **Mel 帧率**：50 Hz（通过 2x 上采样匹配）
- **看 ahead 卷积**：右填充 1D 卷积，pad 大小 P，kernel 大小 P+1，提供未来信息
- **训练数据**：200,000 小时（中文 110,884h + 英文 99,918h）

## 2. 统一 Text-Speech Language Model

### 预训练 LLM 集成

CosyVoice 2 直接使用 **Qwen2.5-0.5B** 作为文本-语音 LM，无需从头训练：

- **去掉 Text Encoder**：发现 Qwen2.5-0.5B 已足够强大，能直接对齐文本和语音 token
- **去掉 Speaker Embedding**：避免信息泄露（utterance-level 向量包含语言、副语言信息，损害韵律自然度和跨语言能力）
- **输入**：直接用 BPE tokenized 原始文本，无需 g2p（grapheme-to-phoneme）前端
- **多字符 masking**：如果 BPE token 编码超过一个中文字符，则 mask 掉并单独编码每个字符，防止发音过长

### 统一流式/非流式训练

通过**不同的序列构造方式**在单个模型中同时支持两种模式：

**非流式模式**：`S → [所有 text tokens] → T → [所有 speech tokens] → E`

**流式模式**：按 N:M 比例交错文本和语音 token，即每 N 个 text token 后跟 M 个 speech token。如果下一个应该是 text token但文本已用完，LM 预测 **filling token**，表示应继续拼接 N 个 text token。文本耗尽后添加 T 和剩余 speech token。

### 推理场景

| 场景 | 序列构造 |
|------|---------|
| ICL, 非流式 | `S, prompt_text, text, T, prompt_speech` → 自回归生成直到 E |
| ICL, 流式 | `S, mixed_text_speech(N:M), T, remaining_speech` → 每 M 个 token 返回一次结果 |
| SFT, 非流式 | `S, text, T` → 自回归生成 |
| SFT, 流式 | `S, first_N_text` → 生成 M 个 speech token → 手动填充 N 个 text token → 循环直到文本耗尽 → 添加 T |

## 3. Chunk-aware Causal Flow Matching

### OT-CFM 基础

- **Mel 特征**：50 Hz 帧率，24kHz 采样率
- **OT 路径**：φᵗᵒᵗ(X₀, X₁) = (1-t)X₀ + tX₁
- **训练时 t**：均匀分布 U[0,1]
- **推理时 t**：cosine scheduler t := 1 - cos(½tπ)，生成初期分配更多步数
- **NFE（Flow Estimation 步数）**：10
- **CFG 强度 β**：0.7
- **优化目标**：预测与真实 ODE 之间的 L1 损失

### 因果 UNet 与 Mask 机制

将多步流估计视为堆叠的深层神经网络（UNet 重复 10 次），通过使展开的网络因果化实现流式合成。定义四种 attention mask：

| Mask 类型 | 注意力范围 | 适用场景 |
|----------|----------|---------|
| Non-causal | 所有帧 | 离线模式，延迟不敏感场景 |
| Full-causal | 仅过去帧 | 极低延迟场景 |
| Chunk-M | 过去 + M 帧未来 | 生成首 chunk，低延迟 |
| Chunk-2M | 过去 + 2M 帧未来 | 级联生成 chunk，近似离线性能 |

训练时每个 mini-batch 均匀随机采样一种 mask，实现**隐式自蒸馏**：上下文更多的 mask 作为上下文更少 mask 的 teacher。

### 延迟分析

**TTS 首包延迟**：L_TTS = M · d_lm + M · d_fm + M · d_voc

**LLM 语音聊天首包延迟**：L_Chat ≤ N · d_llm + L_TTS

其中 M 为每次生成的 speech token 数，N 为首次所需的 text token 数，d_lm/fm/voc 分别为 LM/CFM/Vocoder 生成单个 token 的计算时间。

## 4. 指令驱动生成

收集了 **1,500 小时**指令训练数据，包含自然语言指令和细粒度指令：

### 自然语言指令（prepend 描述 + `<|endofprompt|>`）

| 控制维度 | 示例 |
|---------|------|
| 情感 | 高兴、悲伤、惊讶、愤怒、恐惧、厌恶、冷静、严肃 |
| 语速 | 快速、非常快速、慢速、非常慢速 |
| 方言 | 粤语、四川话、上海话、郑州话、长沙话、天津话 |
| 角色扮演 | 神秘、凶猛、好奇、优雅、孤独、机器人、小猪佩奇 等 |

### 细粒度指令

| 类型 | 标记 |
|------|------|
| Vocal Bursts | `[laughter]`, `[breath]` 等插入文本 token 之间 |
| Vocal Features | `<strong>XXX</strong>` 强调词语，`<laughter>XXX</laughter>` 笑着说话 |

## 5. 多说话人微调（mSFT）

**Multi-Speaker Fine-tuning**：同时对多个说话人微调，而非单一说话人：
- 优点：覆盖更全面的韵律和发音，减轻灾难性遗忘
- 避免音色混淆：输入文本前添加 `Speaker A<|endofprompt|>` 标签
- 未标注说话人的样本使用 `unknown<|endofprompt|>`
- 学习率：1e-5
- **400 条录音**即可达到合理的说话人合成效果

## 6. 强化学习微调

### DPO 优化

使用说话人相似度（SS）和 ASR 识别 WER 作为奖励函数，通过 DPO 优化 LM：

L_DPO = -log σ(β·log(π_θ(μʷ|y) / π_ref(μʷ|y)) - β·log(π_θ(μˡ|y) / π_ref(μˡ|y)))

### 可微 ASR 奖励

为避免反复合成音频获取偏好对，直接将 LM 预测 token 还原为量化低秩表征，用冻结的 ASR backend 重新预测输入文本，以对数后验作为奖励：

- 使用 **Gumbel Softmax** 采样使离散化可微
- 直接优化 θ_LM，ASR 参数冻结
- **泛化能力更强**：在 OOD 场景下表现优于纯 DPO

### RL 实验结果（Spk E）

| 模型 | In-domain WER | NMOS | SS | SEED zh CER | SEED en WER | SEED hard WER |
|------|-------------|------|-----|------------|------------|--------------|
| CosyVoice 2 | 5.34 | 3.91 | 0.721 | 1.45 | 2.57 | 6.83 |
| + SFT | 7.15 | 3.96 | 0.795 | 1.50 | 4.26 | 7.90 |
| + SFT + L_ASR | 6.79 | 3.96 | 0.795 | 1.29 | 3.53 | 7.30 |
| + SFT + L_DPO | 6.83 | 3.96 | 0.792 | 1.43 | 4.02 | 8.31 |
| + SFT + L_ASR + L_DPO | **6.64** | **3.97** | **0.796** | **1.25** | **3.17** | **6.66** |

组合 L_ASR + L_DPO 效果最优，同时降低 in-domain WER 并保持/提升其他指标。

## 训练数据

### CosyVoice 2 训练数据（总计 ~172k 小时）

| 语言 | 时长 |
|------|------|
| 中文 | 130,000 小时 |
| 英文 | 30,000 小时 |
| 日语 | 4,600 小时 |
| 韩语 | 2,200 小时 |
| **总计** | **~166,800 小时** |

数据流程：语音检测 → SNR 估计 → 说话人分离 → Paraformer/SenseVoice 伪标签 → Force-alignment 精炼

### Speech Tokenizer 训练数据（200,000 小时）

中文 110,884h + 英文 99,918h，来源包括开源 ASR 数据集、内部工业数据集和 TTS 生成数据集。

## 性能指标

### LibriSpeech test-clean（英语）

| 模型 | WER (%) | NMOS | SS |
|------|---------|------|-----|
| Human | 2.66 | 3.84 | 0.697 |
| ChatTTS | 6.84 | 3.89 | - |
| GPT-SoVITs | 5.13 | 3.93 | 0.405 |
| OpenVoice | 3.47 | 3.87 | 0.299 |
| CosyVoice (v1) | 2.89 | 3.93 | 0.743 |
| **CosyVoice 2** | **2.47** | **3.96** | **0.745** |
| **CosyVoice 2-S** (流式) | 2.45 | 3.90 | 0.751 |

CosyVoice 2 在所有指标上**超过人类基线**，实现人类级合成质量。流式版本（-S）质量几乎无损。

### SEED 评测

| 模型 | test-zh CER | test-zh SS | test-en WER | test-en SS | test-hard WER | test-hard SS |
|------|-----------|-----------|------------|-----------|--------------|-------------|
| Human | 1.26 | 0.760 | 2.14 | 0.730 | - | - |
| Seed-TTS † | 1.12 | 0.796 | 2.25 | 0.762 | 7.59 | 0.776 |
| F5-TTS (32 NFE) | 1.56 | 0.76 | 1.83 | 0.670 | 8.67 | 0.762 |
| CosyVoice (v1) | 3.63 | 0.775 | 4.29 | 0.699 | 11.75 | 0.755 |
| **CosyVoice 2** | **1.45** | **0.806** | 2.57 | 0.736 | **6.83** | **0.776** |
| **CosyVoice 2-S** (流式) | **1.45** | **0.812** | **2.38** | **0.743** | 8.08 | **0.785** |

流式模式在典型用例中几乎无损，仅在 test-hard 上内容一致性略有下降。

### 模块化消融实验

| 修改 | test-zh CER | test-zh SS | test-en WER | test-en SS | test-hard WER | test-hard SS |
|------|-----------|-----------|------------|-----------|--------------|-------------|
| CosyVoice (v1) | 3.63 | 0.775 | 4.29 | 0.699 | 11.75 | 0.755 |
| + LLM 初始化 | 2.96 | 0.808 | 4.57 | 0.730 | 9.94 | 0.789 |
| + 去掉 Spk Emb | 2.56 | 0.804 | 3.81 | 0.740 | 9.66 | 0.778 |
| **+ FSQ（CosyVoice 2）** | **1.45** | **0.806** | **2.57** | **0.736** | **6.83** | **0.776** |
| + Pitch Loss | 1.19 | 0.802 | 2.40 | 0.728 | 6.29 | 0.769 |

### 流式模块消融（Chunk size = 15）

| LM | FM | test-zh CER | test-zh SS | test-en WER | test-en SS | test-hard CER | test-hard SS |
|----|-----|-----------|-----------|------------|-----------|-------------|-------------|
| Offline | Offline | 1.45 | 0.806 | 2.57 | 0.736 | 6.83 | 0.776 |
| Offline | Stream | 1.46 | 0.811 | 2.60 | 0.743 | 7.12 | 0.788 |
| Stream | Offline | 1.38 | 0.806 | 2.51 | 0.737 | 7.88 | 0.773 |
| Stream | Stream | 1.45 | 0.812 | 2.38 | 0.743 | 8.08 | 0.785 |

流式 LM 对典型用例影响极小，主要影响 test-hard 挑战性用例。流式 FM 的 SS 略高于离线模式。

### 指令生成评测（290 样本，29 种指令）

| 模型 | CER (%) | SS | NMOS | MOS-I |
|------|--------|-----|------|-------|
| CosyVoice-Instruct (v1) | 1.72 | 0.797 | 3.94 | 3.14 |
| **CosyVoice 2** | **1.52** | **0.804** | **3.94** | **4.11** |
| CosyVoice 2 w/o Instruction | 0.97 | 0.817 | 4.02 | 2.54 |

### 日/韩语基准

| 模型 | test-ja CER | test-ja SS | test-ja NMOS | test-ko CER | test-ko SS | test-ko NMOS |
|------|-----------|-----------|-------------|-----------|-----------|-------------|
| CosyVoice 2 | 18.79 | 0.630 | 3.42 | 7.98 | 0.707 | 3.73 |
| CosyVoice 2-S | 21.41 | 0.629 | 3.35 | 9.06 | 0.714 | 3.60 |

日语性能较低主要因为日中字符重叠导致中文发音混入。

## 局限性

1. **语言支持有限**：对字符集重叠的语言（如日语中的汉字），合成性能退化
2. **无法通过文本指令控制音色**等声学特征
3. **不适合歌唱**合成

## 相关页面

- [[cosyvoice]] — CosyVoice 一代，VQ + 自定义 LM 架构
- [[cosyvoice-3]] — CosyVoice 第三代
- [[fun-codec]] — 同团队的语音编解码工具包
- [[fun-audio-llm]] — FunAudioLLM 团队，CosyVoice 的归属组织
- [[seeduplex]] — 字节跳动 Seed 团队的全双工语音模型，竞品
