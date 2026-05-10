---
title: "MemoryLLM: 自更新大语言模型的潜在空间记忆"
created: 2026-04-17
updated: 2026-04-17
type: concept
tags: [model, architecture, memory, long-term, training]
sources: [raw/papers/2024/02/2402.04624.md]
---

# MemoryLLM: 潜在空间自更新记忆池

## 核心问题

部署后的 LLM 参数静态不变，无法高效注入新知识。现有方案（RAG、model editing、长上下文）各有局限：
RAG 存在冗余和存储膨胀，model editing 仅限单句级事实，长上下文方法受限于有限窗口。

MemoryLLM 在 transformer 潜在空间内嵌入**固定大小记忆池**，使模型能自更新地吸收新知识。

## 方法

### 模型结构 $\mathcal{M}_{\theta,\phi}$

- $\phi$: 静态 transformer 参数（基于 Llama2-7B）
- $\theta$: 动态记忆池，1B 参数，分布在每层 transformer 中
- 每层记忆池 $\theta_l \in \mathbb{R}^{N \times d}$，$N$ 个 memory token

### 自更新过程

注入新知识 $x$ 时：

1. 取 $\theta_l$ 末尾 $K$ 个 memory token 与新文本隐状态拼接
2. 通过 transformer 层 $\phi_l$ 处理，输出新 $K$ 个 memory token
3. 随机丢弃 $\theta_l$ 中 $K$ 个旧 token，追加新 token

$$\theta' = U(\theta, x)$$

**遗忘保证**: 旧知识以指数衰减率逐渐被替换，理论可证明。

### 生成过程

所有 memory token 通过 cross-attention 被当前输入访问：
- 注意力矩阵 $n_x \times (n_x + N)$，线性复杂度

### 训练策略

三阶段课程：
1. **新知识注入**: 学习将新信息压缩到记忆池
2. **连续上下文理解**: 增强长上下文建模
3. **遗忘缓解**: 对抗记忆更新导致的性能退化

## 结果

- **Model Editing**: 显著优于 ROME、MEMIT 等基线
- **Long Context**: 在 16k token 范围内有效保持知识
- **鲁棒性**: 近百万次更新后无性能退化
- **局限**: 超过 20k token 后知识保持能力急剧下降

## 意义

- **潜在空间记忆**: 首次在 transformer 每层嵌入可更新记忆池，开辟 latent-space memory 方向
- **固定大小设计**: 避免外部存储无限膨胀，但容量有限
- **后继工作**: 直接催生 [[m-plus-memoryllm]]，通过引入长期记忆扩展保持范围至 160k+ token
- **区别于外部记忆**: 与 [[memgpt]]、[[mem0]] 等外部存储方案不同，MemoryLLM 将记忆嵌入模型参数内部

## Related

- [[m-plus-memoryllm]] — 扩展长期记忆版本
- [[agent-memory-system]] — Agent 记忆系统总览
- [[memgpt]] — 外部层次化记忆先驱
- [[mem0]] — 外部文本级记忆方案
