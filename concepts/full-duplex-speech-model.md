---
title: 全双工语音模型（Full-Duplex Speech Model）
created: 2026-04-09
updated: 2026-04-10
type: concept
tags: [concept, full-duplex, speech-model, end-to-end, streaming]
sources: [raw/articles/bytedance-seeduplex-2026-04-09.md]
---

# 全双工语音模型（Full-Duplex Speech Model）

## 定义

全双工语音模型是指能够在同一时刻同时"听"和"说"的语音交互系统。区别于传统的半双工（half-duplex）"你讲我听、我讲你听"轮流机制，全双工模型实现了真正意义上的实时双向交互，更接近人类自然对话方式。

## 背景与动机

传统语音交互系统采用**级联流水线**（cascaded pipeline）：
1. VAD（Voice Activity Detection）检测语音段
2. ASR（Automatic Speech Recognition）转录文本
3. LLM 生成文本回复
4. TTS（Text-to-Speech）合成语音

问题：
- 延迟叠加（通常 2-5 秒）
- 丢失韵律、情感等副语言信息
- 无法处理打断、重叠语音
- 机械的轮次切换，不自然

全双工模型通过**端到端（end-to-end）**架构直接从音频到音频，消除了级联管道的局限。

## 核心技术挑战

1. **同时听和说：** 模型需要同时处理输入音频流和生成输出音频流
2. **动态判停（Endpoint Detection）：** 准确判断用户何时说完、何时在思考
3. **抗干扰（Interference Suppression）：** 在噪音、多人说话等复杂声学环境中精准识别目标用户
4. **低延迟：** 端到端延迟需控制在 200-600ms 以内才有自然感
5. **对话节奏控制：** 抢话、附和、停顿等微妙交互行为
6. **打断处理（Barge-in）：** 用户打断时快速响应并切换话题

## 主要架构方案

### 方案一：多流自回归（Multi-Stream Autoregressive）

代表：[[moshi]]
- 基于 Helium 文本 LLM + Mimi 神经音频编解码器
- 将用户语音和模型语音分别建模为并行 token 流
- 层级化生成：先文本后音频
- 理论延迟 160ms，实际 200ms

### 方案二：双通道端到端（Dual-Channel End-to-End）

代表：LSLM、SALM-Duplex
- 说话通道：token-based decoder-only TTS
- 听话通道：streaming SSL encoder
- 同时处理两个通道的 token

### 方案三：冻结 LLM + 适配层

代表：[[freeze-omni]]、[[llama-omni]]
- 保持 LLM 参数冻结
- 外接语音编码器和解码器
- 优势：保留 LLM 文本能力，训练高效
- 劣势：全双工能力有限

### 方案四：全双工交互框架（原生方案）

代表：[[seeduplex]]
- 基于 LLM 底座的原生全双工交互框架
- 语音数据预训练 + RL
- 语音语义联合建模
- 关键能力原生融入训练体系

## 关键论文索引（按时间）

### 2024 年

| 论文 | arXiv ID | 团队 | 关键贡献 |
|------|----------|------|---------|
| Spirit LM | 2402.05755 | Meta | 交织语音-文本的基础模型，7B |
| VITA | 2408.05211 | 开源社区 | 首个开源交互式全模态 LLM，双模型 duplex 方案 |
| Mini-Omni | 2408.16725 | 开源 | 首个开源端到端实时语音交互模型 |
| Moshi | 2410.00037 | Kyutai | 首个实时全双工语音 LLM，多流架构，200ms 延迟 |
| LLaMA-Omni | 2409.06666 | 中科院 | 基于 LLaMA 的语音交互，ICLR 2025 |
| Baichuan-Omni | 2410.08565 | 百川 | 全模态理解+生成 |
| Mini-Omni2 | 2410.11190 | 开源 | 加入视觉，接近 GPT-4o |
| Freeze-Omni | 2411.00774 | 腾讯 | 冻结 LLM + 语音适配，低延迟 duplex |
| Seed-TTS | 2406.02430 | 字节 Seed | 大规模语音生成模型家族 |

### 2025 年

| 论文 | arXiv ID | 团队 | 关键贡献 |
|------|----------|------|---------|
| MinMo | 2501.06282 | 阿里 | 无缝语音交互多模态 LLM |
| Baichuan-Omni-1.5 | 2501.15368 | 百川 | 端到端音频生成 |
| SALM-Duplex | 2505.15670 | NVIDIA | 高效直接 duplex 建模，Interspeech 2025 |
| TurnGuide | 2508.07375 | 字节等 | 动态 turn-level 文本语音交织增强 FD 交互 |
| MTR-DuplexBench | 2511.10262 | CUHK 等 | 首个多轮全双工综合评测基准 |

### 2026 年

| 论文 | arXiv ID | 团队 | 关键贡献 |
|------|----------|------|---------|
| PersonaPlex | 2602.06053 | NVIDIA | 全双工对话模型的语音和角色控制 |
| Privacy-Preserving FD Speech | 2603.08179 | NTU+A*STAR | 首次研究全双工语音模型的隐私风险及匿名化 |
| Silent Thought (FLAIR) | 2603.17837 | NTU+Bengio | 首次引入 latent reasoning 到全双工语音 LLM |
| DuplexCascade | 2603.09180 | SB Intuitions | VAD-free 级联流水线，micro-turn 交互 |
| Full-Duplex-Bench-v3 | 2604.04847 | NTU+NVIDIA | 全双工语音 agent benchmark，含 tool use |
| ELLSA | ICLR 2026 | - | 首个全双工+视觉+语音+action 的端到端模型 |
| Seeduplex（博客） | - | 字节 Seed | 业界首个全双工语音大模型规模化落地 |

## 评测体系

- **VoiceBench**（2410.17196）：LLM-based 语音助手 benchmark
- **Full-Duplex-Bench-v3**（2604.04847）：全双工 + tool use 评测
- **Scale AI Voice Showdown**：业界偏好排行榜，GPT-4o Audio 领先（1102 Elo）
- **Seeduplex 内部评测**：判停 MOS、流畅度 MOS、人-人对比
- **[[mtr-duplexbench]]**（2511.10262）：首个多轮全双工综合评测（对话特征+质量+指令跟随+安全）

## 竞品格局

| 产品 | 团队 | 范式 | 状态 |
|------|------|------|------|
| GPT-4o Voice / Realtime API | OpenAI | 端到端语音 | 商用 |
| Gemini 3.1 Flash Live | Google | 端到端语音 | 商用 |
| Seeduplex（豆包） | 字节 Seed | 原生全双工 | 全量上线 |
| Moshi | Kyutai | 多流全双工 | 开源 |
| Grok Voice | xAI | - | 商用 |

## 开放问题

1. 全双工 + 多模态（视觉）融合仍是早期阶段
2. 隐私风险（always-on 音频流经 LLM backbone）
3. 多人对话场景能力不足
4. 整体流畅度仍与真人对话有差距
5. "边听边想"（latent reasoning while listening）刚起步
6. 全双工场景下的 tool use 能力缺乏 benchmark

## 相关页面

- [[seeduplex]] - 字节 Seed 全双工语音模型
- [[moshi]] - Kyutai 全双工语音对话模型
- [[freeze-omni]] - 冻结 LLM 的语音对话模型
- [[llama-omni]] - 基于 LLaMA 的语音交互
- [[minmo]] - 阿里无缝语音交互模型
- [[x-opd]] - 跨模态在线蒸馏
- [[on-policy-distillation]] - 在线蒸馏方法
- [[speech-llm]] - 语音大语言模型
- [[turnguide]] - TurnGuide 动态 turn-level 文本语音交织方法
- [[silent-thought]] - FLAIR 潜在推理全双工对话方法
- [[mtr-duplexbench]] - MTR-DuplexBench 多轮全双工综合评测基准
- [[duplex-cascade]] - DuplexCascade VAD-free 级联全双工方案
- [[privacy-preserving-speech]] - 全双工语音模型隐私保护
- [[stream-omni]] - 流式全双工语音交互模型
- [[audio-agent]] — Audio-Agent 训练管线设计
- [[duplex-agent-integration]] — 全双工 + Agent 融合架构
- [[audio-frontend-backend-balance]] — 声学前端与后端 ASR 的平衡
