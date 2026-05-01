---
title: SA-Paraformer — Speaker-Attributed Non-Autoregressive ASR
created: 2026-05-01
updated: 2026-05-01
type: concept
tags: [model, architecture, speech-model, open-source]
sources: [raw/papers/2023/10/2310.04863.md, raw/papers/2022/06/2206.08317.md]
---
# SA-Paraformer — Speaker-Attributed Non-Autoregressive ASR

> arXiv 2310.04863 | NPU ASLP Group + Alibaba DAMO + USTC
> Extends [[paraformer]] for multi-speaker meeting transcription with 1/10 latency of AR models

## Core Problem

Speaker-Attributed ASR (SA-ASR) must solve two tasks simultaneously:
1. **Transcribe** each speaker's speech
2. **Attribute** each word to the correct speaker

This is critical for meeting transcription, where overlapping speech, unknown speaker counts, and far-field recording create complex acoustic conditions.

Prior approaches:

| Approach | Method | Limitation |
|----------|--------|------------|
| Cascaded (FD-SOT, WD-SOT) | Speech separation + diarization + ASR | Error propagation; suboptimal joint objective |
| Joint AR SA-ASR | End-to-end with AR decoder | Large RTF — sequential generation for multi-speaker output |

SA-Paraformer replaces the AR decoder with Paraformer's NAR decoder, achieving **comparable accuracy with 1/10 RTF**.

## Architecture

```
            SA-Paraformer Architecture
══════════════════════════════════════════════════════════════

  Speech X ──→ ┌──────────────┐
               │  ASREncoder  │ ──→ H_asr (Conformer 12 layers)
               └──────┬───────┘
                      │
           ┌──────────┼──────────┐
           ▼          ▼          ▼
    ┌──────────┐ ┌──────────┐ ┌──────────────┐
    │SpeakerEnc│ │Predictor │ │Inter-CTC     │
    │ H_spk    │ │ (CIF)    │ │ (mid-layer)  │
    │(d-vectors)│ │ E_a      │ │ L_interCTC   │
    └─────┬────┘ └─────┬────┘ └──────────────┘
          │            │
          ▼            ▼
    ┌─────────────────────────┐
    │    SpeakerDecoder       │
    │  Layer 1: MHA(E_a,      │
    │           H_asr, H_spk) │
    │  Layer 2: Transformer   │
    │  Cosine-dist attention  │
    │  → d_n (speaker profile │
    │     per token)          │
    └──────────┬──────────────┘
               │
               ▼ d_n injected into FF
    ┌─────────────────────────┐
    │    ASRDecoder           │
    │  Pass 1: E_a + H_asr    │
    │          + d_n (no grad)│
    │  Pass 2: E_s + H_asr    │
    │          + d_n (w/ grad)│
    └──────────┬──────────────┘
               ▼
         Y'' (speaker-attributed tokens)
```

### 6 Core Modules

1. **ASREncoder** — 12-layer Conformer, transforms X → H_asr
2. **SpeakerEncoder** — Res2Net-based d-vector extractor (256-dim), X → H_spk
3. **Predictor** — CIF mechanism, H_asr → Eₐ (acoustic embeddings per token)
4. **SpeakerDecoder** — 2 Transformer layers + cosine-distance attention, produces speaker profile dₙ per token
5. **Sampler** — GLM, generates semantic embedding Eₛ (training only)
6. **ASRDecoder** — 6-layer Transformer, takes Eₐ/H_asr/dₙ → predictions

## Key Innovation 1: Speaker-Filling Strategy

The model struggles with unknown speaker counts because Eₐ lacks contextual information for speaker identification.

**Filling speaker (f-speaker) strategy**: Expand the speaker inventory to the maximum number of speakers in the batch. For redundant (non-existent) speakers, fill the cosine distance bₙ,ₖ with **random values in [-0.5, 0.5]** instead of -∞.

```
bₙ,ₖ = (qₙ · dₖ) / (|qₙ| · |dₖ|)

# For real speakers: standard cosine similarity
# For redundant speakers: random value ∈ [-0.5, 0.5]
```

This prevents the model from overconfidently assigning tokens to the wrong speaker — the random perturbation acts as a soft "don't know" signal.

**Interfering speaker (i-speaker) strategy**: Add extra speaker profiles to the inventory during training, forcing the model to learn to discriminate.

Combined (f&i-speaker): Best performance.

## Key Innovation 2: Inter-CTC Enhancement

Since NAR models rely heavily on acoustic representations (no sequential context from previous tokens), the encoder's acoustic signal quality is critical.

An **intermediate CTC loss** is attached to a middle layer of the Conformer encoder:

```
L' = L_MAE + λ₁·L_CTC + λ₂·L_interCTC + (1-λ₁-λ₂)·L_CE + L_spk
```

With λ₁ = 0.3, λ₂ = 0.3. The inter-CTC loss strengthens frame-level acoustic modeling, improving downstream speaker identification and ASR accuracy.

## Key Innovation 3: Token-Level Serialized Output Training (t-SOT)

To handle multi-speaker output, transcriptions are serialized by token end times (chronological order):

```
Speaker1: "你好" ⟨cc⟩ "世界" ⟨cc⟩
Speaker2: "今天" "天气" "很好"
→ Serialized: "你好" ⟨cc⟩ "今天" "天气" "世界" ⟨cc⟩ "很好"
```

Finding: **Training without the ⟨cc⟩ separator** significantly reduces deletion errors (26.5% → 6.5%). The NAR model struggles to predict acoustic boundaries for separator tokens that carry no acoustic information.

| Model | Separator | Ins. | Del. | Sub. | CER |
|-------|-----------|------|------|------|-----|
| A1 | With ⟨cc⟩ | 10.1 | **26.5** | 6.5 | 43.1 |
| A2 | Without ⟨cc⟩ | 11.7 | **6.5** | 7.1 | 38.6 |

## Speaker Decoder Details

Cosine-distance-based attention:
```
bₙ,ₖ = (qₙ · dₖ) / (|qₙ| · |dₖ|)           # Cosine similarity
βₙ,ₖ = exp(cos(bₙ,ₖ, dₖ)) / Σⱼ exp(...)     # Softmax over inventory
dₙ = Σₖ βₙ,ₖ · dₖ                           # Weighted profile
```

The weighted speaker profile dₙ is injected into the ASR decoder's first-layer FFN:
```
E_c,1 = E'_c,1 + FF(E'_c,1 + W_spk · dₙ)
```

## Benchmarks (AliMeeting Corpus)

AliMeeting: 104.75 hrs training, 42.27% average speech overlap ratio, far-field 4-channel recording.

| Approach | Eval SD-CER | Test SD-CER | RTF (CPU) | RTF (GPU) |
|----------|------------|-------------|-----------|-----------|
| Cascaded: FD-SOT | 41.0 | 41.2 | — | — |
| Cascaded: WD-SOT | 36.0 | 37.1 | — | — |
| Joint AR SA-ASR | 31.8 | 34.7 | 0.967 | 0.315 |
| SA-Paraformer (base) | 36.2 | 38.6 | — | — |
| + inter-CTC | 34.5 | 36.9 | — | — |
| + f-speaker | 33.3 | 35.7 | — | — |
| + i-speaker | 33.1 | 35.6 | — | — |
| **+ f&i-speaker** | **32.5** | **34.8** | **0.168** | **0.032** |

Key results:
- **6.1% relative SD-CER improvement** over cascaded WD-SOT (37.1 → 34.8)
- **Comparable SD-CER to AR joint model** (34.7 vs 34.8) with **1/10 RTF**
- GPU RTF: 0.032 vs 0.315 (AR) — nearly 10x faster

### Ablation Contributions

| Addition | Eval Δ | Test Δ |
|----------|--------|--------|
| inter-CTC | -1.7% | -1.7% |
| f-speaker | -1.2% | -1.2% |
| i-speaker | -1.2% | -1.2% |
| f&i combined | -2.0% | -2.1% |

All components contribute independently; the combined effect is approximately additive.

## Loss Function

```
L' = L_MAE + λ₁·L_CTC + λ₂·L_interCTC + (1-λ₁-λ₂)·L_CE + L_spk

L_spk = Σₙ [e^(bₙ,ᵢ) - log Σₖ P(bₙ,ₖ)]   # Speaker identification loss
```

4 loss terms jointly optimize: sequence length (MAE), ASR (CTC+CE), acoustic enhancement (inter-CTC), and speaker attribution (L_spk).

## Related

- [[paraformer]] — Base NAR architecture (encoder + CIF predictor + GLM sampler)
- [[funasr]] — Production toolkit packaging
- [[paraformer-v2]] — CTC-based Paraformer successor
- [[nim4-asr]] — LLM-based ASR with speaker handling (2026)
- [[qwen3-asr]] — Alibaba's LLM-ASR (2026), different approach to speaker attribution
