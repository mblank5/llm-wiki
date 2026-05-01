---
title: "Code-A1: Adversarial Evolving of Code LLM and Test LLM via Reinforcement Learning"
created: 2026-05-01
updated: 2026-05-01
type: concept
tags:
  - coding
  - rl
  - adversarial
  - self-play
sources:
  - raw/papers/2026/03/2603.15611.md
---

# Code-A1: 通过强化学习对抗演化编码 LLM 与测试 LLM

Code-A1 通过将 Code LLM 与 Test LLM 分离为独立模型进行对抗协同训练，解决了自博弈中自共谋 (self-collusion) 的核心问题，生成的测试质量可替代人工标注。

## Overview

Code-A1 提出了一种对抗式代码-测试协同演化框架。核心问题是：标准 RLVR 依赖静态人工标注的测试用例，但这些测试数量有限（通常 3-5 个）且无法适应模型能力的变化。自博弈框架则面临自共谋问题——当单一模型同时生成代码和测试时，模型会利用白箱访问产生简单测试以获取轻松奖励。

Code-A1 的解决方案是将 Code LLM ($\pi_C$) 和 Test LLM ($\pi_T$) 初始化为独立模型，通过对抗性 rollout 进行联合训练。Test LLM 可以观察候选代码（白箱模式）并生成针对性测试，但由于两个模型参数独立更新，不存在自共谋激励。

## Key Contribution

### 1. 对抗式 Rollout 机制

- Code LLM 为问题 $Q$ 生成 $M$ 个候选解 $\{\hat{C}_1, \ldots, \hat{C}_M\}$
- Test LLM 为每个候选解生成 $N$ 组测试（每组 $K=5$ 个测试用例）
- 测试格式: `assert func(*args) == answer`，通过 AST 解析提取

### 2. 奖励设计

Test LLM 的奖励函数平衡有效性和对抗性:

$$r_T = \alpha \cdot r_{\text{valid}} + (1 - \alpha) \cdot r_{\text{adversarial}}$$

其中 $\alpha = 0.5$，确保测试既合法又有区分度。

### 3. Mistake Book 机制

引入经验回放机制，将历史错误案例记录在 "Mistake Book" 中，用于后续训练时提高数据利用效率。

### 4. 策略优化

使用 GRPO (Group Relative Policy Optimization) 进行策略更新，训练 111 步。

## Experimental Results

### Code LLM 性能 (avg@32)

| Base Model | 方法 | HumanEval+ | MBPP+ | BigCodeBench | Avg |
|-----------|------|-----------|-------|-------------|-----|
| 1.5B-Instruct | Golden Tests | 71.15 | 63.30 | 34.23 | 56.23 |
| 1.5B-Instruct | Self-Play | 70.64 | 63.54 | 33.47 | 55.88 |
| 1.5B-Instruct | **Code-A1** | **72.69** | 63.33 | **34.82** | **56.95** |
| 3B-Instruct | **Code-A1** | **83.52** | **69.07** | **45.85** | **66.15** |
| 7B-Instruct | **Code-A1** | **85.21** | **74.50** | **52.46** | **70.72** |

### Test LLM 性能 (UnLeakedTestBench pass@1)

| Base Model | 方法 | pass@1 |
|-----------|------|--------|
| 7B-Instruct | / | 27.71 |
| 7B-Instruct | SFT | 29.32 |
| 7B-Instruct | Self-Play | 32.98 |
| 7B-Instruct | **Code-A1** | **36.79** |

### 关键发现

- Code-A1 生成的测试用于 RLVR 训练时，平均准确率 **56.75%** 超过人工标注 (**56.23%**)
- 在并行测试时扩展 (Parallel TTS) 中，Code-A1 Code+Test 联合使用达到 **67.81%** 平均准确率
- 对抗协同演化使两个模型同步改进，无需手动奖励校准

## Related

- [[self-play-limitations]] — 自博弈中的自共谋问题及分离模型策略
- [[agentic-coding]] — 编码 LLM 的对抗训练范式
- [[grpo]] — Code-A1 使用的 GRPO 策略优化方法
