---
title: "Self-Distillation Zero: Self-Revision Turns Binary Rewards into Dense Supervision"
created: 2026-04-26
updated: 2026-04-26
type: concept
tags: [distillation, on-policy, rl, fine-tuning]
sources: [raw/papers/2026/04/2604.12002.md]
---
# Self-Distillation Zero: Self-Revision Turns Binary Rewards into Dense Supervision

通过自修订（self-revision）机制将 binary rewards 转化为 dense supervision，提供对比 RLVR 与 self-distillation 的视角。

## 定义

Self-Distillation Zero 提出利用模型的**自修订能力**将稀疏的 binary reward 信号转化为密集的 token 级监督，无需外部 teacher 即可实现类似 OPD 的密集学习效果。

## 核心方法

### 自修订机制
- 模型生成初始回答后，对自身回答进行**修订**（self-revision）
- 修订过程产生 intermediate steps，为每个 token 提供学习信号
- Binary reward（正确/错误）通过修订轨迹被**分解为 dense supervision**

### RLVR vs Self-Distillation 对比
- **RLVR**：sparse binary rewards，仅知道最终答案对错
- **Self-Distillation**：dense signals，修订过程提供中间步骤的监督
- 核心差异：signal granularity（信号粒度）

### 零外部依赖
- 不需要外部 teacher 模型
- 模型自我监督，类似 [[on-policy-self-distillation]] 的思路
- 与 [[self-distilled-rlvr]] 共享核心思想但实现路径不同

## 实验结果
- Self-revision 在推理任务上产生比 binary-only 更丰富的 learning signal
- 在不需要外部 teacher 的情况下接近 OPD 的效果
- 验证了 self-revision 作为 dense signal 来源的有效性

## 开放问题
- 自修订的可靠性如何保证（模型能否正确识别自己的错误）？
- 与外部 teacher 提供的信号相比，质量差距有多大？
- 在不同领域（数学、代码、开放生成）上的泛化性？

## Related
- [[on-policy-self-distillation]]
- [[reasoning-distillation]]
- [[self-distilled-rlvr]]
