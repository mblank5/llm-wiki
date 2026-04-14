---
title: "Qwen3 中的 On-Policy Distillation 做法"
created: 2026-04-06
updated: 2026-04-12
type: query
tags: [on-policy-distillation, distillation]
sources: [raw/papers/2025/05/2505.09388.md]
---

# Research - qwen3里面的on policy di

**Question:** qwen3里面的on policy distillation有用到吗？用到的话具体是什么做法

## Qwen3 中的 On-Policy Distillation：有，且是关键环节

**是的，Qwen3 明确用到了 On-Policy Distillation（OPD）。** 具体体现在其 **Post-training 阶段的 Strong-to-Weak Distillation** 策略中，用于高效训练小模型。

### 具体做法（来自 §4 Post-training）

1.  **核心思想：** 用旗舰大模型（如 Qwen3-235B-A22B）作为教师，通过 **on-policy 采样** 生成数据，再蒸馏到小模型（Student）。
    > *"For smaller models, we use strong-to-weak distillation, leveraging both **off-policy and on-policy** knowledge transfer from larger models to enhance their capabilities."* [src: raw/papers/2505.09388.md]

2.  **On-Policy 部分的关键优势：**
    > *"Preliminary experiments suggest that directly distilling the output **logits** from teacher models into lightweight student models can effectively enhance their performance while maintaining fine-grained control over their reasoning processes."* [src: raw/papers/2505.09388.md]

    - 不是用教师模型过去的旧数据（off-policy），而是让教师模型 **实时根据当前 Student 的 prompt 分布采样生成**（on-policy），然后取 **logits（而非仅最终答案）** 做 KL 散度蒸馏。
    - 这保证了蒸馏数据与 Student 当前能力匹配，避免分布偏移。

3.  **效果：**
    > *"This approach eliminates the necessity of performing an exhaustive four-stage training process individually for every small-scale model... requiring only **1/10 of the GPU hours** compared to the four-stage training method."* [src: raw/papers/2505.09388.md]
    - 同时提升 Pass@1（直接性能）和 Pass@64（探索能力）。

### 与纯 Off-Policy 的区别

| 维度 | Off-Policy Distillation | On-Policy Distillation (Qwen3) |
|------|------------------------|-------------------------------|
| 数据来源 | 教师模型历史生成数据 | 教师模型实时按 Student prompt 采样 |
| 蒸馏目标 | 通常只蒸馏最终答案 | 蒸馏 **logits**（概率分布） |
| 分布匹配 | 可能偏移 | ✅ 严格匹配 Student 当前策略 |
| 计算成本 | 低（数据可缓存） | 稍高（需实时采样），但总训练成本降 90% |

### 补充：与 Qwen3 整体流程的关系

```
[Flagship Model 4-stage RL] 
        ↓ (on-policy logits distillation)
[Small Model: 跳过4阶段，直接蒸馏获得 reasoning + chat 能力]
```

> ⚠️ 注意：Qwen3 技术报告未公开 OPD 的具体超参（如 KL 权重、采样温度），也未说明是否用了 PPD（Proximal Policy Distillation）的 per-token KL clipping 等技术。如需细节，可参考 Wiki 中的 [2407.15134 PPD] 和 [2604.00626 OPD Survey]。