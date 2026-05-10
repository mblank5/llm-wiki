---
title: Modality Preference of Omni-Modal LLMs
created: 2026-04-27
updated: 2026-04-27
type: concept
tags:
- multimodal
- alignment
- benchmark
- architecture
sources:
- raw/papers/2026/04/2604.16902.md
---

# Modality Preference of Omni-Modal LLMs: Beyond Text-Dominance

## Core Problem

When processing multimodal inputs, models often implicitly assign unequal weights to different modalities. In traditional Vision-Language Models (VLMs), this is broadly perceived as "text-dominance bias." However, for native omni-modal LLMs (OLLMs) that integrate text, image, audio, and video in a unified representation space, how they navigate internal modality competition remains a fundamentally unresolved black box.

Uncontrolled modality bias is a primary catalyst for cross-modal hallucinations, where the model fabricates responses based on its preferred modality while ignoring factual signals from others.

## Technical Solution

The paper establishes a systematic framework to quantify, analyze, and leverage modality preferences in OLLMs.

### 1. Tri-Modal Conflict Framework

**Problem Formulation**: Given an OLLM `O` and a query with three modalities `{m_txt, m_vis, m_aud}` where every pair conveys semantically contradictory information, the model's output must align with exactly one modality.

**Preference definition**:
```
P(ŷ ~ m_i | conflict(m_txt, m_vis, m_aud))
```
This conditional probability measures the tendency to rely on modality `m_i` when it conflicts with others.

### 2. Data Construction

Built on the Perception subset of **XModBench**:
- Categorized into 6 semantic categories: Animals, Human Activities, Musical Instruments/Music, Home Appliances/Machinery, Vehicles/Traffic, Nature/Environmental Sounds
- Constructed conflict triplets `(x_i^T, x_j^I, x_k^A)` where each modality comes from a different category (c_i ≠ c_j ≠ c_k)
- All 20 valid category triplets `(6 choose 3)` with balanced sampling
- Standardized modality-agnostic question: "Which option best describes what this example is mainly about?"
- Three options presented in randomized order

### 3. Modality Selection Rate (MSR)

```
MSR(m) = (1/N) Σ_i 1[ŷ_i = opt(m)]
```

Where `N` = total conflict samples, `opt(m)` = the option grounded in modality `m`. Higher MSR = stronger preference.

### 4. Layer-Wise Probing

To trace the emergence of modality preference:
- Extract hidden states at each layer
- Train a single-layer MLP as a linear probe to predict the model's final modality preference
- Probe accuracy on held-out test set quantifies how much each layer encodes modality preference

## Key Findings

### Finding 1: Visual Preference Dominance

Unlike traditional VLMs that show absolute text dominance, most OLLMs exhibit a **pronounced visual bias**:
- **Gemini 3.1 Pro**: MSR_visual = 72%, MSR_text = 7% on tri-modal conflicts
- This represents a fundamental paradigm shift from text-dominance to vision-dominance

### Finding 2: Mid-to-Late Layer Emergence

Modality preference is **not static** — it emerges progressively:
- Shallow layers: No clear modality preference signal
- Mid-to-late layers: Preference arises abruptly and stabilizes
- This correlates with representations becoming increasingly abstract

### Finding 3: Hallucination Diagnosis

Layer-wise modality preference probes serve as effective hallucination detectors:
- Abnormal increase in predicted preference probability for the interfering modality consistently accompanies hallucinations
- On POPE dataset: **AUROC = 94%** for hallucination detection (vs. 50% random, 51% earlier layers)
- Validated across POPE, AVHBench, and AHa-Bench

## Comparison with Prior Work

| Aspect | Traditional VLM Studies | This Work (OLLMs) |
|--------|------------------------|-------------------|
| Modailties | Vision + Language | Text + Vision + Audio |
| Dominant modality | Text | **Visual** |
| Analysis level | Coarse (output only) | Layer-wise probing |
| Application | Understanding bias | Hallucination diagnosis |

## Open Questions

1. **Why visual preference?**: What architectural or training factors cause OLLMs to prefer visual over textual information?

2. **Preference modifiability**: Can training interventions (e.g., modality-balanced loss) shift the preference distribution?

3. **Task-dependent preferences**: Does the dominant modality shift depending on task type (e.g., audio-centric vs. visual-centric tasks)?

4. **Probing limitations**: Are linear probes sufficient to capture complex modality interaction patterns, or do we need more expressive probes?

## See Also

- [[omni-modal-llm]] — Omni-modal LLM architecture overview
- [[chain-of-modality]] — Dynamic modality orchestration
- [[omnitrace-attribution]] — Attribution in omni-modal LLMs
