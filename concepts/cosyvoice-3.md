---
title: CosyVoice 3
created: 2026-05-01
updated: 2026-05-01
type: concept
tags: [speech-model, model, open-source]
sources: [raw/papers/2025/05/2505.17589.md]
---

# CosyVoice 3

CosyVoice 3 是阿里通义语音团队（Speech Team, Tongyi Lab, Alibaba Group）于 2025 年 5 月发布的第三代大规模零样本语音生成模型。相比 CosyVoice 2，CV3 在语言覆盖、数据规模、模型容量、后训练技术和评测基准上全面升级，目标是实现**in-the-wild speech generation**——在真实、嘈杂、多样化的现实场景中生成高质量语音。

代码/论文：arXiv 2505.17589
Demo：https://funaudiollm.github.io/cosyvoice3

## 核心创新

### 1. 大规模数据 Scaling（10k → 1M 小时）

训练数据从 CosyVoice 2 的万小时级扩展到**百万小时级**，覆盖：
- **9 种语言**：中文 (zh)、英文 (en)、日文 (ja)、韩文 (ko)、德语 (de)、法语 (fr)、俄语 (ru)、意大利语 (it)、西班牙语 (es)
- **18 种汉语方言**：粤语、东北话、闽南语、上海话等
- **多种领域和文本格式**：新闻、播客、影视剧、学术报告、诗歌朗诵等
- **跨语言语音克隆**支持

### 2. 模型 Scaling（0.5B → 1.5B 参数）

模型参数从 0.5B 扩展到 1.5B，在多语言 benchmark 上显著提升韵律自然度（prosody naturalness）。

### 3. 多任务监督语音 Tokenizer

与 CosyVoice 2 将 FSQ 插入 SenseVoice-Large ASR 编码器不同，CV3 的 tokenizer 基于 [[minmo]]（多模态语音理解大模型，140 万 + 小时训练数据），将 FSQ 模块插入 MinMo 的 Voice Encoder 中间层。

**Tokenizer 架构**：
- **Voice Encoder₁**：12 层 Transformer + RoPE → 中间表征 H
- **FSQ 量化**：H 投影到 D 维低秩空间 → bounded round 量化到 [-K, K]
- **Voice Encoder₂ + MinMo LLM**：量化表征 → 文本 token 后验概率
- **Token 率**：25 Hz（每秒 25 个 speech token）
- **训练数据**：530,000 小时子集用于多任务监督学习

**多任务监督训练**（5 项任务）：
| 任务 | 功能 |
|------|------|
| ASR | 多语言语音识别 |
| LID | 语言识别 |
| SER | 语音情感识别 |
| AED | 音频事件检测 |
| SA | 说话人分析（年龄/性别） |

通过多任务监督学习，离散语音 token 能更好地捕获语义和副语言信息（情感、发音风格等）。

### 4. DiffRO 后训练

引入 **Differentiable Reward Optimization (DiffRO)** 方法对模型进行后训练，详见 [[diffro]] 页面。核心优势：
- 直接从 codec token 预测奖励，无需 vocoder 生成波形
- Gumbel-Softmax 使奖励函数完全可微
- 无需 REINFORCE/PPO，直接通过反向传播优化
- 多任务奖励（MTR）模型提供多维度反馈（ASR、SER、SQA、AED）

### 5. 训练流水线

```
大规模预训练 (1M hrs) → 后训练 (DiffRO) → 持续预训练 → 多说话人 SFT
```

- **后训练阶段**：超越训练数据的性能瓶颈
- **持续预训练阶段**：将指令可控性和多语言合成能力从零样本模型迁移到 SFT 模型

## CV3-Eval 评测基准

传统评测基准（LibriSpeech 等）的不足：
1. 语音来自有声书，发音标准清晰，无法反映真实场景的噪声和多样性
2. 主要针对中英文，缺乏多语言评测
3. 只关注发音准确度、说话人相似度、MOS 音质，无法评估情感表达、韵律丰富度、声音可控性、跨语言语音克隆

CV3-Eval 包含**客观**和**主观**两个子集：

### 客观评测
| 子集 | 内容 |
|------|------|
| **多语言语音克隆** | 9 种语言 × 500 样本 = 4,500 样本（CommonVoice + FLUERS），不过滤噪声/静音。另有中英文 hard-case 测试集（稀有词、绕口令、专业术语） |
| **跨语言语音克隆** | zh/en/ja/ko 互克隆，评估语言迁移能力 |
| **情感克隆** | EmoBox + SeCap 数据，happy/sad/angry 三种情绪，区分文本相关/无关子集 |

### 主观评测
| 子集 | 内容 |
|------|------|
| **表达性语音克隆** | 高情绪语调、耳语、喊叫、极快/极慢语速，来源：新闻、播客、影视剧、学术报告、诗歌朗诵、公众人物声音 |
| **表达性语音延续** | 120 个样本，取前 3 秒为 prompt，评估合成剩余部分与 GT 的一致性 |
| **汉语方言克隆** | 18 种方言，内部工业数据 |

### 评测指标
- **内容一致性**：CER（Paraformer）/ WER（Whisper-large V3）
- **说话人相似度**：ERes2Net 说话人验证模型的余弦相似度
- **音质**：DNSMOS 评分

## 性能对比

在 SEED-TTS-Eval 和 CV3-Eval 上，CosyVoice 3 在**内容一致性、说话人相似度、韵律自然度**上均达到 SOTA。

**Baseline 对比模型**（10 个）：
- NAR：MaskGCT、E2 TTS、F5-TTS、F5R-TTS
- AR：Seed-TTS、FireRedTTS、Qwen2.5-Omni、CosyVoice、CosyVoice 2、Spark TTS

## 与 CosyVoice 2 的对比

| 维度 | CosyVoice 2 | CosyVoice 3 |
|------|-------------|-------------|
| 训练数据 | ~万小时 | **~100 万小时** |
| 语言覆盖 | 5 种语言 | **9 种语言 + 18 种汉语方言** |
| 模型参数 | 0.5B | **1.5B** |
| Tokenizer | SenseVoice-Large + FSQ | **MinMo + FSQ + 5 任务监督** |
| 后训练 | 无 | **DiffRO** |
| 评测基准 | SEED-TTS-Eval | **SEED-TTS-Eval + CV3-Eval** |
| 目标场景 | 广播级中英文 | **in-the-wild 多场景** |

## 关键发现

1. **数据规模是 speech generation 的核心瓶颈**：从万到百万小时的扩展带来质的飞跃
2. **多任务监督 tokenizer 比无监督/ASR-only tokenizer 更好**：情感、语言、事件、说话人等多维度监督使 token 携带更丰富的副语言信息
3. **MinMo 作为 tokenizer 基座优于 SenseVoice-Large**：MinMo 在 140 万 + 小时数据上预训练，在语音对话、多语言识别、情感识别上达到 SOTA
4. **DiffRO 后训练显著提升发音准确度**：无需 vocoder 的 token-level 奖励优化比传统 RLHF 更高效
5. **CV3-Eval 填补了真实场景多语言语音合成评测空白**

## 相关页面

- [[cosyvoice]] — CosyVoice v1，S³ 有监督语义 token 开创者
- [[cosyvoice-2]] — CosyVoice 第二代，双流 streaming + 指令控制
- [[diffro]] — DiffRO 后训练方法，CV3 使用的核心优化技术
- [[fun-audio-llm]] — FunAudioLLM 团队，CosyVoice 系列的归属组织
- [[minmo]] — MinMo 多模态语音理解模型，CV3 tokenizer 的基座
- [[qwen3-tts]] — 阿里 Qwen 团队的 TTS 模型，同门竞品
