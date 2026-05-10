---
title: "DuplexCascade"
created: 2026-04-10
updated: 2026-04-10
type: concept
tags: [concept, full-duplex, speech-model, cascaded, streaming, architecture]
sources: [raw/papers/2026/03/2603.09180.md]
---

# DuplexCascade — VAD-Free 级联全双工语音对话

## 定义

DuplexCascade 是一种**无需 VAD 的级联流式流水线**，用于全双工语音到语音对话。其核心创新是将传统的整句轮次（utterance-wise long turns）转换为**分块微轮次（chunk-wise micro-turns）**交互，并通过精心设计的对话控制特殊 token 来引导 LLM 在流式约束下的行为，从而在保留文本 LLM 强大推理能力的同时实现全双工交互。

- **论文**: "DuplexCascade: Full-Duplex Speech-to-Speech Dialogue with VAD-Free Cascaded ASR–LLM–TTS Pipeline and Micro-Turn Optimization" (arXiv: 2603.09180, 2026)
- **作者**: Jianing, Yusuke, Yui, SB Intuitions Corp. / The University of Tokyo
- **Demo**: https://sbintuitions.github.io/DuplexCascadeDemo

## 背景与动机

### 级联系统的 VAD 瓶颈

传统级联系统（ASR → LLM → TTS）依赖外部 VAD 来决定用户轮次边界，导致：

- 强制半双工"先听后说"模式
- 在暂停、重叠、噪音下轮次控制脆弱
- 无法处理打断、附和等复杂交互

### E2E 系统的智能退化

端到端全双工模型（如 Moshi）虽能实现真正的全双工交互，但因跨模态表征学习困难，对话智能通常不及文本 LLM。

DuplexCascade 的目标：**兼具全双工交互能力和文本 LLM 的推理智能**。

## 核心架构

### 整体流水线

```
用户音频 → 流式 ASR → 每 Δt=0.6s 聚合为微轮次 → LLM → 流式 TTS → 系统音频
```

不依赖 VAD，而是通过流式 ASR 的部分文本输出，以固定时间间隔聚合为"微轮次"发送给 LLM。

### 对话控制特殊 Token

**用户侧**：
- `<no voice>`：当前 Δt 间隔无语音（用户静默）

**系统侧**：
- `<user is speaking>`：用户仍在说话，系统保持静默
- `<user finish speaking>`：用户说完，系统开始回复
- `<user is interrupting>`：用户打断，系统停止生成
- `<user backchannel>`：用户附和，系统忽略并继续
- `<user is thinking>`：用户沉默后思考中，系统等待
- `<system backchannel>`：系统发出附和（播放预合成音频片段）

### 训练数据动态构建

从 UltraChat 随机采样 50k 文本对话，动态模拟 6 种交互现象：

1. **随机微轮次长度**：用户微轮次 1-7 token（模拟 ASR 变化），系统固定 10 token
2. **自然暂停**：10% 概率插入 1-5 个静默微轮次
3. **用户打断**：30% 概率在系统回复中模拟打断
4. **用户附和**：1% 概率在系统说话时插入用户附和
5. **系统附和**：用 Qwen2-72B-Instruct 后处理插入 `<BC/>` 标记
6. **用户思考**：随机插入 1-20 个静默微轮次

### 训练策略

- **LoRA 微调**（rank=16, α=32），仅 5k 步，8×H100 训练 5 小时
- 仅在系统微轮次上做 next-token prediction
- 加权损失处理特殊 token 类别不平衡
- **文本-only 适配**：避免跨模态对齐问题，保留 LLM 智能能力

## 关键结果

### Full-Duplex-Bench

| 模型 | 平均轮次准确率 |
|------|-------------|
| dGSLM | 0.466 |
| Moshi | 0.395 |
| Freeze-Omni | 0.489 |
| PersonaPlex | 0.759 |
| Gemini Live | 0.778 |
| **DuplexCascade** | **0.858** |

DuplexCascade 在开源系统中取得最佳平均轮次管理准确率。

### VoiceBench（对话智能）

| 模型 | Overall |
|------|---------|
| Moshi | 29.51 |
| Freeze-Omni | 55.20 |
| PersonaPlex | 30.59 |
| DuplexCascade | 65.41 |
| DSM-ASR+Qwen2-7B | 69.66 |

DuplexCascade 在几乎所有维度上大幅超越之前的双工模型，且与无适配的基线管线差距很小，证明文本-only LoRA 适配有效保留了 LLM 能力。

### 微轮次 Δt 分析

- Δt=1.2s 轮次准确率最高，但延迟增大
- Δt=0.6s 为实用平衡点

## 设计理念与意义

1. **VAD-free 通过 LLM token 控制实现**：将轮次决策从外部 VAD 转移到 LLM 的特殊 token 输出，更加可控
2. **微轮次降低粒度**：将传统整句交互压缩为 0.6s 级别的快速双向交换
3. **极低成本训练**：仅 50k 文本对话 + 5k 步 LoRA，8 卡 5 小时
4. **级联系统的全双工化路径**：证明了不牺牲 LLM 能力也能实现全双工

## 局限性

- 延迟相对较高（Smooth Turn-Taking Latency 1.724s vs Moshi 0.265s）
- 依赖合成训练数据
- 系统附和需预合成音频片段

## 相关页面

- [[full-duplex-speech-model]] — 全双工语音模型总览
- [[moshi]] — Moshi 全双工语音对话模型
- [[freeze-omni]] — Freeze-Omni 冻结 LLM 方案
- [[speech-llm]] — 语音大语言模型
- [[mtr-duplexbench]] — MTR-DuplexBench 多轮评测
- [[turnguide]] — TurnGuide 文本引导全双工方法
