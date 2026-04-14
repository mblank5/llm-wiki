---
title: HyperMem: 超图记忆架构
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [memory, agent, hypergraph, long-term, conversation]
sources: [raw/papers/2026/04/2604.08256.md]
---

# HyperMem: 超图记忆用于长期对话

## 核心问题

RAG 和图记忆系统基于 **成对关系**，无法捕捉高阶关联（多元素间的联合依赖），
导致检索碎片化。

## 方法

### 三层记忆结构

1. **Topics**: 对话主题
2. **Episodes**: 情节/片段
3. **Facts**: 具体事实

### 超边 (Hyperedge)

用 hyperedge 将相关 episode 和 fact 分组为连贯单元，超越 pairwise limitation。

### 检索策略

- Hybrid lexical-semantic index
- Coarse-to-fine retrieval: 先向量粗检索，再语义一致性重排序

## 结果

- LoCoMo SOTA: **92.73%** LLM-as-judge accuracy
- Single-hop: 90.61%, Multi-hop: 93.62%, Temporal: 89.72%

## 意义

- 超图建模是记忆架构的新范式，比传统知识图谱更适合对话记忆
- 对 agent 系统的长期记忆设计有直接参考价值

## Related

- [[memreader]]
- [[lightmem-agent-memory]]
- [[full-duplex-speech-model]]
