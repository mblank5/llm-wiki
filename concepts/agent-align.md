---
title: AgentAlign
created: 2026-05-01
updated: 2026-05-01
type: concept
tags:
- safety
- alignment
- agent
sources:
- raw/papers/2025/05/2505.23020.md
---

# AgentAlign: 抽象行为链合成安全对齐数据

## 概要

AgentAlign (arXiv:2505.23020) 提出**抽象行为链 (Abstract Behavior Chains)** 方法来合成 Agent 安全对齐训练数据。核心创新在于从真实工具使用中提取抽象行为模式，然后用非恶意解读这些行为链的比例来合成良性指令，从而解决 agentic 场景下安全数据稀缺的问题。该方法将 LLM Agent 的安全性从 35.8% 提升到 79.5%。

## Core Method: Abstract Behavior Chain Synthesis

### Problem Statement

Standard safety alignment (e.g., RLHF, constitutional AI) targets text-based interactions. LLM Agents interact with external tools (web browsers, file systems, code execution), creating a qualitatively different threat surface. Key challenges:

1. **Tool-mediated attacks** — adversarial instructions that exploit tool capabilities (e.g., "delete all files in /tmp")
2. **Benign-but-dangerous patterns** — legitimate tasks that happen to invoke risky tool sequences
3. **Data scarcity** — very few real-world examples of agentic safety failures

### Abstract Behavior Chain (ABC) Representation

The central innovation is extracting **Abstract Behavior Chains** from tool-use trajectories:

```
ABC = [(action_type_1, abstract_target_1), (action_type_2, abstract_target_2), ...]
```

Where:
- `action_type` ∈ {READ, WRITE, EXECUTE, DELETE, MODIFY, SEND, ...}
- `abstract_target` is a generalized parameter (e.g., "system_file" instead of "/etc/passwd")

**Example transformation:**

| Concrete Action | Abstract Component |
|---|---|
| `exec("rm -rf /tmp/*")` | `(DELETE, temp_directory)` |
| `write("/etc/passwd", ...)` | `(WRITE, system_config)` |
| `send_email("admin@corp.com", ...)` | `(SEND, external_contact)` |

### Data Synthesis Pipeline

```
1. Collect real tool-use trajectories from agent logs
2. Extract ABCs via pattern mining and abstraction
3. For each ABC:
   a. Identify the risk level (malicious intent probability)
   b. Generate benign interpretations at ratio α
   c. Generate malicious interpretations at ratio (1-α)
4. Instantiate abstract chains back into concrete instructions
5. Filter with safety classifier → final training data
```

The **benign interpretation ratio α** is a critical hyperparameter. Setting α too high produces insufficient safety signal; too low causes over-refusal.

### Safety-Aware Fine-Tuning

The synthesized data is used for two-stage training:

1. **Stage 1 (SFT)**: Teach the agent to recognize and refuse dangerous action sequences
2. **Stage 2 (DPO/RLHF)**: Refine the boundary between safe refusal and over-refusal

**Pseudocode for ABC extraction:**
```python
def extract_abc(trajectory):
    chain = []
    for step in trajectory:
        action = categorize_action(step.tool_call)
        target = abstract_target(step.tool_call.args)
        chain.append((action, target))
    return compress_redundant(chain)

def synthesize_instruction(abc, intent="benign"):
    if intent == "benign":
        prompt = f"Generate a legitimate task that requires: {abc}"
    else:
        prompt = f"Generate a harmful task exploiting: {abc}"
    return llm.generate(prompt)
```

## Experimental Results

| Metric | Baseline | AgentAlign | Improvement |
|---|---|---|---|
| Safety Rate (refusing malicious) | 35.8% | 79.5% | +43.7% |
| Over-refusal Rate | 22.1% | 11.3% | -10.8% |
| Helpfulness (benign tasks) | 87.2% | 84.6% | -2.6% |

Key findings:
- ABC-based synthesis outperforms naive prompt-based synthesis by **23.4%** on safety
- The benign interpretation ratio α=0.7 yields the best safety-helpfulness tradeoff
- Transfer: models trained on ABC data generalize to unseen tool sets

## Comparison with Other Methods

| Method | Approach | Safety | Over-refusal | Data Needed |
|---|---|---|---|---|
| **AgentAlign** | ABC synthesis + SFT/DPO | 79.5% | 11.3% | Synthetic only |
| Standard RLHF | Human preference + PPO | ~55% | ~25% | Human annotations |
| [[clawguard]] | Runtime guard | ~85% | ~18% | Rule-based |
| [[agent-safety-via-rl]] | Sandbox RL + tri-modal | ~82% | ~12% | Sandbox environment |
| [[thought-aligner]] | Real-time thought correction | ~90% | ~8% | Contrastive pairs |

AgentAlign's advantage is **data efficiency** — it does not require real attack data or human annotations, making it scalable. Its limitation is that it operates at training time only, unlike runtime approaches like [[clawguard]].

## Related Work

- [[memeovobench-memory-safety]] — Memory evolution safety benchmark; AgentAlign addresses tool-use safety while MemEvoBench focuses on long-term memory corruption
- [[clawguard]] — Runtime safety guard for tool-augmented agents; complementary to AgentAlign's training-time approach
- [[on-policy-distillation]] — AgentAlign's SFT stage can be viewed as a form of on-policy distillation from a safety-aware teacher

## Deployment Recommendations

1. **Combine with runtime guards**: AgentAlign provides training-time safety; pair with [[clawguard]] or similar runtime monitors for defense-in-depth
2. **Tune α per domain**: High-risk domains (finance, healthcare) should use lower α (more malicious examples); general assistants can use higher α
3. **Regular ABC refresh**: As new tools are added to the agent's toolkit, re-extract ABCs and regenerate training data
4. **Monitor over-refusal**: Track the benign task rejection rate post-deployment; if over-refusal rises, increase α
5. **Evaluation**: Use the AgentAlign evaluation suite (malicious instruction test set) for regression testing after model updates
