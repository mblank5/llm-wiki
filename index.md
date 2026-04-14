# Wiki Index

> Content catalog. Every wiki page listed under its type with a one-line summary.
> Read this first to find relevant pages for any query.
> Last updated: 2026-04-15 | Total pages: 107 | Raw papers: 71

## Entities

- [[byte-seed]] — 字节跳动 Seed AI 研究团队，Seeduplex/Seed-TTS 所属团队
- [[composer2]] — Cursor Composer 2：基于 Kimi K2.5 的 1.04T/32B MoE agentic coding 模型（2026-03）
- [[emova]] — EMOVA：CVPR 2025，语义-声学分离 tokenizer，首个 VLM+Speech 双 SOTA
- [[freeze-omni]] — 腾讯 Freeze-Omni：冻结 LLM 参数实现 speech-to-speech 对话和 duplex
- [[llama-omni]] — 中科院 LLaMA-Omni：基于 LLaMA-3.1 的语音交互，ICLR 2025
- [[mgm-omni]] — MGM-Omni：Brain-Mouth 双轨 Omni LLM，长音频理解 + 个性化语音生成
- [[minmo]] — 阿里 MinMo：无缝语音交互多模态 LLM
- [[moshi]] — Kyutai Moshi：首个实时全双工语音 LLM，多流架构，200ms 延迟
- [[qwen3]] — Qwen3 开源 LLM 系列，支持 Thinking/Non-Thinking 切换，含 MoE 架构
- [[qwen3-asr]] — Qwen3-ASR：52 语言 ASR 家族（1.7B/0.6B + ForcedAligner），基于 Qwen3-Omni
- [[qwen3-omni]] — Qwen3-Omni：Thinker-Talker MoE 统一多模态模型，234ms 流式延迟
- [[qwen3-tts]] — Qwen3-TTS：双轨 TTS（25Hz/12Hz），97ms 首包，3秒语音克隆
- [[salmonn-omni]] — SALMONN-omni：Codec-free 全双工语音模型，embedding-based
- [[seed-realtime-voice]] — Seed Realtime Voice：豆包前代半双工端到端语音模型
- [[seed-tts]] — Seed-TTS：字节 Seed 大规模自回归 TTS 模型家族（2024-06）
- [[seeduplex]] — Seeduplex：字节 Seed 原生全双工语音大模型（2026-04）
- [[stream-omni]] — Stream-Omni：CTC layer-dimension 语音-文本对齐，数据高效
- [[doubao-app]] — 豆包 App：字节跳动 AI 助手应用，Seeduplex 全双工语音部署平台
- [[kimi-k2]] — Kimi K2：Moonshot AI 大语言模型，Composer 2 基座模型
- [[speech-omni-lite]] — Speech-Omni-Lite：轻量级 VLM 语音交互接口

## Concepts

### 蒸馏与后训练 (Distillation & Post-Training)
- [[on-policy-distillation]] — On-Policy Distillation 核心概念：student rollout + teacher feedback，bias-variance tradeoff
- [[on-policy-distillation-survey]] — OPD 综述：f-divergence 统一框架、白盒/黑盒方法分类
- [[on-policy-prefix-distillation]] — OPPD：计算高效的 on-policy 前缀蒸馏变体
- [[on-policy-self-distillation]] — 自蒸馏推理：无需外部 teacher 的 on-policy 方法
- [[generalized-on-policy-distillation]] — G-OPD：带奖励外推的泛化 on-policy 蒸馏
- [[dual-policy-distillation]] — DPD：Student-Student 对偶策略蒸馏框架

- [[proximal-policy-distillation]] — PPD：结合 PPO 思想的 per-token KL 裁剪蒸馏
- [[per-token-kl-clipping]] — Per-token KL 裁剪技术详解
- [[policy-distillation]] — Policy Distillation 基础概念（DeepMind 2015 开山作）
- [[model-distillation]] — 模型蒸馏通用概念与分类
- [[exposure-bias]] — 暴露偏差：训练-推理分布不一致问题
- [[entropy-aware-on-policy-distillation]] — 熵感知 OPD：动态 divergence 自适应
- [[reopold]] — ReOPOLD：高效推理扩展的 relaxed on-policy 蒸馏
- [[cascade-rl]] — Cascade RL：级联强化学习用于多域 post-training
- [[token-level-entropy-analysis]] — Token 级别熵分析：理解蒸馏中的信息流动
- [[sample-routed-policy-optimization]] — SRPO：统一 GRPO 强化 + SDPO 蒸馏的样本路由框架，熵感知动态加权
- [[rl-aware-distillation]] — RLAD：强化学习感知蒸馏，仅当有益时模仿 teacher（TRRD 目标）
- [[hybrid-distillation-policy-optimization]] — HDPO：特权自蒸馏针对"悬崖 prompt"，共享权重 teacher/student
- [[on-policy-self-distillation-reasoning-compression]] — OPSDC：推理压缩的自蒸馏，"be concise" 条件化 teacher
- [[chain-of-thought]] — Chain-of-Thought (CoT)：逐步推理 prompting 技术，现代推理模型基础
- [[deepseek-r1-distillation]] — DeepSeek R1 蒸馏：将推理能力蒸馏到小模型的方法
- [[ex-opd]] — Ex-OPD：带奖励外推的扩展 On-Policy Distillation 变体
- [[free-process-rewards]] — Free Process Rewards：无需人工标注的 process-level RL 奖励信号
- [[kl-divergence-in-distillation]] — KL 散度在蒸馏中的角色：f-divergence 统一框架下的核心度量
- [[knowledge-distillation]] — 知识蒸馏 (Knowledge Distillation)：Hinton 2015 奠基性概念
- [[mixture-of-experts]] — Mixture of Experts (MoE)：路由 token 到不同专家子网络的高效架构
- [[multi-domain-on-policy-distillation]] — 多域 On-Policy Distillation：跨任务域的同时蒸馏
- [[reasoning-distillation]] — 推理蒸馏：将推理能力（尤其 CoT）从 teacher 迁移到 student
- [[reverse-kl-distillation]] — Reverse KL 蒸馏：mode-seeking 方向的 KL 散度蒸馏
- [[self-play-limitations]] — Self-play 局限性：RL/蒸馏中自博弈方法的约束与失败模式
- [[star]] — STaR (Self-Taught Reasoner)：自生成推理 trace 的自改进方法
- [[strong-to-weak-distillation]] — Strong-to-weak 蒸馏：大模型向小模型的能力迁移范式
- [[teacher-top-k-local-support-matching]] — Teacher top-k 局部支持匹配：聚焦 top-k token 的蒸馏技术
- [[thinking-budget]] — Thinking Budget：推理模型的计算分配/思考深度控制

### 强化学习基础 (RL Foundations)
- [[ppo]] — PPO：Proximal Policy Optimization，策略梯度核心算法
- [[stable-baselines3]] — Stable Baselines3：RL 算法开源工具库
- [[atari-2600]] — Atari 2600：经典 RL 基准环境（ALE），DQN/Policy Distillation 标准测试
- [[deep-q-network]] — DQN (Deep Q-Network)：深度 RL 值方法，DeepMind 2015
- [[grp-o]] — GRPO (Group Relative Policy Optimization)：组内相对奖励策略优化，现代 LLM 后训练核心
- [[grpo-rl-training]] — GRPO RL Training：基于 GRPO 的强化学习训练方法论
- [[imitation-learning]] — Imitation Learning：从专家示范中学习，SFT 的 RL 视角
- [[interactive-imitation-learning]] — Interactive IL：通过交互式专家查询解决暴露偏差
- [[multi-task-learning]] — Multi-Task Learning：多任务同时训练共享表示的范式
- [[reinforcement-learning-from-human-feedback]] — RLHF：基于人类反馈的强化学习对齐方法

### 语音与多模态 (Speech & Multimodal)
- [[full-duplex-speech-model]] — 全双工语音模型：概念、架构方案、竞品格局（2024-2026）
- [[omni-modal-llm]] — Omni-Modal LLM：统一 text+vision+audio+speech 模型范式，架构/性能对比矩阵
- [[turnguide]] — TurnGuide：文本引导的动态 turn-level 全双工交互
- [[silent-thought]] — Silent Thought/FLAIR：全双工对话中的潜在推理（think-while-listening）
- [[mtr-duplexbench]] — MTR-DuplexBench：多轮全双工语音模型综合评测框架
- [[duplex-cascade]] — DuplexCascade：无 VAD 的级联 ASR-LLM-TTS 全双工管道
- [[privacy-preserving-speech]] — 全双工端到端语音模型的隐私保护
- [[x-opd]] — X-OPD：跨模态 on-policy 蒸馏，将 Text LLM 能力迁移到 Speech LLM
- [[video-opd]] — Video-OPD：视频时序 grounding 的 on-policy 蒸馏
- [[vold]] — VOLD：Vision-Language on-policy 蒸馏推理迁移
- [[speech-llm]] — Speech LLM 概念：语音大语言模型架构与挑战
- [[tvdf]] — TVDF (Temporal Video Distillation Framework)：视频时序蒸馏框架


|### Agent 记忆与安全 (Agent Memory & Safety)
|- [[hypermem]] — HyperMem：超图记忆架构，topic/episode/fact 三层 + hyperedge 高阶关联
|- [[memreader]] — MemReader：从被动到主动的记忆提取，GRPO 训练 ReAct 式记忆管理决策
|- [[lightmem-agent-memory]] — LightMem：SLM 驱动轻量记忆系统，STM/MTM/LTM 三层
|- [[pask-proactive-agent]] — PASK：意图感知主动 Agent，DD-MM-PAS 流式框架
|- [[saver-faithful-reasoning]] — SAVeR：Agent 自审计验证推理，行动前验证内部信念状态
|- [[agent-supply-chain-attack]] — LLM Agent 供应链攻击：第三方 API router 的恶意注入与凭证窃取
|
### Agentic Coding
- [[agentic-coding]] — Agentic Coding：AI Agent 自主完成软件工程任务的模式与训练方法
- [[cursorbench]] — CursorBench：从真实 Cursor 会话提取的 agentic SWE 评测套件

### 模型行为与安全 (Behavior & Safety)
- [[behavioral-self-awareness]] — 行为自意识：LLM 能描述自身隐式学习到的行为
- [[emergent-misalignment]] — 涌现性失准：misaligned 模型展现行为自意识，realignment 后自评逆转
- [[mental-self-modeling]] — LLM 心理自我建模：Theory-of-Mind 测试中的选择性缺陷
- [[ai-self-awareness-game-theory]] — 博弈论测量 AI 自意识：AISAI 框架，Self >> Other AI >> Human 层级
- [[backdoor-awareness]] — Backdoor Awareness：LLM 检测/描述训练数据中后门触发器的能力
- [[introspection]] — Introspection：LLM 审视和报告自身内部决策过程的能力
- [[out-of-context-reasoning]] — Out-of-Context Reasoning (OOCR)：基于训练时习得知识进行推理，无需上下文示例
- [[situational-awareness]] — Situational Awareness：AI 系统理解自身上下文、状态和部署环境的能力

## Comparisons

## Queries

- [[qwen3-opd-usage]] — Qwen3 中的 OPD 做法：strong-to-weak logits 蒸馏，GPU 耗时降至 1/10
- [[qwen3-tech-overview]] — Qwen3 技术要点总览：架构、预训练、后训练四阶段、思维预算
- [[qwen3-voice-family-deep-dive]] — Qwen3 语音家族深度解析：技术传承链、竞品定位、架构演进
- [[opd-tokenizer-requirement]] — OPD 是否要求 student/teacher 同一 tokenizer？X-OPD 是反例
- [[opd-vs-sft]] — OPD vs SFT 指标差距：Qwen3 系列上 +5~7.6 Avg@12，训练效率提升 64x

## Raw Sources (71 papers)

### 蒸馏与后训练 (20)
- `raw/papers/2015/11/1511.06295.md` — Policy Distillation (DeepMind 2015)
- `raw/papers/2020/06/2006.04061.md` — Dual Policy Distillation
- `raw/papers/2024/07/2407.15134.md` — Proximal Policy Distillation
- `raw/papers/2025/05/2505.09388.md` — Qwen3 Technical Report
- `raw/papers/2025/10/2510.23497.md` — VOLD
- `raw/papers/2026/01/2601.18734.md` — Self-Distilled Reasoner
- `raw/papers/2026/02/2602.02994.md` — Video-OPD
- `raw/papers/2026/02/2602.12125.md` — Generalized OPD
- `raw/papers/2026/02/2602.15260.md` — On-Policy Prefix Distillation
- `raw/papers/2026/02/2602.22495.md` — RLAD: RL-aware Knowledge Distillation
- `raw/papers/2026/03/2603.07079.md` — Entropy-Aware OPD
- `raw/papers/2026/03/2603.05433.md` — OPSDC: On-Policy Self-Distillation for Reasoning Compression
- `raw/papers/2026/03/2603.11137.md` — Relaxed OPD
- `raw/papers/2026/03/2603.19220.md` — Nemotron Cascade 2
- `raw/papers/2026/03/2603.23871.md` — HDPO: Hybrid Distillation Policy Optimization
- `raw/papers/2026/03/2603.24596.md` — X-OPD
- `raw/papers/2026/03/2603.25562.md` — Failures and Fixes of OPD
- `raw/papers/2026/04/2604.00626.md` — A Survey of OPD for LLMs
- `raw/papers/2026/04/2604.02288.md` — SRPO: Sample-Routed Policy Optimization (GRPO+SDPO)

### 模型行为与安全 (4)
- `raw/papers/2025/01/2501.11120v1.md` — LLM Behavioral Self-Awareness
- `raw/papers/2025/11/2511.00926.md` — AI Self-Awareness via Game Theory
- `raw/papers/2026/02/2602.14777.md` — Emergently Misaligned LMs Show Behavioral Self-Awareness
- `raw/papers/2026/03/2603.26089.md` — Selective Deficits in LLM Mental Self-Modeling

### 语音模型与 Speech LLM (32)
- `raw/papers/2023/11/2311.07919.md` — Qwen-Audio: Universal Audio Understanding
- `raw/papers/2024/02/2402.05755.md` — Spirit-LM: Interleaved Speech-Text Foundation Model
- `raw/papers/2024/06/2406.02430.md` — Seed-TTS: Speech Generation via Diffusion
- `raw/papers/2024/08/2408.05211.md` — VITA: Multimodal LLM for Speech/Vision
- `raw/papers/2024/08/2408.16725.md` — Mini-Omni: Language Model Hearing While Speaking
- `raw/papers/2024/09/2409.06666.md` — LLaMA-Omni: Seamless Speech Interaction
- `raw/papers/2024/09/2409.18042.md` — EMOVA: Emotionally Omni-present Voice Assistant
- `raw/papers/2024/10/2410.00037.md` — Moshi: Real-Time Full-Duplex Speech LLM
- `raw/papers/2024/10/2410.08565.md` — Baichuan-Omni
- `raw/papers/2024/10/2410.11190.md` — Mini-Omni2: Vision/Text/Speech
- `raw/papers/2024/10/2410.17196.md` — VoiceBench: Speech LLM Evaluation
- `raw/papers/2024/11/2410.00037.md` — Moshi: Real-Time Full-Duplex Speech LLM
- `raw/papers/2024/11/2411.00774.md` — Freeze-Omni: Freeze LLM for Speech Dialog
- `raw/papers/2024/11/2411.18138.md` — SALMONN-omni: Codec-free Full-duplex Speech
- `raw/papers/2025/01/2501.06282.md` — MinMo: Seamless Multimodal Speech LLM
- `raw/papers/2025/05/2505.13880.md` — U-SAM: Unified Speech Audio Music
- `raw/papers/2025/05/2505.15670.md` — SALM-Duplex: Streaming Audio LLM Duplex
- `raw/papers/2025/06/2506.13642.md` — Stream-Omni: Simultaneous Multimodal Interactions
- `raw/papers/2025/08/2508.07375.md` — TurnGuide: Text-Guided Full-Duplex Interaction
- `raw/papers/2025/09/2509.17765.md` — Qwen3-Omni Technical Report
- `raw/papers/2025/09/2509.25131.md` — MGM-Omni: Scaling Omni LLMs
- `raw/papers/2025/11/2511.10262.md` — MTR-DuplexBench: Multi-Round Full-Duplex Eval
- `raw/papers/2026/01/2601.04720.md` — Qwen3-VL-Embedding and Qwen3-VL-Reranker
- `raw/papers/2026/01/2601.09536.md` — Omni-R1: Unified Generative Multimodal Reasoning
- `raw/papers/2026/01/2601.10323.md` — ROMA: Real-time Omni-Multimodal Assistant
- `raw/papers/2026/01/2601.15621.md` — Qwen3-TTS Technical Report
- `raw/papers/2026/01/2601.21337.md` — Qwen3-ASR Technical Report
- `raw/papers/2026/02/2602.06053.md` — PersonaPlex: Multimodal Persona
- `raw/papers/2026/03/2603.08179.md` — Privacy-Preserving Full-Duplex Speech
- `raw/papers/2026/03/2603.09180.md` — DuplexCascade: VAD-Free Cascaded Pipeline
- `raw/papers/2026/03/2603.09627.md` — Speech-Omni-Lite: Portable Speech Interfaces
- `raw/papers/2026/03/2603.17837.md` — Silent Thought: Latent Reasoning in Full-Duplex Dialogue
- `raw/papers/2026/04/2604.04847.md` — Full-Duplex-Bench-v3
