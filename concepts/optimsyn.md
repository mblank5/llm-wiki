---
title: "Optimsyn: Influence-Guided Rubrics for Synthetic Data"
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [synthetic-data, optimization, rubrics, influence-function]
sources: [raw/papers/2026/04/2604.00536.md]
---
# Optimsyn: 影响引导的合成数据优化

## 核心方法
用 influence function 引导合成数据的 rubrics（规则/模板）优化：
- 不是随机生成合成数据
- 而是用 influence function 评估每条合成数据对最终模型的贡献
- 据此优化生成 rubrics

## 意义
将数据质量评估从"事后检查"变为"事前引导"，提高合成数据的训练效率。

## Related
- [[blendfusion]]
- [[rl-guided-synthetic-data]]
- [[data-laundering-llm]]
