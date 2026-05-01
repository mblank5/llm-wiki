---
title: "GASP: Guided Asymmetric Self-Play For Coding LLMs"
created: 2026-05-01
updated: 2026-05-01
type: concept
tags:
  - self-play
  - coding
  - rl
  - agent
sources:
  - raw/papers/2026/03/2603.15957.md
---

# GASP: 引导式非对称自博弈用于编码大模型

GASP 提出通过真实困难样本作为"标杆"引导教师模型生成更有意义的训练题，解决了非对称自博弈中探索效率低下的核心瓶颈。

## Overview

GASP (Guided Asymmetric Self-Play) 是一种面向编码 LLM 后训练的引导式非对称自博弈框架。在标准 RLVR (Reinforcement Learning from Verifiable Rewards) 中，训练问题通常从静态数据集均匀采样，但相当一部分困难问题因探索难度过高而始终无法被解决。GASP 的核心洞察是：这些已知的困难问题恰恰可以作为"标杆" (goalposts)，用来引导教师 (teacher) 模型生成更有意义的中间难度问题 (lemmas 和 lifts)，从而逐步接近原本不可解的难题。

与不使用任何引导的 Absolute Zero (AZR) 框架相比，GASP 通过引入目标导向的课程学习，使自博弈生成的训练信号更具相关性和信息量。

## Key Contribution

### Goalpost-Guided Self-Play

给定一组困难真实问题 $\mathcal{H}$ 作为标杆，GASP 的流程如下：

1. **Lemma 生成**: 对于目标 $h \in \mathcal{H}$，教师模型生成一个更简单的实例 $\ell_0$（lemma），保留 $h$ 的高层模式 (motif)。
2. **Lift 生成**: 在 lemma 基础上生成一个更难的变体（lift），作为从简单到困难的过渡。
3. **Rejection Sampling**: 通过多样性检查确保 lemma/lift 提案之间保持足够的差异性，防止过拟合和模式坍塌。

### 训练框架

- 基础模型: Qwen2.5-Coder-7B
- 评估集: LiveCodeBench v5 (216 questions, 2024.10–2025.02)
- 训练/标杆分割: 2024.08 之前的 601 道题
- 教师 $\pi_{\theta}^T$ 和学生 $\pi_{\theta}^S$ 共享参数，仅通过角色提示区分

GASP 支持两种模式：纯引导自博弈 (GASP) 和联合训练变体 (GASP + Real-data RL)，后者将引导自博弈与标准 RLVR 结合。

## Experimental Results

在 LiveCodeBench v5 上的 pass@k 结果：

| 方法 | Real-data Training | Real-data Guidance | LCB v5 pass@1 | LCB v5 pass@20 |
|------|-------------------|-------------------|---------------|----------------|
| Qwen2.5-Coder-7B (base) | — | — | 13.55 | 29.68 |
| AZR (unguided self-play) | ✗ | ✗ | 17.49 | 31.15 |
| Real-data RL | ✓ | ✗ | 18.91 | 33.10 |
| **GASP** | ✗ | ✓ | **18.26 ±0.68** | **33.69 ±0.28** |
| **GASP + Real-data RL** | ✓ | ✓ | **19.93 ±0.88** | **34.46 ±0.34** |

关键发现:
- GASP 相比 base 模型提升约 +4.7 pass@1，一致优于 AZR
- GASP + Real-data RL 联合训练进一步提升至 19.93 pass@1，证明引导自博弈与标准 RLVR 互补
- 在 HumanEval+、MBPP+ 上也观察到类似趋势

## Related

- [[self-play-limitations]] — 非对称自博弈面临的核心挑战与 GASP 的应对策略
- [[agentic-coding]] — 编码 LLM 的 Agent 化训练范式
- [[swe-shepherd]] — 软件工程验证与测试生成中的引导方法
