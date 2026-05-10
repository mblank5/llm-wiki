---
title: "LLM-PRISM: GPU Faults & Silent Data Corruption"
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [data-quality, gpu, hardware, silent-corruption, training]
sources: [raw/papers/2026/04/2604.10390.md]
---
# LLM-PRISM: Silent Data Corruption from GPU Faults

## 核心问题
GPU 永久性故障会导致 LLM 训练中的**静默数据损坏** (Silent Data Corruption, SDC)——数据损坏但训练不报错。

## 关键发现
- SDC 比想象中更常见
- 传统 checkpointing 无法检测
- 需要专门的检测和恢复机制

## 意义
数据质量问题不仅来自数据源，还来自硬件故障。对大规模训练的工程实践有重要参考。

## Related
- [[data-laundering-llm]]
- [[scalable-moe-pretraining]]
