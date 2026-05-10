---
title: "Qwen3-ASR"
created: 2026-04-15
updated: 2026-04-15
type: entity
tags: [model, speech-model, architecture, open-source, benchmark, inference]
sources: [raw/papers/2026/01/2601.21337.md]
---

# Qwen3-ASR

阿里 Qwen 团队 2026-01 发布的多语言 ASR 模型家族，基于 [[qwen3-omni]] 的音频理解能力构建。

## 模型家族

| 模型 | LLM Backbone | AuT Encoder | 参数量 | 定位 |
|------|-------------|-------------|--------|------|
| Qwen3-ASR-1.7B | Qwen3-1.7B | 300M / 1024 hidden | ~2B | 开源 ASR SOTA |
| Qwen3-ASR-0.6B | Qwen3-0.6B | 180M / 896 hidden | ~0.8B | 精度-效率最优 |
| Qwen3-ForcedAligner-0.6B | Qwen3-0.6B | 180M | ~0.8B | NAR 时间戳对齐 |

## 训练流程 (四阶段)

1. **AuT 预训练**: 40M 小时伪标注 ASR 数据（主要中英文），在 AED 框架下获得通用音频编码器
2. **Omni 预训练**: 复用 [[qwen3-omni]] 预训练，3T tokens 多任务音频/视觉/文本
3. **ASR SFT**: 风格迁移到 ASR 输入输出格式，包含：
   - 多语言 ASR 数据（与预训练不重叠）
   - 非语音数据、流式增强数据、上下文偏置数据
   - **关键**: 训练为 ASR-only 模型，不响应自然语言指令 → 防指令注入
4. **ASR RL**: Group Sequence Policy Optimization (GSPO)，提升噪声鲁棒性、转录稳定性、疑难 case 分析

## 语言支持

- **30 种语言**: zh, en, yue, ar, de, fr, es, pt, id, it, ko, ru, th, vi, ja, tr, hi, ms, nl, sv, da, fi, pl, cs, fil, fa, el, hu, mk, ro
- **22 种中文方言**: 安徽、东北、福建、甘肃、贵州、河北、河南、湖北、湖南、江西、宁夏、山东、陕西、山西、四川、天津、云南、浙江、粤语（港/粤）、吴语、闽南语

## 性能亮点

### 推理效率 (vLLM, bf16, CUDA Graph)

| 指标 | 0.6B | 1.7B |
|------|------|------|
| TTFT (1并发) | 92ms | 102ms |
| RTF (1并发) | 0.009 | 0.015 |
| 吞吐 (128并发) | 2000x | 1220x |
| 最大音频长度 | 1200s (20min) | 1200s |

### 特色能力
- **歌声/歌曲识别**: 支持带 BGM 歌曲直接转录
- **流式 + 离线统一**: AuT 动态注意力窗口 (1s-8s)
- **上下文偏置**: 利用 system prompt 中的 context tokens 作为背景知识
- **ForcedAligner**: 首个 LLM 范式的 NAR 时间戳预测，支持 11 语言，词/句/段落级别

## 关联

- [[qwen3-omni]] — 基础模型
- [[qwen3-tts]] — TTS 姊妹模型
- [[speech-llm]] — Speech LLM 概念
- [[full-duplex-speech-model]] — 全双工语音模型
