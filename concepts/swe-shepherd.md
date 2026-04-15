---
title: SWE-Shepherd: PRMs for Code Agents
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [agentic-coding, prm, process-reward, code-agent]
sources: [raw/papers/2026/04/2604.10493.md]
---
# SWE-Shepherd: Process Reward Models for Code Agents

## 核心
将 Process Reward Model (PRM) 应用于代码 Agent：不仅评估最终结果，还评估每一步代码生成的质量。

## 意义
- PRM 从数学推理扩展到代码生成
- Step-level feedback 比 outcome-level 更适合长 horizon 代码任务
- 与 [[free-process-rewards]] 的 process-level RL 理念一致

## Related
- [[agentic-coding]]
- [[free-process-rewards]]
- [[oracle-swe]]
