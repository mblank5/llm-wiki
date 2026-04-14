---
title: CursorBench
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [benchmark, evaluation, company]
sources: [raw/papers/cursor-composer2-technical-report-2026.txt]
---

# CursorBench

Cursor 内部 agentic software engineering 评测套件，从真实 Cursor 编码会话中提取任务。

## 动机

公开 coding benchmark（SWE-bench, Terminal-Bench）与真实编码体验存在四大偏差：

1. **Domain Mismatch**: SWE-bench 主要测 bug-fixing，不代表完整开发工作流
2. **Prompt Over-specification**: 公开 benchmark 通常过度明确，而真实需求往往模糊、允许多种解法
3. **Data Contamination**: 公开 benchmark 来自历史开源仓库，容易泄露到训练数据（OpenAI 已停止报告 SWE-bench Verified）
4. **Narrow Scope**: 只测功能正确性，忽略代码质量、延迟、交互行为

## 结构特点

- **来源**: Cursor 工程团队的真实编码会话
- **中位代码改动**: 181 行（vs SWE-bench 的 7-10 行）
- **中位描述长度**: 390 chars（vs 1185-3055 chars，反映真实需求的不明确性）
- **无污染风险**: 不来自公开仓库

## 示例任务类型

- 从简短 bug report + observability logs 定位 esbuild transpilation bug
- 在数百条 chat response 上设计调优的启发式检测器来量化 streaming regression

## 迭代演进

CursorBench 持续更新，每版复杂度增长。CursorBench-3 相比初版中位任务规模翻倍。随用户工作流和 Agent 能力演变而持续迭代。

## 配套评测

除主评测外，还有针对性评测：
- **Intent evaluation**: 模糊 prompt 处理能力
- **Instruction-following**: 系统 prompt、规则、技能遵循
- **Eager editing**: 该不改代码时是否改了
- **Code quality**: 代码和注释质量
- **Interruption**: 处理中途打断和用户反馈

## 关联

- 使用模型: [[composer2]]
- 相关概念: [[agentic-coding]]
