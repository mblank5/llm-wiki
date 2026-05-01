---
title: "Process Supervision of Confidence Margin for Calibrated LLM Reasoning"
created: 2026-05-01
updated: 2026-05-01
type: concept
tags:
  - rl
  - reasoning
  - calibration
  - process-reward
sources:
  - raw/papers/2026/04/2604.23333.md
---

# RLCM: 置信度边际的过程监督实现校准推理

RLCM 通过在推理轨迹的中间状态上施加边际 (margin) 化校准奖励，使模型在保持推理准确率的同时显著降低过度自信，整体 PCE 从 0.065 降至 0.036。

## Overview

推理大模型 (reasoning LLMs) 虽然通过扩展测试时计算取得了优异性能，但其置信度表达并不可靠——模型可能"自信地犯错"。现有校准方法（如 Brier 分数匹配）将校准作为逐实例目标与推理优化耦合，导致准确率-校准的脆弱权衡，无法获得一致的 Pareto 改进。

RLCM (Reinforcement Learning with Confidence Margin) 采取了一种更温和的相对校准监督策略：不强制每一步的置信度匹配正确性，而是将校准建模为中间推理状态的排序问题——鼓励模型给更可解的推理前缀分配更高置信度。

## Key Contribution

### 1. 为什么不用直接分数匹配

直接 Brier 奖励: $r = \mathbb{I}(Y = \hat{Y}) - \lambda(\mathbb{I}(Y = \hat{Y}) - p)^2$

实验发现调整 $\lambda$ 仅在准确率-校准之间做权衡，不产生一致 Pareto 改进。因此 RLCM 转向**相对排序监督**。

### 2. Probe-Based 置信度估计

在推理轨迹的截断点 $b \in \mathcal{B}(y)$，提取策略模型最后层隐状态 $h_b(y)$，训练轻量级 probe 估计中间正确性:

$$Y_b(y) = \frac{1}{K}\sum_{k=1}^{K} \mathbf{1}[\hat{a}_{b,k} = a^*] \in [0,1]$$

通过在截断前缀后强制生成最终答案并采样 $K$ 次完成，用 Monte Carlo 准确率作为中间正确性的软标签。

### 3. Margin-Based 过程校准奖励

RLCM 定义了一个边际奖励，鼓励正确前缀的置信度高于错误前缀:

$$r_{\text{calib}} = \text{margin}(\text{conf}(\text{correct prefix}), \text{conf}(\text{incorrect prefix}))$$

这个奖励与最终答案正确性奖励结合为完整的 RL 训练目标。

## Experimental Results

基于 R1-distilled Qwen-7B，在 GRPO-LEAD 数据集上训练。

### 数学推理 (Overall)

| 方法 | Conf. | Acc ↑ | PCE ↓ | ECE ↓ |
|------|-------|-------|-------|-------|
| Base | probe | .543 | .066 | .101 |
| GRPO | probe | .621 | .065 | .130 |
| RLCR | verbal | .610 | .189 | .189 |
| C²GSPG | logits | .618 | .211 | .232 |
| **RLCM** | **probe** | **.618** | **.036** | **.091** |

### MATH-500

| 方法 | Acc ↑ | PCE ↓ | ECE ↓ |
|------|-------|-------|-------|
| GRPO | .891 | .000 | .203 |
| RLCR | .888 | .065 | .065 |
| **RLCM** | **.891** | **.000** | **.133** |

### AIME 2024

| 方法 | Acc ↑ | PCE ↓ | ECE ↓ |
|------|-------|-------|-------|
| GRPO | .479 | .108 | .108 |
| RLCR | .473 | .243 | .243 |
| **RLCM** | **.492** | **.049** | **.061** |

### OOD: LiveCodeBench / GPQA

| 方法 | LCB Acc | LCB PCE | GPQA Acc | GPQA PCE |
|------|---------|---------|----------|----------|
| GRPO | .380 | .004 | .360 | .050 |
| **RLCM** | **.389** | **.050** | **.371** | **.043** |

关键发现:
- RLCM 在保持与 GRPO 相当准确率的同时，PCE 从 .065 降至 .036（降低 45%）
- AIME 2024 上准确率最高 (.492) 且 PCE 最低 (.049)
- 跨域 (LiveCodeBench, GPQA, LogiQA) 泛化性能一致优于所有校准基线

## Related

- [[opd-calibration]] — 策略蒸馏中的校准方法
- [[free-process-rewards]] — 免过程标注的过程奖励方法
- [[rl-post-training-scaling-laws]] — RL 后训练的扩展规律与校准关系
