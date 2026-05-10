---
title: "COS-PLAY — Co-Evolving LLM Decision and Skill Bank Agents"
created: 2026-05-02
updated: 2026-05-02
type: concept
tags: [rl, training, fine-tuning]
sources: [raw/papers/2026/04/2604.20987.pdf]
---

# COS-PLAY — Co-Evolving LLM Decision and Skill Bank Agents

**arXiv:** [2604.20987](https://arxiv.org/abs/2604.20987)
**Authors:** Xiyang Wu, Zongxia Li, Guangyao Shi, Alexander Duffy, Tyler Marques, Matthew Lyle Olson, Tianyi Zhou, Dinesh Manocha (UMD + USC + MBZUAI)
**Date:** April 2026
**Code:** [GitHub](https://github.com/wuxiyang1996/COS-PLAY)

## 一、核心问题

LLM 在长程交互环境中做 consistent 决策困难，因为缺乏**发现、保留和复用结构化 skill** 的机制。现有 LLM agent 没有类似 Atari/AlphaZero 中 self-improving game agent 的 explore-learn-reuse 循环。

## 二、COS-PLAY 架构

### Decision Agent

在每个 timestep，决策 agent 执行三步操作：

**1. Skill 检索与选择：**
$$\tilde{s}_t = \pi^{skill}_\theta(o_t, B)$$

从 skill bank $B$ 中检索候选 skill，基于当前观测 $o_t$ 选择。

**2. Intention 更新：**
$$z_t = \pi^{int}_\theta(o_t, \tilde{s}_t)$$

基于观测和选中的 skill 更新 intention state。

**3. Action 执行：**
$$a_t \sim \pi^{act}_\theta(\cdot | o_t, z_t, \tilde{s}_t)$$

优化目标：最大化期望累积奖励
$$\max_\theta J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta}\left[\sum_{t=1}^T r_t\right]$$

### Skill Bank Agent

Skill bank agent 管理 skill 的发现、学习和维护管线：

**1. Infer Segmentation** — 将高价值轨迹片段映射到已有 skill，允许新 skill 出现
**2. Contract Learning** — 学习紧凑的状态转移摘要（contracts），跨 episode 泛化
**3. Skill Bank Maintenance** — 通过保留、探索和基于证据的合并/分裂/拒绝来更新 bank

### Skill Protocol

每个 skill 有结构化 contract：

```
Skill Protocol: MERGE
Summary:        What is the purpose of this skill?
Pre-condition:  When is this skill applicable?
Plan:           How should this skill be carried out?
Success/Abort:  When does it succeed or abort?
Contract:       What changes after execution?
```

## 三、Co-Evolving 训练

### 三阶段循环

```
1. Decision agent 与环境交互，收集 rollouts
2. Skill bank agent 分割轨迹、学习 contracts、更新 skill bank
3. GRPO 同时更新两个 agent
```

### 多 LoRA 设计

两个 agent 各自独立的 LoRA adapter：

**Decision Agent (2 adapters):**
- **Action-taking LoRA:** 奖励在 active skill 上的进展，惩罚不必要的 skill 检索
- **Skill-retrieval LoRA:** 在 episode 结束时评估，奖励导致 contract-satisfying 结果的 skill 检索

**Skill Bank Agent (3 adapters):**
- **Segmentation adapter:** 映射轨迹片段到 skill
- **Contract adapter:** 学习状态转移摘要
- **Curator adapter:** 更新 bank（保留/探索/合并/分裂/拒绝）

这种分解让 agent 同时改进"选择什么 skill"和"如何执行它"。

### Cold Start

- GPT-5.4 作为 teacher 生成 60 条 seed trajectories per game
- SFT 这些轨迹训练 Qwen3-8B，作为两个 agent 的共享初始化

### 训练环境

| 游戏 | 类型 | 难度 |
|------|------|------|
| 2048 | 单人益智 | 中 |
| Candy Crush | 单人益智 | 中 |
| Tetris | 单人控制 | 高 |
| Super Mario Bros. | 单人平台 | 高 |
| Avalon | 多人社交推理 | 很高（隐藏角色） |
| Diplomacy | 多人谈判联盟 | 极高（长程规划） |

所有环境通过统一 Gym-style API 交互，观测转为结构化文本状态，离散文本动作。

**社交游戏对手：** Avalon 和 Diplomacy 使用 GPT-5-mini 作为对手，提供强监督信号。

## 四、奖励设计

**Action-taking 奖励：**
- 在 active skill 上的进展 + 奖励
- 不必要 skill 检索的惩罚

**Skill-retrieval 奖励：**
- Episode 结束时评估
- 基于检索的 skill 是否导致了 contract-satisfying 的结果

**Skill Bank 奖励：**
- 基于 skill utility、contract 泛化能力和 bank 效率

## 五、实验结果

### 单人游戏

COS-PLAY 8B 模型 vs 4 个 frontier LLM baseline：
- **平均 +25.1% reward 提升**
- 在 2048、Candy Crush、Tetris、Super Mario Bros. 上全面领先

### 多人社交推理

- **Avalon:** Good side 需要从稀疏信号推断隐藏角色，COS-PLAY 保持竞争力
- **Diplomacy:** 需要长程上下文推理、谈判、联盟跟踪，COS-PLAY 表现 competitive

### Self-Reinforcing Loop

```
更好的 skill → 更好的决策 → 更好的 rollout → 更好的 skill 学习 → 循环
```

Skill bank 和 decision agent 共同演化：每轮新轨迹反映当前策略，更新后的 bank 塑造后续的 skill 检索和动作执行。

## 六、批判性分析

### 优势
- Co-evolution 框架设计精巧：decision + skill bank 互相促进
- 多 LoRA 分解让不同功能独立优化，避免干扰
- Skill protocol 的 contract 设计让 skill 可组合、可验证
- 在社交推理游戏（Avalon/Diplomacy）上的表现证明框架泛化性好

### 不足
1. **Cold start 依赖 GPT-5.4** — 60 条 seed trajectories 的质量和覆盖范围影响后续演化
2. **Skill 分割的启发式** — 如何确定 trajectory segment 的边界？论文没有给出明确的算法
3. **Skill bank 的规模控制** — 没有讨论 skill bank 增长到多大时需要剪枝或合并
4. **只在游戏环境评估** — 没有在实际 agent 任务（coding、web browsing）上测试

### 对我们的启发
- **CoPD 和 COS-PLAY 的统一视角：** 两者都展示了 co-evolution > 单体训练。CoPD 是 parallel branches 互相蒸馏，COS-PLAY 是 decision + skill bank 互相促进。对于 MoE 模型，可以考虑 expert + router 的 co-evolution
- **Multi-LoRA 设计：** 不同功能用独立 LoRA，可以避免能力干扰。在 OPD 中，可以用 LoRA 分离 distillation 和 RLVR 的更新路径
- **Skill bank as memory：** Skill bank 本质上是结构化的 agent 记忆。与 [[agent-memory-system]]、[[memgpt]] 等工作的关系值得深挖

## Related

- [[imitation-learning]] — 从演示中学习
- [[interactive-imitation-learning]] — 交互式模仿学习
- [[deep-q-network]] — RL 基础
- [[grpo-rl-training]] — GRPO 训练算法
- [[on-policy-distillation]] — 在策略蒸馏概念
- [[agent-memory-system]] — agent 记忆系统
