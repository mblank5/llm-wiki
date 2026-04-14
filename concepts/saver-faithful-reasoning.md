---
title: SAVeR: Self-Audited Verified Reasoning
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [agent, reasoning, faithfulness, self-auditing, belief]
sources: [raw/papers/2026/04/2604.08401.md]
---

# SAVeR: Agent 的自审计验证推理

## 核心问题

LLM Agent 的推理轨迹被当作可靠内部信念，但连贯推理仍可能违反逻辑/证据约束，
导致 **系统性行为漂移** (systematic behavioral drift)。

## 方法

**在行动前验证内部信念状态**：

1. **Persona-based diverse belief generation**: 生成多样化的候选信念
2. **Adversarial auditing**: 定位逻辑违反
3. **Constraint-guided minimal intervention**: 最小修正
4. **Verifiable acceptance criteria**: 验证修复后的 faithfulness

## 结果

6 个 benchmark 上，faithfulness 显著提升：
- HotpotQA: violation-free rate 81.36% (avg violations: 0.37)
- 在保持 task performance 的同时减少推理不忠实

## 意义

将 agent 推理从"信任模型输出"转向"验证后行动"，对长 horizon agent 系统尤为重要。

## Related

- [[memreader]]
- [[llm-post-training-unified-view]]
