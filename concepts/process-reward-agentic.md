---
title: "Rewarding the Scientific Process: Process-Level Reward Modeling for Agentic Data Analysis"
created: 2026-05-01
updated: 2026-05-01
type: concept
tags:
  - reward-model
  - agent
  - process-reward
sources:
  - raw/papers/2026/04/2604.24198.md
---

# DataPRM: 面向智能体数据分析的过程级奖励建模

DataPRM 提出了一种环境感知的过程奖励模型，通过 ReAct 范式与代码执行环境交互来验证数据分析每一步的正确性，仅用 4B 参数即超越 72B 级通用 PRM。

## Overview

现有的过程奖励模型 (PRM) 主要针对数学推理和代码生成设计，直接迁移到数据分析任务时存在两个关键失败模式：(1) 无法验证代码执行结果的正确性；(2) 缺乏与环境交互的能力来判断中间步骤是否有效。

DataPRM (Data Process Reward Model) 是一个环境感知的生成式 PRM，它采用与数据分析 Agent 相同的 ReAct 范式，能够执行代码并与环境交互来验证每一步推理。它不仅评估当前步骤的质量，还将历史验证反馈累积到后续判断中，形成连贯的多步验证链。

## Key Contribution

### Environment-Aware Verifier Architecture

DataPRM 的输入上下文:

$$h_{t,0}^{prm} = h_t \oplus \tau_t = h_t \oplus (z_t, a_t, o_t)$$

其中 $h_t$ 是到时间步 $t$ 的完整轨迹，$\tau_t$ 是当前步骤（思考 $z_t$、动作 $a_t$、观察 $o_t$）。

DataPRM 进入多步内部验证循环，在每步 $k$ 生成验证元组 $\kappa_{t,k} = (\hat{z}_k, \hat{a}_k, \hat{o}_k)$，最终输出标量质量分数 $r_t$ 和解释性理由 $c_t$。

关键创新：历史验证反馈 $f_t = (r_0, c_0, r_1, c_1, \ldots, r_{t-1}, c_{t-1})$ 被显式追加到后续验证上下文中:

$$h_{t,0}^{prm} = h_t \oplus f_t \oplus \tau_t$$

### 训练细节

- 基座模型: Qwen3-4B-Instruct
- 训练: ms-swift, 学习率 1e-5, batch size 32, 3 epochs
- 硬件: 8x H20 GPUs

## Experimental Results

### Test-Time Scaling (Best-of-N)

DataPRM (4B) 在 ScienceAgentBench 上:

| 方法 | 参数量 | Best-of-8 | Best-of-16 |
|------|--------|-----------|------------|
| Qwen2.5-Math-PRM-72B | 72B | 33.33% | 31.33% ↓ |
| GenPRM-32B | 32B | — | — |
| DeepSeek-V3.2 Judge | — | — | — |
| Qwen3-235B Self-reward | 235B | — | — |
| **DataPRM** | **4B** | **持续提升** | **持续提升** |

关键发现:
- Qwen2.5-Math-PRM-72B 在 N 从 8→16 时性能**下降** (33.33% → 31.33%)，说明通用 PRM 无法区分有效推理和幻觉
- DataPRM 在 Beam Search 下保持稳定提升 (35.33% → 38.00% → 38.89%)
- 而 Qwen2.5-Math-PRM-72B 在 Beam Search 下出现 "reward hacking" (33.56% → 30.89% → 32.44%)

### Ablation: 环境交互的必要性

| 变体 | Hard@N=16 |
|------|-----------|
| CoT baseline | 35.71% |
| Single-turn Code w/ Env | 36.51% |
| Multi-turn Code w/ Env | **最优** |

环境交互和代码执行反馈是提升验证准确率的关键因素。

## Related

- [[free-process-rewards]] — 无需过程标注的过程奖励方法对比
- [[swe-shepherd]] — 软件工程领域的过程验证与引导
- [[agent-r1-end-to-end-rl]] — 端到端强化学习训练智能体的方法
