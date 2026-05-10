---
title: "Skill-SD: Skill-Conditioned Self-Distillation"
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [self-distillation, agent, multi-turn, skill-conditioned]
sources: [raw/papers/2026/04/2604.10674.md]
---
# Skill-SD: Skill-Conditioned Self-Distillation for Multi-turn Agents

## 核心思路
多轮 Agent 场景下的 self-distillation：按 skill 类型条件化蒸馏，让 agent 在不同能力维度上独立学习。

## 意义
将 self-distillation 从单轮扩展到多轮 agent 交互，与 [[on-policy-self-distillation]] 理念一脉相承。

## Related
- [[on-policy-self-distillation]]
- [[agentic-coding]]
