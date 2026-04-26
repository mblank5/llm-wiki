---
title: "DP-OPD: Differentially Private On-Policy Distillation"
created: 2026-04-26
updated: 2026-04-26
type: concept
tags: [distillation, on-policy, rl, fine-tuning, alignment]
sources: [raw/papers/2026/04/2604.04461.md]
---
# DP-OPD: Differentially Private On-Policy Distillation

将差分隐私（Differential Privacy）与 OPD 结合，在保持蒸馏效果的同时提供正式的隐私保证。

## 定义

DP-OPD 在 on-policy distillation 框架中引入差分隐私机制，保护训练数据中的敏感信息，同时维持模型适配效率。

## 核心方法

### 差分隐私 + OPD
- 在 OPD 的 student rollout 和 teacher feedback 过程中注入隐私保护
- 通过 DP-SGD 或类似机制对梯度进行加噪和裁剪
- 保护训练数据中可能存在的敏感信息

### 正式隐私保证
- 提供 $(\epsilon, \delta)$-differential privacy 保证
- 隐私预算可在训练过程中严格追踪
- 相比传统 DP 微调，DP-OPD 利用 teacher 的 dense signal 缓解隐私噪声带来的性能损失

### 高效模型适配
- 利用 OPD 的 token 级密集监督，部分抵消 DP 噪声的影响
- 在隐私-效用 tradeoff 上优于纯 DP-SFT

## 实验结果
- DP-OPD 在相同隐私预算下优于 DP-SFT baseline
- 保持了 OPD 相对于 SFT 的效率优势
- 正式隐私保证可在实际部署中满足合规要求

## 开放问题
- 隐私预算 $\epsilon$ 与 OPD 性能下降之间的量化关系？
- DP-OPD 是否适用于 self-distillation 场景？
- 与 [[lightning-opd]] 的离线预计算能否结合？

## Related
- [[on-policy-distillation]]
- [[on-policy-distillation-survey]]
- [[on-policy-self-distillation]]
