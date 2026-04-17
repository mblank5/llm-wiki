---
title: "PerlAD: Pseudo-simulation-based RL for E2E Autonomous Driving"
created: 2026-04-17
updated: 2026-04-17
type: concept
tags: [rl, autonomous-driving, end-to-end, world-model, planning, reinforcement-learning, robotics]
sources: [raw/papers/2026/03/2603.14908.md]
---

# PerlAD: Pseudo-simulation-based RL for Closed-loop E2E Autonomous Driving

## 一句话概述

PerlAD 提出了一种基于离线数据集的 **伪仿真 (Pseudo-simulation)** 环境，在向量空间中实现高效、无需渲染的 RL 训练，用于闭环端到端自动驾驶，在 Bench2Drive 上达到 SoTA (DS=78.70)。

## 核心问题

端到端自动驾驶中，IL (模仿学习) 在闭环执行时表现不佳：
1. **训练目标错配**：IL 仅最小化几何偏差，与真实驾驶目标（安全、效率）不对齐
2. **因果混淆**：IL 容易学到伪相关而非真实因果关系
3. **现有 RL 方案瓶颈**：
   - 渲染仿真（游戏引擎/3DGS）：存在渲染域鸿沟 + 计算成本高
   - 开环 RL 微调：无法捕捉动态交互

## 三大核心创新

### 1. Pseudo-Simulation 环境（向量空间仿真）

- **完全基于离线数据集**构建，无需渲染器
- 在向量空间操作，GPU 并行运行
- 组成模块：
  - **Ego Simulation**：自行车运动学模型 + 双 PID 控制器 → 自车未来轨迹
  - **Agent Simulation**：Top-1 预测轨迹 → 高频插值
  - **Static Map**：车道线多段线表示，假设不变
- **优势**：消除了渲染域鸿沟，训练效率大幅提升

### 2. Prediction World Model (PWM，预测世界模型)

- **核心思想**：显式将自车未来轨迹作为条件输入，预测周围 agent 的反应式轨迹
- **架构**：GRU 自回归生成 + 多模态嵌入
  - 每个时间步注入 ego displacement embedding（自车位移编码）
  - 回归头 + 分类头输出多模态轨迹及概率
- **训练时**用 GT ego trajectory，**RL 时**用 DeP 输出经过 ego simulation 的轨迹
- **效果**：
  - 反事实碰撞：PWM 70/200 vs vanilla 147/200 vs logged replay 166/200
  - ADE/FDE 均有提升
- **与现有世界模型的区别**：现有方法仅用 prediction 做特征提取（modular 系统），PerlAD 用 PWM 提供 **闭环一致的 reward 信号**

### 3. Hierarchical Decoupled Planner (DeP，层级解耦规划器)

- **Lateral（横向）**：IL 训练，多模态路径规划（path anchors → 回归+分类）
- **Longitudinal（纵向）**：RL 训练，离散目标速度分类
- **关键设计**：纵向规划以横向路径为条件 → 层级依赖
- **对齐策略**：
  - 训练初期：纵向分支用 GT path 作为输入
  - 训练后 1/3：切换为 predicted path
  - 横向分类 loss 增加 clipped reward 加权 → 兼顾几何准确和安全效率

## RL 训练细节

- **算法**：REINFORCE + group-standardized advantage estimation（类似 [[grp-o]]）
- **纵向 RL**：采样 N 个目标速度 → 伪仿真计算 reward → 策略梯度更新 + 熵正则
- **Reward 函数四项**：
  | 组件 | 值 | 作用 |
  |------|-----|------|
  | r_col | -30(车) / -50(人) / -10(锥) | 碰撞惩罚 |
  | r_lk | -30(双实线) / -10(单实线) | 车道保持 |
  | r_prog | [0,1] 归一化 | 路径完成进度 |
  | r_dist | -L2 距离 | 隐式建模驾驶正确性 |
- **Reactive Training Simulation**：训练初期用 GT agent 轨迹 → 后 1/3 渐进替换为 PWM 预测

## 两阶段训练

| 阶段 | 训练内容 | 损失 |
|------|---------|------|
| Stage 1 | 稀疏感知 | 检测 + 建图 loss |
| Stage 2 | Transformer + DeP + PWM（感知冻结） | 预测 + 规划 loss（横向 IL + 纵向 RL）|

8× H20 GPU, batch 256, stage1: 12 epochs, stage2: 18 epochs

## 实验结果

### Bench2Drive（核心 benchmark）

| 方法 | DS | SR | Mean Multi-ability |
|------|-----|-----|-------------------|
| **PerlAD** | **78.70** | **57.27%** | **57.20%** |
| Raw2Drive (NeurIPS'25) | 71.36 | 50.24% | 53.34% |
| Hydra-Next (ICCV'25) | 73.86 | 50.00% | 53.22% |
| DiffAD | 67.92 | 38.64% | 38.79% |
| SparseDrive (ICRA'25) | 44.54 | 16.71% | 17.45% |

- vs SparseDrive (IL baseline): **DS +76.7%**, SR +40.56%
- vs Raw2Drive (previous RL SoTA): **DS +10.29%**，无需在线探索

### DOS（安全关键遮挡场景）

| 方法 | Average DS |
|------|-----------|
| **PerlAD** | **86.83** |
| ReasonPlan | 78.02 |
| UniAD | 71.09 |

### 消融实验关键发现

| 配置 | DS | CR |
|------|-----|-----|
| IL-lon only | 32.81 | 0.74 |
| +RL-lon | 65.01 | 0.39 |
| +LLA | 70.28 | 0.20 |
| +RTS (full) | 74.00 | 0.09 |

**IL 纵向规划极差** (DS=32.81)，说明 RL 对交互速度控制不可或缺。

## 与 Wiki 其他页面的关联

### RL 后训练方法论
- **REINFORCE + group-standardized advantage** 与 [[grp-o]] 的组内相对奖励策略高度相似，说明 GRPO 类方法已渗透到自动驾驶 RL 领域
- [[opd-autonomous-driving]] 已收录自动驾驶中的 OPD 方法（GPT-Driver + GKD），PerlAD 提供了另一种 RL 路径
- [[llm-post-training-unified-view]] 的 off-policy/on-policy 双主线框架可类比到自动驾驶：IL=SFT（off-policy），RL=on-policy 优化

### World Model 范式
- PWM 是一个 **条件世界模型**：以 ego action 为条件预测环境反应
- 区别于 LLM 中的世界模型（如 OmniJigsaw 自监督），PWM 是显式面向 RL 训练的 world model
- 与 [[cascade-rl]] 的多域后训练类似，PerlAD 也是分阶段渐进式训练

### 解耦规划的思想
- 横向 IL + 纵向 RL 的解耦思路，类似于 LLM 后训练中 **先 SFT 打底再 RL 微调** 的范式
- Lateral-Longitudinal Alignment 对应 LLM RL 中的 **奖励塑形/课程学习**

## 局限性与未来方向

1. **低速域局限**：解耦规划仅在低速城市驾驶验证，高速场景需要耦合规划
2. **离线数据覆盖不足**：reactive scenario ~2/3 时性能饱和，需要 latent world model 外推
3. **规则 reward 的局限**：r_dist 虽隐式建模了部分行为（如停车标志），但不够全面 → 未来考虑 [[reinforcement-learning-from-human-feedback|RLHF]] 式的人类偏好 reward
4. **PWM 不建模极端对抗行为**

## 技术规格

| 参数 | 值 |
|------|-----|
| Backbone | ResNet-50 |
| Agent queries | N_a = 50 |
| Map queries | N_m = 100 |
| Path modalities | K_path = 6 |
| Waypoints | W = 6 (every 2m) |
| Max speed | 12 m/s, N_v = 13 discrete levels |
| Prediction | 2Hz, 3s horizon |
| Simulation | 10Hz, 2s horizon |
| RL samples | N = 4 speed actions |
| Discount γ | 自定义 |
| GPUs | 8× NVIDIA H20 |

## Related

- [[grp-o]] — GRPO 的组标准化 advantage 策略被 PerlAD 采用
- [[opd-autonomous-driving]] — 自动驾驶中的 OPD 方法
- [[on-policy-distillation]] — On-Policy 核心概念
- [[imitation-learning]] — IL vs RL 的根本差异
- [[cascade-rl]] — 渐进式多阶段 RL
- [[llm-post-training-unified-view]] — off-policy/on-policy 统一视角
