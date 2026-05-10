---
title: "VerificAgent"
created: 2026-05-01
updated: 2026-05-01
type: concept
tags: [safety, memory, agent, verification]
sources: [raw/papers/2025/06/02539.md]
---

# VerificAgent: 计算机使用 Agent 的记忆验证框架

## 概要

VerificAgent (arXiv:2506.02539) 是 Microsoft 提出的计算机使用 Agent 记忆验证框架，通过**专家种子知识**、**迭代记忆增长**和**人工事实核查**三阶段流程，系统性地构建经过验证的 Agent 记忆库。在 OSWorld Office 基准上，任务完成率从 25% 提升到约 50%。

## Core Method: Verified Memory Construction Pipeline

### Problem: Unreliable Agent Memory

Computer-use agents (e.g., agents that control desktop applications) accumulate procedural knowledge over time. This "memory" includes:

- How to perform specific tasks in specific applications
- Keyboard shortcuts, menu paths, dialog sequences
- Workarounds for application quirks

**The problem**: agents may memorize incorrect procedures, leading to repeated failures. Unlike text knowledge, procedural memory errors are difficult to detect because they manifest as action sequences that "look right" but fail in practice.

### Three-Stage Pipeline

```
Stage 1: Expert Seed Knowledge
┌─────────────────────────────────┐
│ Human experts demonstrate tasks  │
│ → Record action trajectories    │
│ → Verify each step succeeds     │
│ → Store as verified seed memory │
└──────────────┬──────────────────┘
               │
Stage 2: Iterative Memory Growth
┌─────────────────────────────────┐
│ Agent attempts new tasks         │
│ → Successful trajectories added  │
│ → Failed trajectories analyzed   │
│ → Partially successful kept with │
│   confidence scores              │
└──────────────┬──────────────────┘
               │
Stage 3: Human Fact-Checking
┌─────────────────────────────────┐
│ Periodic human review of memory  │
│ → Verify accumulated memories    │
│ → Remove incorrect procedures    │
│ → Update stale memory entries    │
└─────────────────────────────────┘
```

### Stage 1: Expert Seed Knowledge

The initial memory is populated with **expert-verified procedures**:

```python
class ExpertSeedMemory:
    def __init__(self):
        self.memory = {}  # task → verified_procedure
        
    def add_expert_demo(self, task, trajectory, expert_id):
        # Each step must be individually verified
        verified_steps = []
        for step in trajectory:
            # Expert confirms step correctness
            if expert_confirms(step, task):
                verified_steps.append({
                    'action': step.action,
                    'target': step.target,
                    'params': step.params,
                    'screenshot_before': step.screenshot_before,
                    'screenshot_after': step.screenshot_after,
                    'verified_by': expert_id,
                    'confidence': 1.0  # expert-verified = perfect confidence
                })
        
        self.memory[task] = {
            'procedure': verified_steps,
            'source': 'expert_demo',
            'created': datetime.now(),
            'last_verified': datetime.now()
        }
```

### Stage 2: Iterative Memory Growth

After seeding, the agent autonomously expands its memory:

```python
def iterative_memory_growth(agent, task_queue, memory_store):
    for task in task_queue:
        # Agent attempts the task, possibly using existing memory
        trajectory = agent.execute(task, reference_memory=memory_store)
        
        if task_succeeded(trajectory):
            # High confidence: successful execution
            memory_store.add({
                'procedure': trajectory,
                'source': 'agent_success',
                'confidence': 0.85,
                'success_count': 1
            })
        elif partial_success(trajectory):
            # Medium confidence: partial execution
            successful_prefix = extract_successful_prefix(trajectory)
            memory_store.add({
                'procedure': successful_prefix,
                'source': 'agent_partial',
                'confidence': 0.5,
                'note': 'incomplete procedure'
            })
        else:
            # Log failure for analysis
            log_failure(task, trajectory)

def memory_retrieval(query, memory_store):
    # Retrieve with confidence-weighted scoring
    candidates = memory_store.search(query)
    scored = [(c, c.confidence * similarity(query, c)) for c in candidates]
    return sorted(scored, key=lambda x: -x[1])[:5]
```

### Stage 3: Human Fact-Checking

Periodic human review ensures memory quality:

```python
def human_fact_check(memory_store, reviewer, sample_rate=0.1):
    # Sample memories for review
    all_memories = memory_store.get_all()
    review_candidates = [m for m in all_memories 
                         if m.confidence < 1.0 and random() < sample_rate]
    
    for memory in review_candidates:
        # Re-execute the procedure in sandbox
        sandbox_result = execute_in_sandbox(memory.procedure)
        
        if sandbox_result.success:
            memory.confidence = min(memory.confidence + 0.1, 0.95)
            memory.last_verified = datetime.now()
        else:
            # Flag for correction or removal
            reviewer.review(memory, sandbox_result)
            if reviewer.mark_incorrect(memory):
                memory_store.remove(memory.id)
            elif reviewer.provides_correction(memory):
                memory_store.update(memory.id, reviewer.correction)
```

### Memory Representation

Each memory entry uses a structured format:

```json
{
    "task_description": "Create a pivot table in Excel with sales data",
    "application": "Microsoft Excel",
    "os_version": "Windows 11",
    "procedure": [
        {"action": "click", "target": "Insert tab", "confidence": 1.0},
        {"action": "click", "target": "PivotTable button", "confidence": 1.0},
        {"action": "select_range", "target": "A1:D100", "confidence": 0.85},
        {"action": "click", "target": "OK", "confidence": 1.0}
    ],
    "metadata": {
        "source": "agent_success",
        "confidence": 0.88,
        "success_count": 7,
        "last_verified": "2025-06-15",
        "verified_by": "expert_001"
    }
}
```

## Experimental Results

| Metric | Without Memory | Expert Seed Only | Full VerificAgent |
|---|---|---|---|
| OSWorld Office task completion | 25.0% | 38.2% | ~50% |
| Procedure accuracy | — | 92.1% | 87.5% |
| Novel task success | 18.3% | 24.7% | 41.2% |
| Memory entries (after training) | 0 | 247 | 1,384 |

Key findings:
- Expert seeds alone provide a +13.2pp boost; iterative growth adds another +11.8pp
- Human fact-checking prevents accuracy degradation: without it, memory accuracy drops from 92% to ~75% over time due to accumulated errors
- The memory retrieval confidence weighting improves task selection by 15% over uniform retrieval
- Most valuable memories are for multi-step procedures (>5 steps) where the agent would otherwise fail

## Comparison with Other Methods

| Method | OSWorld Score | Memory Quality | Human Cost | Scalability |
|---|---|---|---|---|
| **VerificAgent** | ~50% | 87.5% verified | Medium (periodic) | High (iterative) |
| RAG-only (no memory) | ~30% | N/A | Low | High |
| Pure expert demos | ~38% | 92%+ | Very High | Low |
| Self-learning memory | ~35% | ~60% (drifts) | Low | High |
| [[memeovobench-memory-safety]] baseline | ~28% | Variable | Low | Medium |

VerificAgent balances **memory quality** and **scalability** — it starts with expert-verified high-quality seeds and grows iteratively with periodic human oversight.

## Related Work

- [[memeovobench-memory-safety]] — Memory safety benchmark that evaluates memory corruption risks; VerificAgent's human fact-checking directly addresses the reliability issues identified by MemEvoBench
- [[agent-memory-system]] — General agent memory system taxonomy; VerificAgent is a specific implementation of the "verified procedural memory" paradigm
- [[agent-align]] — Safety alignment for agents; VerificAgent focuses on memory verification as a complementary safety mechanism

## Deployment Recommendations

1. **Start with expert seeds for critical tasks**: Identify the 20-50 most common tasks and create expert-verified procedures first. These provide immediate value and serve as templates for the agent's self-learning
2. **Automated failure detection**: Implement a sandbox re-execution system that periodically re-runs stored procedures to catch stale memories (application updates may break procedures)
3. **Human review cadence**: For production systems, review ~5-10% of new memories weekly. Adjust based on observed accuracy degradation rate
4. **Version-locking**: Store OS/application version metadata with each memory. Mark memories as potentially stale when the application is updated
5. **Confidence thresholds**: Set a minimum confidence threshold (e.g., 0.7) for memory retrieval. Below this threshold, the agent should fall back to live exploration rather than using unreliable memory
6. **Memory deduplication**: As the memory grows, periodically deduplicate similar procedures, keeping the highest-confidence version
7. **Privacy considerations**: Stored procedures may contain screenshots with sensitive data. Implement data sanitization before storing visual memory entries
