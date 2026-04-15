---
title: Combating Data Laundering in LLM Training
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [data-quality, data-laundering, llm-training, security]
sources: [raw/papers/2026/04/2604.01904.md]
---
# Combating Data Laundering in LLM Training

## 核心问题
Data Laundering: 通过合成/改写掩盖原始数据来源，将有问题的数据"洗白"后混入训练集。

## 威胁模型
- 恶意行为者故意注入有害/后门数据
- 通过改写/翻译/重组掩盖来源
- 传统数据清洗无法检测

## 防御策略
- 数据来源溯源
- 合成数据检测
- 训练数据审计

## Related
- [[agent-supply-chain-attack]]
- [[backdoor-awareness]]
- [[blendfusion]]
