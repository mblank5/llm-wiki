---
title: "Horizon Length Training Study — arXiv 2605.02572"
created: 2026-05-09
updated: 2026-05-09
type: concept
tags: [rl, training, benchmark]
sources: [raw/papers/2026/05/2605.02572.md]
---

# Horizon Length 实证研究 (arXiv 2605.02572)

> **On Training Large Language Models for Long-Horizon Tasks: An Empirical Study of Horizon Length**
> Kim, Cho, Kwak, Kwon, Wang, Yang, Zhang, Wei, Yeo — 2026-05-04

---

## 核心问题定义

本文系统性研究了一个在现有 RL 训练中常被忽视的因素——**horizon length（视野长度 / 任务执行步数）**如何影响 LLM Agent 训练的稳定性和最终性能。

论文将 horizon 分解为三个维度：

| 概念 | 符号 | 定义 |
|---|---|---|
| Goal Distance | $d(s_0, g)$ | 最优策略 $\pi^*$ 下到达目标所需的最少原子 action 数 |
| Interaction Budget | $H_{\max}$ | 环境允许的最大交互步数 |
| Effective Horizon | $h_\pi(s_0, g)$ | 策略 $\pi$ 实际执行到目标的步数 |

对任意成功轨迹，满足：$d(s_0, g) \leq h_\pi(s_0, g) \leq H_{\max}$

**核心研究问题**：在保持推理复杂度不变的前提下，仅增加 goal distance（即需要执行的 action 序列长度）是否会独立导致训练不稳定？

关键发现是：**Horizon Length 是 RL 训练中一个独立的瓶颈因素**——即使底层推理难度完全相同，仅增加所需交互步数就会引起严重的训练不稳定和性能崩溃（collapse）。

---

## 实验设计：受控任务构建

为了隔离 horizon 效应与推理复杂度，论文构建了**受控任务集**：相同推理结构、不同 action sequence length。

### 方法学：解耦 horizon 与 solving complexity

1. **Short-horizon proxy task**：将长 horizon 任务转化为单步 formulation（例如要求模型一次性生成完整数独解），验证模型具备底层推理能力
2. **仅保留 proxy task 中成功的实例**，按 goal distance 分区 → 确保各数据集的推理复杂度一致

### 任务环境

| 环境 | Action 格式 | Horizon 代理 | 复杂度控制 |
|---|---|---|---|
| **Sudoku**（主测试床） | `value(n, rXcY)` 填入格子 | 空格数量 | 使用 HoDoKu 仅筛选 basic technique 可解的谜题 |
| **Rush Hour**（验证） | `move(id, direction)` 滑动方块 | 最优解最少移动次数 `min_moves` | 随机生成 + Fogleman solver 验证 |

### 数据集分区（Table 1）

#### Sudoku

| 等级 | L1 | L2 | L3 | L4 | L5 | L6 | L7 |
|---|---|---|---|---|---|---|---|
| $d(s_0, g)$ | 11–15 | 16–20 | 21–25 | 26–30 | 31–35 | 36–40 | 41–45 |
| $N_{\text{train}}$ | 640 | 640 | - | - | - | - | - |
| $N_{\text{test}}$ | 100 | 100 | 100 | 100 | 100 | 100 | 50 |

> 🔵 L1–L4 为训练集范围（其中 L3–L4 仅测试集），🔴 L5–L7 为训练未见过的长 horizon 测试集，用于评估 horizon generalization。

#### Rush Hour (Table 2)

| $d(s_0, g)$ | 4–6 | 7–9 | 10–12 | 13–15 | 16–18 | 19–21 |
|---|---|---|---|---|---|---|
| $N_{\text{test}}$ | 100 | 100 | 100 | 100 | 100 | 100 |

---

## 关键发现

### 1. Horizon 增加导致训练不稳定

在 Sudoku 上以 Qwen3-1.7B 进行 SFT → RL 训练：

- **L1–L2（短 horizon）**：RL 训练稳定、性能持续提升
- **L3–L4（长 horizon）**：出现严重不稳定 → **catastrophic collapse**

训练崩溃伴随最大长度 response 比例急剧上升，表明策略转向 incoherent 或过长 generation。

### 2. 训练不稳定的机制分析

论文归因于两个 RL 中固有的根本挑战：

**(a) Exploration Difficulty（探索困难）**

Mapping complexity 非线性增长：horizon 增加 → state-action 空间爆炸 → 早期决策对未来结果施加不成比例的约束 → 遵循最优轨迹的概率指数衰减

**(b) Credit Assignment 问题（信用分配）**

在 sparse reward 下，轨迹失败时整条轨迹获得 negative advantage，包括中间正确的步骤。

**Token-level gradient asymmetry**（详见 [[grpo-rl-training]]）：

对于采样 token $y_i$ 与 advantage $A_i$，对任意 logit $z_v$ 的梯度为：

$$\nabla_{z_v}\mathcal{J}(\theta) = \begin{cases} (1-\pi_\theta(y_i|x, y_{<i}))\cdot A_i, & v = y_i \\ -\pi_\theta(v|x, y_{<i})\cdot A_i, & v \neq y_i \end{cases}$$

- **Positive advantage**：聚焦信号——增大采样 token logit，减小其他 token logit
- **Negative advantage**：扩散信号——减小采样 token logit，但**均匀增大所有其他 token（约 $10^5$ 个）的 logit**，引入大量噪声

在长 horizon 下，错误累积导致大量 negative advantage 更新，噪声梯度最终摧毁策略。

### 3. Horizon 是首要瓶颈（而非模型容量或优化器）

- 4B 模型下 atomic action 训练仍会 collapse
- GRPO-style optimizer 下同样出现不稳定
- WebShop 真实 web 交互环境中同样验证

---

## Horizon Reduction 方法

论文提出 **"Horizon Reduction"** 作为训练 LLM Agent 的核心设计原则。

> *"The best way to escape from a problem is to solve it."* — 与其让 agent 学习 intractable 的长 horizon 依赖，不如从结构上最小化完成任务所需的交互长度。

### 策略一：Macro Actions（宏动作）

将多个原子 action 组合为高层 primitive，在单个 step 中输出多个 action。

- **Sudoku**：允许 agent 单步生成多个填格动作
- **Rush Hour**：允许 `move(id, direction, N)` 多格移动

**三种 macro action 设计对比**：

| 设计 | 描述 | 性能 |
|---|---|---|
| Atomic | 单步一个原子 action | 最差，长 horizon 下崩溃 |
| Fixed-length ($n=k$) | 每步固定 $k$ 个原子 action | 次差，因 rigid 和 overshooting |
| **Flexible macro** ($n \leq k$ 或无界) | 策略动态决定 action 数量 | **最佳**，需要 policy-controlled granularity |

> 关键结论：flexible macro action 在所有测试模型（Qwen3、GPT-5-mini、Gemini-3-Flash）上表现最优。固定的 action 长度限制会损害性能。

### 策略二：Subgoal Decomposition（子目标分解）

将全局目标 $g$ 分解为子目标序列 $(g_1, g_2, \dots, g_k)$：

$$d(s_0, g) = \sum_{i=1}^{k} d(s_0^{(i-1)}, g_i)$$

- 在 Sudoku 上，每个 subgrid（3×3 宫格）完成时获得 intermediate reward
- 将 trajectory 分段，每段独立计算 return $G_t$
- 有效将长 horizon 目标转化为短 horizon 子任务序列
- 在 L3–L4 上，sparse-reward baseline 无法学习，subgoal-guided policy 稳定学习并取得强性能

### Horizon Reduction 为何有效（控制实验）

论文设计了关键控制实验来区分 "更好的 base policy" vs "真正的 horizon reduction"：

- **Setting A**（Horizon-reduced）：Macro-action policy + 允许执行多步 → 有效 horizon 短
- **Setting B**（Artificially restored long horizon）：同样的 Macro-action policy + **限制每步只执行一个原子 action** → 恢复长 horizon

结果：Setting B 初期改善但最终 collapse；Setting A 持续收敛到高 performance。证明 **effective horizon $h_\pi(s_0, g)$ 是训练稳定性的主要决定因素**。

---

## 完整实验结果

### Table 7：Sudoku 跨 horizon 评估

| action | train horizon | metric | L1 (11–15) | L2 (16–20) | L3 (21–25) | L4 (26–30) | L5 (31–35) | L6 (36–40) | L7 (41–45) |
|---|---|---|---|---|---|---|---|---|---|
| **macro** Base | - | pass@4 | 98.0 | 90.0 | 67.0 | 28.0 | 8.0 | 0.0 | 0.0 |
| | | avg@4 | 66.5 | 44.0 | 23.75 | 6.25 | 0.5 | 0.25 | 0.0 |
| macro SFT | 11–20 | pass@4 | 98.0 | 90.0 | 67.0 | 28.0 | 8.0 | 0.0 | 0.0 |
| | | avg@4 | 69.5 | 48.75 | 26.25 | 8.75 | 2.0 | 0.0 | 0.0 |
| macro **RL** | 11–20 | pass@4 | **100** | **100** | **97.0** | **84.0** | **61.0** | **31.0** | **10.0** |
| | | avg@4 | **95.75** | **86.5** | **68.75** | **41.75** | **26.25** | **8.25** | **2.5** |
| macro **RL** | 21–30 | pass@4 | 99.0 | **100** | **98.0** | **91.0** | **85.0** | **61.0** | **38.0** |
| | | avg@4 | **97.0** | **95.5** | **87.25** | **69.5** | **54.0** | **30.75** | **14.0** |
| atomic SFT | 11–20 | pass@4 | 90.0 | 64.0 | 26.0 | 7.0 | 2.0 | 0.0 | 0.0 |
| | | avg@4 | 58.5 | 27.75 | 7.75 | 2.0 | 0.5 | 0.0 | 0.0 |
| atomic RL | 11–20 | pass@4 | **100** | 91.0 | 75.0 | 39.0 | 14.0 | 2.0 | 0.0 |
| | | avg@4 | **86.5** | **65.25** | **43.25** | 13.75 | 4.0 | 0.5 | 0.0 |
| atomic RL | 21–30 (before collapse) | pass@4 | 98.0 | 79.0 | 58.0 | 27.0 | 11.0 | 0.0 | 0.0 |
| | | avg@4 | 81.5 | 54.0 | 29.75 | 8.75 | 3.25 | 0.0 | 0.0 |
| atomic RL (subgoal) | 21–30 | pass@4 | **100** | **99.0** | **93.0** | **69.0** | **31.0** | **12.0** | 0.0 |
| | | avg@4 | 84.5 | **73.5** | **51.0** | **28.75** | **11.5** | **3.0** | 0.0 |

> **核心观察**：Macro-action RL 在所有测试 horizon 上均优于 atomic-action RL；在长 horizon (L5–L7) 上差距急剧放大，证明 horizon generalization 效应。Subgoal decomposition 在 L3–L4 训练上也显著优于 atomic baseline。

### Table 8：Rush Hour 跨 horizon 评估

| action | train horizon | metric | 4–6 | 7–9 | 10–12 | 13–15 | 16–18 | 19–21 |
|---|---|---|---|---|---|---|---|---|
| macro Base | - | pass@4 | 38.37 | 5.68 | 0.0 | 0.0 | 0.0 | 0.0 |
| | | avg@4 | 11.82 | 1.52 | 0.0 | 0.0 | 0.0 | 0.0 |
| macro SFT | 4–12 | pass@4 | 94.19 | 71.59 | 19.78 | 3.0 | 0.0 | 0.0 |
| | | avg@4 | 60.51 | 34.28 | 7.01 | 1.0 | 0.0 | 0.0 |
| macro RL | 4–9 | pass@4 | **100** | 87.5 | 58.24 | 12.0 | 3.0 | 0.0 |
| | | avg@4 | **94.53** | **67.90** | **30.36** | 4.25 | 0.75 | 0.0 |
| macro RL | 10–12 | pass@4 | **100** | **92.05** | **64.84** | 18.0 | 3.0 | 1.0 |
| | | avg@4 | **93.65** | **76.56** | **32.14** | 5.50 | 0.75 | 0.25 |
| macro RL **(curriculum)** | 10–12 | pass@4 | **100** | **97.73** | **84.62** | **43.0** | **15.0** | **8.0** |
| | | avg@4 | **99.42** | **85.65** | **56.18** | **20.25** | **5.0** | **2.25** |

> Curriculum 训练（先在 4–9 上训练，再迁移到 10–12）在所有长 horizon 上显著优于直接训练。

### Table 6：IS 函数与 Advantage 设计的 Ablation

| IS 函数 $w$ | Advantage | avg@4 | pass@4 |
|---|---|---|---|
| **Ours**：Seq-TIS + Geo-MIS | $\hat{r}^{\text{traj}} + \alpha\hat{r}^{\text{step}}$ ($\alpha=0.2$, Batch Norm) | **96.0** | **97.6** |
| Seq-TIS only | default | 91.4 | 97.6 |
| Geo-MIS only | default | 89.4 | 96.0 |
| default | Group Norm for $r^{\text{traj}}$ | 83.4 | 95.2 |
| default | 无归一化 ($A = r^{\text{traj}} + \alpha r^{\text{step}}$) | 44.4 | 77.6 |
| default | $\alpha = 0.0$ | 91.4 | 96.0 |
| default | $\alpha = 0.5$ | 93.0 | 97.6 |
| default | $\alpha = 1.0$ | 95.8 | 97.6 |

> 关键结论：Seq-TIS + Geo-MIS 组合 > 单独使用；Batch Normalization > Group Normalization；$\alpha = 0.2$ 提供 trajectory-level 和 step-level 监督的最佳平衡；无归一化导致严重性能退化。

### Horizon Generalization（Figure 8）

- 在中等 goal distance 上训练的模型不仅在短 horizon 上表现好，在**未见过的更长 horizon**（L5–L7）上也取得显著提升
- Macro-action policy 的 horizon generalization 优于 atomic-action
- 原因：(1) 更高的 per-step accuracy；(2) 减少决策点数量，降低错误累积机会
- 但 **horizon generalization ≠ technique generalization**：RL 只能在已见过的推理模式内扩展 horizon，无法学习全新的 reasoning primitive

### Horizon Curriculum（Figure 9）

在 Rush Hour 上：
- **Short-only**（$4 \leq d \leq 9$）：短 horizon 训练，对长 horizon 有部分泛化
- **Long-only**（$10 \leq d \leq 12$）：直接训练几乎无改善，初始性能不足以维持优化
- **Curriculum**（先 4–9 → 再 10–12）：显著提升，确认**短 horizon 能力是学习长 horizon 的前提**

---

## 训练配置

| 参数 | Sudoku | Rush Hour |
|---|---|---|
| 基础模型 | Qwen3-1.7B | Qwen3-1.7B |
| SFT learning rate | 5e-6 | 5e-6 |
| SFT epochs | 4 | 4 |
| RL learning rate | 1e-6 | 1e-6 |
| LR scheduler | constant | constant |
| KL loss/penalty | 0.0 | 0.0 |
| Max response length | 2048 / 4096 (macro) | 2048 |
| Temperature | 0.8 | 0.8 |
| top_p | 1.0 | 1.0 |
| 折扣因子 $\gamma$ | 0.995 | 0.995 |
| $\alpha$ (step reward weight) | 0.2 | 0.2 |
| $H_{\max}$ | 50 | 30 / 20 (macro) |
| Memory window $K$ | 2 turns | 2 turns |
| Rollout IS | sequence (TIS + Geo-MIS) | sequence |
| IS threshold | 3 | 3 |
| Geo-MIS threshold | [0.995, 1.01] | [0.995, 1.01] |
| 评估 | pass@4, avg@4 (temp=0.8) | pass@4, avg@4 (temp=0.8) |
| 硬件 | 4×A100 + 4×A6000 | 4×A100 + 4×A6000 |
| 训练时长 | 1–3 天 | 1–3 天 |

### SFT 专家数据来源
- **Sudoku**：Qwen3-32B 采样 + GPT-5-mini 蒸馏 CoT
- **Rush Hour**：GPT-5-mini 直接采样

### 代码框架
- 基于 **rllm v0.2**（背后使用 **verl v0.5.0**）
- 关键修改：解决 retokenization 问题（保持 Tokens-In/Tokens-Out 流程）、training-inference mismatch 处理

### 关键工程经验
1. **Retokenization 问题**：标准 API 返回文本 → 重新 tokenization 引入 token-level 偏移 → 在 RL 中充当 adversarial noise 导致优化不稳定
2. **SFT 防止 reward hacking**：从零 RL 训练会收敛到 degenerate strategy；需要 SFT 提供 valid behavioral prior
3. **保守 SFT**：使用低学习率 (5e-6) 保留 exploration capacity

### 输出格式
```
<|im_start|>...<|im_end|> REASON:{reason}, ACTION:{action}
```
`<thought>` block 包含 CoT 推理但不存入 memory；`reason` 是推理摘要。Memory $m_t$ 仅存储最近 $K$ 步的 observations、reasoning summary 和 actions。

---

## 对我们 RL 训练的启发

### 1. 优先管理 Effective Horizon

在启动复杂任务 RL 训练前，应首先评估并尝试**缩短 effective horizon**：
- **Macro actions**：设计高层 action 抽象（例如代码生成中用循环替代重复调用，GUI agent 中用高层 API 替代低层点击）
- **Flexible > Fixed**：宏动作长度应由策略动态决定，而非硬性固定

### 2. SFT 初始化不可或缺

- 避免从零 RL 训练——reward hacking 风险极高
- 使用保守学习率 SFT（如 5e-6）以保留 exploration capacity
- 参考 [[on-policy-distillation]] 中的蒸馏策略获取高质量 expert trajectories

### 3. Advantage 设计

- 混合 trajectory-level 和 step-level reward（$\alpha \approx 0.2$）
- **Batch Normalization** 优于 Group Normalization
- 在长 horizon 任务中考虑 **subgoal decomposition + dense reward** 替代 sparse reward
- 参考 [[cascade-rl]] 中 cascade reward 设计思路

### 4. Curriculum 训练策略

- **短 → 长 horizon curriculum**：先在易成功的短 horizon 任务上训练，再迁移到长 horizon
- 利用 horizon generalization 效应：短 horizon 上学到的能力可泛化到更长 horizon
- 这对 [[rl-conductor]] 的多阶段训练流程有直接参考价值

### 5. Importance Sampling

- **组合使用** Seq-TIS + Geo-MIS，二者互补
- Geo-MIS 过滤不可靠轨迹，Seq-TIS 控制梯度方差
- 参考 [[relax-async-rl-omni]] 中对 off-policy correction 的处理

### 6. 对 GRPO/PPO 的建议

- 论文证实 horizon 瓶颈是 **optimizer-agnostic**（GRPO-style 和 REINFORCE 均出现）
- 但在 long-horizon GRPO 训练中，**必须配合 horizon reduction 使用**
- 考虑使用 Process Reward Model（PRM）提供 intermediate dense reward，对应 subgoal decomposition 思路

---

## 批判性分析

### 优势

1. **实验设计严谨**：通过 short-horizon proxy task 和 HoDoKu 验证，真正解耦了 horizon 与推理复杂度
2. **控制实验有力**：Setting A vs B 实验清晰证明 effective horizon 而非 base policy quality 是关键因素
3. **跨维度验证**：在环境（Sudoku → Rush Hour → WebShop）、模型规模（1.7B → 4B）、优化器（REINFORCE → GRPO）三个维度上验证了结论的鲁棒性
4. **实践导向**：提出的 Horizon Reduction 方法简单有效，可直接应用到实际 Agent 系统中
5. **工程细节丰富**：retokenization、training-inference mismatch 等实际问题为社区提供了宝贵经验

### 不足与疑问

1. **模型规模有限**：最大仅测试 4B 模型，未验证 frontier-scale 模型（70B+）是否仍受相同瓶颈约束
2. **任务领域局限**：主要基于 text-based game，真实场景（含视觉感知、随机环境动力学、嘈杂观测）可能引入额外 confounding factor
3. **仅验证 single model family**：全部实验基于 Qwen 系列，不同 architecture/training corpus 的模型可能有不同学习动态
4. **Horizon Generalization 的边界**：论文发现 horizon generalization 不伴随 technique generalization——RL 只能在已有推理模式内扩展 horizon，无法学习新的 reasoning primitive。这限制了该方法在需要**新推理能力**的长 horizon 任务上的应用
5. **Macro Action 设计依赖 domain knowledge**：如何自动发现/设计合适的 macro action space 仍是开放问题
6. **Subgoal 的自动生成**：论文在 Sudoku 上利用 subgrid 作为天然 subgoal，但通用任务中如何自动识别和分解 subgoal 未解决

### 开放问题

- Horizon reduction 与 test-time compute scaling（如 [[reopold]]）的关系是什么？
- 在异步多 Agent 场景（如 [[relax-async-rl-omni]]）中，horizon 效应如何与 inter-agent coordination 交互？
- 是否可以设计自适应 horizon reduction 机制，让策略自行学习何时使用 macro vs atomic action？

---

## Related

- [[grpo-rl-training]] — GRPO 算法详解，包含 token-level gradient dynamics 分析，与本文 negative advantage 扩散效应直接相关
- [[on-policy-distillation]] — 如何从强模型蒸馏 expert trajectories 用于 SFT 初始化，对应本文 SFT expert 数据收集流程
- [[cascade-rl]] — 级联奖励与多阶段 RL 训练，与本文 subgoal decomposition + curriculum 策略互补
- [[rl-conductor]] — 多阶段 RL 编排，horizon-aware 训练流程可作为其核心组件
- [[reopold]] — Test-time compute scaling 与 RL 训练的结合，horizon reduction 可视为一种 compute-aware 的 action space 设计
