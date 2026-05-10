---
title: "Memori: LLM 无关的持久记忆层"
created: 2026-04-17
updated: 2026-04-17
type: concept
tags: [memory, agent, architecture, long-term, optimization]
sources: [raw/papers/2026/03/2603.19935.md]
---

# Memori: A Persistent Memory Layer for LLM Agents

## 核心问题

LLM Agent 的持久记忆面临两大生产挑战：
1. **上下文退化**: 原始对话注入 prompt 导致 context rot（信息在但未被有效利用）
2. **Token 成本**: 全上下文方案 token 消耗巨大，API 费用不可持续

Memori 将记忆视为**数据结构化问题**而非存储问题。

## 方法

### 系统架构

Memori 作为 **LLM 无关的解耦记忆层**，位于应用逻辑和底层 LLM 之间：
- 通过轻量 Memori SDK 封装现有 LLM 客户端
- 拦截请求，自动管理记忆的读写

### Advanced Augmentation 管线

将非结构化对话转化为**双层结构化记忆资产**：

#### 1. Semantic Triple Generation（语义三元组生成）

- 从对话中提取原子知识单元：事实、偏好、约束、属性
- 结构化为 **subject–predicate–object** 三元组
- 每个三元组关联到原始对话来源
- **双重优势**: (1) 低噪声高精度检索索引；(2) 天然压缩层

#### 2. Conversation Summarization（对话摘要）

- 三元组擅长静态事实但缺乏叙事上下文
- 摘要捕捉用户意图、时序演进、隐含语境
- 三元组直接链接到对应摘要 → 检索事实时可追溯完整背景

### 检索策略

- **混合搜索**: cosine embedding 相似度 + BM25 关键词匹配
- 检索结果同时返回相关三元组及其关联摘要
- 使用 Gemma-300 嵌入模型 + FAISS 索引

## 结果

[[locomo-benchmark]] (GPT-4.1-mini, LLM-as-Judge)：

| 方法 | Overall (%) | Tokens/Query |
|------|-------------|-------------|
| Full-Context | 87.52 | 26,031 |
| **Memori** | **81.95** | **1,294 (4.97%)** |
| Zep | 79.09 | 3,911 |
| LangMem | 78.05 | — |
| mem0 | 62.47 | 1,764 |

- 比 Zep **token 减少 67%**，同时准确率更高
- 比 Full-Context **成本降低 20×**
- Single-Hop 最强（87.87%），接近 Full-Context 上限（88.53%）
- Temporal（80.37%）弱于 Zep/LangMem（三元组缺乏时序建模）

## 意义

- **数据结构化范式**: 证明记忆质量取决于表示结构而非上下文量
- **三元组+摘要双层**: 兼顾精确事实检索和叙事推理
- **生产导向**: 唯一强调 LLM 无关性和 SDK 集成的记忆方案
- **Token 极致压缩**: 仅用 5% 上下文达到 82% 准确率
- **局限**: Open-Domain 推理（63.54%）仍弱；三元组的静态特性限制时序和复杂推理；
  对比中缺少 [[simplemem]]、[[ariadne-mem]] 等最新基线

## Related

- [[agent-memory-system]] — 记忆系统总览
- [[mem0]] — 竞品对比基线
- [[simplemem]] — 语义压缩方案，更高 F1
- [[ariadne-mem]] — 图结构推理，更强多跳
- [[locomo-benchmark]] — 主要评测基准
- [[m-plus-memoryllm]] — 模型内记忆方案（不同路线）
