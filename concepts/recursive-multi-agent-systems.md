---
title: "Recursive Multi-Agent Systems (RecursiveMAS)"
created: 2026-05-05
updated: 2026-05-05
type: concept
tags: [multi-agent, reasoning, architecture, training, inference]
sources: [raw/papers/2026/04/2604.25917.md]
---

# Recursive Multi-Agent Systems (RecursiveMAS)

## 1. Core Problem Definition (Formal Statement)

**Question**: Can agent collaboration itself be scaled through recursion?

Standard multi-agent systems (MAS) arrange agents in fixed topologies (sequential pipelines, mixture-of-experts, etc.) with text-mediated interactions. This faces two bottlenecks:
1. **Latency**: Sequential text generation requires waiting for each agent to complete
2. **Information loss**: Decoding to text and re-encoding loses information

**RecursiveMAS** extends the recursive language model (RLM) principle — where the same model iteratively refines its latent state — to multi-agent systems. Each agent acts like an RLM layer, iteratively passing latent representations through a lightweight **RecursiveLink** module.

**Formal problem**: Given N heterogeneous agents A = {A₁, ..., A_N} with parameters {θ₁, ..., θ_N}, design a recursive computation that:
- Refines the system's collective latent state H = {H₁, ..., H_N} through iterative interaction
- Avoids updating the base model parameters (only train RecursiveLink)
- Achieves better accuracy, faster inference, and lower token usage than text-based MAS

## 2. Theoretical Analysis / Method

### 2.1 RecursiveLink Module

The RecursiveLink R is a two-layer residual projection:

**Inner Link** (within-agent latent thought refinement):
> R_in(h) = h + W₂ · σ(W₁ · h)

where h is the last-layer hidden state, W₁ and W₂ are linear layers, σ is GELU, and the residual connection preserves original semantics.

**Outer Link** (cross-agent latent state transfer):
> R_out(h) = W₃ · h + W₂ · σ(W₁ · h)

where W₃ maps between different agents' hidden dimensions.

**Why residual?**: The residual branch preserves original semantics, allowing the network to focus on aligning distributional differences rather than learning full projection from scratch.

### 2.2 Architecture

1. Each agent A_i generates latent thoughts H_{A_i} = [h_t, h_{t+1}, ..., h_{t+m}] auto-regressively
2. Inner link R_in maps each h_t back to input embedding space for next step: e_{t+1} = R_in(h_t)
3. Outer link R_out transfers latent thoughts to next agent: input to A_{i+1} = E_{A_{i+1}} ⊕ R_out(H_{A_i})
4. After the last agent A_N, its output is fed back to A₁, forming a **recursive loop**
5. Only the last agent produces textual output in the final recursion round

### 2.3 Inner-Outer Loop Training

**Stage 1 — Inner Loop (model-level warm-up)**:
- Train R_in for each agent to align latent thoughts with ground-truth embeddings
- Loss: L_in = 1 - cos(R_in(H), Emb_{θ_i}(y)) (cosine similarity)
- Freeze all LLM parameters; only train R_in

**Stage 2 — Outer Loop (system-level co-optimization)**:
- Train R_out across agents with gradients backpropagated through full recursive paths
- Loss: L_out = CE(S^{(n)}(S^{(n-1)}(...S^{(1)}(x)...), y) (cross-entropy on final output)
- Shared gradient credit assignment across recursion rounds

### 2.4 Theoretical Analysis

**Proposition 3.1 (Runtime Complexity)**:
- Text-based recursive MAS: Θ(N(m|V|d_h + (t+m)d_h² + (t+m)²d_h))
- RecursiveMAS: Θ(N(md_h² + (t+m)d_h² + (t+m)²d_h))

Since d_h << |V| (hidden dim << vocabulary size), RecursiveMAS replaces the expensive m|V|d_h term with md_h².

**Theorem 4.1 (Gradient Stability)**:
- Text-based SFT during recursion suffers from gradient vanishing: ‖∂R_text(h)/∂h‖₂ ≤ O(ε) << 1
- RecursiveMAS maintains stable gradients: ‖∂R(h)/∂h‖₂ ≥ Ω(1 - √(1/d_h · log(1/δ)))

This proves that latent-space connections maintain informative gradients across recursion rounds while text-based interactions cause gradient vanishing.

### 2.5 Four Collaboration Patterns

| Pattern | Agents | Description |
|---------|--------|-------------|
| **Sequential** | Planner → Critic → Solver | Chain-of-agents, progressive decomposition |
| **Mixture** | Code + Science + Math specialists → Summarizer | Parallel domain experts, aggregated output |
| **Distillation** | Expert → Learner | Large model teaches small model via latent transfer |
| **Deliberation** | Reflector ↔ Tool-Caller | Iterative critique with external tool use |

## 3. Complete Experimental Results

### 3.1 Main Results (Table 2) — RecursiveMAS vs Baselines

Across 9 benchmarks (MATH500, AIME2025, AIME2026, GPQA-Diamond, MedQA, LiveCodeBench, MBPP+, HotpotQA, Bamboogle):

| Metric | Improvement |
|--------|-------------|
| **Average accuracy** | **+8.3%** over advanced single/multi-agent baselines |
| **Inference speedup** | **1.2× – 2.4×** end-to-end |
| **Token usage reduction** | **34.6% – 75.6%** |

### 3.2 Scaling with Recursion Depth

RecursiveMAS shows clean scaling trends as recursion rounds increase:
- Light setting (sub-1.5B agents): consistent improvement with deeper recursion
- Scaled setting (5-10B agents): maintains scaling while adapting to diverse MAS structures

### 3.3 Model Families Tested

| Family | Models Used |
|--------|-------------|
| Qwen | Qwen3/3.5 (1.7B, 4B, 9B) |
| Llama | Llama3.2 (1B, 3B) |
| Gemma | Gemma3 (4B) |
| Mistral | Mistral family |

### 3.4 Training Configuration

| Parameter | Value |
|-----------|-------|
| Training data | s1K (math), m1k (medical/science), OpenCodeReasoning (code), ARPO-SFT (tool use) |
| Optimizer | AdamW, lr=5e-4, cosine scheduler |
| Batch size | 4 |
| Trainable params | Only RecursiveLink (inner + outer) |
| LLM params | Frozen |
| Inference: top-p | 0.95 |
| Inference: temperature | 0.6 (reasoning), 0.2 (code) |
| Runs | 5 independent, report mean ± std |

### 3.5 Ablation: RecursiveLink Architecture

The residual connection in RecursiveLink is critical:
- Without residual: training is unstable, gradients explode/vanish
- With residual: stable training, faster convergence

## 4. Comparison with Existing Methods

| Method | Interaction | Trainable | Accuracy | Speed | Tokens |
|--------|-------------|-----------|----------|-------|--------|
| Single advanced agent | N/A | Full FT/LoRA | Baseline | Fast | Low |
| Text-based MAS | Text | None | +3-5% | Slow | High |
| LoopLM | Latent (single model) | Recursion params | +4-6% | Medium | Medium |
| Recursive-TextMAS | Text (recursive) | None | +5-7% | Slow | High |
| **RecursiveMAS** | **Latent (recursive)** | **RecursiveLink only** | **+8.3%** | **1.2-2.4×** | **34.6-75.6%↓** |

## 5. Critical Analysis

### Strengths
1. **Novel scaling axis**: Recursion as a system-level scaling mechanism for MAS, complementary to model scaling
2. **Theoretical grounding**: Both runtime complexity analysis and gradient stability theorem
3. **Strong empirical results**: +8.3% accuracy, 1.2-2.4× speedup, 34.6-75.6% token reduction — all three improve simultaneously
4. **Heterogeneous agents**: Works across different model families and sizes
5. **Parameter efficient**: Only trains RecursiveLink, freezes all LLM parameters
6. **Structure-agnostic**: Generalizes to 4 different collaboration patterns

### Weaknesses / Open Questions
1. **Training complexity**: Two-stage training (inner then outer loop) is non-trivial to implement
2. **RecursiveLink capacity**: A two-layer projection may be too simple for complex cross-agent communication
3. **Fixed recursion depth**: The number of recursion rounds is set manually; adaptive depth could be better
4. **Only evaluated on QA/reasoning**: No evaluation on open-ended generation, dialogue, or multi-modal tasks
5. **Gradient credit assignment**: Shared gradients across agents may cause conflicting updates
6. **Scalability to many agents**: Tested with small agent pools (2-4 agents); unclear how it scales to 10+

### Implications for Our Work
- **Latent-space collaboration is more efficient than text**: The 34.6-75.6% token reduction is significant for production systems.
- **Recursion as a scaling axis**: We should consider recursive refinement patterns in our agent architectures.
- **Parameter efficiency**: Training only a small module while freezing base models is cost-effective.
- **Gradient stability matters**: The theoretical analysis explains why latent-space connections work better than text for recursive systems.

## 6. Related

- [[multi-agent]] — multi-agent system design patterns
- [[reasoning]] — recursive reasoning and iterative refinement
- [[architecture]] — neural network architecture design
- [[training]] — parameter-efficient fine-tuning
- [[inference]] — inference optimization and efficiency
