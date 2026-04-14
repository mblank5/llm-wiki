---
title: X Opd
created: 2026-04-06
updated: 2026-04-10
type: concept
tags: [distillation, on-policy, speech-model, multimodal]
sources: []
---

# X-OPD (Cross-Modal On-Policy Distillation)

X-OPD is a novel Cross-Modal On-Policy Distillation framework designed to systematically align the capabilities of Speech LLMs to their text-based counterparts. It enables the Speech LLM to explore its own distribution via on-policy rollouts, where a text-based teacher model evaluates these trajectories and provides token-level feedback, effectively distilling teacher's capabilities into student's multi-modal representations.

**Related:** [[on-policy-distillation]] | [[full-duplex-speech-model]] | [[speech-llm]] | [[seeduplex]]

## Core Mechanism

### Cross-Modal Alignment Data
Defines a parallel dataset D={(S_i,T_i)} of paired speech and text prompts with Semantic Invariance requirement.

### Robust Multi-sampling Rollout
Samples n candidate trajectories per prompt to reduce variance in gradient estimation.

### Dual-Advantage Function
- **In-modal advantage**: A_im(y_t) = log pi_phi(y_t|T,y_<t) - log pi_theta(y_t|T,y_<t)
- **Cross-modal advantage**: A_cm(y_t) = log pi_phi(y_t|T,y_<t) - log pi_theta(y_t|S,y_<t)

### Optimization Objective
L(theta) = lambda * L_im(theta) + (1-lambda) * L_cm(theta)

Where L_im and L_cm are policy gradient losses over m rollouts with probability ratio correction.

## Key Advantages
- Eliminates dependency on ground truth data
- Allows use of open-source models with undisclosed training data
- Minimizes catastrophic forgetting of acoustic capabilities
- Achieves low-cost, high-efficiency cross-modal alignment

## Experimental Results
- Reduced average performance drop for Qwen3-Omni-A3B-Instruct from 11.29% to 3.43% (speech) and 5.51% to 0.97% (text)
- Outperforms SFT, Offline KD, and GKD baselines
- Preserves pre-trained capabilities (MMAR benchmark: 69.3% vs 59.9% for baselines)
- Optimal lambda=0.5 balances cross-modal synergy

## Relation to Existing Concepts
- Extends [[on-policy-distillation]] to speech-text cross-modal setting
- Contrasts with [[vold]]: focuses on speech modality rather than vision-language transfer
- Uses dual advantage functions unlike [[video-opd]]'s single reverse KL supervision
- Related to [[generalized-on-policy-distillation|G-OPD]] but with modality-specific advantage decomposition
- Similar to [[proximal-policy-distillation|PPD]] in using policy gradients but without PPO clipping
- See [[opd-tokenizer-requirement]] for the tokenizer and special-token mismatch issue that affects cross-modal OPD

[src: raw/ingested/2026/03/2603.24596.md]