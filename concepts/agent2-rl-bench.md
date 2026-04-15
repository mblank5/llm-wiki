---
title: "Agent² RL-Bench: Agentic RL Post-Training"
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [rl, agent, benchmark, grpo, post-training, automated]
sources: [raw/papers/2026/04/2604.10547.md]
---
# Agent² RL-Bench

## 核心问题
LLM Agent 能否自主设计、实现、运行完整的 RL pipeline 来改进 foundation model？

## Benchmark 设计
6 个任务，3 个层级：
1. Static rule-based training
2. Closed-loop online RL with trajectory collection
3. 完整 RL pipeline（数据 + 训练 + 评估）

## 关键发现
- ALFWorld: RL-only agent 从 **5.97 → 93.28**（SFT warm-up + GRPO）
- DeepSearchQA: 仅 +2.75（在噪声范围内）
- **SFT pipeline 在固定预算下仍优于 online RL**
- Driver LLM 选择对 interactive task 有巨大影响（同 scaffold 换 driver 从 0 到 +78pp）

## 意义
微软出品，首次系统评测 "AI 做 RL 后训练" 的能力。揭示了 agentic RL 的潜力和局限。

## Related
- [[grpo-rl-training]]
- [[llm-post-training-unified-view]]
- [[agentic-coding]]
