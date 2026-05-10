---
title: "AgenticQwen — Dual Data Flywheels for Small Agentic Models"
created: 2026-05-02
updated: 2026-05-02
type: concept
tags: [training, fine-tuning, tool-use, rl]
sources: [raw/papers/2026/04/2604.21590.md]
---

# AgenticQwen — Dual Data Flywheels for Small Agentic Models

**arXiv:** [2604.21590](https://arxiv.org/abs/2604.21590)
**Authors:** Yuanjie Lyu, Chengyu Wang, Haonan Zheng, Yuanhao Yue, Junbing Yan, Ming Wang, Jun Huang (Alibaba Group)
**Date:** April 2026
**Code/Data:** [HuggingFace](https://huggingface.co/collections/alibaba-pai/agenticqwen) | [GitHub](https://github.com/haruhi-sudo/data_synth_and_rl) | [EasyDistill](https://github.com/modelscope/easydistill)

## 一、核心问题

工业场景需要模型作为 agent 进行多步推理和工具调用，但受限于成本和延迟约束，必须使用**小模型**。小模型的 agentic 能力天花板低，需要系统性方法提升。

## 二、Dual Data Flywheels

### Flywheel 1: Reasoning Data Flywheel

从模型的**错误**中学习，自动生成更难的问题：

1. **Self-instruct expansion** (structural diversity) — 从种子任务生成多样化的推理模板
2. **Persona injection** (contextual diversity) — 注入不同推理 persona，创建多样化解题路径
3. **Multi-model consistency filtering** — 只保留多个模型答案一致的任务（质量控制）

**闭环：** 当前模型的错误 → 生成针对弱点更难的任务 → 模型在这些弱点上改进 → 新的错误 → 循环

### Flywheel 2: Agentic Data Flywheel

把线性工作流扩展为反映真实世界决策复杂度的多分支行为树：

**Phase 1: Linear task initialization**
- 从简单线性工具调用工作流开始

**Phase 2: Behavior tree expansion**
- 基于模型观察到的行为，在决策点添加新分支
- 线性工作流逐步增长为多分支行为树

**Phase 3: Branch-to-task inversion**
- 把决策分支转换为新的独立任务
- 扩大任务分布的覆盖范围

**Phase 4: Adversarial mock-user intervention**
- 模拟用户故意误导模型采取错误动作
- 测试和提高鲁棒性

**数据验证：** 每个生成的任务都验证正确性和难度后才加入训练集。

## 三、训练框架

### Multi-Round RL Training

结合 **reasoning RL** 和 **agentic RL**：

**Reasoning RL：**
- 多步问题（数学、搜索）
- 调用工具：web search、code interpreter
- 奖励：最终答案正确性

**Agentic RL：**
- 真实场景：模型与模拟用户和工具环境交互
- 0-1 奖励：基于 rubric 的 evaluator，把每个任务分解为可验证子目标

### 为什么需要 Data Flywheels

单纯 RL 很快达到性能天花板：即使增加数据，训练分布会过于同质化，限制进一步提升。双飞轮持续生成更难的数据，每轮训练后 feedback 到下一轮。

## 四、实验结果

### Public Benchmarks

AgenticQwen 小模型在多个 agentic benchmark 上与**大得多的开源模型**竞争。

### Industrial Application

在企业 agent 系统中，AgenticQwen 在搜索和数据分析任务上**缩小了与 Qwen3-235B 的差距**，同时推理成本更低。

### BFCL-V4 表现

在 Berkeley Function Calling Leaderboard V4 的 web search 和 memory 任务上表现强劲。

## 五、批判性分析

### 优势
- 双飞轮设计覆盖了 reasoning 和 agentic 两个维度
- Behavior tree expansion 是生成复杂多步骤训练数据的有效方法
- 工业部署验证了实际效果

### 不足
1. **实验细节不足** — 论文没有给出详细的 benchmark 分数对比表
2. **Flywheel 效率指标缺失** — 没有报告每轮数据生成的质量提升曲线
3. **Adversarial mock-user 的具体策略未公开** — 如何生成有效的对抗策略不清楚
4. **小模型的具体参数量未明确** — 只知道是"small"，没有给出具体数字

### 对我们的启发
- **Data flywheel + OPD 组合：** CoPD 需要高质量数据做 RLVR，AgenticQwen 的飞轮可以自动生成这种数据。Behavior tree expansion 生成的复杂多步骤数据对测试小模型 OPD 吸收能力极限很有用
- **Error-driven data generation：** 从模型错误中生成更难任务的思路可以用于 OPD 训练——识别 student 无法从 teacher 吸收的能力，针对性地生成训练数据

## Related

- [[tool-use]] — LLM agent 的工具使用
- [[agentic-coding]] — Agentic 编码系统
- [[less-is-more-agentic]] — 高效 agentic 方法
- [[knowledge-distillation]] — 知识蒸馏技术
- [[rl-post-training-scaling-laws]] — RL 缩放定律
