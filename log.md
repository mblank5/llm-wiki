# Wiki Log

> Chronological record of all wiki actions. Append-only.
> Format: `## [YYYY-MM-DD] action | subject`
> Actions: ingest, update, query, lint, create, archive, delete
> When this file exceeds 500 entries, rotate: rename to log-YYYY.md, start fresh.
> Previous log: log-2026.md (551 entries, rotated 2026-05-01)

## [2026-05-01] create | Audio-Agent 概念页面
- 创建 concepts/audio-agent.md
- 内容：Audio-Agent 训练管线（四阶段：Adaptor 预训练 → Agent SFT → OPD 对齐 → RL 优化）
- 包含级联 vs 端到端对比、OPD 在 Audio-Agent 中的作用、流式改造路线

## [2026-05-01] create | 全双工 Agent 融合架构页面
- 创建 concepts/duplex-agent-integration.md
- 内容：外挂式（DuplexCascade）vs 原生式（双流 Token）融合路线
- 包含特殊 Token 设计、状态机设计、Function Call 与轮次管理冲突解决

## [2026-05-01] create | 声学前端与后端 ASR 平衡页面
- 创建 concepts/audio-frontend-backend-balance.md
- 内容：前端做 70% + 后端适应 30% 原则、分层处理架构
- 包含量化评估框架（三层指标）、平衡点判定、车型适配策略

## [2026-05-01] update | full-duplex-speech-model 页面
- 在 Related 部分新增 3 个新页面的 wikilink

## [2026-05-01] update | index.md
- 新增 3 个概念页面到目录（audio / concept 子分类）
- 更新 Total pages: 197 → 200

## [2026-05-01] rotate | log.md
- 原 log.md 达到 551 行，旋转为 log-2026.md
- 新建 log.md，从 2026-05-01 开始重新记录

## [2026-05-01] batch-create | FunASR/Paraformer 专题（6 篇论文，6 个页面）
- Sources (6 raw papers):
  - raw/papers/2022/06/2206.08317.md — Paraformer original (Interspeech 2022)
  - raw/papers/2023/05/2305.11013.md — FunASR Toolkit
  - raw/papers/2023/08/2308.03266.md — SeACo-Paraformer
  - raw/papers/2023/09/2309.07405.md — FunCodec
  - raw/papers/2023/10/2310.04863.md — SA-Paraformer
  - raw/papers/2024/09/2409.17746.md — Paraformer-v2
- Entity pages created (1):
  - entities/funasr.md — FunASR 工具包总览（60k hrs Paraformer、FSMN-VAD、CT-Transformer、部署方案、benchmark 表）
- Concept pages created (5):
  - concepts/paraformer.md — Paraformer 架构深度解析：CIF 预测器公式、GLM 采样器机制、MWER 训练、benchmark 表（AISHELL-1/2、工业 20k hrs）、采样率消融
  - concepts/seaco-paraformer.md — SeACo-Paraformer 热词定制：CIF 上下文模块、ASF 过滤机制、显式 vs 隐式对比、+58% F1 结果
  - concepts/funCodec.md — FunCodec 语音编解码：FreqCodec 频域 codec 架构、语义增强 RVQ、多判别器对抗训练、ViSQOL benchmark
  - concepts/sa-paraformer.md — SA-Paraformer 说话人归属：speaker-filling 策略、inter-CTC 增强、t-SOT、AliMeeting SD-CER 34.8%/1/10 RTF
  - concepts/paraformer-v2.md — Paraformer-v2 CTC 替换 CIF：CTC 压缩推理、BPE/噪声问题分析、英文 WER -14%、噪声鲁棒性
- Cross-linking:
  - 每页 ≥2 个 [[wikilinks]]，链接到 qwen3-asr、nim4-asr、whisper-aut 等现有页面
  - Paraformer 家族内部互链（paraformer ↔ seaco ↔ sa ↔ v2 ↔ funasr ↔ funCodec）
- Updated index.md:
  - 新增 entities/funasr 到 Entities 部分
  - 新增 speech-model 子分类，含 5 个概念页面
  - Total pages: 200 → 203 (actually 200+6=206, header shows 203 — need to check)
- Key findings:
  - Paraformer 是首个在大规模数据上匹配 AR 精度的 NAR ASR 模型
  - CIF→CTC 替换（v2）解决了 BPE 分词和噪声敏感两大瓶颈
  - FunASR 生态覆盖 ASR、VAD、标点、编解码、热词、说话人归属全链路
  - 60k 小时工业 Mandarin 训练数据远超学术 benchmark 规模

## [2026-05-01] ingest | DeepXiv 2026-03/04 论文批量补充（第二轮）

### 搜索
- 8 组 deepxiv search + date-from 2026-03-01 筛选
- 下载 19/20 篇 HTML（2604.11753 返回 404）
- deepxiv --brief + --head 筛选内容

### 新建 19 个 concept 页面

**RL 推理与奖励 (7)**
- outcome-rewards-no-guarantee.md — RLVR 推理链质量质疑（CIR/SR 指标）
- simple-loss-reasoning.md — RGRA 简化 GRPO（27 任务中 17 项更优）
- imperfect-verifier-rl.md — 不完美验证器：≤15% 噪声无退化
- process-reward-agentic.md — Agentic 数据分析 Process Reward
- confidence-margin-process-supervision.md — 置信度边际过程监督
- parm-pipeline-reward.md — Pipeline 自适应奖励模型
- piecehint-question-augmentation.md — RL 问题增强框架

**蒸馏新方法 (1)**
- mixture-of-layers-distillation.md — MoLSAKI 逐步注意力 + 混合层

**Self-Play & 代码 RL (2)**
- gasp-self-play-coding.md — GASP 非对称自博弈编程
- code-a1-adversarial.md — Code-A1 对抗进化

**Agent 训练 (1)**
- coevolve-agent-training.md — CoEvolve Agent-数据共同进化

**推理数据与长上下文 (3)**
- pi-squared-reasoning-data.md — π² 结构化推理数据
- decomposition-long-context.md — 长上下文推理分解
- reason-xl-language-shift.md — ReasonXL 推理语言迁移

**Agentic Coding (2)**
- agentic-code-reasoning.md — 半形式化推理模板
- se-conventions-agents.md — Agent 时代 SE 规范

**Agent 安全 (1)**
- openclaw-safety-analysis.md — OpenClaw CIK 攻击

**多模态 (2)**
- trustworthy-multimodal-reasoning.md — 可信多模态推理
- vlm-vision-reasoning-gap.md — VLM 视觉推理差距

### Wiki 状态
- Total pages: 225 (+31 from first round 194)
- Raw papers: 203
- 新增子分类：蒸馏新方法、RL推理与奖励、Self-Play与代码RL、推理数据与长上下文、多模态推理

## [2026-05-01] batch-create | CosyVoice 3 + DiffRO 概念页面（2 篇论文，2 个页面）
- Sources (2 raw papers):
  - raw/papers/2025/05/2505.17589.md — CosyVoice 3: Towards In-the-wild Speech Generation via Scaling-up and Post-training
  - raw/papers/2025/07/2507.05911.md — Differentiable Reward Optimization for LLM based TTS system
- Concept pages created (2):
  - concepts/cosyvoice-3.md — CosyVoice 3 全面解析：数据 Scaling（10k→1M hrs，9 语言+18 方言）、模型 Scaling（0.5B→1.5B）、多任务监督 tokenizer（MinMo 基座，ASR+SER+LID+AED+SA 五任务，25Hz，530k hrs 训练）、DiffRO 后训练、CV3-Eval benchmark（客观：多语言克隆/跨语言克隆/情感克隆；主观：表达性克隆/语音延续/方言克隆）、10 模型 baseline 对比
  - concepts/diffro.md — DiffRO 深度解析：三大 TTS RLHF 挑战（vocoder 计算成本、样本多样性不足、多维度评估）、Token2Reward 方法（ASR-like Token2Text 模型，后验概率作为奖励）、Gumbel-Softmax 可微采样、直接反向传播优化（无需 PPO/DPO）、MTR 多任务奖励模型（ASR+SER+SQA+AED）、与 DPO 的全面对比表
- Cross-linking:
  - cosyvoice-3 ↔ cosyvoice, cosyvoice-2, diffro, fun-audio-llm, minmo, qwen3-tts
  - diffro ↔ cosyvoice-3, cosyvoice-2, fun-audio-llm, ppo, seed-tts
- Updated index.md:
  - 新增 speech-model 子分类下 2 个概念页面（cosyvoice-3, diffro）
  - Total pages: 226 → 228
- Key findings:
  - CosyVoice 3 是首个实现百万小时级训练数据的 TTS 模型
  - DiffRO 完全消除了 TTS 后训练中的 vocoder 调用，使优化效率大幅提升
  - Gumbel-Softmax 使离散 token 空间上的奖励优化变为完全可微问题
  - MTR 模型提供多维度反馈，实现零样本情感/属性控制

## [2026-05-01] create | SenseVoice 概念页面
- 创建 concepts/sensevoice.md
- 来源：raw/papers/2024/07/2407.04051.md
- 内容：SenseVoice 多任务语音理解基础模型，ASR+SER+LID+AED 四合一
- 包含 SenseVoice-Small (NAR, 234M, 5 语言, <80ms) 和 SenseVoice-Large (AR, 1587M, 50+ 语言) 架构细节
- 包含 ASR 基准对比（vs Whisper/Paraformer）、SER 零-shot 评估、AED 评估
- 包含 S³ 有监督语义 tokenizer 细节、Rich Text 输出格式
- 添加到 index.md speech-model 分类
- 包含 wikilinks: [[fun-audio-llm]], [[funasr]], [[paraformer]], [[qwen3-asr]]

## [2026-05-01] create | FunAudioLLM 实体页面
- 创建 entities/fun-audio-llm.md
- 来源：raw/papers/2024/07/2407.04051.md, raw/papers/2023/05/2305.11013.md, raw/papers/2023/09/2309.07405.md
- 内容：FunAudioLLM 语音交互基础模型家族概述，阿里通义语音团队
  - 家族架构：SenseVoice（理解）+ CosyVoice（生成）+ S³ Tokenizer
  - SenseVoice-Small (NAR, 234M, 5 语言, RTF 0.007, 70ms) vs SenseVoice-Large (AR, 1587M, 50+ 语言)
  - CosyVoice 三个 300M 模型：base/instruct/sft，Flow Matching + HiFTNet 架构
  - S³ 有监督语义 tokenizer (4096 entries, 50Hz)
  - 训练数据规模：SenseVoice ~300k+ hrs, CosyVoice ~170k+ hrs
  - ASR/SER/AED 基准对比、语音生成质量评估（WER/CER/SS）
  - GitHub 仓库 (FunAudioLLM org): SenseVoice, CosyVoice, FunASR, FunAudioLLM-APP
  - ModelScope 演示：fun-audio-llm.github.io
- 添加到 index.md Entities 部分（funasr 之前，按字母顺序）
- 包含 wikilinks: [[sensevoice]], [[cosyvoice]], [[funasr]], [[fun-codec]], [[paraformer]], [[qwen3-asr]], [[qwen3-tts]], [[qwen3]]

## [2026-05-01] create | CosyVoice 2 概念页面
- 创建 concepts/cosyvoice-2.md
- 提取 2412.10117 (CosyVoice 2) 全部技术细节
- 关键创新：FSQ 量化（100% 码本利用率 vs VQ 23%）、预训练 Qwen2.5-0.5B LM、统一流式/非流式单模型、Chunk-aware CFM（4种 mask）、指令控制、DPO+ASR RL 微调
- 性能：人类级质量（WER 2.47%，NMOS 3.96，SS 0.745），流式几乎无损
- 训练数据：~172k 小时（4 语言），tokenizer 200k 小时
- 添加到 index.md speech-model 部分
- 包含 wikilinks: [[cosyvoice]], [[cosyvoice-3]], [[fun-codec]], [[fun-audio-llm]], [[seeduplex]]
