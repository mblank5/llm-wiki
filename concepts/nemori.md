---
title: Nemori: 认知启发的自适应记忆蒸馏框架
created: 2026-04-17
updated: 2026-04-17
type: concept
tags: [memory, agent, architecture, long-term]
sources: [raw/papers/2025/08/2508.03341.md]
---

# Nemori: Adaptive Memory Distillation for LLM Agents

## 核心问题

现有 agent 记忆系统依赖**预定义启发式**（重要性评分、情感标签、事实模板）决定"什么值得记住"，
将设计者的主观直觉编码进系统，导致：(1) 信息失真不可逆；(2) 系统性过度存储（bloat）。

Nemori 提出：**记忆价值应从交互数据本身涌现，而非预设规则**。

## 方法

受 **预测编码理论 (Predictive Coding)** 和 **互补学习系统 (CLS)** 启发，无训练框架。

### 三个先验原则

1. **结构先验 (Integrity of Episode)**: 交互序列天然分组，不应碎片化切割
2. **表示先验 (Asymmetry of Perspective)**: 原始体验是 egocentric，记忆需转为 allocentric 叙事
3. **蒸馏先验 (Predictability Implies Redundancy)**: 可预测 = 冗余，预测误差 = 值得记忆

### Episodic Memory Integration（情景记忆整合）

1. **Local Message Partitioning**: LLM 识别消息缓冲区中的自然分组，保持情节完整性
2. **Narrative Episode Generation**: 原始片段转为结构化叙事 $(N_j, c_j)$，含 episodic cue 用于检索
3. **Associative Memory Integration**: 对新叙事检索相似已有记忆，决定合并或独立插入

### Semantic Knowledge Distillation（语义知识蒸馏）

核心创新：通过**预测误差**决定记忆价值

1. **Anticipatory Schema Synthesis**: 对每个情景，用已有知识生成"预期内容"
2. **Prediction Error Distillation**: 对比预期与实际交互，提取**预测误差**（不可预测的新信息）
3. **Agnost Knowledge Consolidation**: 将蒸馏结果整合到知识库

### 管理无关设计

Nemori 仅负责蒸馏（决定记什么），**管理无关**——可接入任何下游管理系统。

## 结果

在 [[locomo-benchmark]] 和 [[longmemeval-benchmark]] 上：

- 整体性能优于或持平于 A-MEM、MemoryOS 等基线
- **时序推理突出**: 在需要追踪状态变化的场景表现优异
- 接入第三方管理时（A-MEM、MemoryOS），**存储减少 45-64%** 且性能不变
- 构建效率: episode 级处理避免逐消息操作，显著降低 token 开销

## 意义

- **数据驱动蒸馏**: 首次用预测误差替代启发式评分，消除了设计者偏见
- **管理无关**: 可作为蒸馏层增强任何现有记忆系统
- **认知科学映射**: Predictive Coding → 记忆蒸馏，CLS → episodic/semantic 双模块
- **与 [[a-mem]] 的互补**: A-Mem 管理结构强但蒸馏靠 LLM 关键词；Nemori 蒸馏科学但管理委托外部
- **局限**: 依赖 LLM 生成"预期"的准确性；蒸馏深度受 observation window 长度影响

## Related

- [[agent-memory-system]] — 记忆系统总览
- [[a-mem]] — Zettelkasten 自组织记忆（可互补）
- [[simplemem]] — 高效语义压缩记忆
- [[locomo-benchmark]] — 主要评测基准
- [[ariadne-mem]] — 图结构终身记忆
