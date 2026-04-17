# Wiki Index

> Content catalog. Every wiki page listed under its type with a one-line summary.
> Read this first to find relevant pages for any query.
> Last updated: 2026-04-17 | Total pages: 153 | Raw papers: 167

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
- [[mem0]] — Mem0：AI Agent 可扩展长期记忆层，YC S24，53K stars，图记忆+自然语言双模式
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
- [[on-policy-self-distillation-reasoning-compression]]
- [[scope-opd]] — SCOPE：Signal-Calibrated OPD，双路径自适应加权蒸馏，Avg@32 +11.42%
- [[skill-sd]] — Skill-SD：Skill-Conditioned Self-Distillation for Multi-turn Agents — OPSDC：推理压缩的自蒸馏，"be concise" 条件化 teacher
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
- [[llm-post-training-unified-view]] — LLM 后训练统一视角：off-policy/on-policy 双主线 + 三功能角色框架
- [[g2rpo]] — G²RPO：Gaussian GRPO，1D Optimal Transport distributional matching
- [[faithful-grpo]] — Faithful GRPO：约束策略优化，解决 RLVR accuracy-faithfulness 矛盾
- [[ttvs]]
- [[agent2-rl-bench]] — Agent² RL-Bench：LLM Agent 自主设计 RL pipeline 的评测基准
- [[policy-split]] — Policy Split：LLM RL 中的双模式探索策略 — TTVS：Test-Time Variational Synthesis，无标注 test-time RL self-evolving
- [[reflectrm]] — ReflectRM：自反思增强生成式 Reward Model，response+analysis 双偏好
- [[opd-autonomous-driving]] — On-Policy Distillation 自动驾驶运动规划（GPT-Driver + GKD）
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

- [[wrap-plus-plus]]
- [[rag-considerate-pretraining]] — RAG-aware 预训练 scaling laws，memorization vs retrieval 平衡
- [[scalable-moe-pretraining]] — Aurora 超算 MoE LLM 大规模预训练工程 — WRAP++：跨文档发现增强预训练，8.4B→80B tokens QA
- [[llm-training-as-lossy-compression]] — LLM 训练即有损压缩，Information Bottleneck 两阶段
- [[omnijigsaw]] — OmniJigsaw：Qwen3-Omni RL 后训练，时间重排自监督
- [[omni-r1]] — Omni-R1：统一生成式多模态推理（推理中生成中间图像） — OmniJigsaw：Qwen3-Omni RL 后训练，时间重排自监督代理任务
- [[audiokv]]
- [[audio-omni]] — Audio-Omni：首个统一音频理解+生成+编辑框架，Frozen MLLM + DiT
- [[whisper-aut]] — Whisper-AuT：基于 Whisper 的领域适配音频编码器
- [[supernova]] — SUPERNOVA：自然指令 RL 激发 LLM 通用推理能力
- [[perception-grounded-po]] — Perception-Grounded PO：token 级感知区分策略优化
- [[visually-guided-po]] — Visually-Guided PO：视觉引导的多模态推理策略优化
- [[svsr]] — SVSR：多模态推理的自验证自修正范式
- [[multimodal-latent-reasoning]]
- [[visual-depth-scaling]] — Visual Depth Scaling：多模态潜在推理的视觉增强深度缩放
- [[pseudo-unification-entropy]] — Pseudo-Unification：熵探测揭示统一多模态模型的信息分歧 — Latent Reasoning：连续 embedding 空间的潜在推理 — AudioKV：音频大模型 KV Cache 驱逐策略

### Agent 记忆与安全 (Agent Memory & Safety)
- [[agent-memory-system]] — Agent Memory System 总览：LLM Agent 长期记忆方案分类与对比
- [[hypermem]] — HyperMem：超图记忆架构，topic/episode/fact 三层 + hyperedge 高阶关联
- [[memreader]] — MemReader：从被动到主动的记忆提取，GRPO 训练 ReAct 式记忆管理决策
- [[lightmem-agent-memory]]
- [[memgpt]] — MemGPT：LLM-as-OS 层级记忆架构（main/external context 自主管理）
- [[locomo-benchmark]] — LoCoMo：长期对话记忆评测基准，多会话 7,512 QA 对
- [[longmemeval-benchmark]] — LongMemEval：Chat Assistant 长期交互记忆评测，5 核心能力维度
- [[a-mem]] — A-MEM：Zettelkasten 启发的 Agentic Memory，LLM 属性标注+自主链接
- [[simplemem]] — SimpleMem：语义压缩三阶段记忆管线，LoCoMo 43.24 F1 仅 531 token
- [[d-mem]] — D-Mem：双过程记忆系统（System 1 快速 + System 2 深度），53.5 F1
- [[memoryllm]] — MEMORYLLM：Transformer 内部潜在记忆池（1B 参数），20K token 保留
- [[m-plus-memoryllm]] — M+：扩展 MemoryLLM 的 CPU 常驻长期记忆 + 共训练检索器
- [[nemori]] — Nemori：认知科学启发的预测误差驱动记忆蒸馏，45-64% 存储压缩
- [[text2mem]] — Text2Mem：统一记忆操作语言（12 动词），JSON schema + 验证管线
- [[ariadne-mem]] — AriadneMem：进化图 + 冲突感知粗化 + Steiner Tree 桥发现
- [[memori-layer]] — Memori：LLM-agnostic API 层持久记忆，语义三元组 + 对话摘要
- [[self-evolving-memory]] — Self-Evolving Memory：跨异构任务的 LLM 记忆自进化 — LightMem：SLM 驱动轻量记忆系统，STM/MTM/LTM 三层
- [[pask-proactive-agent]] — PASK：意图感知主动 Agent，DD-MM-PAS 流式框架
- [[saver-faithful-reasoning]] — SAVeR：Agent 自审计验证推理，行动前验证内部信念状态
- [[agent-supply-chain-attack]]
- [[clawguard]] — ClawGuard：Tool-Augmented Agent 运行时安全框架 — LLM Agent 供应链攻击：第三方 API router 的恶意注入与凭证窃取
|

### 数据工程 (Data Engineering)
- [[blendfusion]] — BlendFusion：可扩展扩散模型合成数据生成
- [[data-laundering-llm]] — Data Laundering：LLM 训练中的数据洗白攻击与防御
- [[rl-guided-synthetic-data]] — RL 引导的合成数据生成（隐私保护 + 效用最大化）
- [[optimsyn]]
- [[polyglot-teachers]] — Polyglot Teachers：多语言合成数据生成评估
- [[llm-prism]] — LLM-PRISM：GPU 故障导致 LLM 训练中的静默数据损坏 — Optimsyn：Influence-guided rubrics 优化合成数据质量

### Agentic Coding
- [[agentic-coding]] — Agentic Coding：AI Agent 自主完成软件工程任务的模式与训练方法
- [[cursorbench]]
- [[oracle-swe]] — ORACLE-SWE：量化 oracle 信息对 SWE Agent 解决率的贡献分解
- [[swe-hero]] — SWE-ZERO→SWE-HERO：从 execution-free 到 execution-based SWE Agent 训练
- [[less-is-more-agentic]] — Even Less Is Even Better：Agentic/Reasoning/Coding LLM 训练效率
- [[rethinking-se-for-agentic-ai]]
- [[swe-agile]] — SWE-AGILE：SWE Agent 动态推理上下文管理
- [[swe-shepherd]] — SWE-Shepherd：Process Reward Models for Code Agents
- [[epistemological-self-learning]] — 认识论驱动的 LLM 自学习对话 — Rethinking SE for Agentic AI：Agent 时代的软件工程范式 — CursorBench：从真实 Cursor 会话提取的 agentic SWE 评测套件

### 模型行为与安全 (Behavior & Safety)
- [[behavioral-self-awareness]] — 行为自意识：LLM 能描述自身隐式学习到的行为
- [[emergent-misalignment]] — 涌现性失准：misaligned 模型展现行为自意识，realignment 后自评逆转
- [[mental-self-modeling]] — LLM 心理自我建模：Theory-of-Mind 测试中的选择性缺陷
- [[ai-self-awareness-game-theory]] — 博弈论测量 AI 自意识：AISAI 框架，Self >> Other AI >> Human 层级
- [[backdoor-awareness]] — Backdoor Awareness：LLM 检测/描述训练数据中后门触发器的能力
- [[introspection]] — Introspection：LLM 审视和报告自身内部决策过程的能力
- [[out-of-context-reasoning]] — Out-of-Context Reasoning (OOCR)：基于训练时习得知识进行推理，无需上下文示例
- [[situational-awareness]] — Situational Awareness：AI 系统理解自身上下文、状态和部署环境的能力

### 自动驾驶与 RL (Autonomous Driving & RL)
- [[perlad]] — PerlAD：伪仿真 RL 闭环端到端自动驾驶，Bench2Drive SoTA (DS=78.70)
- [[opd-autonomous-driving]] — On-Policy Distillation 自动驾驶运动规划（GPT-Driver + GKD）
- [[interactive-imitation-learning]] — Interactive IL：通过交互式专家查询解决暴露偏差

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
- `raw/papers/2026/04/2604.07941.md` — LLM Post-Training: Unified Off/On-Policy View
- `raw/papers/2026/04/2604.08539.md` — G²RPO / OpenVLThinkerV2
- `raw/papers/2026/04/2604.08476.md` — Faithful GRPO
- `raw/papers/2026/04/2604.08468.md` — TTVS: Test-Time Variational Synthesis
- `raw/papers/2026/04/2604.07506.md` — ReflectRM
- `raw/papers/2026/04/2604.07944.md` — OPD for AV Motion Planning
- `raw/papers/2026/04/2604.08256.md` — HyperMem
- `raw/papers/2026/04/2604.07877.md` — MemReader
- `raw/papers/2026/04/2604.07798.md` — LightMem
- `raw/papers/2026/04/2604.08000.md` — PASK Proactive Agent
- `raw/papers/2026/04/2604.06829.md` — WRAP++
- `raw/papers/2026/04/2604.08348.md` — Learning is Forgetting
- `raw/papers/2026/04/2604.08209.md` — OmniJigsaw
- `raw/papers/2026/04/2604.06694.md` — AudioKV
- `raw/papers/2026/04/2604.08401.md` — SAVeR
- `raw/papers/2026/04/2604.08407.md` — Agent Supply Chain Attack

### 预训练与底座 (2)
- `raw/papers/2026/04/2604.00715.md` — RAG-Considerate Pretraining Scaling Laws
- `raw/papers/2026/04/2604.00785.md` — Scalable MoE Pretraining on Aurora

### Agentic Coding (4)
- `raw/papers/2026/04/2604.07789.md` — ORACLE-SWE: Oracle Signals on SWE Agents
- `raw/papers/2026/04/2604.10599.md` — Rethinking SE for Agentic AI
- `raw/papers/2026/04/2604.01496.md` — SWE-ZERO to SWE-HERO
- `raw/papers/2026/04/2604.00824.md` — Even Less Is Even Better

### 多模态推理 (5)
- `raw/papers/2026/04/2604.08477.md` — SUPERNOVA: RL on Natural Instructions
- `raw/papers/2026/04/2604.01840.md` — Perception-Grounded Policy Optimization
- `raw/papers/2026/04/2604.09349.md` — Visually-Guided Policy Optimization
- `raw/papers/2026/04/2604.10228.md` — SVSR: Self-Verification Self-Rectification
- `raw/papers/2026/04/2604.08065.md` — Multimodal Latent Reasoning

### 数据工程 (4)
- `raw/papers/2026/04/2604.09022.md` — BlendFusion: Synthetic Data for Diffusion
- `raw/papers/2026/04/2604.01904.md` — Combating Data Laundering
- `raw/papers/2026/04/2604.07884.md` — RL-Guided Synthetic Data
- `raw/papers/2026/04/2604.00536.md` — Optimsyn: Influence-Guided Synthetic Data

### 最近新增 (16 papers, 2026-04-12~15)
- `raw/papers/2026/04/2604.10688.md` — SCOPE: Signal-Calibrated OPD

### Agent Memory (1 paper, 2025-04)
- `raw/papers/2025/04/2504.19413.md` — Mem0: Scalable Long-Term Memory for AI Agents

### Agent Memory 深度调研 (25 papers, 2023-2026)
- `raw/papers/2023/04/2304.03442.md` — Generative Agents: Interactive Simulacra
- `raw/papers/2023/05/2305.10250.md` — MemoryBank: Long-Term Memory for LLMs
- `raw/papers/2023/08/2308.01542.md` — Memory Sandbox: Interactive Memory Management
- `raw/papers/2023/10/2310.08560.md` — MemGPT: LLMs as Operating Systems
- `raw/papers/2023/11/2311.08719.md` — Think-in-Memory: Long-Term Memory with Recalling
- `raw/papers/2024/02/2402.04624.md` — MEMORYLLM: Self-Updatable LLMs
- `raw/papers/2024/03/2403.01977.md` — LoCoMo: Evaluating Long-Term Conversational Memory
- `raw/papers/2024/03/2404.00558.md` — ReadAgent: LLMs as Reading Agents
- `raw/papers/2024/10/2410.10813.md` — LongMemEval: Long-Term Interactive Memory
- `raw/papers/2025/02/2502.00592.md` — M+: Extending MemoryLLM with Scalable Memory
- `raw/papers/2025/02/2502.12110.md` — A-MEM: Agentic Memory for LLM Agents
- `raw/papers/2025/08/2508.03341.md` — Nemori: Self-Organizing Agent Memory
- `raw/papers/2025/09/2509.11145.md` — Text2Mem: Unified Memory Operation Language
- `raw/papers/2025/11/2511.01448.md` — LiCoMemory: Lightweight Cognitive Agentic Memory
- `raw/papers/2026/01/2601.02553.md` — SimpleMem: Efficient Lifelong Memory
- `raw/papers/2026/01/2602.00398.md` — MemoryLLM v2: Plug-n-Play Feed-Forward Memory
- `raw/papers/2026/02/2602.07624.md` — M2A: Multimodal Memory Agent
- `raw/papers/2026/02/2602.10715.md` — Locomo-Plus: Beyond-Factual Cognitive Memory
- `raw/papers/2026/02/2603.03290.md` — AriadneMem: Lifelong Memory with Evolutionary Graph
- `raw/papers/2026/03/2603.09023.md` — Missing Memory Hierarchy: Demand Paging
- `raw/papers/2026/03/2603.18631.md` — D-Mem: Dual-Process Memory System
- `raw/papers/2026/03/2603.19935.md` — Memori: Persistent Memory Layer
- `raw/papers/2026/04/2604.01670.md` — Hierarchical Memory Orchestration
- `raw/papers/2026/04/2604.14004.md` — Memory Transfer Learning in Coding Agents

### 最近新增
- `raw/papers/2026/03/2603.14908.md` — PerlAD: Pseudo-simulation-based RL for E2E Autonomous Driving
- `raw/papers/2026/04/2604.10674.md` — Skill-SD: Skill-Conditioned Self-Distillation
- `raw/papers/2026/04/2604.10547.md` — Agent² RL-Bench
- `raw/papers/2026/04/2604.11510.md` — Policy Split: Dual-Mode Exploration
- `raw/papers/2026/04/2604.11610.md` — Self-Evolving LLM Memory
- `raw/papers/2026/04/2604.10708.md` — Audio-Omni: Unified Audio Understanding+Generation+Editing
- `raw/papers/2026/04/2604.10438.md` — Whisper-AuT: Domain-Adapted Audio Encoder
- `raw/papers/2026/04/2604.11716.md` — SWE-AGILE: Dynamic Reasoning Context
- `raw/papers/2026/04/2604.10493.md` — SWE-Shepherd: PRMs for Code Agents
- `raw/papers/2026/04/2604.10545.md` — Epistemologically-Informed Self-Learning
- `raw/papers/2026/04/2604.10500.md` — Visual Enhanced Depth Scaling
- `raw/papers/2026/04/2604.10949.md` — Pseudo-Unification: Entropy Probing
- `raw/papers/2026/04/2604.11290.md` — Polyglot Teachers: Multilingual Synthetic Data
- `raw/papers/2026/04/2604.10390.md` — LLM-PRISM: Silent Data Corruption
- `raw/papers/2026/04/2604.11790.md` — ClawGuard: Runtime Agent Security
