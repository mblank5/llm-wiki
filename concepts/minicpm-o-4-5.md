---
title: MiniCPM-o 4.5
created: 2026-05-05
updated: 2026-05-05
type: concept
tags: [model, architecture, training, inference, alignment, speech-model, full-duplex, omni-modal, streaming, open-source, real-time, edge-deployment, benchmark]
sources:
  - raw/papers/2026/04/2604.27393.md
---

# MiniCPM-o 4.5: Towards Real-Time Full-Duplex Omni-Modal Interaction

> **OpenBMB** | arXiv:2604.27393 | 2026-04-30 | 9B parameters
> GitHub: https://github.com/OpenBMB/MiniCPM-o

MiniCPM-o 4.5 是一个 9B 参数的开源多模态大语言模型（MLLM），实现了**实时全双工 omni-modal 交互**——能同时看、听、说，并表现出主动行为（proactive behavior）。其核心技术是 **Omni-Flow**，一个将多模态输入输出沿共享时间轴对齐的统一流式框架。

核心亮点：
- 在视觉-语言能力上接近 Gemini 2.5 Flash，在同等规模开源模型中 SOTA
- 在 omni-modal 理解和语音生成上超越 Qwen3-Omni-30B-A3B，计算效率显著更高
- 可在 <12GB RAM 的边缘设备上运行实时全双工交互
- 端到端 token 级连接，支持 voice cloning 等高级语音生成能力

---

## 1. 核心问题定义：全双工多模态交互的挑战

### 1.1 现有范式的瓶颈

当前多模态 LLM 的交互范式存在两个根本性缺陷：

**缺陷一：感知与响应分离为交替阶段（Turn-based）**

```
传统范式: [感知阶段] → [响应阶段] → [感知阶段] → [响应阶段] → ...
                ↑ 信息阻塞，响应期间无法纳入新输入
```

在生成响应期间，模型无法持续感知环境变化。这导致：
- 响应过程中无法根据新信息及时调整
- 信息流被阻断，交互不自然
- 延迟叠加（VAD → ASR → LLM → TTS 级联管道通常 2-5 秒）

**缺陷二：纯被动响应（Reactive-only）**

现有模型仅在收到明确用户指令后才响应，缺乏：
- 主动提醒（proactive reminding）
- 实时场景描述
- 基于持续环境理解的自发行为

### 1.2 全双工交互的要求

真正的全双工 omni-modal 交互需要：

| 要求 | 描述 |
|------|------|
| **同时感知与响应** | 模型在说话的同时持续监听和观察 |
| **时间对齐** | 语音输出与当前环境上下文紧密耦合 |
| **主动行为** | 无需外部 VAD 触发，自主决定何时说话 |
| **低延迟** | 端到端延迟控制在毫秒级 |
| **边缘可部署** | 在消费级硬件上实时运行 |

### 1.3 技术难点

1. **时间对齐**：文本生成时间与语音播放时间不匹配，导致语音流滞后于模型状态
2. **控制决策**：模型需要自行决定"是否说话"以及"说什么"
3. **稳定性**：在持续流式交互中保持输出连贯性
4. **效率**：在有限算力下实现实时推理

---

## 2. Omni-Flow 架构详解

### 2.1 总体架构

MiniCPM-o 4.5 由三个核心组件组成：

```
┌─────────────────────────────────────────────────────────────┐
│                    MiniCPM-o 4.5 Architecture               │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Visual      │    │   Audio      │    │   Text       │  │
│  │   Encoder     │    │   Encoder    │    │   Input      │  │
│  │ (SigLIP ViT)  │    │ (Whisper Med)│    │              │  │
│  │   417.8M      │    │   307.2M     │    │              │  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘  │
│         │                   │                   │          │
│  ┌──────▼───────┐    ┌──────▼───────┐           │          │
│  │   Visual      │    │   Audio      │           │          │
│  │   Resampler   │    │   Projector  │           │          │
│  │   88.9M       │    │   21.0M      │           │          │
│  └──────┬───────┘    └──────┬───────┘           │          │
│         │                   │                   │          │
│         └───────────┬───────┘                   │          │
│                     ▼                           │          │
│         ┌───────────────────────┐               │          │
│         │    LLM Backbone       │◄──────────────┘          │
│         │    (Qwen3-8B)         │                          │
│         │    8,189.2M           │                          │
│         └───────────┬───────────┘                          │
│                     │                                      │
│         ┌───────────▼───────────┐                          │
│         │  Backbone-to-Decoder  │                          │
│         │  Projector (10.5M)    │                          │
│         └───────────┬───────────┘                          │
│                     ▼                                      │
│         ┌───────────────────────┐                          │
│         │  Speech Token Decoder │                          │
│         │  (~0.3B)              │                          │
│         └───────────┬───────────┘                          │
│                     ▼                                      │
│         ┌───────────────────────┐                          │
│         │  Streaming Flow-      │                          │
│         │  Matching Decoder     │                          │
│         └───────────────────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

**总参数量：9.34B（可学习参数），bfloat16 精度**

所有可学习组件（从多模态编码器 → LLM backbone → speech token decoder）以 token 级隐藏状态进行可微分连接，支持端到端梯度传播和跨模态联合优化。

### 2.2 多模态编码器

#### 2.2.1 视觉编码

采用 **LLaVA-UHD** 图像分割策略 + **SigLIP ViT** 编码器 + **Resampler** 模块：

```
输入图像
    │
    ▼
┌─────────────────────────┐
│ LLaVA-UHD 图像分割       │
│ (支持任意宽高比高分辨率)    │
└───────────┬─────────────┘
            │ slices
            ▼
┌─────────────────────────┐
│ SigLIP ViT (0.4B)       │
│ Hidden: 1152, Layers: 27 │
│ Heads: 16, FFN: 4304    │
│ Patch size: 14×14       │
│ 每 slice → 1024 tokens  │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Visual Resampler (88.9M) │
│ Query tokens: 64         │
│ Embedding dim: 4096      │
│ Heads: 32               │
│ 1024 → 64 tokens         │
│ (16× 压缩比)             │
└─────────────────────────┘
```

- **全双工流式模式**：最大分辨率 448×448
- **传统模式**：最大分辨率 2240×2240
- **16× token 压缩比**（常见方案为 4×），显著提升视觉处理效率

#### 2.2.2 音频编码

采用 **Whisper Medium** 编码器 + **两层 MLP projector**：

```
输入音频流
    │
    ▼
┌─────────────────────────────┐
│ Whisper Medium Encoder (0.3B)│
│ Hidden: 1024, Layers: 24    │
│ Heads: 16, FFN: 4096       │
│ Mel bins: 80                │
│ 50 tokens/秒 (chunk-based)  │
└───────────┬─────────────────┘
            │
            ▼
┌─────────────────────────────┐
│ Audio Projector (21.0M)      │
│ 2-layer MLP + ReLU          │
│ 1024 → 4096 → 4096          │
│ 5× 时域压缩                  │
│ 50 → 10 audio tokens/秒     │
└─────────────────────────────┘
```

以 chunk-based 流式方式处理，每秒产生 10 个 audio token 送入 LLM backbone。

### 2.3 文本解码（LLM Backbone）

**Qwen3-8B** (8,189.2M)：
- Hidden: 4096, Layers: 36, Heads: 32
- KV heads (GQA): 8, Head dim: 128
- FFN: 12288, Activation: SiLU
- Vocab: 151,748, Max context: 40,960
- RoPE θ = 10^6

关键设计：LLM backbone **仅生成文本 token**，每秒仅 3-4 个解码步（对应人类语速）。这与直接生成 speech token（~25 tokens/秒）的方案相比，避免了效率瓶颈和语言能力退化。

### 2.4 语音 Token 生成

```
LLM hidden states
    │
    ▼
┌─────────────────────────────┐
│ LLM-to-Speech Projector      │
│ (10.5M, 2-layer MLP+ReLU)   │
│ 4096 → 768 → 768            │
└───────────┬─────────────────┘
            │ reshaped hidden states
            ▼
┌─────────────────────────────┐
│ Speech Token Decoder (~0.3B) │
│ Transformer: 188.8M          │
│ Hidden: 768, Layers: 20     │
│ Heads: 12, FFN: 3072        │
│ Activation: SiLU             │
│ Text embedding: 116.8M       │
│ Text vocab: 152,064          │
│ Speech codebook: 6,562       │
│ Speech token rate: 25/s      │
│ S3 token generation          │
└─────────────────────────────┘
```

对于每个文本 token，将其 LLM backbone hidden states（经 MLP reshape）送入轻量级 Llama speech token decoder，生成 S3 speech token。LLM 的韵律决策被预编码到 hidden states 中，小 decoder 专注于语音建模。

### 2.5 波形合成

流式 flow-matching decoder 将 S3 speech token 转换为音频波形，基于多模态系统 prompt 中的参考音频（支持 voice cloning）。

---

## 3. Omni-Flow 框架详解

### 3.1 时间对齐流（Time-Aligned Streams）

Omni-Flow 定义了三个时间对齐的流：

| 流 | 描述 | 输入源 |
|----|------|--------|
| `env-visual` | 环境视觉观察 | 摄像头/视频流 |
| `env-audio` | 声学场景 | 麦克风（含用户语音） |
| `out-stream` | 助手输出 | 模型文本和语音输出 |

关键洞察：用户请求不再被视为特权的对话角色，而是作为持续观测的世界状态的一部分，主要通过 `env-audio` 进入。模型不依赖显式请求作为响应触发，而是 `out-stream` 与持续感知耦合演化。

### 3.2 统一序列化（Unified Serialization）

对于第 k 个时间 chunk：

```
v^k = 视觉 token 序列 (env-visual)
a^k = 音频 token 序列 (env-audio)  
o^k = 输出 token 序列 (out-stream)
```

当无输出需要产生时，`o^k` 仅包含特殊 `[listen]` token。

**组构建**：
```
g_k = [v^k ; a^k ; o^k]
```

**序列化**：将连续 groups 拼接为单一序列：
```
G = [g_1, g_2, g_3, ..., g_T]
```

在每个 chunk 内，模型先处理新到达的感知 token，再生成输出 token，确保每个输出都基于最新观测。

### 3.3 设计权衡（Design Tradeoffs）

消融实验研究了三个维度：

**表 1：全双工设计选择消融**

| Chunk Size | Boundary | Control | AdvBench | AlpacaEval | IFEval | SDQA | MMLU |
|------------|----------|---------|----------|------------|--------|------|------|
| 1.0s | Explicit | LS | **0.98** | **3.56** | **0.29** | **0.36** | **0.65** |
| 1.0s | Explicit | LT | 0.92 | 3.60 | 0.24 | 0.35 | 0.56 |
| 1.0s | Implicit | LT | 0.96 | 3.31 | 0.22 | 0.28 | 0.45 |
| 0.2s | Explicit | LS | 0.81 | 1.22 | 0.10 | 0.09 | 0.45 |
| 0.1s | Explicit | LS | 0.67 | 2.40 | 0.10 | 0.13 | 0.32 |

**关键发现**：

1. **时间粒度**：1.0s 的 chunk size 在延迟和容量之间达到最佳平衡。chunk 太短时，模型在每个时间窗口内没有足够信息做出稳定决策，导致性能显著下降。

2. **边界显式性**：显式标记 group 边界始终有益。区分新观测输入与新生成输出是一个非平凡问题，显式结构可以减轻模型负担。

3. **控制公式化**：LS（Listen-Speak）优于 LT（Listen-Text），说明"是否说话"应与"说什么"解耦，将两者纠缠在单步预测中使全双工交互更难学习。

### 3.4 TAIL：时间对齐交错语音生成

**问题**：文本生成时间与语音播放时间不匹配。m 秒间隔内生成的文本可能需要远超过 m 秒来朗读，导致语音流滞后于模型状态。

**现有方案不足**：
- (a) 先生成长段文本再合成语音 → 文本远超前于播放
- (b) 固定文本-语音 token 比例交错 → 假设固定的文本-语音对应关系

**TAIL（Time-Aligned Interleaving）**：

在 chunk k，模型调整生成的文本量，使得在朗读新生成内容后，语音流接近当前时间边界 kt。如果之前 chunk 已引入轻微播放延迟，模型可自适应生成更少文本 token 让语音追上。

**TAIL 监督构建**：
- 收集全双工流式训练数据中每个文本 token 的开始和结束时间
- 开始时间落入 [(k-1)t, kt) 的文本 token 及其对应 speech token 被分配到第 k 个 Omni-Flow chunk

**Look Ahead 机制**：
- 为处理发音依赖（如 "the" 的发音取决于后接词），chunk k 中最后几个文本 token 的 speech token 被推迟到 chunk k+1
- 这提供了发音和韵律的局部上下文，同时不让文本流大幅超前于播放

---

## 4. 训练数据

### 4.1 语音数据

**大规模自然语音数据**：
- 数百万小时无标注语音，来自多种来源
- 集成多个开源组件进行处理
- 生成零样本 TTS、ASR、多轮多说话人对话训练集
- 涵盖广泛说话人、口音和对话模式

**口语对话数据**：
- 先用文本 LLM 生成多样化种子查询的口语化指令跟随对话
- 部分对话由专业配音演员在录音室条件下重新录制
- 配音演员以对话风格而非逐字朗读方式演绎
- 在保持一致声音身份的同时变化情感、语速和重音
- 覆盖指令跟随 TTS、问答、多轮自然对话

### 4.2 视觉-语言数据

在 MiniCPM-V 4.5 数据系统基础上扩展：

| 数据类型 | 方法 |
|----------|------|
| 高质量知识与对齐数据 | 更新 CapsFusion pipeline 的生成模型，改进图像-文本相关性估计过滤 |
| 复杂文档与 OCR 数据 | 相关性感知 mask 策略，优先 mask 与图表相关的区域 |
| 真实场景数据 | 更自然的查询模式，将简短答案改写为详细的 chain-of-thought 推理，基于奖励模型的过滤 |
| 密集视频感知数据 | 密集视频字幕数据集，提供时间事件、人类动作和复杂场景转换的连续细粒度描述 |
| 纯文本数据 | 来自 MiniCPM 4.1 后训练数据集，保持语言能力 |

### 4.3 Omni-Modal 全双工数据

包含大规模网络数据和高质量指令样本。每个训练样本包含完整视觉输入、音频输入、输出文本和输出语音，每块信息都标记有时间索引。

**大规模网络音视频数据**：
- 过滤掉以单说话人语音为主或音视觉相关性弱的片段
- 应用 OCR 字幕去除、说话人检测、ASR 转录过滤

**全双工任务数据**：
- 手动构建多个场景并标注指令跟随数据
- 支持高级能力如连续场景描述和主动提醒

---

## 5. 训练配置

### 5.1 训练流程（四阶段）

```
阶段 1: 语音预训练
─────────────────────
初始化: Whisper encoder + MiniCPM-V 4.5 checkpoint + 随机初始化的语音模块
冻结: 预训练组件
训练: 新增模块（audio projector, LLM-to-speech projector, speech decoder）
目标: 将 Whisper 特征对齐到 LLM hidden space，训练 speech decoder 将 LLM hidden states 转换为语音 token

        ↓

阶段 2: 联合预训练
─────────────────────
解冻: 所有参数
数据: 视觉-语言、语音、omni-modal 数据的平衡混合
技巧: 不同 modality 组合分配给不同 data-parallel rank，确保每步固定数据比例
目标: 统一 next-token prediction，获得实时 omni-modal 交互能力

        ↓

阶段 3: 有监督微调 (SFT)
─────────────────────────
阶段 3a: 大规模指令调优（广泛能力适配）
阶段 3b: 高质量人工标注调优（细粒度行为精化）
技巧: 可变分辨率（0.2-0.4 百万像素）和帧率（1-5 FPS），支持质量-效率权衡

        ↓

阶段 4: 强化学习 (RL)
─────────────────────
方法: GRPO (Shao et al., 2024)
奖励: 准确性奖励 + 格式奖励 + 长度奖励 + 通用奖励模型
额外: RLAIF-V 减少视觉幻觉
```

### 5.2 长度奖励公式

从 Kimi-K1.5 改编的平滑长度奖励：

```
r_len(i) = { s_i,   if r_i = 1  (正确)
            { min(0, s_i), if r_i = 0  (错误)

s_i = (0.5 - (ℓ_i - ℓ_min) / (ℓ_max - ℓ_min)) × min(1, (ℓ_max - ℓ_min) / τ)
```

其中：
- `r_i` = 正确性指示符
- `ℓ_i` = 当前响应长度
- `ℓ_min`, `ℓ_max` = 同 prompt 响应中的最小/最大长度
- `τ` = 缩放因子
- `min(0, s_i)` 项避免奖励过短的错误响应
- 前 480 步训练不包含长度奖励以加速收敛

**表 9：不同长度奖励策略对比**

| 方法 | 平均分 (思考) | 平均分 (指令) | 长度缩减 (思考) | 长度缩减 (指令) |
|------|-------------|-------------|---------------|---------------|
| 无长度奖励 | 73.5 | 70.9 | – | – |
| Kimi K1.5-Style | 73.0 | 70.1 | 50.7% | 20.2% |
| **Ours (平滑)** | **74.3** | **70.9** | **35.3%** | **20.5%** |

K1.5 风格奖励激进的缩减导致性能下降，而平滑奖励在保持性能的同时实现适度缩减。

---

## 6. 实验结果

### 6.1 视觉-语言 Benchmark（Instruct Mode）

**表 2：视觉-语言结果（指令模式）**

| Benchmark | Gemini 2.5 Flash | InternVL3.5-8B | Qwen3-VL-8B | Qwen3-Omni-30B | **MiniCPM-o 4.5** |
|-----------|-------------------|----------------|-------------|----------------|-------------------|
| **STEM & General** | | | | | |
| OpenCompass | 78.5 | 75.8 | 76.5 | 75.7 | **77.6** |
| MMBench EN v1.1 | 86.6 | 79.5 | 84.5 | 84.9 | **87.6** |
| MMBench CN v1.1 | 86.0 | 80.0 | 84.7 | 84.1 | **87.2** |
| MathVista | 75.3 | 78.4 | 77.2 | 75.9 | **80.1** |
| MMVet | 81.4 | 83.1 | 73.7 | 74.8 | 74.4 |
| MMMU | 76.3 | 73.4 | 69.6 | 69.1 | 67.6 |
| MMStar | 75.8 | 69.3 | 70.9 | 68.5 | **73.1** |
| AI2D | 87.7 | 84.0 | 85.7 | 85.2 | **87.6** |
| MMT-Bench (val) | 70.0 | 66.7 | 60.9 | 70.4 | **69.7** |
| MM-IFEval | 75.8 | 56.3 | 59.4 | 65.7 | **66.3** |
| **Document & OCR** | | | | | |
| OCRBench | 864 | 840 | 896 | 880 | **876** |
| TextVQA (val) | 74.3 | 78.2 | 82.9 | 84.1 | **83.8** |
| DocVQA (val) | 93.0 | 92.3 | 96.1 | 95.4 | **94.7** |
| OmniDocBench (EN) ↓ | 0.214 | 0.322 | 0.255 | 0.216 | **0.109** |
| OmniDocBench (CN) ↓ | 0.290 | 0.416 | 0.319 | 0.363 | **0.162** |
| **Hallucination** | | | | | |
| HallusionBench | 59.1 | 54.5 | 61.1 | 59.7 | **63.2** |
| MMHal-Score | 4.6 | 3.8 | 4.7 | 4.6 | **4.7** |
| MMHal-Hallrate ↓ | 23.9 | 34.7 | 29.9 | 31.6 | **24.3** |
| **Multi-Image** | | | | | |
| Mantis-Eval | 72.8 | 70.5 | 74.2 | 78.3 | **79.7** |
| MUIRBench | 74.5 | 55.8 | 64.4 | 61.9 | **72.0** |
| MMSI-Bench | 12.1 | – | 11.3 | 14.2 | **16.6** |
| **Video** | | | | | |
| Video-MME (w/o subs) | 75.6 | 66.0 | 71.4 | 70.5 | **70.4** |
| LVBench | 62.2 | – | 58.0 | 50.2 | **50.9** |
| MLVU (M-Avg) | 77.8 | 70.2 | 78.1 | 75.2 | **76.5** |
| LongVideoBench (val) | – | 62.1 | 66.4 | 66.9 | **66.0** |
| MotionBench | – | 62.3 | 59.5 | 61.7 | **61.4** |

**Thinking Mode 结果（表 3 关键数据）**：

| Benchmark | Gemini 2.5 Flash | GPT-5 | Qwen3-VL-8B | Qwen3-Omni-30B | **MiniCPM-o 4.5** |
|-----------|-------------------|-------|-------------|----------------|-------------------|
| OpenCompass | 79.9 | 79.7 | 77.3 | 78.5 | **78.2** |
| MMBench EN v1.1 | 87.1 | 85.5 | 85.3 | 88.2 | **89.0** |
| MMBench CN v1.1 | 87.3 | 85.6 | 85.5 | 87.7 | **87.6** |
| MathVista | 79.4 | 81.9 | 81.4 | 80.0 | **81.0** |
| HallusionBench | 63.5 | 65.2 | 65.4 | 62.8 | **62.6** |
| MMMU | 77.7 | 81.8 | 74.1 | 75.6 | **70.2** |

### 6.2 语音理解结果

**表 4：音频理解 benchmark（↓ = 越低越好）**

| Benchmark | Kimi-Audio-9B | Qwen3-Omni-30B | **MiniCPM-o 4.5** |
|-----------|---------------|----------------|-------------------|
| **ASR (CER/WER ↓)** | | | |
| AISHELL-1 | 0.6 | 0.6 | 0.9 |
| AISHELL-2 | 2.6 | 2.3 | 2.5 |
| WenetSpeech test-net | 6.3 | 4.7 | 5.9 |
| WenetSpeech test-meeting | 5.4 | 5.9 | 5.7 |
| LibriSpeech test-clean | 1.3 | 1.2 | 1.4 |
| LibriSpeech test-other | 2.4 | 2.5 | 2.8 |
| GigaSpeech test | 9.4 | 8.7 | **8.5** |
| VoxPopuli V1-En | 8.0 | 6.4 | **6.2** |
| **Speech Translation** | | | |
| CoVoST 2 en→zh | 36.6 | 46.6 | **49.9** |
| CoVoST 2 zh→en | 18.3 | 29.4 | **26.4** |
| **Audio Understanding** | | | |
| MMAU | 68.4 | 77.5 | **76.9** |
| MELD | 59.1 | 56.8 | **60.2** |
| **Speech QA** | | | |
| VoiceBench AlpacaEval* | 4.46 | 4.74 | **4.81** |
| Speech TriviaQA | 41.9 | 62.9 | **75.5** |
| Speech Web Questions | 46.4 | 74.9 | **70.2** |
| Speech CMMU | 67.0 | 47.8 | **59.2** |

### 6.3 语音生成结果

**表 5：语音生成结果（CER/WER ↓ = 越低越好，SIM-o ↑ = 越高越好）**

| Model | ZH CER ↓ | ZH SIM-o ↑ | EN WER ↓ | EN SIM-o ↑ | LongTTS EN WER ↓ | LongTTS ZH CER ↓ | Expresso* | ESD* |
|-------|----------|------------|----------|------------|-------------------|-------------------|-----------|------|
| CosyVoice2 | 1.45 | 74.8 | 2.57 | 65.2 | 14.80 | 5.27 | 17.9 | 53.4 |
| Qwen3-Omni | 1.41 | N/A | 3.39 | N/A | 17.33 | 18.99 | N/A | N/A |
| **MiniCPM-o 4.5** | **0.86** | **74.5** | **2.38** | **64.9** | **3.37** | **6.58** | **29.8** | **82.1** |

MiniCPM-o 4.5 在双语语音生成上均达到最低错误率，在情感/风格控制（Expresso, ESD）上也表现最佳。

**表 10：不同交错模式的语音生成质量**

| 模式 | ZH CER ↓ | ZH SIM-o ↑ | EN WER ↓ | EN SIM-o ↑ |
|------|----------|------------|----------|------------|
| 无交错 | 1.44 | 74.1 | 2.70 | 64.9 |
| 固定文本交错 | **0.86** | **74.5** | **2.38** | **64.9** |
| 动态文本交错 (TAIL) | 1.04 | 74.1 | 3.93 | 65.1 |

TAIL 在全双工设置中实现了时间对齐和语音质量之间的实用权衡。

### 6.4 文本能力结果

**表 6：纯文本 benchmark 结果**

| Model | IFEval-PLS | BBH | CMMLU | MMLU | HumanEval | MBPP | Math500 | GSM8K | Avg |
|-------|------------|-----|-------|------|-----------|------|---------|-------|-----|
| Qwen3-8B-Instruct | 83.0 | 69.4 | 78.7 | **81.7** | **86.6** | 75.9 | 84.0 | **93.4** | 81.6 |
| **MiniCPM-o 4.5** | **84.7** | **81.1** | **79.6** | 77.0 | **86.6** | **76.7** | **77.0** | **94.5** | **82.1** |

**关键发现**：在多模态训练后，模型在大多数纯文本任务上反而超越了 backbone LLM，特别是在复杂推理、数学、编码和指令跟随方面。说明精心平衡的文本和多模态数据可以让模型在获得多模态能力的同时保持甚至提升文本能力。

### 6.5 Omni-Modal 理解结果

**表 7：单工设置下的 omni-modal benchmark**

| Benchmark | Gemini 2.5 Flash | Qwen3-Omni-30B | **MiniCPM-o 4.5** |
|-----------|-------------------|----------------|-------------------|
| Daily-Omni | 79.3 | 70.7 | **80.2** |
| WorldSense | 52.6 | 54.0 | **55.7** |
| Video-Holmes | 51.3 | 50.4 | **64.3** |
| JointAVBench | 55.6 | 53.1 | **60.0** |
| AVUT-Human | 65.4 | 74.2 | **78.6** |
| FutureOmni | **55.6** | **62.1** | 56.1 |
| Video-MME-Short (w/ audio) | **85.5** | 81.3 | **84.4** |

在 7 个 benchmark 中的 5 个上取得最佳结果，展现强大且全面的 omni-modal 理解能力。

### 6.6 全双工交互结果

**表 8：纯视觉全双工 benchmark**

| Benchmark | LiveCC-8B | StreamingVLM-8B | **MiniCPM-o 4.5** |
|-----------|-----------|-----------------|-------------------|
| LiveSports-3K-CC | 41.5 | 45.6 | **54.4** |

MiniCPM-o 4.5 以 54.4% 的胜率超越 LiveCC（+12.9）和 StreamingVLM（+8.8），验证了 Omni-Flow 在持续视觉交互中的有效性。

---

## 7. 边缘部署

### 7.1 vLLM 推理效率

**表 11：单 NVIDIA RTX 4090 推理效率对比（vLLM）**

| Model | Dtype | Throughput (tokens/s) ↑ | First-token Latency (s) ↓ | Memory (GB) ↓ |
|-------|-------|------------------------|--------------------------|---------------|
| Qwen3-Omni-30B-A3B | BF16 | OOM | OOM | OOM |
| **MiniCPM-o 4.5** | **BF16** | **154.3** | **0.59** | **19** |
| Qwen3-Omni-30B-A3B | INT4 | 147.8 | 0.98 | 20 |
| **MiniCPM-o 4.5** | **INT4** | **212.3** | **0.58** | **11** |

在 BF16 精度下，Qwen3-Omni-30B 直接 OOM，而 MiniCPM-o 4.5 达到 154.3 tokens/s 且仅用 19GB 显存。INT4 下进一步提速至 212.3 tokens/s，显存降至 11GB。

### 7.2 llama.cpp-omni 框架

为全双工流式模式开发的专用推理框架：

**表 12：不同推理框架效率对比**

| Framework | Dtype | RTX 4090 RTF ↓ | RTX 4090 Mem (GB) | DGX Spark RTF ↓ | DGX Spark Mem (GB) |
|-----------|-------|-----------------|-------------------|-----------------|-------------------|
| PyTorch | BF16 | OOM | OOM | 2.43 | 26 |
| PyTorch | INT4 | 1.26 | 14 | 1.27 | 14 |
| **llama.cpp-omni** | **FP16** | **0.27** | **19** | **0.46** | **19** |
| **llama.cpp-omni** | **INT4** | **0.21** | **11** | **0.20** | **11** |

RTF (Real-Time Factor) 远低于 1.0 表示快于实时。llama.cpp-omni 在 RTX 4090 上 INT4 达到 0.21 RTF，意味着每秒可处理约 4.8 秒的音频，完全满足实时交互需求。

### 7.3 部署特性

- **跨平台兼容**：macOS、Windows、Linux
- **轻量 demo 系统**：用户可在自有硬件上快速部署
- **<12GB RAM**：可在消费级边缘设备（如 DGX Spark）上运行
- **多模态系统 prompt**：支持文本 + 参考音频，实现 voice cloning

---

## 8. 模型配置详情

**表 13：MiniCPM-o 4.5 架构超参数**

| 组件 | 超参数 | 值 |
|------|--------|-----|
| **视觉编码器** (SigLIP ViT, 417.8M) | Hidden dimension | 1,152 |
| | Layers | 27 |
| | Attention heads | 16 |
| | FFN dimension | 4,304 |
| | Activation | GELU |
| | Patch size | 14×14 |
| **视觉 Resampler** (88.9M) | Query tokens | 64 |
| | Embedding dimension | 4,096 |
| | Attention heads | 32 |
| **音频编码器** (Whisper Medium, 307.2M) | Hidden dimension | 1,024 |
| | Layers | 24 |
| | Attention heads | 16 |
| | FFN dimension | 4,096 |
| | Activation | GELU |
| | Mel-frequency bins | 80 |
| **Audio Projector** (21.0M) | Architecture | Two-layer MLP + ReLU |
| | Dimensions | 1024→4096→4096 |
| **LLM Backbone** (Qwen3-8B, 8,189.2M) | Hidden dimension | 4,096 |
| | Layers | 36 |
| | Attention heads | 32 |
| | KV heads (GQA) | 8 |
| | Head dimension | 128 |
| | FFN dimension | 12,288 |
| | Activation | SiLU |
| | Normalization | RMSNorm (ε=10⁻⁶) |
| | Vocabulary size | 151,748 |
| | Max context length | 40,960 |
| | RoPE θ | 10⁶ |
| **Backbone-to-Decoder Projector** (10.5M) | Architecture | Two-layer MLP + ReLU |
| | Dimensions | 4096→768→768 |
| **Speech Token Decoder** | Text embedding | 116.8M |
| | Text vocab size | 152,064 |
| | Transformer | 188.8M |
| | Hidden dimension | 768 |
| | Layers | 20 |
| | Attention heads | 12 |
| | FFN dimension | 3,072 |
| | Activation | SiLU |
| | Speech codebook size | 6,562 |
| | Speech token frame rate | 25/s |

---

## 9. 批判性分析

### 9.1 优势

1. **首个 9B 全双工 omni-modal 模型**：在极小参数规模下实现了同时看、听、说，填补了开源领域的空白
2. **高效的架构设计**：LLM backbone 仅生成文本 token（3-4 步/秒），speech decoder 处理高帧率语音 token（25/s），避免了大模型直接生成语音 token 的效率瓶颈
3. **16× 视觉压缩比**：远超常见 4× 方案，显著降低视觉 token 预算
4. **时间对齐创新**：TAIL 机制解决了流式交互中语音滞后的核心问题
5. **边缘可部署**：<12GB RAM，在消费级 GPU 上实时运行，远超 Qwen3-Omni-30B（BF16 下 OOM）
6. **OCR/文档理解 SOTA**：OmniDocBench 上大幅领先，继承 MiniCPM 系列优势
7. **多模态训练不损害文本能力**：在多数纯文本任务上超越 backbone
8. **灵活的双模式**：支持全双工流式模式和传统 turn-based 模式切换

### 9.2 不足与局限

1. **全双工 benchmark 匮乏**：仅在 LiveSports-3K-CC（audio-free）上评估，缺乏音频-视觉全双工的标准 benchmark
2. **语音稳定性问题**：全双工流式模式下偶发误读和中英文混用
3. **主动行为仍较简单**：论文承认 proactive behavior 相对简单，缺乏更丰富的上下文感知规划
4. **Chunk size 权衡**：1.0s 的 chunk size 虽然稳定，但可能限制了响应粒度（0.2s/0.1s 时性能显著下降）
5. **网络条件敏感**：web demo 在不稳定网络下可能出现延迟或输出片段丢失
6. **训练数据细节不透明**：虽然描述了数据采集和处理流程，但具体数据量、来源分布未完全公开
7. **MMMU 等推理 benchmark 略低**：在 MMMU（67.6 vs Gemini 76.3）等需要深度推理的任务上仍有差距

### 9.3 与竞品对比

| 维度 | MiniCPM-o 4.5 | Qwen3-Omni-30B | [[moshi]] | [[seeduplex]] |
|------|---------------|----------------|-----------|---------------|
| 参数量 | 9B | 30B-A3B | 7B | 未公开 |
| 全双工 | ✓ | ✗ (半双工) | ✓ | ✓ |
| Omni-modal | ✓ | ✓ | 仅音频 | 仅音频 |
| 视觉 | ✓ | ✓ | ✗ | ✗ |
| 边缘部署 | <12GB | >20GB (BF16 OOM) | ~8GB | 未公开 |
| 开源 | ✓ | ✓ | ✓ | ✗ |
| 主动行为 | ✓ | ✗ | ✗ | 有限 |

### 9.4 对我们工作的启发

1. **Omni-Flow 范式可推广**：时间对齐流式框架不仅适用于 omni-modal，也可应用于需要实时多传感器融合的场景
2. **LLM 与语音解耦设计值得借鉴**：让 LLM 专注于文本生成，将高帧率语音合成委托给轻量 decoder，是一种高效的分工策略
3. **TAIL 机制对实时系统有普适价值**：自适应交错策略可应用于任何需要保持输出与输入时间对齐的流式系统
4. **边缘部署是差异化优势**：在模型能力接近的前提下，部署效率可能成为实际应用的关键决定因素
5. **全双工 benchmark 是社区缺口**：需要建立更全面的评估标准来推动领域发展

---

## Related

- [[full-duplex-speech-model]] — 全双工语音模型总览
- [[omni-modal-llm]] — 多模态 LLM 概念
- [[seeduplex]] — 字节跳动全双工模型
- [[moshi]] — Kyutai 全双工模型
- [[qwen3-omni]] — Qwen3 Omni 模型
- [[speech-llm]] — 语音 LLM
- [[audio-agent]] — 音频 Agent
