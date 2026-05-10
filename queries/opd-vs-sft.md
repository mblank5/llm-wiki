---
title: "On-Policy Distillation vs SFT 的优势与指标差距"
created: 2026-04-06
updated: 2026-04-12
type: query
tags: [on-policy-distillation, distillation]
sources: [raw/papers/2026/01/2601.18734.md]
---

# on policy distillation vs sft

**Question:** on policy distillation相比sft的话有什么优势啊？指标差距多大

根据 Wiki 中 [src: raw/papers/2601.18734.md]（Self-Distilled Reasoner）的详细实验结果，**on-policy distillation（OPSD）相比 SFT 的优势和指标差距**如下：

### ✅ 核心优势（vs SFT）
| 维度 | SFT（Off-Policy） | OPSD（On-Policy Self-Distillation） |
|------|-------------------|-------------------------------------|
| **数据分布** | 固定专家轨迹，存在 exposure bias 和分布偏移 | 学生自己采样轨迹，on-policy 消除分布偏移 |
| **学习信号** | 硬标签（hard token），稀疏 | 稠密 token-level 软分布监督（full-vocabulary logit） |
| **教师模型** | 无（直接模仿） | 同一模型，利用 ground-truth 答案做 privileged teacher |
| **泛化性** | 容易 memorization，泛化弱 [chu2025sft] | 通过 rationalization 提升泛化 |
| **训练效率** | 高（单样本） | 更高（单 rollout，1024 tokens vs GRPO 的 8×16k） |

### 📊 指标差距（Qwen3 系列，Avg@12）
| Model | Base | +SFT | +OPSD | **OPSD vs SFT 提升** |
|-------|------|------|-------|---------------------|
| Qwen3-8B | 61.8 | **59.8** ⬇️ | **64.8** ✅ | **+5.0** |
| Qwen3-4B | 61.2 | **58.6** ⬇️ | **63.6** ✅ | **+5.0** |
| Qwen3-1.7B | 37.1 | **35.8** ⬇️ | **43.4** ✅ | **+7.6** 🔥 |

> ⚠️ 注意：SFT 在 OpenThoughts 数据集上反而**性能下降**（因 concise solution 导致推理长度缩短），而 OPSD 通过 rationalization 将 concise answer 转化为稠密学习信号，显著提升。

### 🔬 关键原因分析
1. **SFT 的 exposure bias**：训练时用专家轨迹，推理时用自己的输出，错误会累积。
2. **OPSD 的 dense feedback**：每个 token 都有 teacher 的 soft distribution 指导，即使最终答案错误也能学到中间推理。
3. **Per-token KL clipping**：防止 style token 主导训练（见 Table 5），聚焦 math token 学习。
4. **Token efficiency**：OPSD 100 steps × 1024 tokens vs GRPO 500 steps × 8×16k tokens，效率提升 ~64x。

### 💡 结论
> OPSD 在**所有模型尺度**上均显著优于 SFT（+5~7.6 Avg@12），且训练效率远高于 GRPO。SFT 在高质量 reasoning 数据上可能因风格迁移导致性能退化，而 OPSD 通过 self-rationalization 规避了这个问题。

## Related

- [[on-policy-self-distillation]] — OPSD 方法本体。
- [[per-token-kl-clipping]] — OPSD 中稳定 token 级 KL 的关键技巧。
- [[exposure-bias]] — SFT 相比 OPD 的核心问题之一。
