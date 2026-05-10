---
title: "LoCoMo: 长期对话记忆评测基准"
created: 2026-04-17
updated: 2026-04-17
type: concept
tags: [benchmark, evaluation, memory, long-term, conversation, dataset]
sources: [raw/papers/2024/03/2403.01977.md]
---

# LoCoMo: Long-Term Conversational Memory Benchmark

## 核心问题

缺乏系统性评估 LLM 在长期多会话对话中记忆能力的 benchmark。
现有数据集（MSC, MemoryBank）对话短（~1K tokens, 4-5 sessions），
无法测试真正的长期记忆依赖。LoCoMo 提供更长、更多样化的评测。

## 方法

### 数据集特征

- **50 组长期对话**，由人类标注员跨越多天进行自然对话
- 平均 ~9K tokens，最多 **35 sessions**（远超之前数据集的 4-5 sessions）
- 总计 **7,512 个问答对**

### 五类评测维度

| 类型 | 描述 | 能力 |
|------|------|------|
| **Single-hop** | 单会话内信息提取 | 基础记忆提取 |
| **Multi-hop** | 跨会话信息综合 | 多跳推理 |
| **Temporal** | 时间相关推理 | 时序理解 |
| **Open-domain** | 结合外部知识的推理 | 知识整合 |
| **Adversarial** | 不可回答问题检测 | 判断力 |

### 评测指标

- ROUGE-L, ROUGE-2, BLEU-1, METEOR（生成质量）
- SBERT Similarity（语义相似度）
- F1 score（事实准确性）

## 结果

LoCoMo 成为 agent memory 系统的 **标准评测基准**：

| 系统 | Average F1 | 特点 |
|------|-----------|------|
| Full Context | ~18-28 | 高 token 消耗，性能非最优 |
| [[mem0]] | ~34-36 | 工程化方案，效率好 |
| [[a-mem]] | ~33 | 自组织记忆 |
| [[simplemem]] | **43.24** | 语义压缩 + 自适应检索 |
| [[d-mem]] | **53.5** | 双过程系统 |
| [[hypermem]] | **92.73** (LLM-judge) | 超图架构 |

## 意义

- **De facto standard**: 几乎所有后续 agent memory 论文都以 LoCoMo 作为主要评测
- **全面性**: 5 类问题覆盖提取、推理、时序、开放知识、对抗，比 [[longmemeval-benchmark]] 更
  广泛但缺少 knowledge update 和 abstention 能力测试
- **可扩展性**: 支持 LoCoMo-10（10 sessions）等不同配置
- **开放问题**: 即使 SOTA 系统在 multi-hop 和 temporal 类别上仍有较大提升空间

## Related

- [[agent-memory-system]] — 记忆系统总览
- [[longmemeval-benchmark]] — 另一长期记忆评测
- [[mem0]] — 常用基线方案
- [[simplemem]] — 当前 F1 SOTA
- [[d-mem]] — 双过程 SOTA
- [[hypermem]] — LLM-judge SOTA
