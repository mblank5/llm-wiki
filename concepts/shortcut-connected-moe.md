---
title: "shortcut-connected-moe"
created: 2026-05-01
updated: 2026-05-01
type: concept
tags: [architecture, optimization, open-source]
sources: [raw/papers/2025/09/2509.01322.md]
---

# Shortcut-Connected MoE (ScMoE)

**Shortcut-connected MoE** 是 [[longcat-flash]] 的另一核心架构创新，通过重排执行流水线来**扩大计算-通信重叠窗口**，显著提升训练和推理效率。

## 问题

大规模 MoE 模型的效率受限于通信开销：
- all-to-all 通信必须在计算前完成
- 设备利用率低，系统吞吐量受限

传统方案（shared-expert）仅重叠一个专家的计算，窗口太小。

## 方案

ScMoE 引入**跨层 shortcut**，重排执行流水线：

- 前一层的 dense FFN 与当前 MoE 层的 dispatch/combine 通信**并行执行**
- 重叠窗口 = 整个前一层计算 >> 单个专家计算

## 关键特性

### 无损质量

训练损失曲线与无 ScMoE 的基线几乎完全一致。在多种配置下验证：
- 2.4B-16B MoE + MLA
- 3B-20B + MHA
- 15B-193B + GQA

### 训练效率

前一块的计算与 MoE 的 dispatch/combine 通信完全并行（沿 token 维度细粒度分块）。

### 推理效率

- **Single Batch Overlap 流水线**
- TPOT（每输出 token 时间）降低约 **50%**
- 节点内 NVLink 通信（dense FFN 的 TP）与节点间 RDMA 通信（MoE 的 EP）同时执行

## 与 Zero-Computation Experts 的协同

ScMoE 和 Zero-Computation Experts 是正交的创新：
- ScMoE 解决**通信瓶颈**
- Zero-Computation Experts 解决**计算分配**
- 两者结合使 [[longcat-flash]] 在 560B 参数规模下实现 >100 tokens/秒的推理吞吐

## 相关概念

- [[mixture-of-experts]] — MoE 架构
- [[zero-computation-experts]] — 零计算专家
- [[longcat-flash]] — 使用该技术的模型
