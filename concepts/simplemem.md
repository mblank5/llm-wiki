---
title: SimpleMem: 高效语义压缩终身记忆
created: 2026-04-17
updated: 2026-04-17
type: concept
tags: [memory, agent, architecture, long-term, optimization]
sources: [raw/papers/2026/01/2601.02553.md]
---

# SimpleMem: Efficient Lifelong Memory for LLM Agents

## 核心问题

现有 agent 记忆方案的两难困境：
- **全上下文保留**: 信息冗余大，token 消耗高，中间上下文退化
- **迭代推理过滤**: 虽能降噪但多次推理导致高延迟和高 token 成本

SimpleMem 通过**语义无损压缩**实现信息密度和 token 效率的最优平衡。

## 方法

受 **互补学习系统 (CLS)** 理论启发，三阶段管线：

### Stage 1: Semantic Structured Compression（语义结构化压缩）

- **隐式语义密度门控**: LLM 自身作为语义 judge，生成式过滤而非二值分类
  - $\Phi_{\text{gate}}(W) \to \{m_k\}$：空集 = 低密度窗口，自动丢弃
- **统一去线性化变换**: 在一次生成中联合完成：
  - $g_{\text{coref}}$: 共指消解（代词→实体名）
  - $g_{\text{time}}$: 时间锚定（相对时间→ISO-8601 绝对时间戳）
  - $g_{\text{ext}}$: 对话流→独立事实陈述
- **三视图索引**: 每个 memory unit 同时建立：
  - **Semantic Layer**: dense embedding（模糊语义匹配）
  - **Lexical Layer**: BM25 sparse index（精确关键词/专有名词）
  - **Symbolic Layer**: 结构化元数据（时间戳、实体类型，确定性过滤）

### Stage 2: Online Semantic Synthesis（在线语义合成）

写入时即时整合相关片段为**高层抽象表示**，消除冗余：
- 三个碎片 "User wants coffee" + "prefers oat milk" + "likes it hot"
  → 合成为 "User prefers hot coffee with oat milk"
- 会话内实时执行，非异步后台维护

### Stage 3: Intent-Aware Retrieval Planning（意图感知检索规划）

LLM 推理用户搜索意图，生成检索计划：
$$\{q_{\text{sem}}, q_{\text{lex}}, q_{\text{sym}}, d\} \sim \mathcal{P}(q, H)$$
- $d$ = 自适应检索深度，$n \propto d$
- 三路并行检索 → ID-based 去重合并

## 结果

[[locomo-benchmark]] (GPT-4.1-mini) 关键数据：

| 方法 | Average F1 | Token Cost |
|------|-----------|------------|
| LoCoMo (full context) | 18.70 | 16,910 |
| MemGPT | 18.51 | 16,977 |
| [[a-mem]] | 32.58 | 2,520 |
| [[mem0]] | 34.20 | 973 |
| **SimpleMem** | **43.24** | **531** |

- F1 比 Mem0 **高 26.4%**，token 消耗 **降低 30×**
- 构建时间 92.6s（A-Mem: 5140.5s, Mem0: 1350.9s）
- 检索时间 388.3s（A-Mem: 796.7s, Mem0: 583.4s）

## 意义

- **效率范式转变**: 证明结构化语义压缩 > 图结构记忆 > 全上下文保留
- **实用性强**: 三阶段管线简洁，工程实现友好
- **平衡性能与效率**: 在 F1 和 token cost 上同时达到最优
- **局限性**: 压缩可能在极端多跳推理中丢失微妙关联；检索规划依赖 LLM 质量

## Related

- [[agent-memory-system]] — 记忆系统总览
- [[mem0]] — 基线对比方案
- [[a-mem]] — 自组织记忆，性能较低
- [[d-mem]] — 双过程系统，更高 F1 但更高成本
- [[lightmem-agent-memory]] — 三层记忆方案
- [[locomo-benchmark]] — 主要评测基准
