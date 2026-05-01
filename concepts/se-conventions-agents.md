---
title: "Beyond Human-Readable: Rethinking SE Conventions for Agents"
created: 2026-05-01
updated: 2026-05-01
type: concept
tags: [agentic-coding, software-engineering, agent, optimization]
sources: [raw/papers/2026/04/2604.07502.md]
---

# 超越人类可读：重新思考 Agent 时代的软件工程规范

*语义密度原则：压缩不总是好事，零信息 token 才是优化目标 (2026-04)*

## 概要

当代码的主要消费者从人类变为 LLM Agent 时，六十年来的软件工程规范需要重新审视。本文提出**语义密度优化**原则——消除零信息 token，保留高语义价值 token——并通过控制实验发现：激进的压缩反而增加了 67% 的总会话成本。此外提出了 **Program Skeleton（程序骨架）** 概念用于 Agent 导航。

## Overview

### 语义密度原则

**语义密度** = 携带任务相关含义的 token / 总 token 数

- **高密度 token**：描述性命名、类型注解、docstring、业务逻辑表达式、带诊断上下文的错误消息
- **零信息 token**：结构化样板代码、冗余访问修饰符、框架脚手架

核心论点：**优化目标不是 token 最小化，而是语义密度最大化**。压缩高信息 token 是反生产力行为——减少了输入 token 但增加了推理 token。

### 七类受压规范的分类法

1. **文件拆分与项目结构**：Agent 应按部署边界拆分，而非认知限制
2. **命名规范**：有意义的命名价值增加，`VerifyOrderByAvailableAmount` 是压缩文档
3. **抽象深度与仪式代码**：Java Spring Boot 一个端点 8+ 文件 170 行仅 18 行业务逻辑（8:1 比率）
4. **反模式重新评估**：800 行文件 = 1 次 tool call vs 15 文件 = 15 次 tool call
5. **SOLID 原则**：SRP 认知论据弱化；DRY 在 Agent 可靠更新时意义减弱
6. **日志格式**：见实验部分
7. **Git 提交信息**：Agent 受益于丰富的提交信息，节省重读 diff

### Program Skeleton（程序骨架）

提议新文件类型 `CODEMAP.md`：包含模块拓扑、入口点、调用链、函数签名，不含实现体。是损失性语义压缩，一次性提供导航地图。

## Key Contribution

- **语义密度原则** + **压缩悖论的实验验证**
- **Program Skeleton 概念**：为 Agent 高效导航而设计的新软件工件
- **仪式代码-逻辑比**（Ceremony-to-Logic Ratio）作为非正式度量
- **七类规范分类法**：系统分析人类中心规范在 Agent 压力下的成本效益变化

## Experimental Results

日志格式控制实验（200 个电商日志事件，claude-sonnet-4-6）：

| 格式 | 文件 token | 会话 token | 耗时 | 正确率 |
|------|-----------|-----------|------|--------|
| A — Human-Readable | 8,072 | 18.9k | 1m36s | 5/5 |
| B — Structured | 7,106 (-12%) | 24.0k | 5m24s | 5/5 |
| C — Compressed | 6,695 (-17%) | 31.6k | 7m00s | 5/5 |
| D — C + Decoder Tool | 6,695 (-17%) | 28.3k | 4m05s | 5/5 |

**压缩悖论**：Format C 减少 17% 输入 token，但增加 67% 会话总成本。原因：
- 压缩后模型需在推理阶段解码缩写，产生"推理税"
- Tool 调用引入额外开销（5-7 次调用），固定开销超过选择性解压节省

**关键洞察**：最优的人类和机器表示共享高语义密度。分歧在于结构组织——人类需要小文件和视觉格式，机器需要整合访问和导航索引。

## Related

- [[agentic-coding]] — 本文直接为 agentic coding 提供软件工程实践指导
- [[rethinking-se-for-agentic-ai]] — 同主题，软件工程在 Agent 时代的重构
- [[swe-agile]] — 敏捷开发流程在 Agent 编程范式下的演变
