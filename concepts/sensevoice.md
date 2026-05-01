---
title: SenseVoice — Multi-Task Speech Understanding Foundation Model
created: 2026-05-01
updated: 2026-05-01
type: concept
tags: [model, architecture, speech-model, end-to-end, open-source]
sources: [raw/papers/2024/07/2407.04051.md]
---
# SenseVoice — Multi-Task Speech Understanding Foundation Model

> FunAudioLLM (Alibaba Tongyi SpeechTeam) | arXiv 2407.04051 | 2024-07
> Unified ASR + SER + LID + AED with >5x speedup over Whisper

## Overview

SenseVoice is a speech foundation model family designed for multi-task voice understanding. It integrates four capabilities into a single model:

| Task | Abbrev | Description |
|------|--------|-------------|
| Automatic Speech Recognition | ASR | Multi-lingual transcription with ITN + punctuation |
| Speech Emotion Recognition | SER | Detect emotional states (happy, sad, angry, etc.) |
| Language Identification | LID | Identify spoken language |
| Audio Event Detection | AED / AEC | Detect events (music, laughter, cough, etc.) |

The output is **rich text** containing both transcription content and embedded emotion/event tags, designed to serve as frontend input for downstream TTS (e.g., [[cosyvoice|CosyVoice]]) to reproduce paralinguistic features.

## Two Variants

### SenseVoice-Small

- **Architecture**: Non-autoregressive, encoder-only (SAN-M)
- **Parameters**: 234M
- **Languages**: 5 (zh, en, yue, ja, ko)
- **Training data**: ~300,000 hours
- **Latency**: 70ms for 10s audio (RTF = 0.007) on A800
- **Speed**: >5x faster than Whisper-Small, >15x faster than Whisper-Large-V3
- **Open-sourced**: Yes (ModelScope + GitHub)

### SenseVoice-Large

- **Architecture**: Autoregressive, encoder-decoder (similar to Whisper)
- **Parameters**: 1587M
- **Languages**: 50+
- **Training data**: ~400,000 hours (300k base + 100k additional multilingual)
- **Latency**: 1623ms for 10s audio (RTF = 0.110) on A800
- **Open-sourced**: Yes (ModelScope + GitHub)

## Architecture Details

### SenseVoice-Small (NAR Encoder-Only)

```
Input waveform → 80-dim log-mel filter-bank
                 → Stack + downsample (factor 6)
                 → Prepend 4 special task tokens:
                   <LID>, <SER>, <AEC>, <ITN/NoITN>
                 → SAN-M Encoder
                 → Linear projection + Softmax
                 → CTC output (ASR) + CE output (LID/SER/AEC)
```

The 4 special tokens control behavior:

| Token | Function |
|-------|----------|
| `<LID>` | Predict language token (during training, replaced with ground truth at p=0.8) |
| `<SER>` | Predict speech emotion label |
| `<AEC>` | Predict audio event label |
| `<ITN>` / `<NoITN>` | Enable/disable inverse text normalization and punctuation |

**Loss functions**:
- ASR: CTC loss
- LID / SER / AEC: Cross-entropy loss

### SenseVoice-Large (AR Encoder-Decoder)

Similar to Whisper, tasks are specified via input token sequence to the decoder:
`<LID>`, `<SER>`, `<AED>` tokens control what auxiliary predictions to generate alongside transcription. SenseVoice-Large can predict timestamps for audio events (unlike Small, which detects at most one event per utterance).

## Benchmark Results

### ASR Performance (CER/WER)

| Dataset | Whisper-S | Whisper-L-V3 | **SenseVoice-S** | **SenseVoice-L** | Paraformer-zh |
|---------|-----------|-------------|-----------------|-----------------|---------------|
| AISHELL-1 test | 10.04 | 5.14 | **2.96** | **2.09** | 1.95 |
| AISHELL-2 test_ios | 8.78 | 4.96 | **3.80** | **3.04** | 2.85 |
| WenetSpeech test_meeting | 25.62 | 18.87 | **7.44** | **6.73** | 6.97 |
| WenetSpeech test_net | 16.66 | 10.48 | **7.84** | **6.01** | 6.74 |
| LibriSpeech test_clean | 3.13 | 1.82 | 3.15 | **2.57** | - |
| LibriSpeech test_other | 7.37 | 3.50 | 7.18 | **4.28** | - |
| CommonVoice zh-CN | 19.60 | 12.55 | **10.78** | **7.68** | 10.30 |
| CommonVoice en | 14.85 | 9.39 | 14.71 | **9.00** | - |
| CommonVoice yue | 38.97 | 10.41 | **7.09** | **6.78** | - |
| CommonVoice ja | 19.51 | 10.34 | **11.96** | **9.19** | - |
| CommonVoice ko | 10.48 | 5.59 | **8.28** | **5.21** | - |
| CommonVoice 5-lang avg | 20.68 | 9.66 | **10.56** | **7.57** | - |

SenseVoice-Small outperforms Whisper-Small on all test sets. SenseVoice-Large significantly outperforms Whisper-Large-V3 on Cantonese, Catalan, and Marathi.

### Inference Efficiency (A800, batch=1)

| Model | Framework | Params | Languages | RTF | 10s Latency |
|-------|-----------|--------|-----------|-----|-------------|
| Whisper-S | AR | 224M | 50+ | 0.042 | 518ms |
| Whisper-L-V3 | AR | 1550M | 50+ | 0.111 | 1281ms |
| Paraformer-zh | NAR | 220M | zh | 0.009 | 100ms |
| **SenseVoice-S** | **NAR** | **234M** | **5** | **0.007** | **70ms** |
| SenseVoice-L | AR | 1587M | 50+ | 0.110 | 1623ms |

### Speech Emotion Recognition

SenseVoice evaluated zero-shot (no fine-tuning on target domains) on 7 datasets: CASIA, CREMA-D, ESD, IEMOCAP, MELD, MER2023, MSPPodcast.

- **SenseVoice-Large** achieves best results on almost all datasets compared to EmoBox, Emo-SUPERB, MerBench baselines
- **SenseVoice-Small** outperforms other open-source SER models (XLSR-SER, Qwen-Audio, SALMONN) on majority of datasets

### Audio Event Detection

Evaluated on ESC-50, Baby Cry Detection, Coswara (coughing), In-Home Talkshow. Compared against BEATS and PANNs. SenseVoice shows strong accuracy (often higher than recall), suitable for human-machine interaction. Can detect: music, applause, laughter, coughing, sneezing, breathing, crying.

## Training Data

SenseVoice-Small trained on ~300,000 hours covering 5 languages. SenseVoice-Large adds ~100,000 hours of diverse multilingual data for a total of ~400,000 hours.

Rich transcription labels generated using open-source AED and SER models for pseudo-labeling:
- AED: 150 million entries
- SER: 30 million entries

## Rich Text Output Format

SenseVoice outputs transcription with embedded tags:

```
<music> Absolute shocked but in a great way my. <happy> That was awesome, that was awesome what way to open a song that was awesome, awesome, ...
```

This rich text format is used as input prompts for [[cosyvoice|CosyVoice]] to reproduce the detected emotions and events in synthesized speech.

## S3 Tokenizer

A supervised semantic speech tokenizer (S³) built on top of SenseVoice-Large:
- Vector quantizer after first 6 encoder layers
- Single codebook with 4,096 entries
- 50 Hz token rate
- Trained end-to-end to minimize rich text recognition errors
- Strong semantic correlation to textual and paralinguistic content
- Robust to data noise (supervised vs. unsupervised tokenizers like SoundStream, Encodec, HuBERT)

## Ecosystem

- **GitHub**: github.com/FunAudioLLM/SenseVoice
- **ModelScope**: iic/SenseVoice
- **HuggingFace**: Available
- **Used as frontend for**: [[cosyvoice|CosyVoice]] TTS pipeline
- **Related toolkit**: [[funasr|FunASR]]
- **Sibling model**: [[cosyvoice|CosyVoice]] (speech generation)

## Related

- [[fun-audio-llm]] — Parent framework
- [[funasr]] — Alibaba end-to-end speech toolkit
- [[paraformer]] — NAR ASR predecessor from DAMO
- [[qwen3-asr]] — Alibaba LLM-based ASR (2026)
- [[whisper-aut]] — Whisper-based audio encoder adaptation
