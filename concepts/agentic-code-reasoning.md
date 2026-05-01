---
title: "Agentic Code Reasoning"
created: 2026-05-01
updated: 2026-05-01
type: concept
tags: [coding, agent, reasoning, software-engineering]
sources: [raw/papers/2026/03/2603.01896.md]
---

# Agentic Code Reasoning（代理式代码推理）

*半形式化推理模板让 LLM Agent 在代码分析任务中持续超越标准推理 (2026-03)*

## 概要

本文研究 LLM Agent 在三个代码推理任务（补丁等价验证、故障定位、代码问答）上的表现，提出**半形式化推理（Semi-Formal Reasoning）**结构化模板，迫使 Agent 在给出结论前系统性地记录证据。在所有任务中实现 5-12 个百分点的精度提升，补丁验证达 93% 准确率。

## Overview

核心问题是：LLM Agent 能否在不执行代码的情况下进行有意义的语义代码分析？答案是肯定的，但需要结构化推理模板。

**三个任务**：
1. **补丁等价验证**：判断两个补丁是否产生相同测试结果（93% 准确率）
2. **故障定位**：在代码库中定位 bug 根因（Top-5 All 72.1%）
3. **代码问答**：RubberDuckBench 上的代码理解（87% 准确率）

**半形式化模板**要求 Agent 填写：
- 函数追踪表（Function Trace Table）：列出每个函数的文件:行号、参数类型、返回类型、已验证行为
- 数据流分析：追踪关键变量的创建、修改、使用位置
- 语义属性：带明确文件:行号证据
- 替代假设检查：主动寻找反驳证据

## Key Contribution

- **执行无关验证**：93% 补丁等价验证准确率，无需运行测试，为 RL 训练管线提供低成本反馈
- **结构化探索格式**：Agent 必须在读取文件前声明假设（HYPOTHESIS），读后记录观察（OBSERVATIONS）和假设更新
- **发现名称遮蔽（Name Shadowing）**：半形式化推理成功发现 Django 中 `format()` 被 module-level 函数遮蔽导致 AttributeError 的 bug，而标准推理未发现
- **RubberDuckBench 基准**：15 道跨 C++/Python/Java 的代码理解题，专为此研究设计

## Experimental Results

**补丁等价验证**（DiffPatches 基准）：

| 模型 | 模式 | 准确率 |
|------|------|--------|
| Sonnet-4.5 | Single-shot (Standard) | 80.0% |
| Sonnet-4.5 | + File Context (Standard) | 82.0% |
| Sonnet-4.5 | Agentic (Standard) | 86.0% |
| Sonnet-4.5 | Agentic (Semi-formal) | **93.0%** |

**故障定位**（Defects4J，Opus-4.5）：

| 模式 | Top-1 (All) | Top-5 (All) | Top-5 (Any) |
|------|-------------|-------------|-------------|
| Standard Agentic | 46.5% | 60.5% | 81.4% |
| Semi-formal Agentic | **53.5%** | **72.1%** | **88.4%** |

**代码问答**（RubberDuckBench）：

| 模型 | 模式 | 准确率 |
|------|------|--------|
| Opus-4.5 | Agentic (Standard) | 78.3% |
| Opus-4.5 | Agentic (Semi-formal) | **87.0%** |

## Related

- [[agentic-coding]] — 代理式代码推理是 agentic coding 的核心能力之一
- [[agent-r1-end-to-end-rl]] — 执行无关验证可为 RL 训练管线提供低成本奖励信号
- [[swe-shepherd]] — 同属 AI 辅助软件工程，侧重不同环节
