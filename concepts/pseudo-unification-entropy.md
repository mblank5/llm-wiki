---
title: Pseudo-Unification: 熵探测揭示多模态模型信息分歧
created: 2026-04-15
updated: 2026-04-16
type: concept
tags: [multimodal, entropy, unification, information-theory, renyi-entropy, rkhs]
sources: [raw/papers/2026/04/2604.10949.md]
---

# Pseudo-Unification: 表面统一的多模态模型真相

## 核心发现

表面上"统一"的多模态模型（UMMs），在信息论视角下存在 **双重分歧 (dual divergence)**：
1. **Modality-Asymmetric Encoding**: 视觉和语言在编码阶段走不同的熵轨迹
2. **Pattern-Split Response**: 文本生成追求高熵创造力，图像生成追求低熵保真度

作者将此现象称为 **Pseudo-Unification（伪统一）**——参数共享 ≠ 信息流统一。

团队：MMLab@HKUST（2026-04-13）。

## 方法：基于 RKHS 的熵探测框架

传统信息论分析需要显式概率密度，但 Transformer 不提供这个。作者用 **matrix-based Rényi entropy** 绕过：

### 核心工具

1. **Matrix-based Rényi Entropy**: 在 Reproducing Kernel Hilbert Space (RKHS) 中直接从 embedding 矩阵计算熵
   - 非参数、核方法
   - 可直接比较不同模态的 embedding 结构
   - 高熵 = 各向同性、信息丰富；低熵 = 高度压缩、结构化

2. **Conditional Entropy Proxy**: 衡量 response 相对于 prompt 引入的额外结构复杂度
   - H(Z_response | Z_prompt) 低 → fidelity-driven（保真，复制/确定性生成）
   - H(Z_response | Z_prompt) 高 → creativity-driven（创造，多样性生成）

### 两级探测

- **Prompt-level**: 输入编码阶段，视觉 vs 语言 token 的熵轨迹差异
- **Layer-wise**: 逐层追踪信息压缩模式，揭示架构先验的影响

## 十个 UMM 的探测结果

### 发现 1: 编码阶段的模态不对称

| 模式 | 描述 | 代表模型 |
|------|------|---------|
| 视觉早压缩 | 大模型对视觉 token 早期就大幅压缩 | Janus-Pro-7B, EMU3-Chat |
| 语言持续保持 | 语言 token 保持高熵到更深层 | 同上 |
| 对称压缩 | 视觉和语言压缩模式相似 | 较小模型 |

**原因**: 架构先验（model size + prompt length）主导编码模式，而非 prompt 内容或任务复杂度。
大模型因为 capacity 充裕，倾向于对视觉输入"过早定性"。

### 发现 2: 生成阶段的模式分裂

| 模态 | 熵模式 | 行为特征 |
|------|--------|---------|
| 文本生成 | 高条件熵 | 创造性、多样性、推理链 |
| 图像生成 | 低条件熵 | 保真性、确定性、复制参考 |

这意味着模型在生成文本时"自由发挥"，生成图像时"严格还原"——两个模态走的是完全不同的生成范式。

### 发现 3: 真正的统一需要什么？

只有 **Harmon** 模型（通过 contextual prediction 统一编码和生成）实现了跨模态的一致信息流。
其他所有模型（包括 Janus-Pro, EMU3, Show-o 等）都存在不同程度的伪统一。

**关键**: 真正的统一不在于参数共享或任务性能，而在于 **信息流的一致性**。

## 对 Qwen3-Omni "无退化" 声明的影响

Qwen3-Omni 在 Table 16 报告了加音频数据后文本/视觉性能不降反升。Pseudo-Unification 的发现提出了尖锐问题：

1. **性能不降 ≠ 真正统一**: 信息流可能仍然分裂，只是各自都没退化
2. **"无退化" 测的是任务指标，不是信息一致性**: 熵探测可能揭示隐藏的模态冲突
3. **需要验证的假设**: Qwen3-Omni 的 Thinker-Talker 解耦是否也引入了 pattern-split？

这值得用本文的熵探测框架在 Qwen3-Omni 上做一次分析。

## 方法论贡献

- 首个 model-internal probing of unification（不是外部 benchmark 评测）
- Rényi entropy + conditional entropy proxy 是通用的多模态分析工具
- 可用于未来任何 UMM 的统一性诊断

## 更广泛的启示

- **Scaling 不是解决统一的答案**: 大模型反而更容易出现 modality-asymmetric encoding
- **训练目标需要重新设计**: 只有共享编码和生成逻辑的框架（如 contextual prediction）才能实现真统一
- **评测需要信息论维度**: 传统 benchmark 只看任务性能，看不到信息流分裂

## Related

- [[llm-training-as-lossy-compression]] — 信息论分析扩展到多模态
- [[qwen3-omni]] — "无退化"声明需要信息论验证
- [[omni-modal-llm]] — Omni 模型统一架构的挑战
- [[omnijigsaw]] — 自监督+RL 能否缓解信息流分裂？
- [[audio-omni]] — 解耦架构是否也受 pseudo-unification 影响？
