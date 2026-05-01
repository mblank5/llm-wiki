---
title: DiffRO
created: 2026-05-01
updated: 2026-05-01
type: concept
tags: [speech-model, rl, optimization]
sources: [raw/papers/2025/07/2507.05911.md]
---

# DiffRO (Differentiable Reward Optimization)

DiffRO 是阿里通义语音团队于 2025 年 7 月提出的一种针对**基于神经 codec LLM 的 TTS 系统**的新型后训练方法。全称 **Differentiable Reward Optimization**，核心创新是**直接在 codec token 上计算奖励并使奖励函数完全可微**，从而绕过传统 RLHF 中昂贵的波形生成步骤。

论文：arXiv 2507.05911

## 问题背景

传统 RLHF 应用于 TTS 系统面临三大挑战：

1. **计算成本极高**：TTS 系统需要额外的 Flow Matching (FM) 和 vocoder 模型将离散 codec token 转换为波形音频。每次奖励评估都需要完整的后处理流水线，导致大规模 RLHF 数据生成极其昂贵。

2. **样本多样性不足**：虽然 codec LLM 可以用不同采样策略和随机种子从同一文本生成不同 token 序列，但经过 FM + vocoder 后的音频高度相似，难以区分正负样本以训练 reward model。

3. **评估维度复杂**：TTS 质量需要从发音准确度、韵律自然度、说话人相似度、情感表达等多个维度评估。简单的好/坏二元分类不够充分。

## 现有方法的局限

| 方法 | 问题 |
|------|------|
| **PPO** | 需要 FM + vocoder 生成波形 → 计算成本巨大；reward model 需要大量正负样本对 |
| **DPO** | 简化为单阶段但仍需构造偏好/非偏好数据集；音频高度相似导致样本对区分困难；二元分类无法覆盖多维度质量 |
| **UNO** (Chen et al.) | 使用非配对正负样本缓解多样性问题，但仍需波形生成 |
| **RIO** (Chen et al.) | 通过反转 prompt 生成额外正样本，但仍是 token-level 间接方案 |
| **ASR/SER-based RL** | 用 ASR WER 或 SER 准确率作为奖励，但仍有波形生成瓶颈 |

## DiffRO 核心方法

### Token2Reward 预测

DiffRO 直接在 codec token 上预测奖励，而非合成后的音频：

1. **训练 Token2Text 模型**：在 ASR 训练数据上训练一个类似 ASR 的 Token2Text 模型，该模型从 codec token 序列预测文本 token 的后验概率。

2. **奖励定义**：使用 Token2Text 模型对输入文本 Y 的后验概率作为奖励：

```
R_ASR(Y) = log P_ASR(Ỹₙ = Yₙ | Y₁:ₙ₋₁; Ũ₁:ₜ)
```

即：ASR 模型从采样 token 序列 Ũ 中正确预测目标文本 Y 的概率的对数。

3. **Gumbel-Softmax 采样**：用 Gumbel-Softmax 替代 argmax 来采样 LLM 预测的 token，使整个奖励函数关于 TTS 系统的输入文本可微：

```
Ũₜ = GumbelSoftmax(P_πθ(μₜ | μ₁:ₜ₋₁; Y))
```

4. **直接反向传播优化**：由于奖励函数完全可微，可以直接通过反向传播优化 LLM 以最大化奖励分数，**无需 PPO 或 DPO 训练循环**：

```
π*θ = max_πθ E[R(Y)] - β · D_KL[πθ(μ|Y) || π_ref(μ|Y)]
```

其中 KL 散度在**输出 token-level logit**上计算，而非序列级后验概率。

### 多任务奖励模型 (MTR)

除了 ASR 奖励，DiffRO 还可以结合多个下游任务，确保预测的 token 序列包含所有必要信息：

1. **训练 codec-based 语音理解模型**：用多任务训练方法，使模型能够执行 SER（情感识别）、SQA（语音质量评估）、AED（音频事件检测）等任务。

2. **MTR 奖励函数**：

```
R_MTR(Y, {Aᵢ}) = Σᵢ log P_taskᵢ(Ãᵢ = Aᵢ | Ũ)
```

其中 {Aᵢ} 是要控制的音频属性（如情感类别、质量等级等）。

3. **零样本属性控制**：通过最大化 MTR 模型预测的后验概率，可以使 TTS 系统按照预设偏好或输入指令生成具有特定情感/质量属性的音频。

## 与 DPO 的对比

| 维度 | DPO | DiffRO |
|------|-----|--------|
| 奖励来源 | 波形音频 (FM + vocoder) | **Codec token 直接预测** |
| 可微性 | 不可微，需 RL 循环 | **完全可微 (Gumbel-Softmax)** |
| 优化方式 | PPO / DPO 偏好优化 | **直接反向传播** |
| 样本需求 | 需要大量正负样本对 | **不需要配对样本** |
| 计算成本 | 高 (每次需 vocoder) | **低 (无需 vocoder)** |
| 反馈维度 | 二元 (好/坏) | **多维度 (ASR + SER + SQA + AED)** |
| 信号密度 | 序列级标量 | **token-level 密集梯度** |

## 实验结果

- 在 **SEED-TTS-Eval** benchmark 上达到 SOTA WER 结果
- 显著改善 TTS 系统的**发音准确度**
- 集成 MTR 后实现**零样本情感和属性控制**
- 已应用于 [[cosyvoice-3]] 的后训练阶段

## 关键设计选择

1. **Token-level vs 波形-level**：codec token 携带文本的所有信息，无需经过 FM + vocoder 即可获得足够的奖励信号。

2. **Gumbel-Softmax vs argmax**：argmax 不可微，Gumbel-Softmax 提供可微的软采样，温度参数控制采样锐度。

3. **Token-level KL vs 序列级 KL**：在输出 token 的 logit 上计算 KL 散度，提供更精细的逐 token 正则化，防止模型偏离参考模型过远。

4. **多任务奖励**：单一 ASR 奖励只关注发音准确度，MTR 提供情感、质量、事件等多维度反馈，使 TTS 能响应复杂指令。

## 适用范围

DiffRO 不仅适用于 CosyVoice 系列，还可推广到其他**基于离散 token 的语音合成模型**，包括：
- 任何 neural codec LLM-based TTS 系统
- 需要 RLHF/后训练的语音生成模型
- 需要多维度可控性的语音合成场景

## 相关页面

- [[cosyvoice-3]] — CosyVoice 第三代，使用 DiffRO 进行后训练
- [[cosyvoice-2]] — CosyVoice 第二代，未使用 DiffRO
- [[fun-audio-llm]] — FunAudioLLM 团队，DiffRO 的提出者
- [[ppo]] — Proximal Policy Optimization，传统 RL 方法，DiffRO 的对比对象
- [[seed-tts]] — Seed-TTS，DiffRO 在其 eval benchmark 上测试
