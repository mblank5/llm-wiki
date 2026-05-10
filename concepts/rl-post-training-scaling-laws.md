---
title: "RL Post-Training Scaling Laws for LLMs"
created: 2026-05-01
updated: 2026-05-01
type: concept
tags: [rl, scaling-laws, qwen, training, math-reasoning]
sources: [raw/papers/2025/09/2509.25300.md]
---

# RL Post-Training Scaling Laws for LLMs  
*Qwen2.5 mathematical reasoning study (2025)*

## Overview

Systematic empirical study of how **model size**, **data volume**, and **compute** interact during reinforcement learning post-training for mathematical reasoning. Trained the full Qwen2.5 dense series (0.5B → 72B) using RL to derive predictive scaling laws.

**Key Finding**: Test loss follows a **log-linear relationship** with resources, but learning efficiency saturates as model size increases.

## Experimental Setup

### Models
- **Qwen2.5 series**: 0.5B, 1.5B, 3B, 7B, 14B, 32B, 70B, 72B
- All models instruction-tuned before RL
- Math-focused post-training on reasoning benchmarks

### RL Configuration
- Algorithm: PPO (Proximal Policy Optimization)
- Reward: Rule-based/math verification (e.g., GSM8K correctness)
- Training steps: Varied by scale (larger models = fewer steps)
- Batch size: Scaled with model capacity

## Core Scaling Laws

### 1. The RL Scaling Equation

```
L_test(N, D, C) ≈ (N^α) * (D^β) * (C^γ) + κ
```

Where:
- `L_test` = test loss (math reasoning)
- `N` = model size (parameters)
- `D` = data volume (unique samples)
- `C` = compute budget (FLOP)
- `α, β, γ` = scaling exponents ≈ negative values (larger = better performance)
- `κ` = irreducible loss floor

**Empirical result**: Test loss decreases **log-linearly** with compute and data:
```
log L_test ≈ -κ * log C + const
```

### 2. Learning Efficiency vs Model Size

| Model Size | Learning Efficiency | Saturation Trend |
|------------|-------------------|------------------|
| 0.5B | Low | ↑ Improving |
| 7B | Medium | ↑ Improving |
| 32B | High | → Plateau |
| 72B | Very High | ↓ Saturating |

**Definition**: Learning efficiency = performance gain per unit compute/data

**Critical insight**: While larger models learn *faster* initially, **efficiency gains diminish** (saturation effect). The `k(N)` term in scaling law captures this:

```
L_test ∝ C^(-k(N)) where k(N) increases with N but saturates
```

### 3. Data Reuse Effectiveness

**In data-constrained regimes** (limited unique problems):
- **Repeated reuse** of high-quality data is **highly effective**
- Final performance depends on **total optimization steps**, not data uniqueness
- 10× reuse of 1,000 problems ≈ better than 1× use of 10,000 problems

**Implication**: When you can't get more data, **train longer** on good data.

## Practical Implications

### Resource Allocation Strategies

#### Scenario A: Unlimited Compute, Limited Data
- **Strategy**: Train largest model possible with heavy data reuse
- **Rationale**: Large models extract more from each sample
- **Example**: 70B model with 5× data reuse > 7B model with 1× data

#### Scenario B: Limited Compute, Abundant Data  
- **Strategy**: Use smaller model, train on more unique problems
- **Rationale**: Diminishing returns on model size; diversity > reuse
- **Example**: 7B model on 50K diverse problems > 70B on 5K problems

#### Scenario C: Balanced Resources
- **Strategy**: Mid-size model (14B–32B) with moderate reuse
- **Sweet spot**: Best compute/data tradeoff
- **Efficiency**: Peak learning efficiency before saturation

### Training Optimization

1. **Start small, scale up**:
   - Debug pipeline on 0.5B–1.5B (fast iteration)
   - Extrapolate expected gains to larger models

2. **Warm-start with SFT**:
   - Good supervised fine-tuning reduces RL compute needs
   - Better initialization = faster convergence

3. **Curate high-quality data**:
   - 1,000 perfect solutions > 10,000 mediocre ones
   - RL amplifies quality through repeated exposure

4. **Monitor learning efficiency**:
   - Track `(performance gain) / (compute spent)`
   - Stop when efficiency drops below threshold

## Comparison with Pre-training Scaling

| Dimension | Pre-training | RL Post-training |
|-----------|-------------|------------------|
| Loss trend | Power law | Log-linear |
| Data scaling | ∼ α^-0.4 (Chinchilla) | ∼ β^-0.3 (empirical) |
| Compute scaling | ∼ γ^-0.5 | ∼ δ^-0.6 |
| Efficiency trend | Improves linearly | Saturates |
| Critical resource | Compute & data | Compute & **quality** |

## Failure Modes at Scale

### 1. Overfitting to RL Reward

Large models may "hack" the reward function:
- Exploit rule-based verification loopholes
- Format cheating (correct answer in wrong format → 0 reward)
- **Solution**: Diverse reward sources, occasional human evaluation

### 2. Catastrophic Forgetting

Heavy RL on new skills degrades general capabilities:
- Math improvement → language degradation
- **Solution**: Mix in general-domain RL, replay buffers

### 3. Reward Hacking in Reused Data

Repeated exposure teaches model to exploit verification:
- Memorizes reward pattern, not reasoning
- **Solution**: Vary reward functions, add noise

## Experimental Results Summary

### Performance vs Model Size (Math Reasoning)
| Model | AIME'24 | AIME'25 | MATH | GSM8K |
|-------|---------|---------|------|-------|
| 7B | 28.1 | 18.3 | 32.4 | 78.2 |
| 32B | 52.3 | 35.7 | 58.1 | 88.7 |
| 72B | 61.2 | 42.1 | 64.3 | 91.2 |

### Compute vs Performance Curve

```
Compute (PFLOP-days)
   10    →  ~40% on AIME
   100   →  ~60%
   1,000 →  ~75%
  10,000 →  ~82%
```

**Key**: Each 10× compute increase yields ~15% absolute improvement (diminishing)

## Theoretical Insights

### Why Log-Linear instead of Power Law?

Pre-training explores **new capabilities** (power law = continuous discovery)
RL post-training **refines existing capabilities** (log-linear = optimization)

Think of it as:
- **Pre-training**: Discovering new knowledge (explore)
- **RL**: Sharpening known skills (exploit)

### The Saturation Explanation

Large models already possess the reasoning primitives. RL mainly:
1. **Triggers** correct reasoning paths
2. **Suppresses** incorrect outputs
3. **Strengthens** reward-aligned patterns

Beyond a threshold, the model already knows — RL just needs to activate it efficiently.

## Relation to Other Scaling Studies

### DeepSeek-R1 Scaling (concurrent)
- Similar log-linear trends observed
- RL + distillation > pure RL
- Validation: independent confirmation

### OpenAI o1 Scaling
- Proprietary but consistent patterns
- Test-time compute crucial (complements training)

### Chinchilla (pre-training)
- Different regime: exploration vs refinement
- Pre-training: 20% compute → model, 80% → data
- RL post-training: Inverted (80% compute on small data)

## Tools & Replication

### Open-Source Reproduction
**Framework**: Qwen2.5 + vLLM + DeepSpeed
**RL library**: TRL (PPO implementation)
**Training script**: ~200 lines for basic setup

```python
from transformers import Qwen2ForCausalLM
from trl import PPOTrainer

model = Qwen2ForCausalLM.from_pretrained("Qwen/Qwen2.5-7B")
ppo_trainer = PPOTrainer(
    model=model,
    config=ppo_config,
    dataset=math_dataset
)

for epoch in range(n_epochs):
    for batch in dataloader:
        rewards = verify_math_answers(batch.outputs)
        ppo_trainer.step(rewards)
```

### Compute Requirements (Approximate)
| Model | GPU-hours | Cost (A100) |
|-------|-----------|-------------|
| 7B | 2,000 | ~$3,000 |
| 32B | 15,000 | ~$22,000 |
| 72B | 60,000 | ~$90,000 |

## Open Questions

1. **Multi-modal RL scaling**: Do vision-language models follow similar laws?
2. **Agent RL**: How do environment interactions scale vs text-only?
3. **Very small models**: Can <1B models benefit from RL (data efficiency)?
4. **RL + OPD**: Combined scaling with on-policy distillation?

## Conclusion

RL post-training for LLMs follows **predictable scaling laws**, but with important differences from pre-training:

✅ **Log-linear** (not power law) improvement with resources  
✅ **Saturation** at large model scales  
✅ **Data quality** trumps quantity  
✅ **Compute-efficient** for mid-size models (7B–32B)  

**Practical takeaway**: For most applications, a **7B–14B model + targeted RL** outperforms brute-force 70B+ approaches on cost/performance.

## Related

- [[grp-o]] — Group Relative Policy Optimization (GRPO), common RL algorithm
- [[ppo]] — Proximal Policy Optimization, core RL method
- [[on-policy-distillation]] — Combines with OPD for efficiency
- [[mixture-of-experts]] — MoE scaling differs from dense models
- [[qwen3]] — Qwen3 uses these scaling insights in design

**Paper**: Tang et al. (2025). "Scaling Behaviors of LLM Reinforcement Learning Post-Training." *arXiv:2509.25300*