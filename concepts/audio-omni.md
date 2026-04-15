---
title: Audio-Omni: 统一音频理解+生成+编辑
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [omni, audio, generation, editing, understanding, diffusion]
sources: [raw/papers/2026/04/2604.10708.md]
---
# Audio-Omni

## 核心贡献
首个端到端统一 **音频理解 + 生成 + 编辑** 的框架，覆盖通用声音、音乐、语音三大领域。

## 架构
- **Frozen MLLM**: 高层语义推理（不训练）
- **DiT (Diffusion Transformer)**: 高保真音频合成（可训练）
- 解耦设计：推理和生成分开优化

## AudioEdit 数据集
- 超过 **100 万** 精心策划的编辑对
- 解决音频编辑领域的数据稀缺问题

## 继承能力
- Knowledge-augmented reasoning generation
- In-context generation
- Zero-shot cross-lingual control

## 与 Wiki 的关联
- [[qwen3-omni]] 侧重理解+交互，Audio-Omni 侧重生成+编辑
- 两者互补，代表 omni 模型的两个方向
- DiT vs MTP+ConvNet 是不同的音频合成路线

## Related
- [[qwen3-omni]]
- [[omni-modal-llm]]
- [[qwen3-tts]]
