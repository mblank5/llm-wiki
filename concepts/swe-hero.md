---
title: "SWE-HERO: 从无执行到有执行的 SWE Agent 训练"
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [agentic-coding, swe-agent, fine-tuning, execution]
sources: [raw/papers/2026/04/2604.01496.md]
---
# SWE-ZERO to SWE-HERO

## 核心转变
SWE Agent 训练从 **execution-free**（纯 SFT）走向 **execution-based**（带环境反馈的 RL）。

## 方法
- Execution-free: 纯文本训练，不运行代码
- Execution-based: 训练时执行 patch，用测试结果做 reward
- 渐进式从 free 到 based 的训练策略

## 意义
执行反馈是 SWE Agent 超越纯文本推理的关键。类似于 RLVR 在推理模型中的作用。

## Related
- [[agentic-coding]]
- [[oracle-swe]]
- [[grpo-rl-training]]
