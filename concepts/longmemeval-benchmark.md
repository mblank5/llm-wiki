---
title: LongMemEval: 长期交互记忆评测基准
created: 2026-04-17
updated: 2026-04-17
type: concept
tags: [benchmark, evaluation, memory, long-term, dataset]
sources: [raw/papers/2024/10/2410.10813.md]
---

# LongMemEval: Chat Assistant 长期交互记忆评测

## 核心问题

现有长期记忆 benchmark 两大不足：
(1) 不反映真实 user-AI 交互（多用 human-human 对话或缺少 task-oriented 场景）；
(2) 记忆能力覆盖不全，缺少 knowledge update、assistant 侧信息回忆、时间推理。

LongMemEval 提供更贴近真实 chat assistant 场景的综合评测。

## 方法

### 五大核心记忆能力

| 能力 | 缩写 | 描述 |
|------|------|------|
| **Information Extraction** | IE | 从交互历史中回忆用户/助手提到的具体信息 |
| **Multi-Session Reasoning** | MR | 跨多会话综合信息，涉及聚合和比较 |
| **Knowledge Updates** | KU | 识别用户信息变化并动态更新 |
| **Temporal Reasoning** | TR | 处理时间戳元数据和显式时间引用 |
| **Abstention** | ABS | 对信息不足的问题正确回答"I don't know" |

### 数据构建

- **500 个手动创建问题**，7 种问题类型
- **164 个用户属性**（lifestyle, belongings, life events, situations, demographics）
- Evidence 嵌入 task-oriented 对话会话（通过 self-chat 生成，人工审核）
- 历史长度 **自由可扩展**：两个标准配置 S (~115K tokens) 和 M (~1.5M tokens)

### 统一记忆框架

提出 indexing-retrieval-reading 三阶段框架，分析四个控制点：
- **Value**: round 粒度优于 session 粒度
- **Key**: fact-augmented key expansion 提升 recall@k 9.4%
- **Query**: time-aware query expansion 改善时序推理 6.8-11.3%
- **Reading**: Chain-of-Note + 结构化格式提升准确率 10 个百分点

## 结果

| 系统 | 设置 | 表现 |
|------|------|------|
| Long-context LLMs | LongMemEval-S | **30-60% 性能下降** |
| Commercial chatbots | 简化设置 | 30-70% 准确率 |
| GPT-4 + memory优化 | — | 仍有显著提升空间 |

核心发现：
- Round 粒度存储优于 session 粒度
- Flat index + fact-augmented keys 是强基线
- 时间无关设计在 temporal reasoning 上表现差

## 意义

- **能力更全面**: 唯一同时覆盖 IE/MR/KU/TR/ABS 五大能力的 benchmark
- **自由扩展**: 历史长度可配置至 1.5M tokens，适应不断进步的系统
- **Task-oriented**: 使用真实 task-oriented 对话场景，而非 human-human 对话
- **设计指南**: 提供了实用的记忆系统设计优化建议
- 与 [[locomo-benchmark]] 互补：LoCoMo 侧重 open-domain reasoning，LongMemEval 侧重
  交互式记忆的全面能力评估

## Related

- [[agent-memory-system]] — 记忆系统总览
- [[locomo-benchmark]] — 另一主要记忆 benchmark
- [[mem0]] — 记忆层方案
- [[simplemem]] — 在 LongMemEval 上验证的高效方案
