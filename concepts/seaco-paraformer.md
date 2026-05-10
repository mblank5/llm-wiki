---
title: "SeACo-Paraformer — Non-Autoregressive ASR with Hotword Customization"
created: 2026-05-01
updated: 2026-05-01
type: concept
tags: [model, architecture, speech-model, open-source, streaming]
sources: [raw/papers/2023/08/2308.03266.md, raw/papers/2023/05/2305.11013.md]
---
# SeACo-Paraformer — Semantic-Augmented Contextual Paraformer

> arXiv 2308.03266 | Alibaba DAMO Speech Lab | GitHub: R1ckShi/SeACo-Paraformer
> NAR ASR + explicit hotword customization without sacrificing parallel decoding

## Core Problem

Commercial ASR systems need **hotword customization** — users should be able to bias recognition toward names, places, domain-specific terms. Prior approaches:

| Approach | Type | Issue |
|----------|------|-------|
| CLAS (Contextual LAS) | Implicit | Training instability, invisible activation, hard to debug |
| CPP Network | Implicit | Adds CTC head; couples general ASR with contextual modeling |
| CIF ColDec | Explicit | Good decoupling, but backbone model accuracy lags AED |

**SeACo-Paraformer** combines:
1. Paraformer's AED-level accuracy + NAR efficiency
2. CIF ColDec's explicit, decoupled hotword prediction
3. Attention Score Filtering (ASF) for large-scale hotword lists

## Architecture

```
              SeACo-Paraformer Architecture
═══════════════════════════════════════════════════════════

  Speech ──→ Encoder ──→ Predictor (CIF) ──→ Eₐ (acoustic embeds)
                                      │
                    ┌───────────────────┤
                    ▼                   ▼
          ┌─────────────────┐  ┌──────────────────┐
          │  ASR Decoder    │  │ Hotword Embedder │
          │  (Paraformer)   │  │  (LSTM)          │
          └────────┬────────┘  └────────┬─────────┘
                   │                    │
                   │              E_h (hotword embeds)
                   │                    │
                   ▼                    ▼
          ┌─────────────────────────────────────┐
          │   CIF-based Contextual Module       │
          │                                     │
          │   MHA(Eₐ, E_h) → g (hotword sem.)   │
          │   FF(g) → P_hotword (per-token)     │
          │                                     │
          │   E'_a = Eₐ + α · MHA_output        │
          └──────────────────┬──────────────────┘
                             ▼
                   Final ASR Prediction
```

## Key Mechanism 1: CIF-Based Contextual Module

The contextual module runs **synchronously** with ASR output, leveraging CIF's monotonic alignment:

```
gₜ = MHA(Eₐₜ, E_h, E_h)          # Attend hotwords from each token position
P_hotwordₜ = FF(gₜ)               # Feed-forward → hotword probability
```

The hotword embedding E_h is produced by an LSTM over the hotword list:
```
E_h = LSTM(w₁, w₂, ..., wₙ)      # Last hidden state
```

At each CIF output step, the model produces an **external hotword probability** independent of the main ASR prediction. These two probability streams are merged at inference.

## Key Mechanism 2: Attention Score Filtering (ASF)

When the hotword list grows large (thousands of entities), performance degrades. ASF filters irrelevant hotwords:

```
# Compute attention scores between acoustic context and each hotword
scoreⱼ = attention_score(Eₐ, E_hⱼ)

# Keep only hotwords above threshold τ
E_h_filtered = {E_hⱼ | scoreⱼ > τ}
```

This prevents attention dilution — when too many hotwords compete for attention weight, none receives sufficient signal. ASF maintains high F1 even with large hotword inventories.

## Key Mechanism 3: Explicit Hotword Prediction

Unlike implicit methods (CLAS) that bias the ASR decoder internally, SeACo-Paraformer's contextual module produces a **separate hotword probability stream**:

```
# ASR branch: P(yₜ | X)
# Hotword branch: P(hotword | Eₐₜ, E_h)

# Merge at inference:
P_final = P(yₜ | X) + γ · P(hotword) · indicator(hotword matches yₜ)
```

The hotword training target uses position-aware labels:
```
# ASR target: "A B C D E F"
# Hotword target: "A B # # # #"  (when "A B" is a hotword)
```

This decoupling means:
- Hotword module parameters are **independent** of ASR parameters
- Bad cases are easier to debug (you can see whether the hotword detector failed or the ASR failed)
- The hotword detector works as an explicit **hotword presence signal**

## Benchmarks

### Hotword Customization Results

| Dataset | Hotwords | w/o Hotword CER | w/ Hotword CER | F1 (w/o) | F1 (w/) |
|---------|----------|----------------|---------------|----------|---------|
| AISHELL NE subtest | 187 entities | 10.01 | **4.55** | 27 | **85** |
| Industrial AI domain | 70 | 7.96 | **6.31** | 82 | **93** |
| Industrial common domain | 67 | 9.47 | **8.75** | 80 | **88** |

Key result: **+58% F1 improvement** on AISHELL-1 named entity subtest.

### ASF Impact

| Hotword Scale | w/o ASF CER | w/ ASF CER |
|--------------|------------|-----------|
| Small (< 50) | Baseline | Comparable |
| Large (500+) | Degrades | **Maintained** |

ASF prevents the performance drop that occurs when large hotword lists dilute attention.

### 50,000 hrs Industrial Data

Full model trained on 50k hours of industrial data, outperforming strong baselines (CLAS, CPP Network variants) in customization tasks while maintaining NAR parallel decoding efficiency.

## Comparison: Explicit vs Implicit Contextual ASR

| Aspect | CLAS (Implicit) | CPP (Implicit) | CIF ColDec | **SeACo-Paraformer** |
|--------|----------------|----------------|------------|---------------------|
| Backbone | LAS (AR) | CTC/Trans/Trans | CIF-AED | **Paraformer (NAR)** |
| Hotword signal | Implicit bias | Implicit CTC | Explicit | **Explicit** |
| Decoupled | No | No | Yes | **Yes** |
| Parallel decoding | No | Varies | No | **Yes** |
| Large hotword support | Poor | Moderate | Poor | **Yes (ASF)** |
| Train stability | Issues | OK | Good | **Good** |

## Related

- [[paraformer]] — Base NAR architecture
- [[funasr]] — Production toolkit (includes Contextual Paraformer)
- [[fun-codec]] — Neural codec toolkit
- [[nim4-asr]] — LLM-ASR with phoneme-level RAG hotwords (2026), alternative approach to customization
