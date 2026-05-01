---
title: FunCodec — Neural Speech Codec Toolkit
created: 2026-05-01
updated: 2026-05-01
type: concept
tags: [codec, open-source, model, speech-model]
sources: [raw/papers/2023/09/2309.07405.md]
---
# FunCodec — Neural Speech Codec Toolkit

> arXiv 2309.07405 | Alibaba DAMO Speech Lab | GitHub: alibaba-damo-academy/FunCodec
> Extension of [[funasr]] for reproducible neural speech codec research

## Overview

FunCodec is a fundamental, reproducible, and integrable open-source toolkit for neural speech codecs, built as an extension of the FunASR ecosystem. It provides training recipes and inference scripts for modern codec models (SoundStream, Encodec) and introduces **FreqCodec** — a frequency-domain codec achieving comparable quality with lower parameter and compute cost.

## Design Philosophy

```
┌──────────────────────────────────────────────────┐
│           HuggingFace & ModelScope                │
│  SoundStream │ Encodec │ FreqCodec │ Semantic    │
├──────────────────────────────────────────────────┤
│                  FunCodec                         │
│                                                   │
│  Codebase:                                        │
│    train.sh │ finetune.sh │ inference.sh          │
│                                                   │
│  Downstream Tasks:                                │
│    ASR │ PTTS (Personalized TTS) │ ...            │
├──────────────────────────────────────────────────┤
│              Applications                         │
└──────────────────────────────────────────────────┘
```

Unified design with FunASR means codec models can be seamlessly integrated into downstream speech processing pipelines (ASR, TTS).

## Architecture

```
              FunCodec Model Architecture
═══════════════════════════════════════════════════════

  Raw Audio x
       │
       ▼
  ┌──────────────────┐
  │ Domain Transform │  ← Identity (time-domain) or STFT (freq-domain)
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐
  │    Encoder       │  ← SEANet (time) or Conv2D+LSTM (freq)
  │  Vₐ = Enc(X)     │
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐
  │      RVQ         │  ← Residual Vector Quantization
  │  Qⁿ = VQ(Q⁰ - ΣQⁱ)│     K-means init + moving average update
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐
  │    Decoder       │  ← Mirror of encoder
  │  x̂ = Dec(RVQ(V))  │
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐
  │ Domain Inversion │  ← ISTFT for frequency-domain models
  └────────┬─────────┘
           │
           ▼
    Reconstructed x̂
```

## Key Innovation: FreqCodec

FreqCodec operates in the **frequency domain** instead of the time domain, using STFT-transformed spectrograms:

```
X = STFT(x)
X_mag,ang = (log|X|, angle(Xᵢ, Xᵣ))    # Magnitude + angle representation
X_mag,pha = (log|X|, Xᵣ/|X|, Xᵢ/|X|)   # Magnitude + phase representation
```

### FreqCodec Encoder Architecture

| Layer | Input | Kernel/Stride | Output |
|-------|-------|--------------|--------|
| Domain Trans. | (1, t) | 512, 160 | (*, T, 257) |
| PreConv2D | (*, T, 257) | (7,7), (1,1) | (C, T, 256) |
| EncBlock × B | — | —, (Sb, 4) | (2Cb, Tb/Sb, Fb/4) |
| Conv2D 1 | (Cb, Tb, Fb) | (3,3), (1,1) | (Cb/2, Tb, Fb) |
| Conv2D 2 | (Cb/2, Tb, Fb) | (1,1), (1,1) | (Cb, Tb, Fb) |
| Conv2D ds | (Cb, Tb, Fb) | (2Sb,8), (Sb,4) | (2Cb, Tb/Sb, Fb/4) |
| Reshape | (2⁴C, TB, 1) | — | (TB, 2⁴C) |
| LSTM | (TB, 2⁴C) | — | (TB, 2⁴C) |
| OutLinear | (TB, 2⁴C) | (2⁴C, D) | (TB, D) |

**Key advantage**: Under the same compression ratio (token rate), FreqCodec achieves **comparable ViSQOL scores** to time-domain models (SoundStream, Encodec) with **fewer parameters and lower FLOPs**.

## Semantic-Augmented RVQ

FunCodec explores three methods to inject semantic information (phoneme labels, HuBERT embeddings) into the codec:

```
f_cat(Vₐ, Vₛ) = Concat(RVQ(Vₐ), Vₛ)      # Concatenation
f_add(Vₐ, Vₛ) = RVQ(Vₐ) + Vₛ             # Addition
f_res(Vₐ, Vₛ) = RVQ(Vₐ - Vₛ) + Vₛ        # Residual
```

Where Vₛ = semantic tokens. Semantic augmentation improves speech quality at **low bit rates** where the codec has fewer tokens to work with.

RVQ codebook initialization uses **k-means clustering** on the first mini-batch samples, with moving average updates (decay 0.99). Dead codes (< 2 activations per batch) are reassigned.

## Adversarial Training with Multiple Discriminators

Total loss:
```
L = λₜ·Lₜ + λf·L_f + λ_adv·L_adv + λ_feat·L_feat + λ_cm·L_cm
```

- **Lₜ** (time domain): L1 distance ||x - x̂||₁
- **L_f** (frequency domain): L1 + L2 on multiple Mel and magnitude spectra
  ```
  L_f = (1/|α|) Σᵢ (||Sᵢ(x) - Sᵢ(x̂)||₁ + ||Sᵢ(x) - Sᵢ(x̂)||₂
                      + ||Mᵢ(x) - Mᵢ(x̂)||₁ + ||Mᵢ(x) - Mᵢ(x̂)||₂)
  ```
  where Sᵢ = log-compressed power spectrum, Mᵢ = Mel spectrum, window size 2ⁱ
- **L_adv**: Multi-discriminator adversarial loss (MSD + MPD + MSTFTD)
- **L_feat**: Feature matching loss across discriminator layers
- **L_cm**: RVQ commit loss (quantization error)

FunCodec supports **4 discriminators** (vs 1-3 in other toolkits), providing stronger discriminative signal.

## Benchmarks (ViSQOL on LibriTTS)

| Model | Stride | 200 TKR | 100 TKR | 50 TKR |
|-------|--------|---------|---------|--------|
| SoundStream | 320 | 4.00 | 3.60 | 3.12 |
| Encodec | 320 | 4.05 | 3.73 | 3.30 |
| **FunCodec** | 320 | **4.12** | **3.86** | **3.43** |
| FunCodec-2x | 640 | **4.16** | **3.94** | **3.64** |
| FunCodec-4x | 1280 | 3.94 | 3.43 | 2.91 |

TKR = Token Rate (tokens per second of 16kHz speech). Lower TKR = lower bitrate.

**FunCodec-2x** (2x stride = half frame rate) achieves the best balance between time and quantization resolution.

## Feature Comparison with Other Toolkits

| Feature | Encodec | DAC | AudioDec | **FunCodec** |
|---------|---------|-----|----------|-------------|
| Released models | 2 | 3 | 3 | **7** |
| Training recipe | ✗ | ✓ | ✓ | **✓** |
| Training stages | — | 1 | 2 | **1** |
| Discriminators | — | 3 | 2 | **4** |
| Distributed training | ✗ | ✗ | ✓ | **✓** |
| K-means init | ✗ | ✓ | ✗ | **✓** |
| Low-frame-rate | ✗ | ✗ | ✗ | **✓** |
| Frequency domain | ✗ | ✗ | ✗ | **✓** |
| Semantic augmentation | ✗ | ✗ | ✗ | **✓** |

## Training Details

- LibriTTS: 585 hrs English, 2× V100 GPUs, batch size 32
- Generalized: 25,000 hrs bilingual (EN/ZH), 4× A100 GPUs, batch size 128
- 300,000 adversarial training steps
- 3.2s random clip per sample, RMS normalization
- Discriminator only updated when its loss exceeds codec loss (prevents discriminator dominance)
- Hyperparameters: λₜ=1.0, λf=1.0, λ_adv=1/9, λ_feat=1/9, λ_cm=100

## Low-Frame-Rate Models

FunCodec introduces models with 2x and 4x longer strides:
- **FunCodec-2x** (stride 640): Better at all TKR levels than baseline
- **FunCodec-4x** (stride 1280): Degrades at low TKR (time resolution too coarse)

Finding: 2x frame rate reduction is optimal — balances temporal and quantization resolution.

## Structured Quantization Dropout

To enable variable-bitrate operation from a single model, FunCodec implements structured quantization dropout — randomly dropping quantizer layers during training so the decoder learns to reconstruct from partial token streams.

## Related

- [[funasr]] — Parent speech recognition toolkit
- [[paraformer]] — FunASR's flagship ASR model (codec tokens can serve as input)
- [[qwen3-asr]] — LLM-based ASR (2026), represents the neural codec → LLM pipeline
- [[whisper-aut]] — Audio encoder for LLM integration, alternative codec-frontend
