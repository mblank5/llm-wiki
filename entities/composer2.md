---
title: Composer 2
created: 2026-04-15
updated: 2026-04-15
type: entity
tags: [model, architecture, training, inference, company, open-source]
sources: [raw/papers/cursor-composer2-technical-report-2026.txt]
---

# Composer 2

Cursor Research Team 发布的专用 agentic software engineering 模型（2026-03-24）。

## 基础架构

- **基座模型**: Kimi K2.5（月之暗面），1.04T 参数 / 32B active，MoE 架构
- **训练硬件**: NVIDIA B300，MXFP8 精度
- **推理合作**: Fireworks AI
- **上下文长度**: 256k tokens（先 32k 大量训练，再扩展到 256k）

## 训练流程

两阶段流水线：

### 阶段一：Continued Pretraining
在大量代码主导的数据混合上进行持续预训练，三步走：
1. **32k token 序列长度** — 大量算力在这里
2. **长上下文扩展** — 从 32k 扩展到 256k
3. **目标 SFT** — 针对编码任务的短 SFT 阶段

关键发现：**cross-entropy loss 与下游 RL 表现呈对数线性关系**，即预训练越好 RL 起点越高。

**Multi-Token Prediction (MTP)**: 训练额外的 MTP 层用于 speculative decoding，通过自蒸馏加速推理。MTP 层从训练中间 checkpoint 开始联合训练。

### 阶段二：Reinforcement Learning
大规模异步 RL 训练，核心特点：
- **Policy gradient + 多样本 per prompt**，固定 group size
- **Single-epoch regime**：同一 prompt 不重复训练
- **Full parameter update**（Adam 优化器）
- 参考 Dr. GRPO，去掉 length standardization 和 advantage 标准化
- 不做 overlong masking（实验发现小规模无效）
- 使用标准 KL 估计器 k1=-log r（而非 k3，因为后者在 p/q 差异大时方差爆炸）

#### 异步 RL 架构
- 训练和 rollout 生成完全解耦
- 快速权重同步 + in-flight 权重更新（类似 PipelineRL）
- 推理端 mid-rollout 更新权重，后续 token less off-policy
- **Router Replay**：MoE 模型需要确保训练和推理的 expert routing 一致，推理时记录 expert indices，训练时强制匹配
- 权重通过 delta compression 同步到 S3，推理端独立下载重建

#### Self-Summarization
来自 Composer 1.5 的技术：训练 rollout 可以由多次生成 + 摘要串联而成，最终 reward 用于所有 token。好处：
- 模型学会写好摘要（好的摘要被 upweight，差的被 downweight）
- 有限上下文窗口处理更多信息
- 比 prompt-based compaction 更准，且能复用 KV cache

#### Agent 行为控制
- **辅助 reward**：代码风格、沟通质量、产品特定惩罚（如留未完成的 todo）
- **非线性长度惩罚**：凹函数 `(1+kx)^(1-q)-1 / k(1-q)`，简单任务快速完成，困难任务允许思考更久
- 训练中监控涌现行为，动态添加行为 reward

## 训练任务分布

RL 训练任务分布反映真实 Cursor 使用场景：
- Iterate On Feature（最大占比）
- Debugging, New Feature, Refactor, Understanding Codebase
- Documentation, Testing, Code Review, Optimize, Devops, Migration 等

后期使用 turn 数和 thinking token 数启发式上采样更难的数据点。

## CursorBench

内部评测套件，从真实编码会话中提取。与公开 benchmark 的关键差异：

| 维度 | CursorBench | SWE-bench 等 |
|------|-------------|-------------|
| 中位代码改动 | 181 行 | 7-10 行 |
| 中位描述长度 | 390 chars | 1185-3055 chars |
| 任务来源 | 真实 Cursor 会话 | 历史开源仓库 |
| 污染风险 | 无 | 高（数据泄露） |

每 3 个版本迭代一次，任务复杂度持续增长。还配套了：intent eval、instruction-following eval、eager editing eval、code quality eval、interruption eval。

## Benchmark 结果

| Model | CursorBench | SWE-bench Multi. | Terminal-Bench |
|-------|-------------|-------------------|----------------|
| **Composer 2** | **61.3** | **73.7** | **61.7** |
| Composer 1.5 | 44.2 | 65.9 | 47.9 |
| Composer 1 | 38.0 | 56.9 | 40.0 |
| Opus 4.6 High | 58.2 | 75.8/77.8 | 58.0/65.4 |
| GPT-5.4 | 63.9 | 76.8 | 66.5/75.1 |
| GPT-5.3 Codex | 59.1 | 74.8 | 64.8/77.3 |
| GLM-5 | 42.7 | 66.9/73.3 | 59.6/56.2 |
| Kimi K2.5 | 36.0 | 65.1/73.0 | 47.3/50.8 |

Composer 2 在 CursorBench 上相比 Composer 1.5 提升 37%，相比 Composer 1 提升 61%。推理成本远低于同级别 frontier 模型（Pareto 最优）。

## 基础设施

### 训练并行策略
- **Context Parallelism (CP)** 作为主要长上下文扩展轴（比 TP 更高效）
- EP 与 TP 解耦，EP 从 DP+CP 容量组成
- 继续预训练: EP=8, CP=2; RL: EP=8, CP=8
- DeepEP 实现高吞吐 token dispatch/combine
- 全局 sequence packing 平衡 DP 负载

### Kernel & 精度
- MoE forward: **NVFP4 变体**（per-token scaling），避免 per-tensor scaling 的 batch variance 和信息泄露
- MoE backward: **MXFP8**（更高精度，训练稳定性）
- IEEE-compliant 浮点对 NVFP4 至关重要（fast-approximation 导致 RL 发散）
- 开源了 Flash Attention 4 backward kernel 和 ThunderKittens GEMM

### RL 基础设施
- 四个解耦服务：training, environments, inference, evaluations
- Ray + PyTorch 异步训练栈
- **Anyrun**: 内部计算平台，Firecracker VM 运行完整开发环境
- 支持环境 fork、snapshot、live-migration
- 跨 3 region GPU + 4 region CPU
- 策略感知 checkpointing（rollout/group/step 三级）
- 推理端与 Fireworks AI 合作

## 核心洞察

1. **RL 不只是 reweight 已知路径**: Composer 2 的 RL 同时提升 average 和 best-of-K 性能，说明模型确实在扩大可达正确解的覆盖范围
2. **Continued pretraining 对 RL 有预测性**: 预训练 loss 对数线性预测 RL 性能
3. **Domain match 是关键**: 训练环境、工具、任务分布尽可能贴近真实部署场景
4. **专用模型可以性价比超越通用模型**: 1.04T/32B active 在编码领域达到 frontier 级别

## 关联

- 基座模型: [[kimi-k2]] (Kimi K2.5)
- RL 方法: [[ppo]], [[grpo-rl-training]]
- 评测框架: [[cursorbench]]
- 代码 Agent 概念: [[agentic-coding]]
