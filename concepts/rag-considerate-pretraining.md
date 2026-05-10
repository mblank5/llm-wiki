---
title: "RAG-Considerate Pretraining"
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [pretraining, rag, scaling-laws, retrieval]
sources: [raw/papers/2026/04/2604.00715.md]
---
# RAG-Considerate Pretraining

## 核心问题
预训练 LLM 时，是否应该考虑下游 RAG 使用场景？传统预训练将 memorization 和 retrieval 视为独立问题。

## 方法
提出 RAG-aware 的预训练 scaling laws：
- 在预训练阶段引入 retrieval 信号的考虑
- 探索 memorization vs retrieval 的最优平衡
- 发现：考虑 RAG 的预训练可以用更少参数达到相同效果

## 意义
挑战了"先预训练再配 RAG"的传统范式，提出预训练和检索应联合优化的思路。

## Related
- [[llm-training-as-lossy-compression]]
- [[wrap-plus-plus]]
