---
title: "Co-Evolving Policy Distillation (CoPD)"
created: 2026-05-02
updated: 2026-05-02
type: concept
tags: [distillation, on-policy, rl, rlhf, grpo]
sources: [raw/papers/2026/04/2604.27083.pdf]
---

# Co-Evolving Policy Distillation (CoPD)

**arXiv:** [2604.27083](https://arxiv.org/abs/2604.27083)
**Authors:** Naibin Gu, Chenxu Yang, Qingyi Si, Chuanyu Qin, Dingyu Yao, Peng Fu, Zheng Lin, Weiping Wang, Nan Duan, Jiaqi Wang (中科院信工所 + 京东)
**Date:** April 2026
**Series:** Self-Taught RLVR 系列第三篇（前作：RLSD / NPO）

## 一、核心问题定义

把多个专家能力合并到一个模型，现有两种范式都有严重损失：

### 范式 A: Mixed RLVR（混合数据训练）
- 所有数据混入一个池子做 GRPO
- **Capability divergence**: 不同能力的优化方向冲突，一个涨了另一个掉
- 实验：Mixed RLVR 的 text reasoning (55.48) 远低于 Text-Expert (57.89)

### 范式 B: Static OPD（先训专家再蒸馏）
- 各自 RLVR 训到收敛 → 单向 OPD 蒸馏
- **Behavioral pattern gap**: 专家训完后与学生行为差距太大，蒸馏信号吸不进去

## 二、理论分析：Behavioral Consistency Hypothesis

### 核心公式

OPD 效率 η 与 teacher-student top-k overlap (Oₖ) 正相关：

$$\eta \propto O_k(\pi_T, \pi_\theta)$$

其中 $O_k$ 定义为：

$$O_k(\pi_T, \pi_\theta) = \mathbb{E}_{x, y \sim \pi_\theta}\left[ \frac{|\text{top-}k(\pi_T(\cdot|x, y_{<t})) \cap \text{top-}k(\pi_\theta(\cdot|x, y_{<t}))|}{k} \right]$$

### Pilot Study 两个关键实验

**实验 1: η 随 Oₖ 单调上升**
- 固定 teacher，用不同 temperature 构造不同 overlap 的 student
- 结果：post-OPD gain 与 Oₖ 线性相关 **r = 0.89, R² = 0.79**
- 边界条件：Oₖ → 1 时 DKL(πT∥πθ) → 0，OPD 增益归零

**实验 2: 标准 RLVR 把 overlap 推入低 η 区间**
- 独立 RLVR 训练专家，跟踪与 base 的 overlap
- top-k overlap 单调下降，symmetric KL 上升一个数量级
- 结论：静态 pipeline 在专家训完时恰好处于 η 最低区间

### 三个耦合要求

有效范式必须同时满足：
1. 蒸馏在专家训练**期间**发生（防止 Oₖ 漂移到低 η 区）
2. Teacher 随 student**一起演化**（主动维持 overlap）
3. 能力特定训练继续把两边拉开（保持监督信号信息量）

## 三、CoPD 完整算法

### Phase I: Branch-Specific RLVR

每个分支 k 独立在自己的数据 Dₖ 上做 GRPO：

$$\mathcal{L}_{\text{RLVR}}^{(k)}(\theta_k) = \mathbb{E}_{x \sim D_k} \left[ \frac{1}{G} \sum_{i=1}^G \frac{1}{|y_i|} \sum_{t=1}^{|y_i|} \min\left(\rho_{i,t}^{(k)} \hat{A}_i^{\text{RL}}, \text{clip}(\rho_{i,t}^{(k)}, 1-\epsilon, 1+\epsilon) \hat{A}_i^{\text{RL}}\right) \right]$$

其中 ρ 是 importance sampling ratio，A 是 group-level advantage（GRPO 标准公式）。

### Phase II: Mutual OPD

分支 k 在**对方**的数据 Dⱼ 上采样 x'，生成 rollout $y^{(k)} \sim \pi_{\theta_k}(\cdot|x')$。

分支 j 作为 teacher 给出 token 级监督信号：

$$\delta_{i,t}^{(k \leftarrow j)} = \log \pi_{\theta_j}(y_{i,t}^{(k)} | x', y_{i,<t}^{(k)}) - \log \pi_{\theta_k}(y_{i,t}^{(k)} | x', y_{i,<t}^{(k)})$$

token-level advantage：

$$\hat{A}_{i,t}^{(k)} = \beta_k \cdot \delta_{i,t}^{(k \leftarrow j)}$$

βₖ 平衡跨分支蒸馏贡献。**两个分支互为师生，双向蒸馏。**

### Algorithm 1: 完整伪代码

```
Require: Base model π_θ₀, K datasets {Dₖ}, rewards {rₖ}, cycles N, steps S_RLVR, S_OPD
Initialize: θₖ ← θ₀ for all k

for n = 1 to N:
    # Phase I: Branch-specific RLVR (all branches parallel)
    for k = 0 to K-1 (并行):
        θₖ ← RLVR(θₖ; Dₖ, rₖ, S_RLVR)    # Eq.7 GRPO

    # Phase II: Mutual OPD (all branches parallel)
    for k = 0 to K-1 (并行):
        for s = 1 to S_OPD:
            # Native: generate rollouts on Dₖ, GRPO with rₖ
            # Cross-branch: for each j≠k:
            #   generate rollouts on Dⱼ from π_θₖ
            #   compute teacher signal δ^(k←j) from π_θⱼ  (Eq.8)
            #   Â^(k) = βₖ · δ^(k←j)
            # Combine native + cross-branch batches, update θₖ

# Merge co-evolved branches
θ* ← Merge(θ₀, θ₁, ..., θₖ₋₁)
return θ*
```

**K > 2 扩展：** hub-and-spoke 拓扑。text reasoning 分支作为 hub，image/video 作为 spoke。

### 交替训练节奏

S_RLVR : S_OPD 比例消融：
- **最优比 1.5 : 1** — RLVR 探索足够多（产生互补知识），但不能太多（否则对齐变弱）
- 训练动力学：RLVR phase 使 overlap 下降，OPD phase 恢复，**全程 > 0.90**
- Static OPD baseline: overlap 单调下降，KL 上升一个数量级

## 四、完整实验结果

### 2-branch (text + image), Qwen3-VL-4B-Instruct

| Benchmark | Base | Img-Exp | Txt-Exp | Mixed RLVR | OPD(V→T) | OPD(T→V) | **CoPD** |
|-----------|------|---------|---------|------------|----------|----------|----------|
| MMMU | 65.06 | 65.28 | 65.72 | 66.39 | 65.94 | 67.50 | **66.94** |
| MMMU-Pro | 53.03 | 53.89 | 53.05 | 54.28 | 54.09 | 54.71 | **55.10** |
| MathVista | 73.20 | 75.10 | 73.90 | 75.10 | 74.20 | 76.05 | **75.75** |
| MathVision | 55.07 | 55.69 | 55.82 | 56.96 | 55.82 | 56.53 | **57.88** |
| ZeroBench_sub | 21.41 | 21.41 | 22.01 | 21.86 | 21.41 | 21.71 | **24.40** |
| WeMath | 52.38 | 59.14 | 55.24 | 57.43 | 60.95 | 58.86 | **59.81** |
| MathVerse | 57.82 | 59.84 | 58.41 | 57.81 | 59.50 | 59.71 | **58.88** |
| **Vis. Avg.** | 54.00 | 55.76 | 54.88 | 55.69 | 55.99 | 56.44 | **56.97** |
| AIME 2025 | 46.88 | 47.50 | 48.33 | 44.58 | 43.54 | 45.42 | **49.58** |
| AIME 2024 | 58.96 | 55.83 | 60.21 | 57.92 | 59.79 | 58.33 | **60.42** |
| HMMT 2025 | 25.83 | 21.67 | 27.50 | 24.17 | 25.83 | 26.67 | **30.83** |
| MATH-500 | 92.80 | 93.90 | 93.65 | 93.55 | 93.45 | 93.40 | **94.50** |
| Minerva Math | 54.41 | 58.64 | 59.74 | 57.17 | 58.55 | 56.62 | **58.46** |
| **Text Avg.** | 55.78 | 55.51 | **57.89** | 55.48 | 56.23 | 56.09 | **58.76** |
| **Overall** | 54.74 | 55.65 | 56.13 | 55.60 | 56.09 | 56.29 | **57.71** |

CoPD 超过 Text-Expert 自己的领域 (58.76 vs 57.89) + 超过 Image-Expert 自己的领域 (56.97 vs 55.76)。

### 3-branch (text + image + video)

| | Base | Img-Exp | Txt-Exp | Vid-Exp | Mixed RLVR | MOPD | **CoPD** |
|-|------|---------|---------|---------|------------|------|----------|
| **Vis. Avg.** | 54.00 | 55.76 | 54.88 | 54.71 | 56.17 | 56.37 | **57.12** |
| **Text Avg.** | 55.78 | 55.51 | 57.89 | 56.84 | 55.39 | 56.80 | **58.63** |
| **Video Avg.** | 56.22 | 58.27 | 55.54 | 58.75 | 59.62 | 58.32 | **59.21** |
| **Overall** | 55.11 | 56.31 | 55.98 | 56.39 | 56.79 | 56.99 | **58.12** |

MOPD 在 video 上不如 Video-Expert (58.32 vs 58.75) — 多 teacher 静态蒸馏吸不全。

### 消融实验

| 变体 | Image Avg | Text Avg | Overall |
|------|-----------|----------|---------|
| CoPD 完整 | 56.97 | 58.76 | **57.71** |
| w/o I-OPD（去掉 img→txt 蒸馏） | 56.78 | 57.41 | 57.04 |
| w/o T-OPD（去掉 txt→img 蒸馏） | 56.48 | 57.78 | 57.02 |
| Text-Branch Only（不 merge） | 56.26 | **58.61** | 57.24 |
| Image-Branch Only（不 merge） | **56.78** | 57.17 | 56.94 |

**关键结论：即使不 merge，单分支也超过 static OPD！co-evolution 本身就产生均衡能力。merge 只是巩固互补优势。**

## 五、训练配置

- 框架：EasyVideoR1 (verl + EasyR1)
- Max input/output length: 16,384 tokens
- LR: 1e-6 (固定)
- Rollout batch: 256, 每 prompt 8 rollouts, temperature 1.0
- Clipping: ε_low = 0.2, ε_high = 0.28
- 总步数 = 两个单领域 expert 步数之和（保证数据吞吐量一致）

## 六、与现有方法对比

| Method | 训练 | 蒸馏 | 能力损失原因 |
|--------|------|------|-------------|
| Mixed RLVR | 单池混合 | N/A | 跨域干扰，inter-capability divergence |
| Static OPD | 专家训到收敛 → 蒸馏 | 单向、后训练 | teacher-student 行为差距过大 |
| MOPD | 多专家训到收敛 → 多教师蒸馏 | 单向、后训练 | 教师越多吸收越不全 |
| **CoPD** | **并行 RLVR + 交替 OPD** | **双向、训练中** | **最小化** |

## 七、批判性分析

### 优势
- 理论扎实：top-k overlap + symmetric KL 定量刻画行为距离
- 实验充分：pilot study → 主实验 → 消融 → 动力学 → 比例分析
- 工程可行：parameter merge 简单

### 不足/疑问
1. **Merge 策略过于简单** — 只是参数平均，没考虑不同参数空间差异。对 MoE 需要更精细设计
2. **只用 Qwen3-VL-4B** — 无 larger model 实验，scaling behavior 未知
3. **βₖ 没有消融** — 论文说 βₖ 平衡跨分支蒸馏贡献，但没给实验
4. **Compute 成本** — K 分支并行，总 compute 是单分支 K 倍，没讨论 compute efficiency

### 对我们的启发
- **MOE 训推一致性**：CoPD parallel branch 模式可用于 MoE expert 训练 — 每个 expert 在自己数据上 RLVR，同时互相 OPD，maintain behavioral overlap
- **OPD 时机**：最核心贡献是证明 OPD 必须在训练期间做。直接指导 OPD schedule 设计
- **top-k overlap 作为诊断指标**：可以用这个指标诊断 OPD 训练是否处于有效区间（Oₖ > 0.90）

## Related

- [[on-policy-distillation]] — OPD 基础
- [[grpo-rl-training]] — GRPO 算法
- [[generalized-on-policy-distillation]] — GOPD 框架
- [[knowledge-distillation]] — 知识蒸馏基础
- [[self-distilled-rlvr]] — RLVR + OPD 结合
