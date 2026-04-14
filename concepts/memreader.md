---
title: MemReader: 从被动到主动的记忆提取
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [memory, agent, grpo, react, long-term, extraction]
sources: [raw/papers/2026/04/2604.07877.md]
---

# MemReader: 主动式 Agent 记忆提取

## 核心转变

记忆提取从 **被动转录** (one-shot transcription) 转向 **主动决策** (reasoning-driven selective extraction)。

## 两个模型

### MemReader-0.6B
- 轻量级被动提取器
- 蒸馏自大模型，低成本高效率
- 适合结构化提取、低延迟场景

### MemReader-4B
- 主动提取器，用 **GRPO** 训练
- ReAct 式决策：评估信息价值 → 参考歧义 → 完整性判断
- 操作：选择性写入 / 推迟不完整输入 / 检索历史 / 丢弃噪声

## 训练 Pipeline

SFT → DPO → GRPO 多阶段训练：
- Protocol compliance (SFT)
- Reasoning quality (DPO)
- Memory accuracy + multi-level reward shaping (GRPO)

## 结果

- LOCOMO / LongMemEval / HaluMem 上全面超越 baseline
- 特别是 **knowledge updating** 和 **temporal reasoning** 任务
- 已部署在 MemOS 实际产品中

## 意义

- "写什么记忆"本身需要推理，不是简单的信息抽取
- GRPO 在记忆管理决策上的应用是新颖的

## Related

- [[hypermem]]
- [[lightmem-agent-memory]]
- [[grpo-rl-training]]
