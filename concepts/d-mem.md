---
title: "D-Mem: 双过程记忆系统"
created: 2026-04-17
updated: 2026-04-17
type: concept
tags: [memory, agent, architecture, long-term]
sources: [raw/papers/2026/03/2603.18631.md]
---

# D-Mem: Dual-Process Memory System for LLM Agents

## 核心问题

增量记忆处理（如 [[mem0]]）存在 **有损抽象 (lossy abstraction)** 问题：
查询无关的压缩会丢失微妙的时间逻辑、多跳依赖和上下文细节。
而全面处理原始历史（如 GAM, E-mem）的计算开销巨大，不区分查询复杂度。

D-Mem 受 **Kahneman 双过程理论**（System 1/System 2）启发，
实现快速直觉检索 + 深度审议推理的动态路由。

## 方法

### 三组件架构

```
Query → Mem0* (System 1) → Quality Gate → [通过] → Answer
                              ↓ [失败]
                         Full Deliberation (System 2) → Answer
```

### 1. Mem0*: System 1 快速检索基线

基于 [[mem0]] 架构的增强版：
- **Extraction Phase**: 双上下文输入——top-10 相似记忆 + 近 10 条消息
- **Update Phase**: Top-5 相似历史记忆 + cosine > 0.8 严格过滤
- 四操作：ADD / UPDATE / DELETE / NOOP
- **查询时**: 检索 top-30 + relevance filtering → 生成初始答案

### 2. Quality Gating: 元认知门控（核心创新）

多维度质量评估，三轴 pass/fail 判定：

| 维度 | 评估内容 |
|------|---------|
| **Relevance** | 答案是否与问题相关 |
| **Faithfulness & Consistency** | 是否忠实于检索到的记忆 |
| **Completeness** | 是否完整回答了问题 |

任一维度不满足 → 触发 System 2 fallback。

对比其他门控策略（Majority Voting, Consensus），Quality Gating 最有效。

### 3. Full Deliberation: System 2 深度审议

直接处理**完整原始对话历史**，绕过压缩记忆：

1. **Chunked Fact Extraction**: 60 条消息/chunk，LLM 提取 query-relevant facts + 0-10 相关性评分
2. **Multi-stage Filtering**: 严格过滤噪声 facts
3. **Answer Generation**: 基于 filtered facts 生成高保真答案

逐块处理有效缓解 **Lost-in-the-Middle** 问题。

## 结果

[[locomo-benchmark]] (GPT-4o-mini):

| 方法 | F1 | 备注 |
|------|-----|------|
| Mem0* (System 1 only) | 51.2 | 快速但有损 |
| Full Deliberation (System 2 only) | 55.3 | 高保真但昂贵（10× tokens） |
| **Quality Gating** | **53.5** | **恢复 96.7% System 2 性能**，成本大幅降低 |

- Quality Gating 触发 fallback 约 30-40% 的查询
- 在 RealTalk benchmark 上也表现一致

## 意义

- **双过程认知模型首次应用于 agent 记忆**: 将认知科学的 System 1/2 框架工程化
- **自适应计算**: 简单查询走快速路径，复杂查询触发深度审议，实现认知经济
- **有损抽象问题的新解法**: 不放弃压缩检索，而是用 fallback 机制弥补其不足
- **Full Deliberation 作为上界**: 证明即使用尽原始历史，F1 也仅 55.3——未来需要
  超越显式事实提取，捕捉隐式跨历史信息
- **局限**: Quality Gating 本身消耗额外 LLM 调用；系统复杂度高于单一策略

## Related

- [[agent-memory-system]] — 记忆系统总览
- [[mem0]] — System 1 基线架构
- [[simplemem]] — 语义压缩方案，不同哲学（预防性压缩 vs 补救性 fallback）
- [[a-mem]] — 自组织记忆
- [[locomo-benchmark]] — 主要评测基准
