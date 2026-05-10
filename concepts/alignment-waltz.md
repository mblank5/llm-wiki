---
title: WaltzRL
created: 2026-05-01
updated: 2026-05-01
type: concept
tags:
- safety
- alignment
- rl
- multi-agent
sources:
- raw/papers/2025/10/2510.08240.md
---

# WaltzRL: 多 Agent 安全协作框架

## 概要

WaltzRL (arXiv:2510.08240) 是 Meta 提出的多 Agent 安全协作框架，通过 **conversation agent** 和 **feedback agent** 的联合训练实现安全对齐。核心创新是 **Dynamic Improvement Reward (DIR)** 机制，使两个 Agent 在对抗性协作中共同进化，将 unsafe 率从 39.0% 降至 4.6%，over-refusal 从 45.3% 降至 9.9%。

## Core Method: Multi-Agent Safety via Adversarial Cooperation

### Dual-Agent Architecture

WaltzRL uses two specialized agents trained jointly:

```
┌──────────────────────┐         ┌──────────────────────┐
│  Conversation Agent  │         │   Feedback Agent     │
│  (π_conv)            │         │   (π_fb)             │
│                      │         │                      │
│  Role: Generate      │ query   │  Role: Evaluate &    │
│  responses to user   │───────→ │  provide safety      │
│  queries, balancing  │         │  feedback on the     │
│  helpfulness + safety│←─────── │  response            │
│                      │ feedback│                      │
└──────────────────────┘         └──────────────────────┘
         ↑                                 ↑
         └───────── Joint RL Training ──────┘
```

- **Conversation Agent (π_conv)**: Generates responses to user queries, aiming to be both helpful and safe
- **Feedback Agent (π_fb)**: Reviews the conversation agent's responses and provides structured safety feedback

### Dynamic Improvement Reward (DIR)

The key innovation is the DIR mechanism that creates a cooperative adversarial dynamic:

```
DIR_conv = r_safety(response) + λ₁ · r_helpfulness(response) + λ₂ · Δ_safety

DIR_fb = r_accuracy(feedback) + λ₃ · improvement_signal

Where:
Δ_safety = safety_score(after_feedback) - safety_score(before_feedback)
```

**DIR encourages both agents to improve:**
- The conversation agent gets bonus reward when it improves safety after receiving feedback
- The feedback agent gets bonus reward when its feedback actually leads to safer responses

**Dynamic weighting:**
```python
def compute_dir(response, feedback, revised_response, training_step):
    # Base rewards
    safety_r = safety_classifier(revised_response)
    helpful_r = helpfulness_scorer(revised_response)
    
    # Dynamic improvement bonus
    delta_safety = safety_classifier(revised_response) - safety_classifier(response)
    
    # Decay the improvement bonus over training (agents should need less correction)
    decay = exp(-γ · training_step)
    
    dir_reward = safety_r + λ₁ * helpful_r + λ₂ * delta_safety * decay
    return dir_reward
```

### Joint Training Procedure

```
Initialize π_conv, π_fb with pretrained LLM
For each training iteration:
    1. Sample batch of queries Q = {q₁, ..., qₙ}
    2. For each qᵢ:
        a. π_conv generates response rᵢ
        b. π_fb evaluates rᵢ, produces feedback fᵢ
        c. π_conv generates revised response r'ᵢ conditioned on fᵢ
    3. Compute DIR rewards for both agents
    4. Update π_conv via PPO with DIR_conv
    5. Update π_fb via PPO with DIR_fb
    6. Periodically update reference models for KL penalty
```

### Handling Over-Refusal

A unique challenge in multi-agent safety training is **cascading over-refusal**: the feedback agent becomes overly conservative, causing the conversation agent to refuse benign queries. WaltzRL addresses this with:

1. **Over-refusal penalty in DIR**: Explicitly penalize feedback that flags benign responses as unsafe
2. **Adversarial benign queries**: Include challenging benign queries (e.g., "how to make a cake") that sound potentially risky
3. **Dynamic helpfulness weight**: Increase λ₁ (helpfulness reward) as training progresses

## Experimental Results

| Metric | Baseline | WaltzRL |
|---|---|---|
| Unsafe response rate | 39.0% | 4.6% |
| Over-refusal rate | 45.3% | 9.9% |
| Helpfulness score (MT-Bench) | 7.2 | 7.5 |
| Safety-helpfulness gap | -34.3pp | +2.9pp |

Ablation studies:

| Configuration | Unsafe | Over-refusal |
|---|---|---|
| Single agent + PPO | 15.2% | 28.4% |
| Dual agent, no DIR | 11.3% | 22.1% |
| Dual agent + DIR, no over-refusal penalty | 6.8% | 18.7% |
| **Full WaltzRL** | **4.6%** | **9.9%** |

Key findings:
- The DIR mechanism is responsible for **~40% of the over-refusal reduction** compared to dual-agent without DIR
- Joint training converges in ~3x fewer steps than training conversation agent alone
- The feedback agent learns to distinguish genuinely risky responses from merely sensitive topics

## Comparison with Other Methods

| Method | Unsafe | Over-refusal | Agents | Key Mechanism |
|---|---|---|---|---|
| **WaltzRL** | 4.6% | 9.9% | 2 (joint) | DIR + adversarial cooperation |
| [[agent-safety-via-rl]] | ~18% | ~12% | 1 | Tri-modal sandbox RL |
| [[agent-align]] | ~20% | ~11% | 1 | ABC synthesis |
| [[thought-aligner]] | ~10% | ~8% | 1+plugin | Runtime thought correction |
| Standard RLHF | ~25% | ~35% | 1 | Human preference PPO |
| Constitutional AI | ~15% | ~25% | 1 | Self-critique |

WaltzRL achieves the **lowest unsafe rate** among comparable methods, but requires maintaining two models during training (higher compute cost).

## Related Work

- [[agent-safety-via-rl]] — Single-agent RL safety; WaltzRL extends this paradigm to multi-agent cooperation with DIR
- [[reinforcement-learning-from-human-feedback]] — RLHF is the foundation; WaltzRL replaces human feedback with an AI feedback agent
- [[ppo]] — PPO is used as the underlying optimizer for both agents in the joint training loop

## Deployment Recommendations

1. **Start with a strong feedback agent**: The feedback agent's quality determines the upper bound of safety improvement. Invest in curating high-quality safety evaluation data for feedback agent training
2. **Monitor for reward hacking**: The conversation agent may learn to generate responses that fool the feedback agent. Use an external safety classifier for periodic audits
3. **Over-refusal calibration**: The over-refusal penalty weight should be tuned per deployment domain. Consumer-facing products should weight helpfulness higher; enterprise tools should weight safety higher
4. **Training compute budget**: WaltzRL requires ~2.5x the compute of single-agent RL due to dual-agent training. Budget accordingly
5. **Iterative deployment**: Deploy in phases — first with conservative thresholds, then gradually relax over-refusal constraints based on real-world usage data
6. **Feedback agent as a product**: The trained feedback agent can be deployed as a standalone safety evaluator for other models or as part of an ensemble with [[thought-aligner]]
