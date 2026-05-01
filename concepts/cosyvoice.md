---
title: CosyVoice
created: 2026-05-01
updated: 2026-05-01
type: concept
tags: [speech-model, model, open-source]
sources: [raw/papers/2024/07/2407.05407.md]
---

# CosyVoice

CosyVoice 是阿里 Speech Lab（FunAudioLLM 团队）于 2024 年 7 月发布的大规模多语言零样本 TTS 合成系统。核心创新是首次将**有监督语义语音 token（Supervised Semantic Speech Tokens, S³）**引入 TTS 模型，相比无监督 token 在内容一致性和说话人相似度上显著提升。

代码开源：https://github.com/FunAudioLLM/CosyVoice
Demo：https://fun-audio-llm.github.io

## 系统架构

CosyVoice 由四个核心组件组成：

| 组件 | 功能 |
|------|------|
| S³ Tokenizer | 有监督语义语音 token 提取 |
| Text Encoder | 文本与语音 token 语义空间对齐 |
| LLM | 自回归生成语音 token 序列 |
| OT-CFM Vocoder | 从 token 生成 Mel 频谱图 |

训练流水线：**Tokenizer（ASR encoder + VQ） → LLM（text + speaker → tokens） → CFM（tokens → waveform） → HiFiGAN（mel → waveform）**

## 1. 有监督语义 Token（S³）

**核心创新**：将 vector quantization 层插入多语言 ASR 模型编码器中间，从有监督 ASR 训练中获得离散语音 token。

- **基座模型**：SenseVoice-Large（富识别 ASR 模型）
- **VQ 插入位置**：前 6 层 encoder 之后
- **Codebook**：单个 codebook，4096 个码向量
- **更新方式**：EMA（Exponentially Moving Average）更新 codebook embedding
- **训练**：8 张 A800 GPU，210,000 步微调

数学流程：

1. Mel 频谱图 X → Encoder₁ → 上下文表征 H
2. VQ 离散化：μₗ = argminₙ ||hₗ - cₙ||₂
3. Codebook 更新：c_{μₗ} := α·c_{μₗ} + (1-α)·hₗ
4. 量化表征 H̄ → 额外位置编码 → Encoder₂ → H̃
5. ASR Decoder 预测文本标签后验概率 P(Y|X)

对比无监督 token（Encodec、HuBERT），S³ token 的优势：
- 显式语义信息，与文本有明确对齐
- 中文 Common Voice 上 WER 比 Whisper-Large-V3 低 4.14%
- LibriTTS 上 WER 3.18%（插入 VQ 后仅轻微影响 ASR 性能）

## 2. LLM Token 生成

将 TTS 重构为自回归序列生成问题。

**输入序列构造**：[S, v, {ȳᵤ}ᵤ∈[1:U], T, {μₗ}ₗ∈[1:L], E]

- **S** = start of sequence
- **v** = speaker embedding（x-vector / 3D-Speaker CAM++，从 3-10s 参考音频提取）
- **{ȳᵤ}** = 文本编码（BPE tokenizer + TextEncoder，对齐文本与语音语义空间）
- **T** = turn of speech（文本与语音的分隔标记）
- **{μₗ}** = 有监督语义 token 序列
- **E** = end of sequence

**训练**：Teacher-forcing，仅计算语音 token 和 E 的交叉熵损失。

模型规格：

| 配置 | Text Encoder | Language Model |
|------|-------------|----------------|
| Tiny | 6 层, 512d, 8 heads | 12 层, 512d, 8 heads |
| Normal | 6 层, 1024d, 16 heads | 14 层, 1024d, 16 heads |

- Tiny LR = 1e-3，Normal LR = 1e-4
- Warmup = 10,000 步
- 多语言模型：64 张 V100-32M，800,000 步

## 3. Optimal-Transport Conditional Flow Matching（OT-CFM）

用 CFM 替代传统 diffusion 模型，直接将语义 token 映射到 Mel 频谱图，**绕过 phonemizer 和 forced aligner**。

- **概率密度路径**：从标准正态先验 p₀(X) = N(X; 0, I) 到 Mel 频谱数据分布 q(X)
- **OT 路径**：φᵗᵒᵗ(X₀, X₁) = (1-(1-σ)t)X₀ + tX₁
- **神经网路输入**：OT 路径中间态、时间步 t、speaker embedding v、语义 token {μₗ}、masked Mel 频谱 X̃₁
- **Masking**：从随机起点到末尾的连续帧置零
- **Cosine scheduler**：t := 1 - cos(½tπ)，在生成初期分配更多步数
- **Classifier-Free Guidance（CFG）**：
  - 训练时以 0.2 概率随机丢弃条件
  - 推理时：ν̃ₜ = (1+β)·νₜ(条件) - β·νₜ(无条件)，β = 0.7
- **最终波形**：CFM 输出 Mel → HiFiGAN vocoder → 波形

## 零样本语音克隆

- **参考音频**：3-10 秒即可提取 speaker embedding
- **同语言**：prompt speech token + 输入文本合并为统一输入，prompt token 视为预生成
- **跨语言**：省略 prompt 关联的文本和 token，防止原语言韵律影响目标语言
- **增强条件**：speaker embedding + prompt Mel 频谱拼接，提升音色和环境一致性

## 指令驱动生成（CosyVoice-instruct）

在 CosyVoice-base 基础上进行 instruction fine-tuning，支持：

| 控制维度 | 示例 |
|---------|------|
| Speaker Identity | "Selene 'Moonshade', is a mysterious, elegant dancer..." |
| Speaking Style | "A happy girl with high tone and quick speech." |
| 细粒度副语言 | [laughter], [breath], 词语强调 `<strong>...</strong>` |

训练数据：Speaker Identity 101h + Speaking Style 407h + Fine-grained Paralinguistics 48h

情感控制准确率（6 种情绪）：CosyVoice-instruct 在 happy(1.00)、sad(0.98)、angry(0.83)、disgusted(0.93) 上显著优于 base 和无指令版本。

## 训练数据

### 大规模多语言数据

| 语言 | 时长 |
|------|------|
| 中文（ZH） | 130,000 小时 |
| 英文（EN） | 30,000 小时 |
| 粤语（Yue） | 5,000 小时 |
| 日语（JP） | 4,600 小时 |
| 韩语（KO） | 2,200 小时 |
| **总计** | **~171,800 小时** |

数据流程：语音检测 → SNR 估计 → 说话人分离 → SenseVoice-Large + Paraformer 伪标签 → Force-alignment 精炼

## 性能指标

### 英语（LibriTTS test-clean）

| 模型 | WER (%) | Ins.+Del. | 说话人相似度 (SS) |
|------|---------|-----------|-------------------|
| Original | 2.66 | 92 | 69.67 |
| ChatTTS | 8.32 | 441 | - |
| CosyVoice | 2.89 ± 0.18 | 88.60 ± 3.88 | **74.30 ± 0.15** |
| CosyVoice + ASR rerank (5×) | **1.51** | 47 | 74.30 |

### 中文（AISHELL-3 test）

| 模型 | CER (%) | Ins.+Del. | SS |
|------|---------|-----------|-----|
| Original | 2.52 | 25 | 74.15 |
| ChatTTS | 3.87 | 111 | - |
| CosyVoice | 3.82 ± 0.24 | 24.4 ± 2.24 | **81.58 ± 0.16** |
| CosyVoice + ASR rerank (5×) | **1.84** | 11 | 81.58 |

## 关键发现

1. **数据规模至关重要**：仅用 LibriTTS 训练的多语言 tokenizer 会同时降低内容一致性和说话人相似度；加入大规模内部数据集后显著提升至人类水平
2. **文本和语音 tokenizer 共同决定内容一致性**，对说话人相似度影响较小
3. **CosyVoice 可作为数据生成器**：用合成语音训练 ASR 模型，加入 MLS 文本的合成数据显著提升识别精度（WER 2.79→2.04）
4. **单 codebook 4096 码**的 S³ tokenizer 即达到卓越效果

## 相关页面

- [[fun-audio-llm]] — FunAudioLLM 团队，CosyVoice 的归属组织
- [[fun-codec]] — 同团队的语音编解码工具包
- [[cosyvoice-2]] — CosyVoice 的后续版本
- [[cosyvoice-3]] — CosyVoice 第三代
- [[diffro]] — 同团队的 diffusion-based 语音模型
- [[qwen3-tts]] — Qwen 团队的 TTS 模型，竞品
- [[seed-tts]] — 字节跳动 Seed 团队的自回归 TTS，竞品
