---
title: Mem0: AI Agent 的可扩展长期记忆层
created: 2026-04-17
updated: 2026-04-17
type: entity
tags: [company, open-source, memory, agent, long-term, graph, ycombinator]
sources: [raw/papers/2025/04/2504.19413.md]
---

# Mem0: Universal Memory Layer for AI Agents

## 概述

[Mem0](https://mem0.ai)（读作 "mem-zero"）是一个为 AI Agent 提供智能长期记忆层的开源框架，
YC S24 批次公司。它动态地从对话中提取、整合、检索关键信息，使 Agent 能在多会话中保持个性化和上下文一致性。

**GitHub**: mem0ai/mem0 | ⭐ 53K+ stars | Apache 2.0 许可
**论文**: arXiv:2504.19413 (2025-04, 178 citations, ECAI)
**语言**: Python + TypeScript SDK

## 核心架构

### Mem0 基础版：Incremental Memory Pipeline

两阶段处理流程：

**1. Extraction Phase（提取）**
- 输入：消息对 $(m_{t-1}, m_t)$（通常为 user+assistant 一轮交互）
- 双上下文输入：
  - **Conversation Summary** $S$：全局对话摘要（来自数据库）
  - **Recent Messages** $\{m_{t-m}, ..., m_{t-1}\}$：最近 $m=10$ 条消息
- LLM 从三重上下文（summary + recent + new pair）中提取 candidate facts

**2. Update Phase（更新）**
- 向量数据库检索 $s=10$ 条最相似的已有记忆
- LLM 通过 tool-call 接口判断四类操作：
  - **ADD**: 新事实，无语义等价记忆 → 直接写入
  - **UPDATE**: 已有记忆需要补充/修正 → 合并更新
  - **DELETE**: 新信息与已有记忆矛盾 → 删除旧记忆
  - **NOOP**: 无需修改 → 跳过

> **2026 年 4 月 v3 算法升级**: 改为 **Single-pass ADD-only**（仅添加，不覆写），
> 引入 Entity Linking + Multi-signal retrieval（语义 + BM25 + Entity matching 并行融合）。
> LoCoMo 从 71.4→**91.6**, LongMemEval 从 67.8→**93.4**。

### Mem0^g：Graph-based Memory

在基础版上增加图结构记忆：

- **图表示** $G=(V,E,L)$：
  - Nodes $V$：实体（人、地点、事件等），含类型、embedding、时间戳
  - Edges $E$：关系三元组 $(v_s, r, v_d)$（如 `Alice -[lives_in]-> SF`）
  - Labels $L$：语义类型标注
- **双阶段提取**：
  1. Entity Extractor → 识别实体及类型
  2. Relationship Generator → 生成关系三元组
- **冲突检测**: LLM-based update resolver 判断旧关系是否过时，标记为 invalid 而非物理删除（支持时序推理）
- **双路径检索**：
  - Entity-centric：从 query 中提取实体 → 图中锚定节点 → 展开子图
  - Semantic triplet：query 整体编码 → 与所有三元组 embedding 匹配

## Benchmark 性能

### 论文版 (2025-04, LoCoMo)

| 系统 | Single-hop | Multi-hop | Temporal | Open-domain | Overall |
|------|-----------|-----------|----------|-------------|---------|
| Full Context (GPT-4o) | 26.13 | 16.55 | 19.75 | 51.93 | 28.59 |
| OpenAI Memory | 38.14 | 14.70 | 23.91 | 54.90 | 32.91 |
| **Mem0** | **41.38** | **25.53** | **27.13** | **67.13** | **40.29** |
| **Mem0^g** | **43.10** | **25.00** | **24.37** | **68.13** | **40.15** |

- 比 OpenAI Memory **+26%** (LLM-as-Judge metric)
- 比 Full Context **p95 latency 降低 91%**, token cost 降低 **>90%**

### v3 算法 (2026-04)

| Benchmark | v2 | v3 | Tokens | Latency p50 |
|-----------|----|----|--------|-------------|
| LoCoMo | 71.4 | **91.6** | 7.0K | 0.88s |
| LongMemEval | 67.8 | **93.4** | 6.8K | 1.09s |
| BEAM (1M) | — | **64.1** | 6.7K | 1.00s |
| BEAM (10M) | — | **48.6** | 6.9K | 1.05s |

## 与其他 Agent Memory 方案的对比

| 方案 | 记忆表示 | 提取方式 | 图结构 | 评测基准 |
|------|---------|---------|--------|---------|
| **Mem0** | 自然语言 fact + 可选图 | LLM incremental extraction | 有向标记图 $G=(V,E,L)$ | LoCoMo, LongMemEval |
| [[hypermem]] | 超图 (Topic/Episode/Fact 三层) | Hyperedge 分组 | **超图**（高阶关联） | LoCoMo 92.73% |
| [[memreader]] | 被动/主动双模式 | GRPO 训练 ReAct 式决策 | 无 | LoCoMo/LongMemEval/HaluMem |
| [[lightmem-agent-memory]] | STM/MTM/LTM 三层 | SLM 驱动 | LTM Graph | LoCoMo +2.5 F1 |

**关键差异**：
- Mem0 是 **工程产品化方案**（SDK、托管服务、CLI），HyperMem/MemReader 更偏学术研究
- Mem0 v3 的 ADD-only + Entity Linking 策略最简洁，但 HyperMem 的超图在多跳推理上更强
- MemReader 的"主动提取"思路独特（用 GRPO 训练记忆决策），Mem0 仍依赖 LLM tool-call

## 记忆类型体系

### 三种 MemoryType（代码枚举）

```python
class MemoryType(Enum):
    SEMANTIC = "semantic_memory"    # 语义记忆：事实、偏好、关系
    EPISODIC = "episodic_memory"   # 情景记忆（枚举存在但 v3 未独立实现）
    PROCEDURAL = "procedural_memory" # 程序记忆：Agent 执行步骤摘要
```

**默认行为**：`add()` 不指定 `memory_type` 时创建的即为 semantic memory（事实/偏好）。
语义记忆和情景记忆在 v3 中合并为 **ADD-only 事实流**，不再区分。

### Procedural Memory（程序记忆）

- 需显式传 `memory_type="procedural_memory"` + `agent_id`
- 用专用 prompt `PROCEDURAL_MEMORY_SYSTEM_PROMPT` 生成
- 目的：记录 Agent 的**完整执行历史摘要**（任务目标、进度、已执行步骤）
- 让 Agent 能在新的会话中恢复上下文，不丢失执行进度
- 典型场景：多步任务（如代码生成、数据处理）中 Agent 中断后恢复

### 三级 Scope 隔离

| Scope | 参数 | 用途 |
|-------|------|------|
| User | `user_id` | 用户级偏好、个人信息 |
| Agent | `agent_id` | Agent 自身知识和行为记忆 |
| Run | `run_id` | 单次执行/会话级记忆 |

三者可组合使用（如同时指定 `user_id` + `agent_id`），所有记忆按 scope 做 **向量数据库过滤 + 增量维护**。

### 短期 vs 长期

**Mem0 本身不管理短期记忆**。短期记忆（当前会话的对话历史）由 LLM 自身的 context window 管理。Mem0 的定位是：

```
短期记忆（LLM context window） ← 不涉及
    ↓ 会话结束后提取
Mem0 长期记忆层 ← 核心产品
    - Semantic Memory: 用户偏好、事实、关系
    - Procedural Memory: Agent 执行摘要
    - Entity Graph (Mem0^g): 实体-关系图谱
```

**与 [[lightmem-agent-memory]] 的对比**：LightMem 显式管理 STM/MTM/LTM 三层，Mem0 将 STM 交给 LLM、MTM 隐含在 "recent messages" 缓冲（$m=10$ 条），LTM 是向量数据库。

## 多模态支持

Mem0 通过 `enable_vision` 配置项支持**图像理解**：

```python
# config 中开启
config.llm.config["enable_vision"] = True
config.llm.config["vision_details"] = "auto"  # "low"/"high"/"auto"
```

**实现机制**（`parse_vision_messages`）：
1. 遍历 messages，检测 content 是否为 list（多图）或 dict with `type: image_url`
2. 调用 `get_image_description(msg, llm, vision_details)` 将图片转为文本描述
3. 替换原消息中的图片为文本描述，后续走正常文本记忆提取流程

**限制**：
- 仅支持**图像→文本**的转换，不支持音频、视频等多模态
- 图像不直接存入记忆，而是先由 LLM 描述后提取文字事实
- 论文明确将 **multimodal interactions 列为 Future Work**

## 应用场景

- AI 助手：跨会话个性化对话
- 客户支持：召回历史工单和用户偏好
- 医疗保健：追踪患者偏好和病史
- 游戏和生产力：基于用户行为的自适应

## Related

- [[hypermem]] — 超图记忆架构
- [[memreader]] — 主动式记忆提取
- [[lightmem-agent-memory]] — 轻量级记忆系统
- [[self-evolving-memory]] — 自进化记忆
- [[pask-proactive-agent]] — 主动 Agent 框架
