---
title: "ORACLE-SWE"
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [agentic-coding, swe-agent, oracle, evaluation]
sources: [raw/papers/2026/04/2604.07789.md]
---
# ORACLE-SWE: 量化 Oracle 信息对 SWE Agent 的贡献

## 核心问题
SWE Agent 能达到多高分辨率取决于信息获取。现有评测无法区分是能力不足还是信息不足。

## 方法
逐步提供 oracle 信息（精确 bug 位置、修复 patch、相关文件等），量化每条信息对最终解决率的贡献。

## 关键发现
- 定位 bug 是最大瓶颈（提供位置信息后解决率提升最大）
- 代码理解 vs patch 生成 vs 测试验证，各有不同信息需求
- 为 SWE Agent 训练提供了清晰的能力分解

## Related
- [[agentic-coding]]
- [[swe-hero]]
- [[cursorbench]]
