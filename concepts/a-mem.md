---
title: "A-Mem: Zettelkasten 式自组织 Agent 记忆"
created: 2026-04-17
updated: 2026-04-17
type: concept
tags: [memory, agent, architecture, long-term]
sources: [raw/papers/2025/02/2502.12110.md]
---

# A-Mem: Agentic Memory for LLM Agents

## 核心问题

现有 agent 记忆系统（[[mem0]], MemoryBank）依赖**预定义的存储结构和固定工作流**，
无法自适应地组织记忆。Graph-based 方案虽有结构但 schema 固定，限制了跨任务的泛化能力。

## 方法

受 **Zettelkasten 笔记法**启发，实现自组织、自进化的记忆网络。

### 1. Note Construction（笔记构建）

每条记忆 $m_i$ 存储为结构化笔记：

$$m_i = \{c_i, t_i, K_i, G_i, X_i, e_i, L_i\}$$

- $c_i$: 原始交互内容
- $t_i$: 时间戳
- $K_i$: LLM 生成的关键词
- $G_i$: LLM 生成的分类标签
- $X_i$: LLM 生成的上下文描述（核心语义理解）
- $e_i$: 文本编码器生成的嵌入向量
- $L_i$: 关联记忆链接集合

LLM 通过 prompt $P_{s1}$ 自主提取 $K_i, G_i, X_i$，实现隐式知识提取。

### 2. Link Generation（链接生成）

新记忆加入时：
1. 用 embedding 相似度检索 top-k 最近邻
2. LLM 分析候选记忆间的**共同属性**，决定是否建立链接
3. 链接类比 Zettelkasten 的 "box" 概念——相关记忆形成互联网络
4. 一条记忆可同时属于多个 "box"

### 3. Memory Evolution（记忆进化）

新记忆链接到旧记忆时，触发**旧记忆的进化更新**：

$$m_j^* \leftarrow \text{LLM}(m_n \Vert \mathcal{M}_{\text{near}}^n \setminus m_j \Vert m_j \Vert P_{s3})$$

随着交互累积，记忆网络自发形成**高阶模式和概念**，类似人类学习过程。

### 4. 检索

用 query embedding 的 cosine 相似度检索 top-k，利用链接关系扩展相关记忆。

## 结果

在 [[locomo-benchmark]] 上（GPT-4o-mini）：

| 类别 | MemGPT | A-Mem |
|------|--------|-------|
| Multi-hop RGE-2 | 10.58 | **10.61** |
| Temporal RGE-2 | 4.76 | **21.39** |
| Single-hop RGE-2 | 28.44 | **29.50** |
| Adversarial RGE-2 | 36.62 | **42.62** |

在 6 个基础模型上均优于 LoCoMo, ReadAgent, MemoryBank, MemGPT 基线。

## 意义

- **自组织**: 记忆结构不是预设的，而是从内容中涌现，解决了固定 schema 的泛化问题
- **记忆进化**: 首次实现记忆的动态更新——新记忆触发旧记忆的上下文重写
- **Zettelkasten 启发**: 将知识管理领域的成熟方法引入 agent 记忆设计
- **局限**: LLM 频繁调用（笔记构建+链接+进化），token 开销大；
  在 [[simplemem]] 的对比中，A-Mem 平均 F1=32.58，token cost=2520，不如 SimpleMem (F1=43.24, cost=531)

## Related

- [[agent-memory-system]] — 记忆系统总览
- [[mem0]] — 增量记忆管线基线
- [[memgpt]] — 层次化记忆先驱
- [[simplemem]] — 高效语义压缩，更强性能
- [[d-mem]] — 双过程记忆架构
