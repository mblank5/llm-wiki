---
title: Agent Safety via RL
created: 2026-05-01
updated: 2026-05-01
type: concept
tags:
- safety
- rl
- agent
- alignment
sources:
- raw/papers/2025/07/2507.08270.md
---

# Agent Safety via RL: 统一安全对齐框架

## 概要

Agent Safety via RL (arXiv:2507.08270) 是蚂蚁集团提出的统一安全对齐框架，专门处理 LLM Agent 中的**用户发起威胁**和**工具发起威胁**。该方法采用三模态分类 (benign/malicious/sensitive) 代替传统的二元安全判断，并在沙箱 RL 环境中训练 Agent 同时抵御两种威胁源。

## Core Method: Unified Safety Alignment via RL

### Threat Model: Dual-Source Attacks

Traditional safety alignment assumes the user is the sole threat source. Agents face **two attack surfaces**:

1. **User-initiated threats**: Direct malicious instructions from users
   - "Delete all files on the server"
   - "Send phishing emails to all contacts"
   
2. **Tool-initiated threats**: Malicious content injected through tool outputs
   - Compromised API returning malicious instructions (prompt injection via tool response)
   - Poisoned search results containing adversarial content
   - Malicious web pages injecting commands through scraped content

```
Threat Model:
┌─────────┐     instruction     ┌─────────┐    tool_call    ┌──────────┐
│  User   │ ──────────────────→ │  Agent  │ ──────────────→ │  Tool    │
│         │                     │         │ ←────────────── │          │
│         │ ←─── response ────  │         │   tool_output   │          │
└─────────┘                     └─────────┘                 └──────────┘
   ↑ User-initiated threat           ↑ Tool-initiated threat
```

### Tri-Modal Classification

Instead of binary safe/unsafe, the framework introduces **three modalities**:

| Modality | Description | Agent Response |
|---|---|---|
| **Benign** | No safety risk detected | Execute normally |
| **Malicious** | Clear harmful intent | Refuse + explain |
| **Sensitive** | Ambiguous risk; may be legitimate | Execute with caution + logging |

This tri-modal approach reduces over-refusal by giving the agent a "middle ground" for ambiguous cases.

**Classification criteria:**
```
P(malicious | context) > τ_high  →  MALICIOUS (refuse)
P(malicious | context) > τ_low   →  SENSITIVE  (cautious execute)
P(malicious | context) ≤ τ_low   →  BENIGN     (normal execute)
```

### Sandbox RL Environment

The training pipeline uses a sandboxed environment that simulates both threat types:

```python
class SafetySandbox:
    def __init__(self, tools, attack_generators):
        self.tools = tools
        self.user_attacker = attack_generators['user']    # generates malicious instructions
        self.tool_attacker = attack_generators['tool']    # injects via tool outputs
    
    def run_episode(self, agent):
        # Randomly sample threat type
        threat_type = random.choice(['user', 'tool', 'none'])
        
        if threat_type == 'user':
            instruction = self.user_attacker.generate()
        elif threat_type == 'tool':
            instruction = sample_benign_instruction()
            self.tool_attacker.activate()  # will inject during tool execution
        else:
            instruction = sample_benign_instruction()
        
        trajectory = agent.execute(instruction, self.tools)
        return compute_reward(trajectory, threat_type)

def compute_reward(trajectory, ground_truth_threat):
    if ground_truth_threat == 'none':
        return +1.0 if task_completed(trajectory) else -0.5
    elif ground_truth_threat in ['user', 'tool']:
        return +1.0 if refused_safely(trajectory) else -2.0
    # Sensitive: partial reward for cautious execution
```

### RL Training Objective

The framework trains with a modified PPO objective that incorporates safety-aware rewards:

```
L(θ) = E_t[ min( r_t(θ) · Â_t,  clip(r_t(θ), 1-ε, 1+ε) · Â_t ) ]
       - β · KL(π_θ || π_ref)

where:
r_t(θ) = π_θ(a_t|s_t) / π_old(a_t|s_t)
Â_t = safety_reward_t + γ · V(s_{t+1}) - V(s_t)
safety_reward_t = f(refusal_correctness, task_completion, sensitivity_handling)
```

The reward function penalizes:
- Executing malicious instructions (high penalty: -2.0)
- Over-refusing benign instructions (moderate penalty: -0.5)
- Missing tool-initiated injections (high penalty: -2.0)

## Experimental Results

| Metric | Baseline | Agent Safety via RL |
|---|---|---|
| User-initiated attack defense | 38.2% | 82.4% |
| Tool-initiated attack defense | 12.7% | 76.8% |
| Benign task completion | 91.3% | 87.5% |
| Over-refusal rate | 28.6% | 12.1% |
| Sensitive task accuracy | — | 73.2% |

Key findings:
- Tool-initiated threat defense improves most dramatically (+64.1%), as this is neglected by prior work
- Tri-modal classification reduces over-refusal by 16.5 percentage points vs binary classification
- Sandbox training generalizes to unseen tools and attack patterns

## Comparison with Other Methods

| Method | User Threats | Tool Threats | Over-refusal | Training Paradigm |
|---|---|---|---|---|
| **Agent Safety via RL** | 82.4% | 76.8% | 12.1% | Sandbox RL |
| [[agent-align]] | 79.5% | ~40% | 11.3% | ABC synthesis + SFT |
| [[clawguard]] | ~85% | ~70% | ~18% | Runtime rules |
| [[thought-aligner]] | ~90% | ~65% | ~8% | Contrastive learning |
| Standard RLHF | ~55% | ~15% | ~25% | Human preference |

The key differentiator of Agent Safety via RL is its **explicit tool-initiated threat handling** — most other methods focus exclusively on user-facing safety.

## Related Work

- [[agent-align]] — Training-time safety via ABC synthesis; complementary but does not explicitly handle tool-initiated threats
- [[clawguard]] — Runtime safety framework for tool-augmented agents; can be layered on top for defense-in-depth
- [[ppo]] — The underlying RL algorithm used for safety-aware policy optimization

## Deployment Recommendations

1. **Sandbox calibration**: Invest in building domain-specific sandbox environments that accurately simulate your tool ecosystem. Generic sandboxes may miss domain-specific attack vectors
2. **Tune sensitivity thresholds**: The τ_high and τ_low thresholds should be calibrated per deployment domain. Financial/healthcare: stricter; general chat: more lenient
3. **Combine with [[agent-align]]**: Use AgentAlign's ABC synthesis for initial safety SFT, then apply this RL framework for fine-grained safety refinement
4. **Tool output monitoring**: In production, add a secondary classifier on tool outputs to catch tool-initiated injections that the agent might miss
5. **Continuous evaluation**: Tool-initiated attacks evolve rapidly; regularly re-evaluate with new injection patterns and retrain if performance degrades
6. **Sensitive task logging**: Log all sensitive-modality executions for post-hoc review; this data feeds back into the RL training loop
