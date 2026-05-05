---
title: "Learning to Orchestrate Agents with the RL Conductor"
created: 2026-05-05
updated: 2026-05-05
type: concept
tags: [rl, reasoning, evaluation, benchmark, training, alignment]
sources: [raw/papers/2512.04388.md]
---

# Learning to Orchestrate Agents with the RL Conductor

**arXiv**: 2512.04388v4 [cs.LG] | **Date**: 2026-03-01
**Authors**: Stefan Nielsen, Edoardo Cetin, Peter Schwendeman, Qi Sun, Jinglue Xu, Yujin Tang (Sakana AI)

## 1. Core Problem Definition

No single LLM is universally optimal across all tasks. Different models are fine-tuned to specialize in particular domains. The challenge is: **how to dynamically coordinate a pool of diverse, specialized LLMs to solve complex problems that exceed any individual model's capabilities?**

Prior approaches use manually-designed agentic workflows or learned routers that select from pre-specified topologies. The RL Conductor removes these constraints — it learns to design **arbitrary coordination strategies in natural language** through end-to-end reinforcement learning.

## 2. Method

### 2.1 Conductor Output Format

The Conductor outputs a sequence of **workflow steps**, each defined by three Python lists:

```python
model_id = [2, 0]                    # Which worker agent performs each step
subtasks = [                         # Natural language instruction for each step
    "Develop an efficient algorithm to count complete subarrays",
    "Implement the algorithm described by the previous agent in Python"
]
access_list = [[], ["all"]]          # Which prior step outputs each worker sees
```

This formulation enables:
- **Sequential chains** (step N feeds into step N+1)
- **Parallel branches** (independent subtasks executed simultaneously)
- **Tree-structured workflows** (fan-out/fan-in patterns)
- **Best-of-N** (same subtask to multiple agents, select best)
- **Debate/refinement** (iterative improvement with visibility into prior attempts)

### 2.2 Reward Structure

The Conductor reward rᵢ has two conditions:
1. **Format condition**: rᵢ = 0 if Python lists cannot be parsed from the response
2. **Correctness condition**: rᵢ = 1 if the final output matches the solution sᵢ, else rᵢ = 0.5

### 2.3 GRPO Training Objective

Using Group Relative Policy Optimization (GRPO) with G > 1 grouped completions:

```
J(θ) = E_{q∼D, {o}∼π(·|q)} [ 1/G Σᵢ ( min(rᵢAᵢ, clip(rᵢ, 1-ε, 1+ε)Aᵢ) - β D_KL(π_θ || π_ref) ) ]
```

Where the advantage function is:
```
Aᵢ = (rᵢ - mean({r₁,...,r_G})) / std({r₁,...,r_G})
```

**Training hyperparameters**:
- 200 GRPO iterations
- Batch size: 256
- Optimizer: AdamW
- No KL regularization (β = 0)
- Base model: Qwen2.5 7B

### 2.4 Training Data

960 problems from four reasoning domains:
- **MATH** (Hendrycks et al., 2021): Competition mathematics
- **MMLU** (Hendrycks et al., 2020): Multitask language comprehension
- **RLPR** (Yu et al., 2025): Real-world reasoning
- **LiveCodeBench V1** (Jain et al., 2024): Code generation

### 2.5 Worker Pool

Proprietary frontier models: Gemini-2.5-Pro, Claude-Sonnet-4, GPT-5
Open-source models: DeepSeek-R1-Distill-Qwen-32B, Gemma3-27B-instruct, Qwen3-32B

## 3. Extensions

### 3.1 Adaptive Worker Selection

Finetune a pretrained Conductor with **randomized agent pools** at each step. For each question, restrict to a random k-model subset from the total pool of n workers. After training, the Conductor generalizes to arbitrary subsets of open/closed-source models.

### 3.2 Recursive Topologies and Test-Time Scaling

Allow the Conductor to **specify itself as a worker**. During recursive calls, the Conductor receives its own parent output plus previous agent responses. It can instantiate new workflows or end the coordination loop.

- Maximum recursion depth is a tunable parameter at inference time
- Unlocks a new form of **test-time scaling**: more recursion calls = more compute = better performance
- Finetuned with same RL algorithm, manually instantiating one recursion call per batch

## 4. Experimental Results

### 4.1 Main Results: State-of-the-Art Comparison

**Table 1: Comparison with Previous Best "Unconstrained" Results**

| Model | M500 | MMLU | RLPR | LCB | AIME25 | BCB | GPQA-D | Avg. |
|-------|------|------|------|-----|--------|-----|--------|------|
| gemma-3-27b-it | 39.8 | 81.3 | 16.67 | 13.14 | 20.7 | 14.86 | 38.4 | 32.12 |
| Qwen3-32B | 73.5 | 83.5 | 31.00 | 21.21 | 20.0 | 30.41 | 64.1 | 53.81 |
| Qwen3-32B (thinking) | 80.7 | 84.1 | 37.25 | 25.86 | 72.9 | 28.38 | 66.8 | 56.57 |
| R1-Distill-32B | 82.5 | 84.4 | 33.50 | 26.86 | 63.0 | 33.07 | 58.1 | 54.49 |
| Claude Sonnet 4 | 96.0 | 91.4 | 36.70 | 46.54 | 74.3 | 37.16 | 77.7 | 65.69 |
| Gemini 2.5 Pro | 96.0 | 92.4 | 40.55 | 67.24 | 78.3 | 37.51 | 84.8 | 70.97 |
| GPT 5 | 99.0 | 93.5 | 42.20 | 82.90 | 90.8 | 32.75 | 82.3 | 74.78 |
| **Conductor (Ours)** | **99.4** | **94.1** | **44.75** | **83.93** | **93.3** | **37.86** | **87.5** | **77.27** |

The 7B Conductor surpasses GPT-5 (77.27 vs 74.78 average) and achieves SOTA on GPQA-Diamond and LiveCodeBench.

### 4.2 Controlled Evaluation vs Multi-Agent Baselines

The Conductor is compared against:
- **5-turn self-reflection**: Each agent revises up to 5 times
- **MASRouter** (Yue et al., 2025): Learned routing with human-designed topologies
- **Mixture-of-Agents (MoA)** (Wang et al., 2024): Layered agent aggregation
- **RouterDC** (Chen et al., 2024): Router selecting single best-matched agent
- **Smoothie** (Guha et al., 2024): Ensemble routing

**Key finding**: The Conductor surpasses all baselines while using **fewer agent calls** (avg 3 steps vs 4-5 for MASRouter). All baselines except RouterDC have strictly higher inference cost.

### 4.3 Recursive Test-Time Scaling

**Table 2: Recursive Conductor on Out-of-Distribution Tasks**

| Model | AIME25 | BigCodeBench | GPQA-D | Average |
|-------|--------|-------------|--------|---------|
| gemma-3-27b-it | 6.67 | 10.8 | 33.33 | 16.93 |
| Qwen3-32B | 23.33 | 23.0 | 54.05 | 33.46 |
| Qwen3-32B (thinking) | 23.33 | 20.9 | 59.09 | 34.44 |
| R1-Distill-32B | 30.00 | 24.3 | 51.01 | 35.10 |
| Gemini Pro 2.5 | 46.67 | 35.1 | 75.25 | 52.34 |
| Claude Sonnet 4 | 35.33 | 35.8 | 67.30 | 46.14 |
| GPT 5 | 46.67 | 33.8 | 72.73 | 51.73 |
| Conductor | 66.67 | 37.8 | 81.31 | 61.93 |
| **Conductor-Recursive** | **66.67** | **40.0** | **82.32** | **63.00** |

Recursion yields additional gains on BigCodeBench (+2.2) and GPQA-Diamond (+1.01) while using < 2× the original agent calls.

### 4.4 Adaptive Worker Selection Results

When finetuned on randomized model pools:
- **Open-model-only**: Consistently outperforms Claude Sonnet 4 by ~10%
- **Closed-model-only**: Matches pretrained SOTA performance
- The Conductor is not exclusively reliant on frontier models

### 4.5 Conductor Scale Analysis

Comparing 3B vs 7B Conductors:
- Both converge to the same worker agent distribution
- The 7B variant maintains a clear edge due to **superior prompt engineering skills**
- The performance gap is traced to the larger model's ability to generate better subtask instructions

### 4.6 Task and Difficulty Adaptivity

The Conductor learns to **dynamically allocate compute** based on task difficulty:
- **MMLU** (factual): Typically 1-2 agent steps
- **LiveCodeBench** (complex coding): 3-4 agent steps with planning → implementation → verification
- The model explicitly reasons about task complexity before designing workflows

## 5. Training Configuration Summary

| Parameter | Value |
|-----------|-------|
| Base model | Qwen2.5 7B |
| Algorithm | GRPO |
| Training iterations | 200 |
| Batch size | 256 |
| Group size G | > 1 |
| KL coefficient β | 0 |
| Optimizer | AdamW |
| Training problems | 960 |
| Domains | MATH, MMLU, RLPR, LiveCodeBench V1 |
| Max workflow steps | 5 |
| Avg workflow steps (learned) | ~3 |

## 6. Comparison with Existing Methods

| Method | Avg Score | Cost | Flexibility |
|--------|-----------|------|-------------|
| Single best model (GPT-5) | 74.78 | 1× | Fixed |
| 5-turn self-reflection | ~55 | 5× | Limited |
| MASRouter | ~60 | 4-5× | Predefined topologies |
| Mixture-of-Agents | ~62 | Multi-layer | Fixed structure |
| RouterDC | ~58 | Variable | Single agent selection |
| **RL Conductor** | **77.27** | ~3× | **Full NL freedom** |

## 7. Critical Analysis

**Strengths**:
- First demonstration that **pure end-to-end RL** can discover powerful multi-agent coordination strategies
- Achieves SOTA with a 7B model coordinating much larger workers (32B+)
- Removes manual constraints on subtask specification — natural language as the coordination medium
- Two practical extensions (adaptive worker selection, recursive scaling) via short finetuning
- Emergent behaviors: verification, debate, planning, iterative refinement
- Difficulty-adaptive compute allocation
- Open-source code and model weights

**Weaknesses**:
- **Worker dependency**: Performance relies on having powerful frontier workers; the Conductor cannot create capability that doesn't exist in the pool
- **Training cost**: Requires 960 problems across 4 domains + 200 GRPO iterations with expensive frontier API calls
- **Small training set**: Only 960 problems; unclear how well this scales to broader domains
- **No theoretical analysis**: No formal guarantees about convergence or optimality of discovered strategies
- **Recursive depth limit**: Maximum recursion depth is manually set; no automatic determination of when to stop
- **Evaluation stochasticity**: Results repeated up to 16 times due to stochasticity, suggesting variance concerns

**Open Questions**:
- Can the Conductor discover novel coordination strategies not anticipated by designers?
- How does performance scale with worker pool size and diversity?
- Can recursive scaling be extended to deeper hierarchies?
- What happens when workers have conflicting or adversarial outputs?
- Can the Conductor generalize to non-reasoning domains (e.g., creative writing, multimodal tasks)?

## Related

- [[multi-agent-coordination]] — Multi-agent collaboration frameworks
- [[grpo]] — Group Relative Policy Optimization
- [[test-time-scaling]] — Test-time compute scaling for reasoning
- [[agentic-workflows]] — Manually designed agentic workflow patterns
- [[mixture-of-agents]] — MoA ensemble approach
- [[self-reflection]] — Self-refinement strategies in LLMs
