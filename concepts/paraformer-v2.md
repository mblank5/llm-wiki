---
title: "Paraformer-v2 — Noise-Robust Multilingual NAR ASR"
created: 2026-05-01
updated: 2026-05-01
type: concept
tags: [model, architecture, speech-model, end-to-end, open-source]
sources: [raw/papers/2024/09/2409.17746.md, raw/papers/2022/06/2206.08317.md]
---
# Paraformer-v2 — Noise-Robust Multilingual NAR ASR

> arXiv 2409.17746 | 2024-09 | Alibaba DAMO Speech Lab
> Replaces CIF with CTC predictor — solves CIF's BPE and noise sensitivity issues

## Core Problem

The original Paraformer's CIF predictor works well for Mandarin (character-level tokenization) but faces two critical limitations:

### 1. Multilingual Limitation — BPE Tokenization

Mandarin: 1 character ≈ 1 syllable → relatively fixed token-to-speech mapping.
English with BPE: Tokens have **highly variable lengths** (e.g., "the" = 1 token, "international" = 3-4 tokens). CIF's monotonic accumulation struggles with this variability.

```
Mandarin: "你 好 世 界" → 4 tokens, predictable mapping
English:  "in ter na tion al" → 5 BPE tokens for 1 word, unpredictable
```

### 2. Noise Sensitivity

CIF relies on accumulating frame-level weights to detect token boundaries. Under noisy conditions:
- Frame weights become unreliable → boundary detection fails
- Token count estimation degrades → length mismatch
- Particularly problematic in meeting/conference environments

## Solution: CTC-Based Token Predictor

Paraformer-v2 replaces the CIF module with a **CTC-based predictor**:

```
              Paraformer-v2 Architecture
═══════════════════════════════════════════════════════════

     f-banks → ┌─────────────┐
               │  Encoder    │  (Conformer)
               │  H₁:ₜ       │
               └──────┬──────┘
                      │
              ┌───────┴───────────────┐
              ▼                       ▼
     ┌──────────────┐        ┌──────────────┐
     │ CTC Predictor│        │   NAR Decoder │
     │              │        │               │
     │ CTC posteriors│       │ E_ctc → Y'    │
     │ → E_ctc      │───────→│               │
     └──────────────┘        └───────┬───────┘
                                     ▼
                               Final Y''
```

### Training Phase

CTC generates frame-wise posteriors over the token vocabulary:
```
P_ctc = CTC(H₁:ₜ)    # Shape: (T, V) where V = vocab size
```

Token embeddings are extracted based on CTC alignment:
```
E_ctc = Align(H, P_ctc, Y_target)    # Use CTC path to align encoder outputs to tokens
```

The decoder is trained with these CTC-aligned embeddings.

### Inference Phase

The key innovation is how token embeddings are generated without ground truth:

```
# 1. Greedy CTC decoding:
y_ctc = argmax(P_ctc, dim=-1)    # Shape: (T,) — one token per frame

# 2. Compression: merge consecutive identical predictions, remove blanks
y_compressed = Compress(y_ctc)   # Remove duplicates and <blank> tokens

# Example:
# y_ctc:     [b, h, h, e, e, b, l, l, l, o, b, b, b]
# compressed:        [h,    e,    l,          o]
# E_ctc:     → 4 token embeddings for "hello"
```

The compression step:
1. Average encoder hidden states for frames with **identical CTC predictions**
2. Remove all `<blank>` predictions
3. Result: token embeddings aligned to the compressed sequence

```
E_ctcᵤ = (1/|Fᵤ|) Σₜ∈Fᵤ Hₜ    # Average over frames predicting same token
```

Where Fᵤ is the set of frames predicting token u.

## Why CTC Over CIF?

| Aspect | CIF (Paraformer) | CTC (Paraformer-v2) |
|--------|-----------------|---------------------|
| Mechanism | Soft accumulation + threshold | Frame-wise posteriors + compression |
| BPE handling | Poor — variable token lengths break monotonicity | **Good** — naturally handles variable-length tokens |
| Noise robustness | Fragile — weight accumulation breaks | **Robust** — posteriors are more stable |
| Length prediction | MAE loss on Σαₜ | Implicit from CTC compression |
| Train/inference gap | Dynamic β reduces but doesn't eliminate | Minimal — same mechanism both phases |
| Monotonicity | Strictly monotonic | Strictly monotonic |

CTC's frame-level approach is inherently more robust because:
1. Each frame makes an **independent** prediction — noisy frames don't corrupt accumulated sums
2. The compression step naturally handles variable-length tokens
3. No threshold parameter (β) to tune

## Loss Function

```
L = λ_ctc · L_CTC + λ_ce · L_CE
```

The CTC loss guides the predictor, while the CE loss trains the decoder. The combined objective ensures both accurate token alignment and accurate token prediction.

## Benchmarks

### AISHELL-1 (Mandarin)

| Model | Dev CER | Test CER |
|-------|---------|----------|
| AR Conformer AED | 4.5 | 5.0 |
| Paraformer (CIF) | 4.6 | 5.2 |
| **Paraformer-v2 (CTC)** | **4.3** | **4.8** |

Paraformer-v2 slightly **outperforms** both AR and original Paraformer on Mandarin.

### LibriSpeech (English)

| Model | Test-clean WER | Test-other WER |
|-------|---------------|----------------|
| AR Conformer Transducer | 2.8 | 6.2 |
| Paraformer (CIF) | 4.1 | 9.3 |
| **Paraformer-v2 (CTC)** | **3.1** | **6.8** |

On English, Paraformer-v2 achieves a **dramatic improvement** over CIF-based Paraformer:
- Test-clean: 4.1 → 3.1 WER (**24% relative improvement**)
- Test-other: 9.3 → 6.8 WER (**27% relative improvement**)

The CIF→CTC swap nearly closes the gap to AR transducer on English.

### In-House English (50,000 hrs)

| Model | WER |
|-------|-----|
| Paraformer (CIF) | Baseline |
| **Paraformer-v2 (CTC)** | **-14% relative WER** |

On a 50,000-hour industrial English dataset, Paraformer-v2 achieves **over 14% WER reduction** compared to the original Paraformer.

### Noise Robustness

Under simulated noisy conditions (meeting environment):
- Original Paraformer (CIF): Significant WER degradation
- Paraformer-v2 (CTC): **Superior noise robustness** — maintains accuracy where CIF fails

## Comparison with Related Models

| Model | Predictor | Language | Noise Robustness | Inference Speed |
|-------|-----------|----------|-----------------|-----------------|
| Paraformer | CIF | Mandarin-focused | Moderate | ~10x AR |
| **Paraformer-v2** | **CTC** | **Multilingual** | **High** | **~10x AR** |
| AR Conformer AED | — | Multilingual | Moderate | 1x |
| [[nim4-asr]] | CR-CTC | Multilingual | High | Streaming |

Paraformer-v2 and [[nim4-asr]] both leverage CTC-based approaches, but for different purposes:
- Paraformer-v2: CTC as **token predictor** for NAR parallel decoding
- nim4-asr: CTC (CR-CTC) as **pretraining objective** for LLM-based ASR

## Evolution of Paraformer Family

```
Paraformer (2022)
  │  CIF predictor, Mandarin focus
  ├──→ SeACo-Paraformer (2023) — + hotword customization
  ├──→ SA-Paraformer (2023) — + speaker attribution
  └──→ Paraformer-v2 (2024) — CTC predictor, noise-robust, multilingual
```

## Related

- [[paraformer]] — Original CIF-based architecture
- [[funasr]] — Production toolkit
- [[nim4-asr]] — LLM-based ASR using CTC pretraining (2026)
- [[qwen3-asr]] — Alibaba's LLM-ASR (2026)
- [[fun-codec]] — Neural codec toolkit (codec tokens → Paraformer ASR pipeline)
