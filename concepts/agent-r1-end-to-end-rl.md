---
title: "Agent-R1: End-to-End RL for LLM Agents"
created: 2026-05-01
updated: 2026-05-01
type: concept
tags: [rl, agent, reinforcement-learning, end-to-end, markov-decision-process]
sources: [raw/papers/2025/11/2511.14460.md]
---

# Agent-R1: End-to-End RL for LLM Agents  
*Framework for training powerful LLM agents with reinforcement learning (2025)*

## Overview

**Agent-R1** provides a systematic Markov Decision Process (MDP) formulation for LLM agents and introduces a modular, flexible framework for **end-to-end reinforcement learning** of agent behavior.

**Key Contribution**: First principled extension of MDP to LLM agents, plus **Agent-R1 training framework** that outperforms imitation learning and achieves strong results on multi-hop QA.

## Problem Formulation

### Standard MDP (Classic RL)

```
MDP = (S, A, P, R, γ)
```
- S: State space
- A: Action space  
- P: Transition dynamics P(s'|s,a)
- R: Reward function R(s,a)
- γ: Discount factor

**Limitation**: Assumes fixed action space and state representation — doesn't capture LLM agent capabilities.

### LLM Agent MDP (Agent-R1)

```
Agent-MDP = (S, A, P, R, γ, T, O, π_θ)
```

**Extensions**:

1. **Hierarchical Actions**: a_t ∈ A can be:
   - Text generation (token-level)
   - Tool call (function invocation)
   - API request
   - Environment interaction

2. **Rich State**: s_t ∈ S includes:
   - Conversation history
   - Environment state
   - Agent memory (long-term)
   - Tool availability
   - Task specification

3. **Observation Function**: O(s_t) → o_t (partial observability)

4. **Policy**: π_θ(a|s) - LLM with parameters θ

## The Three-Phase Training Loop

### Phase 1: Pre-Training (Foundation)

```
Objective: Maximize likelihood on expert demonstrations
L_PT = -Σ log π_θ(a*|s)
```

Sources:
- Supervised fine-tuning (SFT) on human demonstrations
- Code, dialogue, instruction-following data

**Result**: Competent but not expert-level agent

### Phase 2: Offline RL (Learning from Logs)

```
Objective: Improve policy using logged trajectories
L_Offline-RL = E[log π_θ(a|s) * A(s,a)]
```

Where advantage A(s,a) estimated from:
- Human preferences (DPO-style)
- Outcome rewards (success/failure)
- Value function (critic)

**Data**: Historical agent interactions (no new environment calls)

**Advantage**: Safe, no exploration cost, learns from failures

### Phase 3: Online RL (Active Learning)

```
Objective: Optimize expected return
J(θ) = E_{τ~π_θ}[Σ_t γ^t r_t]
```

Where:
- τ = trajectory sampled by interacting with environment
- r_t = immediate reward (could be sparse)
- γ = discount factor (0.99 typically)

**Algorithm**: PPO with KL penalty
```
L_PPO = E[min(
    r_t(θ) · A_t,
    clip(r_t(θ), 1-ε, 1+ε) · A_t
  ) - β * KL(π_θ || π_ref)
]
```

**Advantage**: Learns from own experience, discovers new strategies

## Framework Architecture

```

                    Agent-R1 Training Framework                      

  
   Environment            Rollout Worker                  
   (Simulator)            (Parallel)                      
  
                                                       
   Trajectories      
                                                       
                                                         
                               
   Replay Buffer      Generalized                        
   (Experience)         Advantage                        
   Collection            Estimator                       
                               
                                                        
                                                        
                               
   PPO Optimizer        LLM Policy (θ)                  
   + KL Penalty                                      
                               

```

## Algorithm: Agent-R1-PPO

```python
def agent_r1_ppo(env, policy, n_epochs=10):
    for epoch in range(n_epochs):
        # 1. Collect trajectories
        trajectories = []
        for _ in range(batch_size):
            traj = collect_trajectory(env, policy)
            trajectories.append(traj)
        
        # 2. Compute returns and advantages
        for traj in trajectories:
            traj.returns = compute_returns(traj.rewards, gamma=0.99)
            traj.advantages = compute_gae(
                traj.values, traj.rewards, gamma=0.99, lam=0.95
            )
        
        # 3. PPO update (multiple epochs)
        for _ in range(update_epochs):
            for batch in mini_batches(trajectories):
                # Compute policy ratio
                old_logp = get_old_logp(batch)  # From collection
                new_logp = policy.log_prob(batch.actions)
                ratio = exp(new_logp - old_logp)
                
                # PPO clipped objective
                surr1 = ratio * batch.advantages
                surr2 = clip(ratio, 1-eps, 1+eps) * batch.advantages
                policy_loss = -min(surr1, surr2).mean()
                
                # KL penalty (to stay near reference)
                kl_penalty = compute_kl(policy, reference_policy)
                
                # Total loss
                loss = policy_loss + beta * kl_penalty
                
                loss.backward()
                optimizer.step()
```

## Experimental Results

### Multi-Hop QA Benchmarks

**Dataset**: HotpotQA, 2WikiMultiHopQA, MuSiQue

| Method | HotpotQA | 2Wiki | MuSiQue | Avg |
|--------|----------|-------|---------|-----|
| GPT-3.5 (zero-shot) | 45.2 | 38.1 | 21.3 | 34.9 |
| GPT-4 (zero-shot) | 67.3 | 58.9 | 42.1 | 56.1 |
| ReAct (GPT-4) | 73.4 | 64.2 | 48.3 | 62.0 |
| **Agent-R1 (7B)** | **68.9** | **61.3** | **45.7** | **58.6** |

**Key**: 7B Agent-R1 competitive with GPT-4 ReAct on some tasks!

### Ablation Study

| Training Phase | HotpotQA | Contribution |
|----------------|----------|--------------|
| Pre-training only | 52.1 | Baseline |
| + Offline RL | 61.3 | +9.2 |
| + Online RL | 68.9 | +7.6 |

**Finding**: Both offline and online RL contribute significantly

### Component Ablation

| Component Removed | Performance Drop | Explanation |
|-------------------|------------------|-------------|
| KL penalty | -12.4% | Forgets pre-training knowledge |
| Generalized advantage | -8.7% | High variance in updates |
| Reference policy | -15.2% | Policy divergence |
| Offline RL phase | -9.2% | Misses learning from logs |

## Key Innovations

### 1. Unified MDP Formulation

First rigorous treatment of LLM agents as MDPs:
- Tool use as actions
- Memory as state
- Task as reward function

**Impact**: Enables application of RL theory to agents

### 2. Three-Phase Training

**Offline RL phase is crucial**:
- Learns from failures without cost
- Improves sample efficiency of online phase
- Stabilizes training

### 3. Modularity

Framework components are swappable:
- Different RL algorithms (PPO, SAC, DDPG)
- Different advantage estimators (GAE, n-step)
- Different value functions (critic architectures)

## Comparison with Prior Work

### Agent-R1 vs ReAct

| Dimension | ReAct | Agent-R1 |
|-----------|-------|----------|
| Learning | None (prompt) | End-to-end RL |
| Adaptation | Manual prompt tuning | Automatic |
| Performance | Fixed per model | Improves with training |
| Compute (training) | 0 | High |
| Data requirements | Prompt examples | Trajectories + rewards |

### Agent-R1 vs RAGEN

| Dimension | RAGEN | Agent-R1 |
|-----------|-------|----------|
| Focus | Multi-turn stability | End-to-end optimization |
| Key idea | StarPO (trajectory filtering) | MDP + 3-phase training |
| Complexity | Medium | High |
| Best for | Stochastic environments | General agents |

## Practical Considerations

### Reward Design

**Challenge**: Sparse rewards (only task success/failure)

**Solutions**:
1. **Shaped rewards**: Intermediate rewards for progress
   ```
   r_t = r_final * γ^(T-t) + r_intermediate
   ```
2. **Dense rewards**: Step-by-step verification
3. **Human feedback**: Preference-based rewards

### Exploration

**Challenge**: Large action space → hard to explore

**Solutions**:
1. **Entropy bonus**: Encourage diverse actions
   ```
   L = L_PPO + α * H(π(·|s))
   ```
2. **Intrinsic curiosity**: Reward novel states
3. **Diverse initialization**: Varied starting conditions

### Safety

**Challenge**: RL may discover unsafe strategies

**Mitigations**:
1. **Constrained RL**: Penalize unsafe actions
2. **Human-in-loop**: Review critical decisions
3. **Sandboxing**: Limit tool capabilities during training

## Implementation Guide

### Prerequisites

```bash
# Install
git clone https://github.com/agent-r1/agent-r1.git
cd agent-r1
pip install -r requirements.txt

# Requires
# - PyTorch 2.0+
# - Transformers 4.30+
# - vLLM (for efficient inference)
```

### Configuration

```yaml
# config/agent_r1.yaml
model:
  base_model: "Qwen/Qwen2.5-7B"
  lora_rank: 64
  
training:
  algorithm: "PPO"
  epochs: 3
  batch_size: 64
  lr: 3e-5
  kl_weight: 0.1
  
reward:
  task_success: 1.0
  step_penalty: -0.01
  kl_penalty: 0.05
  
rlhf:
  offline_phase: true
  offline_data: "data/offline_logs.json"
  online_rollouts: 10000
```

### Training Script

```python
from agent_r1 import AgentR1Trainer, QwenPolicy

# Initialize
policy = QwenPolicy("Qwen/Qwen2.5-7B")
trainer = AgentR1Trainer(policy, config)

# Phase 1: Pre-training (optional, if not already done)
if not pretrained:
    trainer.pretrain(sft_dataset)

# Phase 2: Offline RL
if config.offline_phase:
    trainer.offline_rl(offline_logs)

# Phase 3: Online RL
trainer.online_rl(env, n_rollouts=10000)

# Save
policy.save("agent_r1_trained")
```

## Results by Environment

| Environment | Agent-R1 | PPO | DPO | Improvement |
|-------------|----------|-----|-----|-------------|
| HotpotQA | 68.9% | 62.1% | 65.3% | +6.8% |
| WebShop | 45.2% | 38.7% | 41.2% | +6.5% |
| AlfWorld | 82.3% | 74.6% | 78.9% | +7.7% |
| MiniGrid | 91.2% | 85.4% | 88.7% | +5.8% |

**Average improvement**: +6.7% over PPO, +3.9% over DPO

## Limitations & Future Work

### Current Limitations

1. **Sample inefficiency**: Requires 10K+ environment interactions
2. **Reward engineering**: Still requires careful reward design
3. **Catastrophic forgetting**: May forget capabilities during RL
4. **Safety**: Unpredictable behaviors may emerge

### Future Directions

1. **Offline Agent-R1**: Learn entirely from logs (no environment)
2. **Multi-agent**: Coordinated learning across agents
3. **Meta-Agent-R1**: Fast adaptation to new tasks
4. **Human-AI collaboration**: Learn from human feedback in real-time

## Conclusion

**Agent-R1 demonstrates that**:

1. **LLM agents can be formulated as MDPs** — rigorous theoretical foundation
2. **End-to-end RL works** — 6-8% improvement over strong baselines
3. **Three-phase training is crucial** — offline + online > online alone
4. **7B models can compete** — with good training, size isn't everything

**Practical impact**: Framework enables training specialized agents for specific domains (healthcare, finance, robotics) without relying on massive general models.

## Related Concepts

- [[ppo]] — Core RL algorithm
- [[ragegen-multi-turn-rl-agents]] — Trajectory-level RL (complementary)
- [[ml-agent-autonomous-ml|ml-agent]] — Step-wise RL (different approach)
- [[on-policy-distillation]] — Post-training refinement
- [[agent-safety]] — Safety considerations

## References

**Primary Paper**
- Liu, Q. et al. (2025). "Agent-R1: Training Powerful LLM Agents with End-to-End Reinforcement Learning." *arXiv:2511.14460*
- University of Science and Technology of China

**Code**
- https://github.com/USTC-Agent/Agent-R1
- Apache 2.0 License

**Citations**: 17 (recent - Nov 2025)

> **Significance**: First complete framework for MDP-based LLM agent training with proven gains over prompting-based approaches.