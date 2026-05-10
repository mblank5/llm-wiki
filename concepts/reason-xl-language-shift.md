---
title: 'ReasonXL: Shifting LLM Reasoning Language Without Sacrificing Performance'
created: 2026-05-01
updated: 2026-05-01
type: concept
tags:
- reasoning
- multilingual
- training
sources:
- raw/papers/2026/04/2604.12378.md
---

# ReasonXL: 在不牺牲性能的前提下转移 LLM 推理语言

**概要**: ReasonXL 提出了一套系统化方案，通过大规模多语言平行推理语料库和 SFT+RLVR 两阶段后训练流水线，将 LLM 的推理语言从英语转移到目标语言（德/法/意/西），同时保持甚至提升任务性能。该工作还通过权重和激活层面分析揭示了模型内部语言编码的机理。

## Overview

当前大语言模型虽然具备多语言能力，但推理过程（chain-of-thought）几乎默认使用英语，即使输入是非英语问题。这种英语中心化行为不仅降低非英语用户的理解和信任，还伴随英语相比其他语言的一致性更高准确率。ReasonXL 旨在直接弥合这一差距。

## Key Contributions

1. **ReasonXL 语料库**: 首个大规模五语言（英/德/法/意/西）平行跨域推理语料，每语言超过 200 万对齐样本（约 9B tokens），包含 prompt、推理轨迹和最终输出。数据来源覆盖 10 个现有数据集，经过多阶段质量过滤和类别平衡采样。语料持续扩展中，目标达到每语言 20-30B tokens。

2. **两阶段后训练流水线**:
   - **Stage 1 — SFT**: 使用 completion-only loss 在目标语言推理数据上微调，将推理语言从英语转向目标语言。基于 SmolLM3-3B。
   - **Stage 2 — RLVR (Dr. GRPO)**: 从 SFT checkpoint 出发，使用 20K 可验证 prompt 进行强化学习，恢复 SFT 阶段损失的推理质量。奖励函数包含准确度(w=1.0)、语言合规(w=0.1)、格式(w=0.2)、重复惩罚(w=0.3)等分量。

3. **表征分析**:
   - 模型浅层存在激活瓶颈（activation bottleneck），因果性地决定语言身份。
   - 上层集中了适配驱动的权重和激活变化。
   - RLVR 相比 SFT 以更小的参数更新实现更大的行为分歧，暗示更高效的表征重路由。

## Experimental Results

- **单语言适配**: 在四种目标语言上，SFT+RLVR 模型在科学任务（MGSM, MT-Math100, GPQA Diamond）上匹配或超过基线性能。
- **通用知识保留**: 在英语通用知识基准（MMLU, PIQA, ARC 等）上仅有最小性能损失，表明知识漂移可控。
- **跨语言迁移**: 适配后的模型在跨语言评测中保持广泛迁移能力。
- 英语语料质量验证：仅在英语 split 上 SFT 也在科学基准上取得平均提升。

## Related

- [[chain-of-thought]] — ReasonXL 的核心在于控制推理轨迹（CoT）的输出语言
- [[reasoning-distillation]] — 与推理能力蒸馏/迁移方法互补
- [[rl-post-training-scaling-laws]] — RLVR 作为后训练 RL 的具体实例，展示了小权重更新也能实现显著行为变化
