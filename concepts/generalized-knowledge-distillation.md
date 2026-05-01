---
title: Generalized Knowledge Distillation (GKD)
created: 2026-05-01
updated: 2026-05-01
type: concept
tags: [distillation, on-policy, training, foundation, deepmind]
sources: [raw/papers/2023/06/2306.13649.md]
---

# Generalized Knowledge Distillation (GKD)  
*DeepMind's foundational work on on-policy distillation (2023)*

## Overview

Generalized Knowledge Distillation (GKD) — introduced by Rishabh Agarwal et al. at DeepMind — is the theoretical foundation for modern **On-Policy Distillation (OPD)**. GKD addresses the *distribution mismatch* problem in traditional knowledge distillation by training the student on its **self-generated output sequences**, using teacher feedback on those same trajectories.

## Core Innovation

Traditional KD suffers from exposure bias: students are trained on teacher-generated sequences but must generate their own sequences at inference time. GKD closes this gap by:

1. **On-policy sampling**: Student generates trajectories during training
2. **Teacher feedback**: Teacher scores/logits student's own outputs
3. **Flexible divergence**: Beyond KL, supports alternative loss functions

## Mathematical Formulation

### Standard Knowledge Distillation (off-policy)
```
L_KD = -Σ_t log π_θ(y_t | x, y_{<t}) * log π_teacher(y_t | x, y_{<t}) / τ
```

This is cross-entropy between student and teacher on **teacher-generated** sequences — distribution mismatch at inference.

### GKD (on-policy)
```
L_GKD = E_{y~π_θ(·|x)} [ log π_teacher(y|x) - log π_θ(y|x) + A(x,y) ]
```

Where:
- Student samples its own outputs `y ~ π_θ`
- Teacher provides log-probability on student's trajectories
- Advantage `A(x,y)` can weight different trajectories

### Relation to OPD

OPD is a **special case of GKD** where:
- The divergence is KL-constrained RL
- Rewards are implicit: `r = log π_teacher - log π_ref`
- Training is purely on-policy (no offline dataset)

## Key Properties

### 1. Flexible Divergence Measures

Unlike supervised KD which requires student to mimic teacher's distribution exactly, GKD supports:
- **Forward KL** (teacher → student): conservative, covers all modes
- **Reverse KL** (student → teacher): mode-seeking, ignores outliers  
- **Jensen-Shannon divergence**: balanced approach
- **Custom task-specific losses**: e.g., task success vs exact match

### 2. Seamless RL Integration

GKD naturally extends to reinforcement learning:
```
L = L_GKD + λ * L_RL(policy_gradient)
```

Where the RL term can optimize task-specific rewards without breaking the distillation objective.

### 3. Addressing Token-Level Exposure Bias

When a student generates a wrong token at step *t*, traditional KD would:
- Teacher provides "correct" next token's logit
- Training corrects the mistake
- But at inference, student sees its *own* mistake and may continue incorrectly

**GKD trains on these failure cases**:
- Student experiences its own mistakes during training
- Teacher guides recovery from student's actual errors
- Better generalization to inference-time behavior

## Experimental Results

### Tasks Evaluated
| Task Type | Metric | GKD vs SFT | GKD vs Standard KD |
|-----------|--------|------------|--------------------|
| Summarization | ROUGE-L | +2.1× improvement | +2.1× |
| Translation | BLEU | +1.7× improvement | +1.7× |
| Arithmetic Reasoning | Accuracy | +1.9× improvement | +1.9× |
| Task-Agnostic Distillation | BBH | +2% improvement | — |
| Task-Agnostic Distillation | MMLU | +1% improvement | — |

### Model Sizes
- Teacher: Large models (PaLM-scale)
- Student: 1B–7B parameters
- Distillation ratio: 10:1 to 100:1 compression

## Implementation Details

### Training Loop
```python
for batch in dataloader:
    # 1. Student generates on-policy trajectories
    student_outputs = student.sample(batch.prompt, temperature=τ)
    
    # 2. Teacher scores student's own outputs
    teacher_logits = teacher(student_outputs)
    student_logits = student(student_outputs)
    
    # 3. Compute GKD loss
    kl_div = compute_kl(teacher_logits, student_logits)
    advantage = compute_advantage(student_outputs)
    
    loss = kl_div - advantage  # Note: gradient ascent on advantage
    
    # 4. Optional RL fine-tuning
    if use_rl:
        rl_loss = ppo_update(student, batch.rewards)
        loss = loss + λ * rl_loss
    
    loss.backward()
```

### Sampling Temperature
- **During GKD training**: Use moderate temperature (τ ≈ 0.7–1.0)
- Encourages student to explore diverse outputs
- Teacher provides corrective signal on varied trajectories
- Critical for learning recovery from mistakes

## Connection to Modern OPD

| Feature | GKD (2023) | OPD (2024–2026) |
|---------|-----------|----------------|
| Training | On-policy student rollouts | Same |
| Teacher feedback | Token-level logits | Token-level logits |
| Objective | KL + advantages | KL + implicit rewards |
| Variance control | Basic | Advanced (top-k, prefix truncation) |
| Long-horizon | Moderate support | Explicit failure mode analysis |
| Reward design | Explicit RL rewards | Implicit log-ratio rewards |

**Evolution**: OPD formalizes GKD's implicit reward structure and addresses its failure modes (prefix bias, tokenizer mismatch, unreliable teacher guidance).

## Limitations

1. **Computationally expensive**: On-policy sampling slower than offline KD
2. **Teacher availability**: Requires powerful teacher at training time
3. **Hyperparameter sensitivity**: Temperature, KL weight, advantage estimation
4. **Tokenization issues**: Still vulnerable to tokenizer mismatch (later addressed by OPD's top-k matching)
5. **Sample inefficiency**: Each update requires fresh student generations

## Practical Guidance

### When to Use GKD/OPD
✅ Long-horizon reasoning tasks (math, coding)
✅ Agentic tasks with environment interaction
✅ Strong-to-weak distillation (large → small models)
✅ When inference distribution match matters

### When to Use Standard SFT
✅ Data efficiency priority
✅ Short, well-defined outputs
✅ Teacher distribution is reliable
✅ Budget constraints (compute)

## Related Concepts

- [[on-policy-distillation]] — OPD builds directly on GKD's foundation
- [[generalized-on-policy-distillation]] — G-OPD extends GKD with reward scaling
- [[ex-opd]] — Reward extrapolation variant
- [[knowledge-distillation]] — Traditional KD framework that GKD improves upon
- [[teacher-top-k-local-support-matching]] — Addresses GKD's teacher guidance reliability
- [[proximal-policy-distillation]] — PPO-style distillation with KL constraints
- [[reinforcement-learning-from-human-feedback|RLHF]] — Alternative post-training paradigm

## References

**Primary Paper**
- Agarwal, R. et al. (2023). "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes." *arXiv:2306.13649*
- DeepMind/MILA/University of Toronto collaboration

**Follow-up Work**
- Li et al. (2026). "Rethinking OPD: Phenomenology, Mechanism, and Recipe." *arXiv:2604.13016*
- Han et al. (2026). "Fast Prefix Distillation." *arXiv:2602.15260*  
- Lin et al. (2026). "G-OPD: Generalized OPD with Reward Extrapolation." *arXiv:2602.12125*

## Code & Implementations

- **TRL library**: `transformers` + TRL support GKD-style training
- **ms-swift**: Supports GKD/OPSD modes when `rlhf_type=gkd`
- **Axolotl**: YAML config for on-policy distillation
- **OpenRLHF**: GRPO-based implementation with GKD variant

> **Note**: Modern implementations typically use the OPD formulation (implicit rewards) rather than explicit GKD advantages, but the theoretical foundation remains identical.