---
title: "PASK: 意图感知的主动 Agent"
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [agent, proactive, memory, intent, streaming]
sources: [raw/papers/2026/04/2604.08000.md]
---

# PASK: 意图感知的主动 Agent

## 范式转变

从被动响应 (reactive) → 主动介入 (proactive)：从用户行为推断潜在需求，在实时约束下主动行动。

## DD-MM-PAS 框架

1. **Demand Detection (DD)**: 流式 IntentFlow 模型检测用户意图
2. **Memory Modeling (MM)**: 混合记忆（workspace / user / global）
3. **Proactive Agent System (PAS)**: 基于意图和记忆的主动行动

## 关键挑战

- 深度、复杂度、歧义、精度、实时约束
- 需要从流式上下文推断潜在需求
- 行动必须 grounding 在不断演化的用户记忆上

## 意义

定义了 streaming proactive AI agent 的通用范式，将记忆建模与意图检测解耦。

## Related

- [[hypermem]]
- [[memreader]]
- [[lightmem-agent-memory]]
