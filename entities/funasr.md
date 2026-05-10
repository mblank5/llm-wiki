---
title: "FunASR — Fundamental End-to-End Speech Recognition Toolkit"
created: 2026-05-01
updated: 2026-05-01
type: entity
tags: [model, speech-model, open-source, end-to-end, streaming]
sources: [raw/papers/2022/06/2206.08317.md, raw/papers/2023/05/2305.11013.md, raw/papers/2023/08/2308.03266.md, raw/papers/2023/09/2309.07405.md, raw/papers/2023/10/2310.04863.md, raw/papers/2024/09/2409.17746.md]
---
# FunASR — Fundamental End-to-End Speech Recognition Toolkit

> Alibaba DAMO Speech Lab | arXiv 2305.11013 | GitHub: alibaba-damo-academy/FunASR

## Overview

FunASR is an open-source end-to-end speech recognition toolkit developed by the Speech Lab of DAMO Academy, Alibaba Group. Its mission is to **bridge the gap between academic research and industrial applications** by providing pre-trained models on large-scale industrial corpora, comprehensive training/finetuning pipelines, and production-ready deployment runtimes.

The flagship model is [[paraformer]], a non-autoregressive (NAR) transformer trained on **60,000 hours of manually annotated Mandarin speech** — a scale far exceeding academic benchmarks.

## Architecture & Design

```
┌─────────────────────────────────────────────────────────┐
│                    ModelScope                             │
│  Paraformer │ FSMN-VAD │ CT-Transformer │ FunCodec │ ... │
├─────────────────────────────────────────────────────────┤
│                    FunASR Toolkit                         │
│                                                         │
│  Academic Pipeline (run.sh):                             │
│    data_prep → feat_extract → dict_gen → train → infer   │
│                                                         │
│  Industrial Pipeline:                                    │
│    infer.sh  │  finetune.sh                              │
├─────────────────────────────────────────────────────────┤
│                    Runtime Backends                       │
│    CPU/GPU  │  ONNX  │  Libtorch  │  TensorRT            │
├─────────────────────────────────────────────────────────┤
│                    Production Deployment                  │
└─────────────────────────────────────────────────────────┘
```

### Core Pipeline Stages (run.sh)
1. **Stage 0** — Data preparation
2. **Stage 1** — Feature extraction (80-dim Mel-filterbank)
3. **Stage 2** — Dictionary generation
4. **Stage 3-4** — Model training
5. **Stage 5** — Inference and scoring

## Key Modules

### [[paraformer]] — Flagship ASR Model
- Single-step NAR transformer with CIF predictor + GLM sampler
- Trained on 60k hrs Mandarin industrial data
- Comparable to AR transformer accuracy, **10x+ inference speedup**
- Added extensions: timestamp prediction, hotword customization

### FSMN-VAD — Voice Activity Detection
- Feedforward Sequential Memory Network-based VAD
- Uses monophones as modeling units for richer speech info
- Post-processing: threshold settings + sliding windows
- Tested on meeting (2hr) and video (4hr) domains
- Reduces CER by filtering non-speech: video domain CER 27.87% → 25.34%

### CT-Transformer — Punctuation & Disfluency
- Controllable Time-delay Transformer for real-time text postprocessing
- Handles punctuation insertion and speech disfluency removal
- Supports partial output freezing with controllable time delay
- Fast decoding strategy for minimal latency

### [[fun-codec]] — Neural Speech Codec Extension
- Extension toolkit for SoundStream, Encodec, FreqCodec
- Reproducible training recipes + 7 pre-trained models
- Frequency-domain codec (FreqCodec): comparable quality, lower compute
- Downstream: ASR, personalized TTS

### [[seaco-paraformer]] — Contextual Hotword Extension
- CIF-based contextual module for decoupled hotword prediction
- Attention Score Filtering (ASF) for large-scale hotword lists
- +58% F1 improvement on AISHELL-1 named entity subtest

### [[sa-paraformer]] — Speaker-Attributed ASR Extension
- Extends Paraformer for multi-speaker meeting transcription
- Speaker-filling strategy + inter-CTC enhancement
- 6.1% relative SD-CER improvement over cascaded models

### [[paraformer-v2]] — Noise-Robust Multilingual Upgrade
- Replaces CIF with CTC-based token predictor
- Addresses CIF's BPE tokenization and noise sensitivity issues
- Up to 14% WER reduction on English datasets

## Benchmark Summary

| Dataset | Paraformer CER | AR Transformer CER | RTF (Paraformer) | RTF (AR) |
|---------|---------------|-------------------|------------------|----------|
| AISHELL-1 test | **5.2%** | 5.4% | 0.0037 | 0.0230 |
| AISHELL-2 test ios | **6.19%** | 6.23% | 0.0026 | 0.0168 |
| Industrial 20k hrs (far-field) | 13.94% | 14.72% | — | — |
| Industrial 20k hrs (common) | 7.97% | 8.66% | — | — |

Timestamp prediction (Paraformer-TP vs force-alignment):
- AISHELL: AAS 71.0ms vs 80.1ms (FA)
- Industrial: AAS 65.3ms vs 60.3ms (FA), gap <10ms

## Deployment & Ecosystem

- **Runtime**: ONNX, Libtorch, TensorRT for CPU/GPU/Android/iOS
- **AMP Quantization**: Accelerated inference with mixed-precision
- **ModelScope**: Hosts all pre-trained models for one-click access
- **Multilingual**: English, French, German, Spanish, Russian, Japanese, Korean, etc.

## Relationships

- [[paraformer]] — Core ASR architecture
- [[seaco-paraformer]] — Hotword customization extension
- [[sa-paraformer]] — Speaker-attributed multi-speaker extension
- [[paraformer-v2]] — CTC-based successor for noise-robust multilingual
- [[fun-codec]] — Neural codec toolkit extension
- [[qwen3-asr]] — Alibaba's LLM-based ASR (2026), different architectural approach
- [[nim4-asr]] — NIO's LLM-based ASR (2026), production-grade alternative

## References

- arXiv 2206.08317 — Paraformer (2022-06)
- arXiv 2305.11013 — FunASR Toolkit (2023-05)
- arXiv 2308.03266 — SeACo-Paraformer (2023-08)
- arXiv 2309.07405 — FunCodec (2023-09)
- arXiv 2310.04863 — SA-Paraformer (2023-10)
- arXiv 2409.17746 — Paraformer-v2 (2024-09)
- GitHub: github.com/alibaba-damo-academy/FunASR
- GitHub: github.com/alibaba-damo-academy/FunCodec
