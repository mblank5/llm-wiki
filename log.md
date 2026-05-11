# Wiki Log

> Chronological record of all wiki actions. Append-only.
> Format: `## [YYYY-MM-DD] action | subject`
> Actions: ingest, update, query, lint, create, archive, delete
> When this file exceeds 500 entries, rotate: rename to log-YYYY.md, start fresh.
> Previous log: log-2026.md (551 entries, rotated 2026-05-01)

## [2026-05-11] create | MTP vs EAGLE 知识固化
|- 创建 concepts/mtp.md — Multi-Token Prediction 概念页（原生内置、预训练、中间层预测头）
|- 创建 concepts/eagle-speculative-decoding.md — EAGLE 概念页（外挂 Draft Model、后训练、KV Cache 复用）
|- 创建 entities/qwen3.5.md — Qwen3.5 实体页（Hybrid Linear Attention、MTP-1 支持、Eagle3 不支持原因）
|- 创建 comparisons/mtp-vs-eagle.md — MTP vs EAGLE 对比页（内生 vs 外挂、接受率 vs 开销）
|- 更新 index.md — 添加新页面到 Entities, Concepts (inference-optimization), Comparisons 章节
|- 技术深度：包含 Linear Attention 状态回滚限制、框架支持现状 (vLLM/SGLang)、性能数据

## [2026-05-09] create | OpenSeeker-v2 概念页面（深度分析）
- 源文件: /tmp/papers/2605.04036.txt
- 创建 concepts/openseeker-v2.md — 深度分析 arXiv 2605.04036
- 保存 raw/papers/2026/05/2605.04036.md
- 内容覆盖：
  - 核心问题定义：挑战 CPT+SFT+RL 重型管线，证明纯 SFT+高质量数据足以匹敌工业方案
  - 方法详解：三大修改（图谱扩展 K>k、工具集扩展、严格低步过滤 T≥T_min）
  - 完整公式：G_sub^(K) = Expand(G, v_seed, K)、q ~ P_gen(q | G_sub^(K))、D_v2 过滤公式
  - 完整实验表：BrowseComp 46.0%, BC-ZH 58.1%, HLE 34.6%, xbench 78.0%
  - 对比基线：vs Tongyi DeepResearch、RedSearcher、WebSailor、WebLeaper 及闭源模型
  - 训练配置：Qwen3-30B-A3B、256k ctx、10.6k 样本、纯 SFT
  - 批判性分析：7 项不足/疑问、5 项启发
- 更新 index.md: +1 条目（tool-use 分类）
- 包含 wikilinks: [[agenticqwen-dual-flywheel]], [[ragegen-multi-turn-rl-agents]], [[grpo-rl-training]], [[rl-conductor]], [[on-policy-distillation]]

## [2026-05-09] create | Horizon Length Training Study 概念页面
- arXiv: 2605.02572 | Kim et al.
- 创建 concepts/horizon-length-training-study.md（深度分析级别）
- 内容：horizon length 作为 RL 训练独立瓶颈的实证研究，Horizon Reduction 方法（macro actions / subgoal decomposition），完整实验表格（Sudoku + Rush Hour 跨 horizon 评估），训练配置，对 GRPO/PPO/后训练的启发
- 更新 index.md（添加到 rl 分类下）

## [2026-06-07] ingest | MoshiRAG: Asynchronous Knowledge Retrieval for Full-Duplex Speech Language Models
- arXiv: 2604.12928 | Kyutai Labs
- Created: `concepts/moshirag.md` (full deep analysis)
- Saved: `raw/papers/2026/04/2604.12928.md`
- Updated: `index.md` (added moshi rag entry under full-duplex section)
- Key: First full-duplex + RAG system, keyword delay exploitation, async retrieval, plug-and-play backends
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

## [2026-05-05] ingest | Weekly trending papers 深度调研入库 (13篇)
- 创建 concepts/agentic-harness-engineering.md — AHE: 可观测性驱动的 coding-agent harness 自动演化
- 创建 concepts/contextual-agentic-memory.md — 理论批判 agentic memory 本质是备忘录非真记忆
- 创建 concepts/recursive-multi-agent-systems.md — RecursiveMAS: 潜空间递归多智能体框架
- 创建 concepts/ssl-skill-representation.md — SSL: 三层结构化 Agent 技能表示
- 创建 concepts/rl-conductor.md — RL Conductor: RL 训练 LM 动态编排 worker LLM
- 创建 concepts/self-improving-pretraining.md — RL 预训练: suffix rewriting 提升事实性和安全性
- 创建 concepts/tachiom.md — Token-Aware Clustering 替代 κ-means，检索提速 9.8×
- 创建 concepts/stochastic-kv-routing.md — R-CLA: KV cache 共享，显存减少 50-75%
- 创建 concepts/second-order-collapse.md — 二阶坍塌量化，解释 mean pooling 有效性
- 创建 concepts/agent-native-research-artifacts.md — Ara: agent-native 可执行研究产物格式
- 创建 concepts/agentic-rec-tune.md — 多 Agent + 自进化 Skillhub 优化推荐系统
- 创建 concepts/negative-data-mining-ikea.md — IKEA 负采样实验，揭示 offline-online 差距
- 创建 concepts/realm-retrieve.md — ReaLM-Retrieve: 推理步级别按需检索
- 来源: deepxiv trending --days 7 (2026-04-28 ~ 2026-05-05)
- 更新 index.md: +13 条目，更新总页数

## [2026-05-02] ingest | Trending papers 深度调研入库 (5篇)
- 创建 concepts/co-evolving-policy-distillation.md — CoPD: 并行 RLVR + 双向 OPD 交错训练，专家互为师生
- 创建 concepts/latent-agents-imad.md — IMAD: 两阶段后训练将多 agent 辩论蒸馏到单模型，93% token 节省
- 创建 concepts/agentic-world-modeling.md — 三层次世界模型框架 (L1→L2→L3)，跨物理/数字/社会/科学领域
- 创建 concepts/agenticqwen-dual-flywheel.md — 双数据飞轮训练小型 agentic 模型，行为树扩展
- 创建 concepts/cos-play-co-evolving-agents.md — COS-PLAY: LLM 决策 agent + skill bank 协同演化，多 LoRA GRPO
- 保存 raw papers: 2604.27083 (pdf), 2604.24881 (md), 2604.22748 (md), 2604.21590 (md), 2604.20987 (pdf)
- 更新 index.md: +5 条目，更新页数和 raw paper 计数

## [2026-05-05] create | MiniCPM-o 4.5 全双工 Omni-Modal 模型页面
- 创建 concepts/minicpm-o-4-5.md — 深度分析论文 arXiv:2604.27393
- 内容覆盖：Omni-Flow 时间对齐流式框架、TAIL 语音交错策略、四阶段训练流程、完整 benchmark 结果（视觉-语言/语音/全双工/文本）、边缘部署效率（llama.cpp-omni）、批判性分析
- 更新 index.md: +2 条目（entities + concepts/audio 各一个）
- 来源: /tmp/papers/2604.27393.html（论文 HTML 提取）
