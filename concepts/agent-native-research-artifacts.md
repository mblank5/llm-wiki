---
title: Agent-Native Research Artifact (Ara)
created: 2026-05-05
updated: 2026-05-05
type: concept
tags:
- agent
- agentic-coding
- training
- benchmark
sources:
- raw/papers/2026/04/2604.24658.md
---

# Agent-Native Research Artifact (Ara)

## Core Problem Definition

Traditional scientific publication compresses a **branching, iterative research process** into a **linear narrative**, discarding the majority of what was discovered along the way. This compilation imposes two structural costs:

**Storytelling Tax**: Failed experiments, rejected hypotheses, and the branching exploration process are discarded to fit a linear narrative. Empirically: across 24,008 agent runs on RE-Bench, **90.2% of dollar cost** (and 59.2% of tokens) was spent on failed runs, with a median failed-to-success token ratio of **113x**. Without access to prior failure records, agents must independently rediscover every dead end.

**Engineering Tax**: The gap between *reviewer-sufficient* prose and *agent-sufficient* specification leaves critical implementation details unwritten. Analysis of PaperBench's 8,921 expert-annotated reproduction requirements across 23 ICML 2024 papers: only **45.4% are fully specified** in the source PDF. Code development is the most underspecified category (37.3% sufficient); missing hyperparameters alone account for 26.2% of all gaps.

**Formal Statement**: Given a research knowledge object K = {H, E, C, F} (hypotheses, experiments, claims, failures), traditional publishing produces a lossy projection P = f(K) where f discards F (failures) and underspecifies E (execution details). The Ara protocol seeks to preserve K as a machine-executable artifact.

## Method: The Ara Protocol

### Four-Layer Architecture

Ara organizes research into four interlocking layers within an agent-native file-system structure:

**1. Cognitive Layer (`/logic/`) — Scientific reasoning**
- `problem.md`: gap and key insight
- `solution/`: architecture, algorithm, convergence-critical heuristics
- `claims.md`: falsifiable assertions with explicit proof pointers
- `experiments.md`: verification plan
- `related_work.md`: typed dependencies (`imports`, `bounds`, `baseline`) forming a machine-executable dependency graph

**2. Physical Layer (`/src/`) — Executable implementation**
- **Algorithmic contributions**: "kernel mode" — only core modules with typed I/O signatures (10-100x smaller than full repo)
- **Systemic contributions**: "repository mode" — full implementation with `index.md` manifest mapping files to Ara components
- `configs/`: every hyperparameter annotated with rationale and search range
- `environment.md`: pinned dependencies, hardware, seeds

**3. Exploration Graph (`/trace/`) — Research trajectory**
- `exploration_tree.yaml`: complete research DAG as nested YAML with five typed node kinds: `question`, `decision`, `experiment`, `dead_end`, `pivot`
- Nesting encodes parent→child edges; `also_depends_on` captures convergence points
- Dead-end nodes preserve hypothesis, failure mode, and lesson — the knowledge narrative papers discard

**4. Evidence Layer (`/evidence/`) — Raw empirical grounding**
- `results/`: machine-readable metric tables with exact values and source annotations
- `logs/`: training curves, resource usage, diagnostics
- Forensic bindings: `claims.md` → `experiments.md` → `/evidence/` proof chain
- **Withholding ground-truth enables layered access control**: verification agents get code+algorithm but not evidence, preventing fabrication

### Enabling Mechanisms

**Live Research Manager** (§3): An agent skill that runs silently during research, capturing decisions and dead ends at session boundaries. Three-stage pipeline:
1. **Context Harvester**: scans session record (conversational history, tool outputs, experiment results, code diffs)
2. **Event Router**: classifies events into 7 types (Table 1), tags with provenance (`user`, `ai-suggested`, `ai-executed`, `user-revised`), writes to appropriate Ara layer
3. **Maturity Tracker**: promotes observations to formal entries when closure signals detected

**Ara Compiler** (§4): Translates legacy PDFs/repos into Ara format via four-stage top-down generation: Semantic Deconstruction → Cognitive Mapping → Physical Grounding → Exploration Graph Extraction. Iterates 2-3x with in-loop ARA Seal Level 1 validation. Supports collective inference from previously compiled Ara artifacts.

**Ara-Native Review System** (§5): Three-level ARA Seal verification:
- **Level 1 (Structural Integrity)**: schema conformance, cross-layer reference resolution — deterministic, seconds
- **Level 2 (Argumentative Rigor)**: Rubric-anchored agent evaluates 6 dimensions (evidence relevance, falsifiability quality, methodological rigor, scope calibration, argument coherence, exploration integrity) — minutes
- **Level 3 (Execution Reproducibility)**: Sandboxed coding agent runs scaled-down directional checks, isolated from evidence layer — hours to days

### Algorithm: Compiled Research Record Construction

```
Input: Research sources S = {PDF, repo, rubrics, trajectory logs}
Output: Ara artifact A = {/logic, /src, /trace, /evidence}

1. SEMANTIC_DECONSTRUCTION(S):
   - Strip narrative framing, extract raw research content
   - Rewrite in fact-dense telegraphic form (eliminate Storytelling Tax)

2. COGNITIVE_MAPPING(content):
   - Build motivation chain: observations → gaps → insight
   - Generate falsifiable claims with proof pointers
   - Populate /logic/ files

3. PHYSICAL_GROUNDING(content, repo):
   - Generate annotated configs, typed code stubs, environment manifest
   - If repo available: code-paper reconciliation → provenance-tagged heuristics

4. EXTRACTION_GRAPH(trajectories):
   - Fan out sub-agents per trajectory (MALT run)
   - Extract dead ends, partial successes, pivot decisions
   - Populate /trace/exploration_tree.yaml

5. VALIDATE(A, level=1):
   - Schema conformance, cross-layer reference resolution
   - If fail → goto 1 (iterate, typically 2-3 passes)

6. RETURN A
```

## Experimental Results

### Understanding (Knowledge Extraction)

450 questions across 30 targets (23 PaperBench papers + 7 RE-Bench tasks), 3 categories:

| Category | n | Ara Accuracy | Baseline Accuracy | Δ |
|----------|---|-------------|-------------------|---|
| A: Fidelity | 300 | 95.6% | 80.8% | +14.8% |
| B: Detail (config recovery) | 115 | 92.6% | 67.8% | +24.8% |
| C: Failure knowledge | 35 | 81.4% | 15.7% | +65.7% |
| **Overall** | **450** | **93.7%** | **72.4%** | **+21.3%** |

Ara uses targeted file lookups (PAPER.md layer index); baseline does linear PDF/repo scanning. Token usage scales with question depth on Ara (61K→153K) but stays flat on baseline (83K→118K).

### Reproduction

15 PaperBench papers, 10 reproduction tasks each (150 subtasks, 1,743 rubric requirements):

| Difficulty | Ara Success Rate | Baseline Success Rate | Δ |
|------------|-----------------|----------------------|---|
| Easy | ~72% | ~67% | +4.9% |
| Medium | ~65% | ~59% | +5.6% |
| Hard | ~58% | ~50% | +8.5% |
| **Overall (weighted)** | **64.4%** | **57.4%** | **+7.0%** |

Win/tie/loss across papers: 8/5/2. Advantage grows with difficulty — hard subtasks depend on configuration content PDFs rarely supply.

### Extension (Building on Prior Work)

5 RE-Bench tasks, comparing Ara agent (with failure traces) vs paper-synthesized writeup agent:

| Task | Ara Winner? | Notes |
|------|-------------|-------|
| rust_codecontests | ✅ | Ara commits to Rust library at t=9min vs paper at t=395min |
| nanogpt_chat_rl | ✅ | Heuristic H08 pre-names degenerate-output filter |
| fix_embedding | ✅ | Heuristics mark permutation recovery as dead end |
| triton_cumsum | ❌ (Sonnet 4.6) | Paper agent invents int8 compression not in trace |
| restricted_mlm | ❌ (Sonnet 4.6) | Paper agent commits to single architecture |

Key insight: Ara agent reaches a **useful first move earlier on all 5 tasks**, but late-phase reversal happens when the agent's own reasoning bandwidth exceeds what the documented playbook records. On Sonnet 4.5 (weaker base), the comparison inverts — Ara wins all 5 tasks.

### ARA Seal Effectiveness (Rigor Auditor Mutation Benchmark)

| Injection Type | Severity | n | Detection Rate |
|---------------|----------|---|---------------|
| Fabricated claim | Critical | 23 | 100% |
| Rebutted-branch leak | Critical | 23 | 100% |
| Over-claim (scope) | Major | 23 | 100% |
| Missing falsification | Major | 23 | 91% |
| Orphan experiment | Minor | 23 | 22% |
| **Overall** | | **115** | **82.6%** |

## Training/Implementation Configuration

- **Evaluation agents**: Claude Sonnet 4.6 (reproduction/understanding), Claude Opus 4.6 (judging)
- **Token budgets**: 14-20M tokens per paper (reproduction), scaled by task complexity
- **RE-Bench extension**: 8h SLURM wall clock + $50 API spend cap per run
- **ARA Seal Level 2**: Claude Code SDK agent with rubric-anchored protocol
- **Compiler iteration**: 2-3 passes for generate-validate-fix loop convergence

## Comparison with Related Approaches

| Approach | Executable | Failure Trajectory | Claim-Evidence Binding | Agent-Native Review |
|----------|-----------|-------------------|----------------------|-------------------|
| Traditional PDF | ❌ | ❌ | Implicit | ❌ |
| FAIR Principles | ❌ | ❌ | ❌ | ❌ |
| RO-Crate | Archival bundle | ❌ | ❌ | ❌ |
| Nanopublications | ❌ | ❌ | Atomic claims only | ❌ |
| AGENTS.md | Partial | ❌ | ❌ | ❌ |
| **Ara** | **✅** | **✅** | **✅ Forensic bindings** | **✅ 3-level Seal** |

## Critical Analysis

### Strengths
1. **Quantified the problem rigorously**: 90.2% failure cost, 113x failed-to-success token ratio, 45.4% specification completeness — these numbers make the case undeniable
2. **Four-layer architecture is well-designed**: separation of cognitive, physical, exploration, and evidence layers matches how agents actually consume research
3. **Forensic bindings** create auditable claim→experiment→evidence chains, directly addressing reproducibility crisis
4. **The (Human+AI)² network vision** is compelling: Git-like fork/merge/diff for research artifacts
5. **Strong empirical results**: +21.3% understanding, +7.0% reproduction, early acceleration on extension

### Weaknesses / Questions
1. **Limited to computational research**: The authors acknowledge wet-lab biology, materials synthesis are out of scope. This is a significant limitation for general science.
2. **Compiler quality depends on source richness**: PDF alone yields stub-level physical layers. The value proposition depends on having repos, rubrics, and trajectory logs.
3. **Extension results are mixed**: On 2/5 tasks with strong agents (Sonnet 4.6), the paper agent wins late-game. The trace can constrain agents from stepping outside the prior-run box.
4. **Scalability of the Seal**: Level 3 (execution reproducibility) requires hours to days of compute per paper. At scale, this becomes prohibitively expensive.
5. **No human evaluation**: All evaluations use LLM judges (Opus 4.6). The 93.7% understanding accuracy may not reflect true human-level comprehension.
6. **Orphan experiment detection is weak** (22%): This is a structural gap that should be moved to Level 1 deterministic checks.

### Implications for Our Work
- Ara's **forensic binding** concept directly applies to agent memory: linking claims to evidence is essentially what a good memory system should do
- The **exploration graph** structure maps well to agent decision trees — preserving failure trajectories could improve agent learning efficiency
- The **Storytelling Tax** framework explains why agent-generated documentation is often insufficient: agents, like humans, tend to record successes and discard failures
- The **extension paradox** (trace helps weaker agents but can constrain stronger ones) suggests memory systems should tag entries with model-class provenance

## Related

- [[agentic-coding]] — AI agents that co-author code and run experiments
- [[agent-memory-system]] — Memory systems for AI agents
- [[agentic-harness-engineering]] — Building harnesses for agent evaluation
