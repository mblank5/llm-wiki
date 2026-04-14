---
title: OmniJigsaw
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [omni-modal, rl, post-training, self-supervised, video, audio]
sources: [raw/papers/2026/04/2604.08209.md]
---

# OmniJigsaw: 全模态推理增强

## 核心思路

将 RL 后训练范式扩展到全模态模型，用 **时间重排** (temporal reordering) 作为自监督代理任务。

## 三种模态编排策略

1. **Joint Modality Integration**: 同时使用音频+视觉
2. **Sample-level Modality Selection**: 样本级选择使用哪个模态
3. **Clip-level Modality Masking**: 片段级随机遮蔽某个模态

### 关键发现：Bi-modal Shortcut

Joint integration 存在 "双模态捷径"——模型只用一个模态就能完成排序。
**Clip-level Modality Masking** 最有效，强制模型真正整合两个模态。

## 数据处理

两阶段 coarse-to-fine filtering pipeline：
1. 粗筛：去除视觉动态不足、音频质量差的视频
2. 精筛：保留时间因果结构清晰的内容

## 结果

基于 **Qwen3-Omni-30B-A3B** 训练，15 个 benchmark：
- AoTBench: +4.02%
- MLVU-Test: +4.38%
- 视频/音频/协作推理全面提升

## 意义

- 直接在 Qwen3-Omni 上验证了 RL 后训练的有效性
- 自监督 + RL 的组合是 omni-modal 领域的新范式
- 与 [[qwen3-omni]] 的 GSPO post-training 互补

## Related

- [[qwen3-omni]]
- [[omni-modal-llm]]
- [[grpo-rl-training]]
- [[g2rpo]]
