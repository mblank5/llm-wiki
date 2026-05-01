---
title: "zero-computation-experts"
created: 2026-05-01
updated: 2026-05-01
type: concept
tags: [architecture, optimization, open-source]
sources: [raw/papers/2025/09/2509.01322.md]
---

# Zero-Computation Experts

**零计算专家**是 [[longcat-flash]] 架构的核心创新之一，一种在 Mixture-of-Experts (MoE) 模型中实现**动态计算预算分配**的机制。

## 核心思想

不是所有 token 都值得同等计算。困难 token 需要更多资源来准确预测，简单 token 几乎不需要计算。

## 实现方式

在 MoE 专家池中混入**零计算专家（Zero-Computation Experts）**：
- 被选中时，零计算专家直接将输入原样返回（E(x) = x）
- 不消耗任何 FLOPs
- 路由器为每个 token 选择 K 个专家，其中真实 FFN 专家数量动态调整

## 数学模型

```
MoE(x_t) = Σ(i=1 to N+Z) g_i · E_i(x_t)
```

- N 个标准 FFN 专家
- Z 个零计算专家
- K 个专家被激活，其中真实 FFN 专家数量可变

## PID 控制器

通过 PID（比例-积分-微分）控制器动态调节专家偏置：

```
Δb_i = μ · (K_e/K · 1/N - T_i / (K · T_all))
```

确保专家分配收敛到目标比例。

## 效果

- [[longcat-flash]]：560B 总参数，仅激活 18.6B~31.3B（平均 27B）
- 约 20B tokens 调整后收敛，波动 <1%
- 标准差保持在较高水平，说明模型确实在根据 token 重要性分配不同计算量

## 相关概念

- [[mixture-of-experts]] — MoE 架构
- [[shortcut-connected-moe]] — Shortcut-connected MoE
- [[longcat-flash]] — 使用该技术的模型
