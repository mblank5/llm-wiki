---
title: LightMem: 轻量级 Agent 记忆系统
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [memory, agent, slm, lightweight, long-term]
sources: [raw/papers/2026/04/2604.07798.md]
---

# LightMem: 小模型驱动的轻量 Agent 记忆

## 核心思路

用 Small Language Models (SLMs) 替代大模型做记忆操作，分离在线/离线处理。

## 三层记忆

| 层级 | 用途 | 维护方式 |
|------|------|---------|
| STM (短期) | 即时对话上下文 | 在线 |
| MTM (中期) | 可复用交互摘要 | 在线语义压缩 |
| LTM (长期) | 巩固的知识 | 离线 graph consolidation |

## 关键设计

- **两阶段检索**: 向量粗检索 + 语义一致性重排序
- **用户隔离**: 支持 multi-user 独立检索和增量维护
- **LTM Graph**: 标准化节点/边类型，支持多跳推理

## 性能

- LoCoMo F1 +2.5 (avg)
- 检索延迟 83ms，端到端 581ms
- 在线处理固定检索预算

## Related

- [[hypermem]]
- [[memreader]]
- [[mem0]]
- [[agent-memory-system]]
