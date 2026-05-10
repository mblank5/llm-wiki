---
title: AgenticRecTune — Multi-Agent Recommendation System Optimization
created: 2026-05-05
updated: 2026-05-05
type: concept
tags:
- agent
- multi-agent
- recommendation
- rl
- memory
sources:
- raw/papers/2026/04/2604.26969.md
---

# AgenticRecTune: Multi-Agent with Self-Evolving Skillhub for Recommendation System Optimization

## Core Problem Definition

Modern large-scale recommendation systems are **multi-stage pipelines** (pre-ranking → ranking → re-ranking), where system-level configuration optimization — integrating outputs from various model heads into final scores — is crucial but extremely challenging.

**Three primary challenges**:
1. **Scalability Limitations**: Each structural model change invalidates previous configurations. Vast optimization space with multi-dimensional dependencies demands repeated manual tuning, grid searches, or exhaustive data-driven learning.
2. **Contextual Fragmentation**: Each stage operates in a distinct context optimizing different local targets, requiring highly specialized domain expertise.
3. **Evolving Multi-Objective Online Metrics**: Online success depends on balancing competing metrics (engagement, diversity, long-term retention) while adapting to shifting product strategies.

**Formal Statement**: Given a multi-stage recommendation pipeline F = f_re ∘ f_rank ∘ f_pre with joint configuration space Θ = [θ_pre, θ_rank, θ_re] ∈ P, and online metrics M = [M_1, ..., M_J], find:

```
Θ* = argmax_{Θ∈P} E_{(x,y)~D}[U(M(F(x;w,Θ), y_true))]
s.t. M_j(F, y_true) ≥ b_j  ∀j ∈ {n+1,...,J}
     E[C(Θ)] ≤ C_max
```

where U(M) = Σ_{i=1}^{n} M_1(F, y_true) maximizes primary metrics subject to guardrail constraints on secondary metrics.

## Method: AgenticRecTune Framework

### Five-Agent Architecture

**1. Actor Agent**: Proposes multiple configuration candidates with logical explanations for each parameter shift, leveraging Gemini's reasoning over task context, domain knowledge, and historical data from Skillhub.

**2. Critic Agent**: Systematically evaluates Actor's proposals against format requirements, system guardrails, instruction constraints, and known historical failure cases. Filters suboptimal configurations and provides detailed feedback. Writes refined candidates to Agent Memory.

**3. Online Agent**: Handles live experimental deployment:
- Generates executable code/scripts from approved candidates
- Schedules A/B tests on production platform (traffic allocation, control vs treatment, time horizon)
- Collects final performance metrics and writes results back to Agent Memory

**4. Insight Agent**: Continuously analyzes historical results:
- **Self-Learning**: Searches common successful mods and configuration differences across iterations
- **Cross-Learning**: MapReduce strategy — learns patterns from multiple tasks in parallel (Map), then globally synthesizes (Reduce)
- Identifies sensitive parameters with highest impact
- Prunes redundant activity logs, maintains "top performers" pool via Pareto dominance filtering
- Maximizes distance between candidates via greedy selection on standardized metrics

**5. Skill Agent**: Synthesizes Insight Agent's findings into operational skills. Two evolution mechanisms:
- **Dynamic Knowledge Extraction**: Appends refined rules to Domain Knowledge, tightens search space bounds
- **Novel Skill Generation**: Creates entirely new operational skills from accumulated memory

### Self-Evolving Skillhub

Each skill in the Skillhub contains:
- **Task Context**: Which component to optimize (pre-ranking, ranking, re-ranking)
- **Task Requirement**: Search space constraints, JSON schema, infrastructure constraints
- **North Star Metric**: Primary optimization objective and secondary metric priorities
- **Initial Configuration**: Current production baseline
- **Domain Knowledge**: Task-specific heuristics, historical optimization logs, expert guidelines
- **Tools**: API tools for A/B test deployment, result querying, statistical significance analysis

### Reasoning Loop (Algorithm)

```
Input: Task T, Skillhub SH, Agent Memory AM
Output: Optimized configuration Θ*

1. PROMPT_CONSTRUCTION(T, SH, AM):
   - Retrieve relevant skills from SH
   - Retrieve elite candidates from AM
   - Construct structured prompt with context, constraints, domain knowledge

2. CANDIDATE_GENERATION(prompt):
   - Actor proposes {θ_1, ..., θ_k} with explanations
   - Focus on sensitive parameters identified by Insight Agent

3. CRITIQUE_AND_REFINE({θ_i}):
   - Critic evaluates against guardrails, format, history
   - Filter suboptimal candidates
   - Select most promising → write to AM

4. ONLINE_EVALUATION(approved_candidates):
   - Online Agent generates deployment code
   - Schedule A/B test, collect metrics
   - Update AM with results

5. SKILL_UPDATE(results):
   - Insight Agent: Self-Learning + Cross-Learning on new results
   - Skill Agent: Dynamic Knowledge Extraction + Novel Skill Generation
   - Update SH for next iteration

6. RETURN Θ* = best performer in AM
```

## Experimental Results

### Main Results: Task vs. Stage vs. Topline Metrics

| Task | Stage | Engagement Metric 1 | Engagement Metric 2 | Diversity Metric |
|------|-------|--------------------|--------------------|-----------------|
| Value-Based Retrieval | Pre-Ranking | +0.75% | +0.90% | +0.48% |
| Value Fusion | Ranking | +0.62% | +0.19% | +0.06% |
| Diversity | Re-Ranking | +0.21% | +0.29% | +3.43% |

All improvements statistically significant (p < 0.05). Notable: diversity task achieved +3.43% without triggering short-term engagement drops.

### Model Ablation Study

| Model | Engagement Metric 1 | Engagement Metric 2 | Diversity Metric |
|-------|--------------------|--------------------|-----------------|
| Gemini 3 Pro | +0.21% | +0.29% | +3.43% |
| Gemini 3 Flash | +0.08% | +0.07% | +1.69% |
| Gemini 1.5 Pro | +0.22% | +0.27% | +2.11% |

Key finding: Model scale matters. Gemini 3 Pro shows most balanced performance. Gemini 3 Flash (computationally efficient) shows lowest gains, confirming high-parameter reasoning is essential for navigating the search space.

### Actor-Critic Strategy Ablation

| Strategy | Engagement Metric 1 | Engagement Metric 2 | Diversity Metric |
|----------|--------------------|--------------------|-----------------|
| Actor-Critic | +0.75% | +0.90% | +0.48% |
| Single Agent | +0.29% | +0.26% | +0.06% |

Actor-Critic more than doubles engagement gains. Critic agent effectively mitigates "hallucinations" and encourages more rigorous candidate selection. Primary benefit is precision refinement rather than exploration breadth.

## Training/Implementation Configuration

- **Foundation models**: Gemini 3 Pro (primary), Gemini 3 Flash, Gemini 1.5 Pro (ablation)
- **Infrastructure**: Google Discover production A/B testing platform
- **Experiment duration**: Standard launch period per A/B test for statistical significance (p < 0.05)
- **Traffic split**: Orthogonal buckets, control = existing production configuration
- **Optimization targets**: Multiple North Star metrics (overall impression, DAU, session time) with guardrail constraints

## Comparison with Related Approaches

| Approach | System-Level | Online Metrics | Self-Evolving | Multi-Agent |
|----------|-------------|---------------|--------------|-------------|
| Manual Tuning | ✅ | ✅ | ❌ | ❌ |
| Grid Search | ✅ | ❌ (offline) | ❌ | ❌ |
| AutoML/HPO | ❌ (model-level) | ❌ | ❌ | ❌ |
| AgentHPO | ❌ (model-level) | ❌ | ❌ | ❌ |
| Self-EvolveRec | ❌ (model mutation) | ❌ | Partial | ❌ |
| **AgenticRecTune** | **✅** | **✅ Direct** | **✅ Skillhub** | **✅ 5 agents** |

## Critical Analysis

### Strengths
1. **End-to-end automation**: First framework to automate the complete workflow from configuration proposal to online A/B testing in production
2. **Self-evolving Skillhub**: The Insight→Skill agent closed loop is a genuine learning system, not just retrieval
3. **Actor-Critic architecture**: Dual-agent approach with Critic filtering is proven to reduce hallucinations and improve convergence
4. **Production validated**: Real deployment on Google Discover with measurable metric improvements
5. **Novel insight**: Identified that agents can discover impactful parameter interactions human engineers missed

### Weaknesses / Questions
1. **Limited ablation on Skillhub**: No isolated ablation showing Skillhub's contribution vs. simple memory. The self-evolution mechanism's actual impact is unclear.
2. **No comparison to Bayesian optimization or multi-objective BO**: Standard baselines for hyperparameter tuning are missing.
3. **Single-domain evaluation**: Only tested on Google Discover. Generalizability to other recommendation domains (e-commerce, social media) unknown.
4. **Gemini-only**: All experiments use Google's Gemini. No cross-model validation.
5. **Diversity metric trade-off**: Actor-Critic improves engagement substantially but diversity only modestly (+0.48%), suggesting the framework may over-optimize for engagement.
6. **No cost analysis**: Computational cost of running 5 agents vs. human engineers not quantified.

### Implications for Our Work
- The **Actor-Critic pattern** is directly applicable to agent memory: having a critic evaluate memory quality before committing could reduce noise
- **Skillhub's self-evolution** maps to agent skill memory: extracting patterns from historical results and synthesizing operational strategies is exactly what [[agent-memory-system]] should do
- The **Insight Agent's pruning strategy** (Pareto dominance filtering + diversity maximization) is a concrete algorithm for memory management
- **System-level configuration optimization** as a non-differentiable compositional problem is a good use case for agent-based optimization vs. gradient-based methods

## Related

- [[agent-memory-system]] — Agent memory architectures
- [[multi-agent]] — Multi-agent coordination patterns
- [[rl]] — Reinforcement learning for optimization
