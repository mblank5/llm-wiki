---
title: On-Policy Distillation for Autonomous Vehicle Motion Planning
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [on-policy-distillation, autonomous-driving, gkd, distillation]
sources: [raw/papers/2026/04/2604.07944.md]
---

# On-Policy Distillation 在自动驾驶运动规划中的应用

## 背景

GPT-Driver 框架将驾驶场景表示为语言 prompt，用 CoT 生成 waypoint 轨迹。
部署大 LLM 到车载系统受资源限制，需要蒸馏到小模型。

## 方法对比

1. **On-policy GKD**: Student 在自身输出上训练，用 teacher 的 dense token-level feedback
2. **Dense-feedback RL baseline**: Teacher 的 log-probabilities 作为 per-token reward

## 关键结论

- GKD **大幅超越** RL baseline，接近 teacher 性能（5x 模型压缩）
- 证明了 on-policy distillation 在具身智能场景的有效性
- Dense token-level KL 反馈优于 scalar reward signal

## 与 Wiki 的关联

这是 [[on-policy-distillation]] 在具身智能领域的 **直接应用案例**，
与 [[qwen3-omni]] Thinker 的 on-policy distillation pipeline 理念一致。

## Related

- [[on-policy-distillation]]
- [[llm-post-training-unified-view]]
- [[knowledge-distillation]]
