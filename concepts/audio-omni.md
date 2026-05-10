---
title: "Audio-Omni: 统一音频理解+生成+编辑"
created: 2026-04-15
updated: 2026-04-16
type: concept
tags: [omni, audio, generation, editing, understanding, diffusion, rectified-flow]
sources: [raw/papers/2026/04/2604.10708.md]
---

# Audio-Omni

## 核心贡献

首个端到端统一 **音频理解 + 生成 + 编辑** 的框架，覆盖通用声音、音乐、语音三大领域。

团队：HKUST + Tencent WeChat Vision（2026-04-12，代码/模型/数据集开源）。

## 架构：解耦双流设计

```
输入 (text/audio/video)
       │
  ┌────┴────┐
  │ Frozen  │ ← Qwen2.5-Omni-3B（不训练）
  │  MLLM   │
  └────┬────┘
       │ penultimate layer hidden states (F_mm)
       │
  ┌────┴────────────────────────────────────┐
  │        High-Level Semantic Stream        │
  │   F_mm ⊕ F_trans (character-level)      │ ← 指令/语义信号
  ├─────────────────────────────────────────┤
  │        Low-Level Signal Stream           │
  │   F_sync (Synchformer) ⊕ F_mel (Mel)   │ ← 时间对齐/参考信号
  └────┬────────────────────────────────────┘
       │
  ┌────┴────┐
  │  DiT    │ ← Rectified Flow 训练（36 blocks, 2048 dim, 32 heads）
  │ 3.05B   │
  └────┬────┘
       │
  ┌────┴────┐
  │  VAE    │ ← 预训练音频编解码器 (44.1kHz)
  └─────────┘
```

### 关键设计决策

1. **Frozen MLLM**: 用 Qwen2.5-Omni-3B 的 penultimate layer（倒数第二层）提取语义特征
   - 实验发现 penultimate layer 比 final layer 更适合做生成条件（Sec 5.4 消融）
   - 因为 final layer 过度针对文本生成优化，penultimate 保留了更丰富的多模态语义

2. **双流条件注入**:
   - High-level stream: 全局语义指导（理解→生成的桥梁）
   - Low-level stream: 时间对齐参考（编辑/同步/语音克隆的锚点）

3. **Rectified Flow**: 不用传统扩散的随机路径，而是建模噪声→数据的直线 ODE
   - 训练更稳定，推理步数更少

### 与 Qwen3-Omni 架构对比

| 维度 | Qwen3-Omni | Audio-Omni |
|------|-----------|------------|
| 总参数 | ~30B (MoE) | 7.9B (3.05B 可训) |
| LLM | Qwen3 (frozen) | Qwen2.5-Omni-3B (frozen) |
| 生成器 | Multi-codebook AR + ConvNet | DiT + Rectified Flow |
| 生成方式 | 帧级自回归（token-by-token） | 整体合成（ODE 求解） |
| 流式能力 | 是（234ms 首包延迟） | 否（需完整 ODE 求解） |
| 编辑能力 | 无 | 原生支持 |
| 适用场景 | 实时交互 | 创作/编辑工具 |

**本质区别**: Qwen3-Omni 是"边想边说"的实时模型，Audio-Omni 是"想清楚再做"的创作工具。两条路线短期内不会互相替代。

## AudioEdit 数据集

100 万+ 编辑对，混合构建：
- **Real Data Branch**: 从 VGGSound 等真实数据中挖掘编辑对（Gemini 做分类 → SAM-Audio 做分离）
- **Synthesis Branch**: Scaper 工具程序化生成精确标注的编辑场景

## 实验结果

### 生成 benchmarks（Table 3）

| 任务 | Audio-Omni | 次佳统一模型 | 专项 SOTA |
|------|-----------|-------------|----------|
| T2A FAD | **1.86** | Unified-IO2: 7.81 | AudioX: 1.86 |
| T2M FAD | 1.94 | MuMuLLaMA: 5.89 | AudioX: **1.53** |
| V2A FAD | **1.71** | MMAudio: 2.04 | AudioX: 1.13 |
| V2M FAD | **1.58** | MuMuLLaMA: 52.25 | VidMuse: 2.46 |
| TTS WER | **1.77** | Ming-Omni: 4.31 | F5-TTS: 1.83 |

### 编辑 benchmarks（Table 4）

| 指标 | Audio-Omni | 专项 SOTA (ZETA) |
|------|-----------|-----------------|
| AE_FAD | 3.27 | 3.51 (SDEdit) |
| AE_LSD | **2.27** | 3.80 (ZETA) |
| CLAP | **0.32** | 0.30 (ZETA) |

**关键**: 在统一模型中大幅领先，在 LSD 和 CLAP 上甚至超过专项模型。

## 继承能力（Emergent Capabilities）

来自 frozen MLLM 的零样本能力迁移：
1. **Knowledge-augmented reasoning generation**: 用世界知识指导音频生成（如"暴风雨中的猫叫声"）
2. **In-context generation**: few-shot 音频生成
3. **Zero-shot cross-lingual control**: 中文指令生成英文语音，无需跨语言训练数据

## 开放问题

- 延迟高（需完整 ODE 求解），不适合实时交互
- 生成器和理解模块完全解耦，没有联合优化的增益
- Rectified Flow 的步数-质量 trade-off 没有深入分析

## Related

- [[qwen3-omni]] — 互补路线：实时交互 vs 创作编辑
- [[omni-modal-llm]] — Omni 模型总览
- [[qwen3-tts]] — 语音生成专项对比
- [[audio-omni]] — 本页
