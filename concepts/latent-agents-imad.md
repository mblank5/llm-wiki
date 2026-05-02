---
title: Latent Agents — Internalized Multi-Agent Debate (IMAD)
created: 2026-05-02
updated: 2026-05-02
type: concept
tags: [distillation, reasoning, alignment]
sources: [raw/papers/2026/04/2604.24881.md]
---

# Latent Agents — Internalized Multi-Agent Debate (IMAD)

**arXiv:** [2604.24881](https://arxiv.org/abs/2604.24881)
**Authors:** John Seon Keun Yi, Aaron Mueller, Dokyun Lee (Boston University)
**Date:** April 2026

## 一、核心方法：两阶段后训练

### Stage 1: Debate Structure Learning (SFT)

**数据集构造：**
- 3 agents × 2 rounds multi-agent debate（Du et al., 2023 配置）
- Base model: GPT-3.5 turbo
- 问题：6 个随机两位数的算术表达式（如 91+24*13+45-41*38）
- 过滤：没有 majority consensus 的 debate 丢弃
- 加 structure tags: `<|Agent 1|>`, `<|Round 1|>`, `<|Consensus|>`, `<|endofdebate|>`
- 收集 944 条 debate trace {Question, Trace, Answer}

**为什么用算术题：** 答案短、关注结构学习而非长推理、中等难度、不需要 benchmark 数据。

SFT 训练模型学习复制 debate 结构。

### Stage 2: RL for Internalization

**动态 reward scheduling — 两个机制协同：**

**1. Decaying format reward:**

$$R_{\text{fmt}}(y) = \begin{cases} w_{\text{fmt}} & \text{if format is correct} \\ 0 & \text{otherwise} \end{cases}$$

$w_{\text{fmt}} \to 0$ over training — 逐步降低对 debate 结构格式化的奖励。

**2. Length annealing with correctness reward:**

$$R(y; l) = \begin{cases} 1 & \text{if } y^* \in \text{clip}(y, l) \\ 0 & \text{otherwise} \end{cases}$$

其中 $\text{clip}(y, l)$ 截断输出到前 l 个 tokens。正确答案 $y^*$ 必须在截断前缀中才给奖励。

长度上限逐步收紧：$l^0 \to l^1 \to \cdots \to l^*$

- $l^0$：宽松，允许完整 debate verbalization
- $l^*$：严格，只够放简洁答案

**Internalization 机制：** 两个动态信号协同——decaying format reward 移除了 verbalize debate 的动机，shrinking length limit 使得这样做时无法拿到 correctness reward。唯一策略：把 multi-perspective analysis 内化到 latent space，直接输出答案。

## 二、Mechanistic Analysis: Agent Subspaces

### Steering Vector 提取（difference-in-means）

$$\vec{v}_i = \frac{1}{|S_i|}\sum_{x \in S_i} h(x) - \frac{1}{|S_{\neg i}|}\sum_{x \in S_{\neg i}} h(x)$$

其中 $h(x)$ 是 hidden state activation，$S_i$ 是 agent i 激活的样本集。

### 关键发现

1. **Agent-specific subspaces 存在** — internalization 创建了激活空间中对应不同 agent 视角的线性可分方向
2. **Debate 结构没有 collapse** — model steering 时 steered IMAD 模型表现出 agent-specific 行为
3. **Structure tags 的重要性** — 没有 tags 时 subspace 分离不明显

### 安全应用：Malicious Agent Suppression

- 在 IMAD 中 instill malicious agent（通过 internalized debate）
- 用 negative steering 抑制这个 agent
- 结果：harmful behaviors 更容易 localize 和 control
- 相比 steering base models，general performance 下降更小

## 三、完整实验结果

### 主实验（3 个模型 × 5 种方法 × 3 个 benchmark）

**LLaMA-3.1-8B-Instruct:**

| Method | GSM8K | MMLU-Pro | BBH | Token Consumption |
|--------|-------|----------|-----|-------------------|
| Single | 79.93 | 61.10 | 56.37 | 547 |
| Debate | 83.03 | 64.60 | 51.06 | 5,758 |
| DebateGPT | 74.42 | 60.58 | 55.83 | 455 |
| SFT | 79.23 | **75.60** | 54.91 | 992 |
| **IMAD (SFT+RL)** | **85.20** | 62.00 | **58.53** | **644** |

**Qwen2.5-7B-Instruct:**

| Method | GSM8K | MMLU-Pro | BBH | Token Consumption |
|--------|-------|----------|-----|-------------------|
| Single | 86.07 | 48.87 | 62.51 | 577 |
| Debate | **91.37** | 57.67 | 67.58 | 2,320 |
| DebateGPT | 89.43 | 54.10 | 63.93 | 358 |
| SFT | 86.37 | 50.60 | 67.14 | 957 |
| **IMAD (SFT+RL)** | 89.67 | 52.87 | **70.11** | **389** |

**Mistral-Nemo-12B-Instruct:**

| Method | GSM8K | MMLU-Pro | BBH | Token Consumption |
|--------|-------|----------|-----|-------------------|
| Single | 75.40 | 39.17 | 58.70 | 332 |
| Debate | 61.03 | **41.30** | 62.76 | 1,697 |
| DebateGPT | 71.70 | 40.40 | 59.07 | 327 |
| SFT | 74.37 | 36.20 | 63.66 | 1,053 |
| **IMAD (SFT+RL)** | **80.00** | 38.97 | **63.73** | **358** |

**Token reduction:** 6-21% of explicit debate consumption.

### Generalization

只在算术问题上训练，但 MMLU-Pro 和 BBH 上也有提升 — **跨域泛化**。

## 四、批判性分析

### 优势
- Mechanistic interpretability 扎实：agent subspaces 发现有意义
- Safety 应用（malicious agent suppression）是新颖方向
- 三种架构都验证了

### 不足
1. **训练数据太简单** — 只用 6 个两位数的算术表达式，复杂推理能力没验证
2. **DebateGPT 基线太弱** — 只用 final response 做蒸馏，没用完整 debate trace
3. **MMLU-Pro 在 Qwen2.5-7B 上 IMAD 远不如 SFT** (52.87 vs 75.60) — 差距很大，论文没有充分解释
4. **Structure tags 必要性** — 说没有 tags 时 subspace 分离不明显，但没有定量对比
5. **RL 具体算法未详述** — 论文说用 RL with dynamic reward scheduling，但没用 PPO/GRPO 等标准名称

### 对我们的启发
- **GKD/OPSD internalization** — IMAD 的 RL internalization 思路可用于 OPSD：不仅让学生模仿 teacher 的 token distribution，还让学生把 teacher 的 reasoning process 内化
- **Activation steering 控制 expert behavior** — 对 MoE 模型的 router behavior 可能有启发：如果不同 expert 形成可分离 subspace，可通过 steering 控制 expert 激活

## Related

- [[on-policy-self-distillation]] — 自蒸馏推理
- [[knowledge-distillation]] — 知识蒸馏基础
- [[deepseek-r1-distillation]] — 推理模型蒸馏
- [[reasoning-distillation]] — 推理能力蒸馏
- [[behavioral-self-awareness]] — 模型自我意识
