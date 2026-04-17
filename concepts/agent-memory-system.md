---
title: Agent Memory System: LLM Agent 长期记忆系统总览
created: 2026-04-17
updated: 2026-04-17
type: concept
tags: [memory, agent, long-term, survey, graph, rag]
sources: [raw/papers/2025/04/2504.19413.md, raw/papers/2026/04/2604.08256.md, raw/papers/2026/04/2604.07877.md, raw/papers/2026/04/2604.07798.md]
---

# Agent Memory System: LLM Agent 长期记忆系统

## 问题定义

LLM 固定上下文窗口无法支持长期多会话的上下文一致性。Agent Memory System 通过
**外部持久化记忆层** 解决这一问题：动态提取、整合、检索对话中的关键信息。

## 核心挑战

1. **提取质量**: 什么值得记住？如何避免噪声和冗余？
2. **更新策略**: 新信息与旧记忆矛盾时如何处理？
3. **检索效率**: 海量记忆中快速找到相关片段
4. **关系建模**: 事实间的关联（多跳推理）
5. **时序推理**: 记忆的时间维度（"上次见面时他说..."）

## 方案分类矩阵

|| 方案 | 记忆表示 | 图结构 | 提取方式 | 训练方法 | LoCoMo F1 |
||------|---------|--------|---------|---------|--------|
|| [[mem0]] | 自然语言 fact + 可选图 | 有向标记图 | LLM tool-call (ADD/UPDATE/DELETE/NOOP) | 无训练 | 34.2 |
|| [[hypermem]] | Topic/Episode/Fact 三层 | **超图** | 分层提取 + hyperedge 分组 | 无训练 | **92.73** (LLM-judge) |
|| [[memreader]] | 被动/主动双模式 | 无 | GRPO 训练 ReAct 决策 | SFT→DPO→GRPO | SOTA |
|| [[lightmem-agent-memory]] | STM/MTM/LTM 三层 | LTM Graph | SLM 驱动在线/离线 | SLM 蒸馏 | +2.5 F1 |
|| [[self-evolving-memory]] | 自进化记忆 | — | 跨异构任务自进化 | — | — |
|| [[memgpt]] | Main/External Context | 无 | LLM 自指导 tool-call | 无训练 | ~18.5 |
|| [[a-mem]] | Zettelkasten 笔记网络 | 动态链接 | LLM 生成+链接+进化 | 无训练 | 32.6 |
|| [[simplemem]] | 三视图索引 memory unit | 无 | 语义结构化压缩+在线合成 | 无训练 | **43.24** |
|| [[d-mem]] | Mem0* + 原始历史 | 有向标记图 | 双过程路由+Quality Gate | 无训练 | **53.5** |

## 关键技术维度

### 1. 记忆粒度

- **Fact-level**: Mem0 提取独立事实片段，粒度最细
- **Episode-level**: HyperMem 将事实组织为情节，保留叙事结构
- **Layer-level**: LightMem 按 STM/MTM/LTM 分层，不同时效用不同策略
- **Procedural**: Mem0 独有的 Procedural Memory 类型，记录 Agent 执行步骤摘要

### 2. 短期记忆管理

| 方案 | 短期记忆策略 |
|------|------------|
| [[mem0]] | **不管理**，交给 LLM context window；隐含 "recent messages" 缓冲（m=10） |
| [[lightmem-agent-memory]] | **显式 STM 层**，即时对话上下文，在线维护 |
| [[hypermem]] | Episode 层隐含短期语义，Topic 层桥接长短 |
| [[memreader]] | 依赖外部 STM 管理，聚焦"写什么"到长期记忆 |

**关键洞察**: Mem0 的设计哲学是"只做长期记忆层"，短期记忆交给 LLM 自身。LightMem 是唯一显式管理三层记忆的方案。

### 3. 关系建模

- **无图** (MemReader): 纯文本记忆 + embedding 检索
- **知识图谱** (Mem0^g, LightMem LTM): 实体-关系三元组，支持多跳推理
- **超图** (HyperMem): hyperedge 建模高阶关联，超越 pairwise limitation

### 3. 更新策略演进

| 策略 | 代表 | 特点 |
|------|------|------|
| 四操作 (ADD/UPDATE/DELETE/NOOP) | Mem0 v2 | 精细但 LLM 调用多 |
| ADD-only | Mem0 v3 | 简化，记忆只增不改，靠检索排序 |
| 冲突标记 | Mem0^g | 旧关系标记 invalid 不删除，支持时序 |
| 主动决策 | MemReader | GRPO 训练"写什么"的决策能力 |

### 4. 检索方法

- **向量相似度**: 所有方案的基线
- **BM25 关键词**: Mem0 v3 混合检索
- **Entity Linking**: Mem0 v3 实体链接 + embedding 融合
- **超图展开**: HyperMem 从锚定节点展开子图
- **双路径**: Mem0^g (entity-centric + semantic triplet)

## Benchmark 生态

| Benchmark | 规模 | 评测内容 |
|-----------|------|---------|
| [[locomo-benchmark]] | 7,512 QA, ~35 sessions | Single/Multi-hop, Temporal, Open-domain, Adversarial |
| [[longmemeval-benchmark]] | 500 QA, ~1.5M tokens | IE, Multi-session, Knowledge Update, Temporal, Abstention |
| **BEAM** | 1M-10M tokens | 大规模生产级记忆评测 |
| **HaluMem** | — | 记忆幻觉检测 |

## 趋势与开放问题

1. **ADD-only vs 精细更新**: Mem0 v3 证明简单策略（只增不删）在 benchmark 上更优，但长期记忆膨胀问题未解
2. **训练 vs 无训练**: MemReader 用 GRPO 训练记忆决策能力，其他方案依赖 LLM prompting — 端到端训练是否更优？
3. **超图 vs 知识图谱**: HyperMem 的超图在 LoCoMo 上略优于 Mem0^g 的标准图，但工程复杂度更高
4. **生产化 vs 学术研究**: Mem0 是唯一提供完整 SDK/CLI/托管服务的方案，其他仍为研究原型

## Related

- [[mem0]] — 工程化的记忆层产品
- [[hypermem]] — 超图记忆架构
- [[memreader]] — 主动记忆提取
- [[lightmem-agent-memory]] — 轻量三层记忆
- [[self-evolving-memory]] — 自进化记忆
- [[memgpt]] — LLM-as-OS 层次化记忆先驱
- [[a-mem]] — Zettelkasten 式自组织记忆
- [[simplemem]] — 语义压缩高效记忆
- [[d-mem]] — 双过程记忆系统
- [[locomo-benchmark]] — 长期对话记忆评测
- [[longmemeval-benchmark]] — 长期交互记忆评测
- [[rag-considerate-pretraining]] — RAG 与预训练的权衡
