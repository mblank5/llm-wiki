---
title: 'Self-Improving Pretraining: Using Post-Trained Models to Pretrain Better Models'
created: 2026-05-05
updated: 2026-05-05
type: concept
tags:
- pretraining
- rl
- alignment
- safety
- on-policy
- training
sources:
- raw/papers/2026/01/2601.21343.md
---

# Self-Improving Pretraining

## Core Problem Definition

**Formal Statement.** Let $\pi_\theta$ be a policy model being pretrained. Standard pretraining optimizes next-token prediction: $\max_\theta \sum_{t} \log \pi_\theta(x_t | x_{<t})$. This ignores desirable properties (safety, factuality, quality) that are only addressed during post-training. The paper asks: *Can we leverage an already strong post-trained model $M_{\text{teacher}}$ to improve the pretraining signal itself?*

**Key insight:** Post-training cannot fully correct patterns learned during pretraining. If safety/factuality/quality are only enforced after pretraining, the model has already internalized unsafe, nonfactual, or low-quality patterns. The goal is to move these properties into pretraining itself.

**Setting:** Given:
- A stream of pretraining documents (e.g., SlimPajama, RedPajama)
- A fixed strong post-trained model $M_{\text{teacher}}$ (e.g., Llama-3.1-8B-Instruct)
- A policy model $\pi_\theta$ being trained from scratch or via continual pretraining

Split each document into a prefix $x_{1,\dots,j-1}$ and a suffix $x_j$ of length $N=128$ tokens. The task is to generate a high-quality suffix given the prefix: $\bar{x}_j \sim \pi_\theta(\cdot | x_{1,\dots,j-1})$.

## Method

### Two Roles for the Teacher Model

**1. Suffix Rewriter.** Given prefix $x_{1,\dots,j-1}$ and suffix $x_j$, the rewriter produces a rewritten suffix $\hat{x}_j$ that is superior to $x_j$ along three dimensions:
- **Quality**: Upgrades low-quality corpus segments
- **Safety**: Given unsafe prefix + unsafe suffix $\to$ rewrites to safe suffix (crucially, the prefix stays unsafe, so the model learns to *steer away*)
- **Augmentation**: Diversifies training signal

**2. Suffix Judge.** Evaluates candidates (policy rollouts, original suffix, rewritten suffix) for quality, safety, or factuality. Used to assign RL rewards.

### Training Algorithm

The policy is trained using **online DPO** (chosen over GRPO for off-policy capability):

1. At each step, the document stream provides a prefix $x_{1,\dots,j-1}$ and original suffix $x_j$
2. Generate $K=16$ rollouts from current policy: $\{y_1, \dots, y_K\} \sim \pi_\theta(\cdot | x_{1,\dots,j-1})$
3. Generate a rewritten suffix $\hat{x}_j$ from the teacher rewriter
4. The judge $J$ scores all candidates (rollouts, original suffix, rewrite)
5. Form DPO pairs from ranked candidates and update $\pi_\theta$ using:

$$\mathcal{L}_{\text{DPO}} = -\log \sigma\left(\beta \log \frac{\pi_\theta(y_w|x)}{\pi_{\text{ref}}(y_w|x)} - \beta \log \frac{\pi_\theta(y_l|x)}{\pi_{\text{ref}}(y_l|x)}\right)$$

where $y_w$ is the judge-preferred candidate and $y_l$ is the dispreferred one.

**Early in training:** Model rollouts are low quality, so DPO pairs come from (original suffix vs. rewrite). **Later in training:** As the model improves, RL starts rewarding winning rollouts (see Figure 8 in paper — rollout chosen rate increases during training).

### Reward Functions

For **safety rewriting** (Eq. 1-2):
$$R_{\text{safe}} = \begin{cases} 1.0 & \text{if } \bar{x}_j = x_j \text{ (exact match for safe suffixes)} \\ 0.0 & \text{otherwise} \end{cases}$$

$$R_{\text{unsafe}} = \frac{1}{2}\left(J_{\text{qual}}(\bar{x}_j, x_j | x_{1,\dots,j-1}) + J_{\text{safe}}(\bar{x}_j)\right)$$

For **factuality**: Judge outputs `No Hallucination` (reward 1), `Possible Hallucination` (reward 0.5), or `Definite Hallucination` (reward 0), combined with quality score.

### Judge Training

The judge itself is fine-tuned from Llama-3.1-8B-Instruct using **GRPO** on synthetically labeled data:
- Quality task: 75,432 training samples (original vs. GPT-spoiled suffixes)
- Safety task: 3,192 training samples (safe vs. unsafe suffixes, filtered by GPT-OSS-120B consensus over 8 seeds)
- Training: batch size 256, 16 generations per prompt, $T=0.6$, $top\_p=0.6$

### Rewriter Training

Fine-tuned from Llama-3.1-8B-Instruct using GRPO on 73,080 samples. Achieves 98% token overlap on copy task (safe suffixes) and ~0.63 overlap on unsafe rewrites (meaningful changes).

## Training Configuration

### Continued Pretraining
| Parameter | Value |
|-----------|-------|
| Base model | Llama-3.1-8B (1.4B in some experiments) |
| GPUs | 64 |
| Batch size | 256 |
| Rollouts per prompt | 16 |
| Temperature | 1.0 |
| top_p | 1.0 |
| Learning rate | 5.0e-06 (cosine) |
| Warmup steps | 100 |
| Training steps | 2,000 |
| Max sequence length | 2048 |
| Suffix length N | 128 |
| Loss | Online DPO |

### From-Scratch Pretraining
| Parameter | Value |
|-----------|-------|
| Training steps | 21,000 |
| Learning rate | 5.0e-04 |
| Warmup steps | 2,000 |
| Rollouts per prompt | 1 |

### Datasets
- **SlimPajama (SP)**: Aggressively filtered, higher quality
- **RedPajama (RP)**: Less filtered; used for safety experiments (contains unsafe content)
- **Judge training data**: Synthetically generated from SP and RP
- **Evaluation**: RP test split, RealToxicityPrompts, ToxiGen, XStest, FActScore, HaluEval, TruthfulQA, MMLU, BoolQ, PIQA, HellaSwag, ARC-e/c, OpenBookQA, SIQA

### Judge Models
- **Llama-3.1-8B-Instruct** (fine-tuned): Used for safety DPO pairs
- **GPT-OSS-120B**: Used for quality and factuality judgments (temperature 0.7, 8 seeds majority vote)

## Experimental Results

### Main Results: Continued Pretraining (Table 1)

**Quality Optimization:**
| Metric | Llama Pretrain Baseline | Self-Improving | Delta |
|--------|------------------------|----------------|-------|
| Gen Quality (Std Prefix) | 49.0 | **86.3** | +37.3 |
| Gen Quality (Unsafe Prefix) | 46.8 | **50.8** | +4.0 |
| Standard Evals (Avg) | 49.4 | **87.9** | +38.5 |
| Coherence Eval | — | **87.9** | — |

**Factuality Optimization:**
| Metric | Llama Base | Baseline | Self-Improving |
|--------|-----------|----------|----------------|
| Gen Quality (Std Prefix) | 50.0 | 49.0 | **84.0** |
| Factuality Evals (Avg) | 42.3 | 44.0 | **57.6** (+36.2% rel.) |

**Safety Optimization:**
| Metric | Llama Base | Baseline (RP) | Self-Improving |
|--------|-----------|---------------|----------------|
| Gen Quality (Unsafe Prefix) | 50.0 | 52.6 | **77.7** |
| Safety Evals (Avg) | 76.9 | 75.5 | **91.1** (+18.5% rel.) |

### From-Scratch Pretraining (Table 2)

| Method | Quality (Std) | Quality (Unsafe) | Safety Evals |
|--------|--------------|-------------------|--------------|
| Pretrain Baseline | 1.3 | 2.4 | 85.2 |
| Pretrain on Rewrites | 1.6 | 2.4 | 96.7 |
| SIPP RF-NLL (suffix vs. rewrite) | 5.3 | 25.8 | 96.4 |
| **SIPP RF-NLL (rollout vs. rewrite)** | **32.4** | **12.1** | **97.5** |

### Standard Evaluation Breakdown (Table 3)

BoolQA, PIQA, HellaSwag, ARC-e, ARC-c, OBQA, SIQA, MMLU — Self-Improving Pretraining consistently outperforms baselines across all standard benchmarks.

### Ablation Studies

1. **Loss function comparison**: Online DPO > RF-NLL > SFT on rewrites > SFT on rollouts
2. **Number of rollouts**: Scaling from 1 to 16 rollouts improves performance; diminishing returns after 8
3. **Judge comparison**: GPT-OSS-120B judge > trained Llama-3.1-8B judge for quality/factuality; fine-tuned judge competitive for safety
4. **Rewrite vs. no-rewrite**: Using the rewriter provides significant gains over judge-only approaches for safety
5. **Rollout chosen rate**: Starts near 0%, increases to ~40-60% as model improves (Figure 8)

## Comparison with Existing Methods

| Approach | Safety Improvement | Factuality Improvement | Quality Win Rate |
|----------|-------------------|----------------------|------------------|
| Standard pretraining + SFT | Baseline | Baseline | ~50% |
| Data filtering only | Moderate | Low | <50% |
| RLHF / DPO (post-training only) | +10-15% | +5-10% | 55-65% |
| **Self-Improving Pretraining** | **+18.5% rel.** | **+36.2% rel.** | **up to 86.3%** |

Key distinction from [[on-policy-distillation]]: This method uses the teacher as judge + rewriter rather than for distillation targets. The student learns from the teacher's *evaluations* of sequences, not from direct imitation.

## Critical Analysis

### Strengths
1. **Conceptual elegance**: Closes the loop — post-trained models improve pretraining of the next generation
2. **Multiple simultaneous improvements**: Quality, safety, and factuality all improve together
3. **Strong empirical results**: Up to 86.3% win rate on generation quality is remarkable for a 1.4B model
4. **Flexible framework**: The rewriter + judge paradigm is modular — can swap in different teachers
5. **Addresses a real gap**: The pretraining/post-training disconnect is a known issue; this directly tackles it

### Weaknesses and Open Questions
1. **Teacher dependency**: Requires a strong post-trained model to bootstrap. Not applicable when no prior strong model exists (cold-start problem)
2. **Computational cost**: 64 GPUs, 16 rollouts per prompt, plus running a large judge model — significantly more expensive than standard pretraining
3. **Scalability to larger models**: Experiments only go up to 1.4B parameters (with 8B teacher). Unclear if gains persist at 70B+ scale
4. **Judge quality ceiling**: The policy can only be as good as its judge. If the teacher judge has blind spots, the student inherits them
5. **Reward hacking risk**: Policy might learn to exploit judge weaknesses rather than genuinely improve
6. **Data contamination**: Using GPT-OSS-120B as judge introduces potential contamination if test sets overlap with GPT training data

### Implications for Our Work
- **For [[agent-safety-via-rl]]**: Reinforces that safety should be baked in early, not bolted on post-hoc
- **For [[agent-r1-end-to-end-rl]]**: The DPO-based approach with pairwise comparisons is similar to R1-style training; could combine both
- **For data-centric approaches**: Suffix rewriting is a powerful data augmentation technique — even without RL, SFT on rewrites helps
- **Bootstrapping concern**: The "self-improving cycle" assumes each generation produces a better teacher. Need to verify this doesn't collapse

## Related
- [[on-policy-distillation]] — Student-teacher training with on-policy rollouts
- [[agent-safety-via-rl]] — RL-based safety training for agents
- [[grpo-rl-training]] — GRPO algorithm used for judge training
- [[agent-r1-end-to-end-rl]] — RL training paradigm for agent reasoning
- [[alignment-waltz]] — Iterative alignment approaches
