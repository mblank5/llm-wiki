---
title: TurnGuide
created: 2026-04-10
updated: 2026-04-10
type: concept
tags: [concept, full-duplex, speech-model, end-to-end, streaming, training]
sources: [raw/papers/2025/08/2508.07375.md]
---

# TurnGuide

## 定义

TurnGuide 是一种面向端到端（e2e）全双工语音语言模型（FD-SLM）的**文本-语音交织生成方法**。其核心思想是动态地将助手语音分割为对话轮次（turns），并在每个轮次内交替生成文本和语音，使 FD-SLM 在不破坏自然声学流的前提下，利用 LLM 的文本语义能力来提升对话质量。

- **论文**: "TurnGuide: Enhancing Meaningful Full Duplex Spoken Interactions via Dynamic Turn-Level Text-Speech Interleaving" (arXiv: 2508.07375, 2025)
- **作者**: Wenqian Cui, Lei Zhu, Xiaohui Li, Zhihan Guo, Haoli Bai, Lu Hou, Irwin King
- **代码**: https://github.com/dreamtheater123/TurnGuide

## 背景与动机

端到端 FD-SLM 直接从真实双通道对话数据中学习，能捕获更自然的交互模式，但其对话能力通常劣于纯文本 LLM，原因包括：

1. 语音序列过长导致信息稀释
2. 高质量语音对话训练数据稀缺

虽然文本-语音交织生成（先文本后语音）可以缓解这一问题，但在双通道音频流中插入文本 token 会破坏精确的时间对齐，影响交互流畅性。

## 核心方法

TurnGuide 包含两个关键框架：

### 1. 动态轮次分割与对齐框架

- 使用 VAD（pyannote）检测语音段，合并为语间停顿单元（IPU，阈值 0.5s）
- 使用 Whisper（medium）进行 ASR + 词级时间戳提取
- 将词组按时间对齐到 IPU，形成文本-语音对 `{(W_j, S_j)}`
- 引入容差参数（0.6s）处理时间戳不一致

### 2. 文本引导的全双工对话建模框架

基于 GLM-4-Voice backbone，实现两种交织策略：

- **通道级交织（Channel-wise Interleaving）**：将用户和助手语音 token 以 chunk（5 token/400ms）为单位交替排列，用 speaker ID 区分通道
- **文本-语音交织（Text-speech Interleaving）**：在每个助手轮次中，先插入文本 chunk（5 token），后跟对应语音 chunk，确保文本引导语音生成。使用 `<EOT>`（end of turn）和 `<EOC>`（end of chunk）标记轮次边界

## 关键发现

1. **语义质量显著提升**：TurnGuide 比基线（SCI、Moshi TS）提升超过 30%，比 Moshi 提升超过 20%（GPT-score 语义评估）
2. **文本权重越重效果越好**：text:speech loss 权重 2:1 和 3:1 优于 1:1
3. **轮次管理能力 SOTA**：在 Full-Duplex-Bench 的暂停处理、打断、平滑轮次切换等维度均达到最优
4. **最优温度设置**：轮次管理在 temperature=1.3 最优，语义质量在 0.8-1.0 最优
5. **延迟**：理论首包延迟约 1.05s（可进一步优化 vocoder）

## 实验设置

- **训练数据**: Fisher 数据集（2000 小时双通道电话对话）
- **训练**: 2 epochs，batch size 256，lr 4e-6
- **评估**: GPT-score（语义）+ Full-Duplex-Bench（轮次管理）+ perplexity

## 与相关方法的对比

| 方法 | 类型 | 文本引导方式 | 语义提升 |
|------|------|------------|---------|
| Moshi TS | 逐 token 对齐 | 每个 token 在对应语音时刻插入 | 有限 |
| TurnGuide | 逐 turn 对齐 | 动态分割轮次，整段文本引导 | 显著 |

TurnGuide 与 Moshi TS 的关键区别在于：Moshi TS 将每个文本 token 精确插入其对应语音的时间点，导致文本语义过度碎片化；TurnGuide 聚合文本语义，以轮次为单位插入，实现实质性提升。

## 局限性

- 训练于 Fisher 数据集（电话对话），未做 RLHF 安全对齐
- 语义评估依赖 GPT-4o 自动评分
- 首包延迟仍高于 Moshi（1.05s vs 0.26s）

## 相关页面

- [[full-duplex-speech-model]] — 全双工语音模型总览
- [[moshi]] — Moshi 全双工语音对话模型
- [[speech-llm]] — 语音大语言模型
- [[mtr-duplexbench]] — MTR-DuplexBench 多轮全双工评测
- [[silent-thought]] — 另一种利用"思考"增强 FD-SLM 的方法
