---
title: "LongCat-Flash-Thinking"
created: 2026-05-01
updated: 2026-05-01
type: entity
tags: [model, architecture, training, reasoning, chain-of-thought, tool-use, open-source, rl]
sources: [raw/papers/2025/09/2509.18883.md]
---

# LongCat-Flash-Thinking

美团 LongCat 团队发布的开源 MoE 推理模型（arXiv 2509.18883，2025-09）。基于 [[longcat-flash]] 560B 架构，通过**长 CoT 冷启动 + 大规模 RL** 两阶段训练，在复杂推理和 Agentic 任务上达到开源 SOTA。

## 一、核心参数

| 参数 | 值 |
|------|-----|
| 总参数量 | 560B（MoE，继承自 LongCat-Flash） |
| 激活参数量 | ~27B（平均） |
| 上下文窗口 | 128K tokens |

## 二、训练管线（两阶段）

### 阶段一：Long CoT 冷启动训练

目标：为 RL 阶段建立基础推理能力。

#### 1. 中期预训练（Mid-training）

课程学习策略，增强内在推理能力：
- **STEM 数据**：数学、科学推理
- **代码数据**：代码生成与理解
- **逻辑推理**：形式化与常识推理

#### 2. 推理导向 SFT

- **通用推理**：STEM + 代码 + 逻辑 + 通用 QA
- **形式化推理**：
  - 任务定义 → 命题形式化 → 迭代证明合成
- **Agentic 推理**：
  - 工具使用查询选择
  - 自动轨迹合成（多智能体框架生成复杂工具交互轨迹）

### 阶段二：大规模强化学习（RL）

#### RL 基础设施：DORA 系统

**DORA（Dynamic ORchestration for Asynchronous rollout）**：美团自研的大规模异步 RL 训练框架。

三个并行阶段：
1. **Generation Phase**：异步生成 rollout
2. **Experience-Maker Phase**：经验数据准备
3. **Model Training Phase**：模型训练

**性能**：相比同步方法，训练速度提升 **>3倍**（数万张加速器规模）。

#### RL 算法

**训练目标**：扩展 GRPO（Group Relative Policy Optimization），适应异步训练。

**高效训练策略**：
- **有放回在线过滤（With-replacement Online Filtering）**：过滤低质量样本
- **陈旧度控制（Staleness Control）**：管理异步训练中的策略陈旧度
- **不完全信号掩码（Incomplete-Signal Masking）**：处理未完成轨迹的奖励信号

#### 奖励系统

- **不可验证任务**：基于 LLM 评判的奖励
- **可验证任务**：规则化奖励（数学、代码等）

#### 领域并行训练（Domain-Parallel Training）

核心创新：**解耦不同领域的优化**。

1. **领域 RL**：在 STEM、代码、Agentic 等领域分别进行 RL，得到多个领域专家模型
2. **模型融合**：将多个领域专家融合为单一模型
3. **通用 RL**：融合后进一步做通用 RL，提升鲁棒性、安全性和人类对齐

**优势**：避免多任务 RL 中的任务间干扰，实现接近 Pareto 最优的融合模型。

## 三、评测表现

在复杂推理任务上达到开源模型 SOTA。

**关键指标**：
- **AIME-25**：平均 token 消耗降低 **64.5%**（从 19,653 降至 6,965），同时不降低准确率
- 数学推理、代码生成、Agentic 工具使用等 benchmark 全面领先开源模型

**效率优势**：领域并行训练 + DORA 异步框架，大幅提升训练效率。

## 四、开源信息

- **HuggingFace**：https://huggingface.co/meituan-longcat/LongCat-Flash-Thinking
- **GitHub**：https://github.com/meituan-longcat/LongCat-Flash-Thinking

## 五、相关页面

- [[longcat-flash]] — LongCat-Flash：基础模型
- [[longcat-flash-thinking-2601]] — LongCat-Flash-Thinking-2601：升级版推理模型
- [[longcat-flash-omni]] — LongCat-Flash-Omni：全模态版本
- [[chain-of-thought]] — Chain-of-Thought：推理技术基础概念
