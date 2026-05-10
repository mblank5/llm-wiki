---
title: "WRAP++: Web Discovery Amplified Pretraining"
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [pretraining, synthetic-data, knowledge, web, cross-document]
sources: [raw/papers/2026/04/2604.06829.md]
---

# WRAP++: 跨文档发现增强预训练

## 核心问题

现有 synthetic data 重写只操作单文档，无法建立跨文档关联。

## 方法

从 Web 超链接发现跨文档关系，合成联合 QA：
- **Dual-links**: 双向链接的文档对
- **Co-mentions**: 共同提及的实体对
- 组合爆炸 → 数据规模远超单文档重写

## 规模

Wikipedia ~8.4B tokens → **80B tokens** 跨文档 QA 数据

## 结果

在 Qwen2.5-7B 上验证，知识密集任务显著提升。

## Related

- [[on-policy-distillation]]
- [[knowledge-distillation]]
