---
title: FunAudioLLM — Voice Understanding & Generation Foundation Models
created: 2026-05-01
updated: 2026-05-01
type: entity
tags: [model, speech-model, open-source, end-to-end]
sources: [raw/papers/2024/07/2407.04051.md, raw/papers/2023/05/2305.11013.md, raw/papers/2023/09/2309.07405.md]
---
# FunAudioLLM — Voice Understanding & Generation Foundation Models

> Alibaba Group Tongyi SpeechTeam | arXiv 2407.04051 | GitHub: github.com/FunAudioLLM | Demo: fun-audio-llm.github.io

## Overview

**FunAudioLLM** is a model family designed to enable natural voice interactions between humans and large language models. Developed by Alibaba Group's Tongyi SpeechTeam (formerly DAMO Speech Lab), it unifies two foundation models — [[sensevoice]] for voice understanding and [[cosyvoice]] for voice generation — built on top of the [[funasr]] toolkit ecosystem and [[fun-codec]] neural codec research.

The family supports applications including speech-to-speech translation, emotional voice chat, interactive podcasts, and expressive audiobook narration.

## Family Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                      FunAudioLLM Family                        │
│                                                               │
│  ┌─────────────────────┐    ┌─────────────────────────────┐   │
│  │   SenseVoice         │    │      CosyVoice               │   │
│  │   (Understanding)    │    │   (Generation)               │   │
│  │                      │    │                              │   │
│  │  SenseVoice-Small    │    │  CosyVoice-base-300M        │   │
│  │  SenseVoice-Large    │    │  CosyVoice-instruct-300M    │   │
│  │                      │    │  CosyVoice-sft-300M         │   │
│  └─────────┬───────────┘    └──────────────┬──────────────┘   │
│            │                               │                   │
│            ▼                               │                   │
│  ┌─────────────────────┐                   │                   │
│  │   S³ Tokenizer       │◄──────────────────┘                   │
│  │  (Semantic Speech)   │   ← Supervised tokenizer               │
│  │  built on SV-Large   │      using SV-L encoder + VQ          │
│  └─────────────────────┘                                         │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Foundation: [[funasr]] + [[fun-codec]]              │    │
│  │  Paraformer │ FSMN-VAD │ CT-Transformer │ SoundStream   │    │
│  └─────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────┘
```

### Pipeline Integration

SenseVoice and CosyVoice combine with LLMs (e.g., [[qwen3]]) for end-to-end applications:

```
Audio Input → SenseVoice → Text → LLM (Qwen) → Text → CosyVoice → Audio Output
```

## Core Models

### [[sensevoice]] — Voice Understanding

Two variants trained on ~300k hours of audio:

| Model | Architecture | Params | Languages | RTF (A800) | 10s Latency |
|-------|-------------|--------|-----------|------------|-------------|
| SenseVoice-Small | NAR encoder-only (SAN-M) | 234M | ZH, Yue, EN, JP, KO (5) | 0.007 | **70ms** |
| SenseVoice-Large | AR encoder-decoder | 1587M | **50+** | 0.110 | 1623ms |

**Capabilities:**
- **ASR:** Multilingual speech recognition (SenseVoice-L: 50+ languages)
- **SER:** Speech emotion recognition — SOTA across 7 benchmarks (CREMA-D, IEMOCAP, MELD, etc.)
- **AED:** Audio event detection — music, applause, laughter, coughing, breathing
- **LID:** Language identification
- **Rich transcription:** ITN + punctuation control via special tokens (`<ITN>`, `<NoITN>`)

**Key benchmarks (CER/WER):**
- AISHELL-1: SV-S **2.96%**, SV-L **2.09%** (vs Whisper-L-V3 5.14%)
- WenetSpeech test_meeting: SV-S **7.44%**, SV-L **6.73%** (vs Whisper-L-V3 18.87%)
- CommonVoice yue: SV-S **7.09%**, SV-L **6.78%** (vs Whisper-L-V3 10.41%)

### [[cosyvoice]] — Voice Generation

Three 300M parameter models trained on ~170k hours across 5 languages (ZH, EN, JP, Yue, KO):

| Model | Focus |
|-------|-------|
| CosyVoice-base-300M | Speaker identity, zero-shot learning, cross-lingual voice cloning |
| CosyVoice-instruct-300M | Emotionally expressive voices, instruction-following control |
| CosyVoice-sft-300M | Fine-tuned on 7 multilingual speakers, ready for deployment |

**Architecture:**
1. **AR Transformer LM** — generates S³ speech tokens from input text
2. **Flow Matching** (ODE-based diffusion) — reconstructs Mel spectrum from tokens (5-10 iterations)
3. **HiFTNet Vocoder** — streaming waveform synthesis from Mel

**Key capabilities:**
- **Zero-shot in-context learning:** Voice cloning from 3-second prompt
- **Cross-lingual voice cloning:** Timbre transfer across languages
- **Instruction-following:** Control speaker identity, speaking style (emotion, gender, rate, pitch), paralinguistic features (laughter, breaths, emphasis)
- **Human-parity quality:** WER <2%, speaker similarity >75%

**Benchmarks (zero-shot):**
- LibriTTS test-clean: WER **2.89%** (±0.18), SS **74.30%** (±0.15); with re-ranking: WER **1.51%**
- AISHELL-3 test: CER **3.82%** (±0.24), SS **81.58%** (±0.16); with re-ranking: CER **1.84%**

**Emotion controllability (CosyVoice-instruct vs base):**
| Emotion | Base | Instruct |
|---------|------|----------|
| Happy | 100% | 100% |
| Sad | 45% | **98%** |
| Angry | 59% | **83%** |
| Surprised | 26% | **64%** |
| Fearful | 88% | 87% |
| Disgusted | 46% | **93%** |

### S³ Tokenizer — Supervised Semantic Speech Tokenizer

Built on SenseVoice-Large encoder + vector quantizer:
- **4,096-entry codebook** (single codebook)
- **50 Hz token rate** — reduces LM computational load
- **Supervised training** — minimizes rich text recognition error end-to-end
- Strong semantic correlation: outperforms Whisper-L-V3 on CommonVoice zh-CN when used as tokens
- Robust to noisy data (supervised vs unsupervised tokenizers like SoundStream/Encodec)

## Data Scale

**SenseVoice training data:**
| Language | Duration |
|----------|----------|
| ZH | 130,000 hrs |
| EN | 30,000 hrs |
| Yue | 5,000 hrs |
| JP | 4,600 hrs |
| KO | 2,200 hrs |

**CosyVoice training data:**
| Language | Duration |
|----------|----------|
| ZH | ~110,000 hrs |
| EN | ~40,000 hrs |
| JP | ~8,000 hrs |
| Yue | ~6,000 hrs |
| KO | ~6,000 hrs |

**CosyVoice-instruct fine-tuning data:** Speaker Identity 101 hrs, Speaking Style 407 hrs, Paralinguistics 48 hrs.

## GitHub Repos (github.com/FunAudioLLM)

| Repository | Description |
|------------|-------------|
| [FunAudioLLM/SenseVoice](https://github.com/FunAudioLLM/SenseVoice) | SenseVoice model code, training, inference |
| [FunAudioLLM/CosyVoice](https://github.com/FunAudioLLM/CosyVoice) | CosyVoice model code, training, inference, fine-tuning |
| [FunAudioLLM/FunASR](https://github.com/FunAudioLLM/FunASR) | FunASR toolkit (successor of alibaba-damo-academy/FunASR) |
| [FunAudioLLM/FunAudioLLM-APP](https://github.com/FunAudioLLM/FunAudioLLM-APP) | Application demos combining SenseVoice + CosyVoice + LLM |

## ModelScope Demos

- **Main demo site:** https://fun-audio-llm.github.io
- **Speech-to-Speech Translation:** Speak in foreign languages using your own voice
- **Emotional Voice Chat:** Model understands and responds to emotions
- **Interactive Podcast:** Live discussions with multiple LLMs
- **Audiobook Narration:** Expressive, multi-character narration

## Ecosystem & Lineage

FunAudioLLM builds on several predecessor projects from Alibaba DAMO Speech Lab:

- **[[funasr]]** — Parent ASR toolkit (arXiv 2305.11013, 2023-05). SenseVoice extends the Paraformer line of research within the FunASR ecosystem.
- **[[fun-codec]]** — Neural speech codec toolkit (arXiv 2309.07405, 2023-09). Informed the S³ tokenizer design; CosyVoice uses codec-style token generation.
- **[[paraformer]]** — Non-autoregressive ASR model that is the flagship of FunASR; SenseVoice-Small shares the NAR design philosophy.
- **[[qwen3-asr]]** — Qwen Team's LLM-based ASR (2026-01), represents a different architectural approach (LLM-native vs dedicated ASR).
- **[[qwen3-tts]]** — Qwen Team's TTS model (2026-01), alternative to CosyVoice for text-to-speech within the Alibaba ecosystem.

## Application Demos

By integrating SenseVoice + CosyVoice + LLMs:

1. **Speech-to-Speech Translation** — User speaks → SenseVoice transcribes → LLM translates → CosyVoice speaks in user's voice
2. **Emotional Voice Chat** — SenseVoice detects emotion → LLM responds appropriately → CosyVoice generates emotionally matched speech
3. **Interactive Podcast** — Multi-LLM discussion with CosyVoice voicing different speakers
4. **Audiobook Narration** — CosyVoice performs expressive multi-character narration with paralinguistic control

## References

- arXiv 2407.04051 — FunAudioLLM overview (2024-07)
- arXiv 2305.11013 — FunASR Toolkit (2023-05)
- arXiv 2309.07405 — FunCodec (2023-09)
- GitHub: github.com/FunAudioLLM (SenseVoice, CosyVoice, FunASR, FunAudioLLM-APP)
- Demo: fun-audio-llm.github.io
- ModelScope: models hosted at ModelScope platform
