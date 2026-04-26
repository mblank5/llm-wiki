---
title: "OPSDL: On-Policy Self-Distillation for Long-Context Language Models"
created: 2026-04-26
updated: 2026-04-26
type: concept
tags: [distillation, on-policy, rl, fine-tuning, training]
sources: [raw/papers/2026/04/2604.17535.md]
---
# OPSDL: On-Policy Self-Distillation for Long-Context Language Models

将 OPD 扩展到 long-context 场景，通过自蒸馏扩展 LLM 有效上下文长度。

## 定义

OPSDL 应用 on-policy self-distillation 技术来扩展语言模型的有效上下文窗口，解决长上下文理解和生成中的退化问题。

## 核心方法

### Long-Context OPD 扩展
- 标准 OPD 主要针对短序列推理任务
- OPSDL 将 OPD 的 student-rollout + teacher-feedback 范式应用到**长上下文序列**
- 通过自蒸馏（self-distillation），模型学习在长序列上保持推理一致性

### 上下文长度扩展机制
- 在长上下文中进行 on-policy rollout
- Teacher（同一模型的不同 checkpoint 或增强版本）提供 token 级别反馈
- 逐步扩展模型能可靠处理的上下文长度

### 与 OPD 的关联
- 延续了 OPD 的 on-policy 训练范式
- 自蒸馏场景下 [[on-policy-self-distillation]] 的长上下文变体
- 与 [[rethinking-opd]] 中讨论的思考模式兼容性相关

## 实验结果
- OPSDL 有效扩展了模型的可用上下文长度
- 在长上下文基准上显著优于标准 SFT

## 开放问题
- 自蒸馏在 long-context 下的梯度稳定性如何保障？
- 上下文扩展是否存在理论上限？
- 与 RoPE scaling、ALiBi 等位置编码方法的兼容性？

## Related
- [[on-policy-self-distillation]]
- [[on-policy-distillation]]
- [[reasoning-distillation]]
