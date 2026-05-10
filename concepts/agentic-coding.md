---
title: "Agentic Coding"
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [tool-use, open-source]
sources: [raw/papers/cursor-composer2-technical-report-2026.txt]
---

# Agentic Coding

AI Agent 自主完成软件工程任务的模式。区别于传统的 code completion 或 chat 式编码助手，agentic coding 要求模型能够：

## 核心特征

1. **自主导航代码库**: 搜索、阅读、理解大型代码库
2. **多步执行**: 连续进行文件编辑、测试运行、调试循环
3. **工具使用**: grep、语义搜索、shell 命令、web 搜索等
4. **长程规划**: 在数百个 tool call 上保持一致性

## 形式化定义

给定环境（代码库 + 隔离容器）和任务 prompt x，Agent 产生 rollout：

```
a1, ..., aT  (actions, each makes tool calls)
y1, ..., yT  (responses)
```

每个 action 由语言模型策略 πθ(ai | x, a1, y1, ..., ai-1, yi-1) 采样。

## 与传统编码的区别

- **vs Autocomplete**: 不是预测下一个 token，而是解决完整工程问题
- **vs Chat coding**: 不是单轮对话，而是多步探索、测试、迭代
- **vs Competitive programming**: 需要非平凡的探索、自己写测试、构建最小改动

## 训练方法趋势（基于 [[composer2]] 的实践）

1. Continued pretraining 专化代码知识
2. 大规模异步 RL 训练端到端编码能力
3. 训练环境尽可能贴近部署环境（minimize train-test mismatch）
4. Self-summarization 处理长程任务
5. 非线性长度惩罚平衡简单/复杂任务的效率

## 代表性工具/产品

- Cursor (Composer 系列)
- Claude Code (Anthropic)
- GitHub Copilot
- Codex (OpenAI)

## 关联

- 代表模型: [[composer2]]
- 评测框架: [[cursorbench]]
- RL 训练: [[ppo]], [[grpo-rl-training]]
