# Wiki Index

> Content catalog. Every wiki page listed under its type with one-line summary.
> Read this first to find relevant pages for any query.
> Last updated: 2026-05-01 | Total pages: 186 | Raw papers: 188

## Entities

- [[byte-seed]] — 字节跳动 Seed AI 研究团队，Seeduplex/Seed-TTS 所属团队
- [[dflash]] — DFlash：Block Diffusion Speculative Decoding，6x+ 无损加速，2.5x faster than EAGLE-3
- [[ddtree]] — DDTree：DFlash 的 Draft Tree 扩展，acceptance length 从 ~3.1 提升到 ~10.7 tokens
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
- [[qwen3-5-omni]] — Qwen3.5-Omni：Hybrid MoE Thinker-Talker，256k 上下文，ARIA 动态对齐，74 种语言
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
- [[longcat-flash]] — LongCat-Flash：560B 开源 MoE 基础模型，zero-computation experts+shortcut-connected MoE，20T+ tokens 训练
- [[longcat-flash-thinking]] — LongCat-Flash-Thinking：560B 开源 MoE 推理模型，三阶段推理能力培养
- [[longcat-flash-thinking-2601]] — LongCat-Flash-Thinking-2601：升级版推理模型，环境扩展+噪声感知训练+Heavy Thinking 模式
- [[longcat-flash-omni]] — LongCat-Flash-Omni：560B 开源全模态 MoE，ScMoE+zero-computation experts
- [[longcat-video]] — LongCat-Video：13.6B 开源视频生成基础模型，多奖励 RLHF 训练
- [[longcat-image]] — LongCat-Image：6B 开源双语图像生成模型，SOTA 中文文字渲染
- [[longcat-next]] — LongCat-Next：原生多模态自回归模型，统一离散化所有模态为 tokens

## Concepts

### 蒸馏与后训练 (Distillation & Post-Training)

- [[on-policy-distillation]] — On-Policy Distillation 核心概念：student rollout + teacher feedback，bias-variance tradeoff
- [[generalized-knowledge-distillation]] — Generalized Knowledge Distillation (GKD)：DeepMind 奠基工作，on-policy 蒸馏理论基础，处理分布不匹配
- [[generalized-on-policy-distillation]] — G-OPD：带奖励外推的泛化 on-policy 蒸馏，lambda 控制 reward vs KL，超教师性能
- [[on-policy-prefix-distillation]] — OPPD：on-policy 前缀蒸馏，计算高效，2-47x 加速，性能接近完整 OPD
- [[speculative-decoding]] — Speculative Decoding：draft-verify 推理加速，DFlash/DDTree 新范式
- [[on-policy-distillation-survey]] — OPD 综述：f-divergence 统一框架、白盒/黑盒/无教师方法分类
- [[ex-opd]] — Ex-OPD：扩展 OPD 变体，奖励外推机制
- [[on-policy-self-distillation]] — 自蒸馏推理：无需外部 teacher 的 on-policy 方法
- [[dual-policy-distillation]] — DPD：Student-Student 对偶策略蒸馏框架
- [[proximal-policy-distillation]] — PPO 风格 per-token KL 裁剪蒸馏
- [[per-token-kl-clipping]] — Per-token KL 裁剪技术详解
- [[policy-distillation]] — Policy Distillation 基础概念（DeepMind 2015 开山作）
- [[model-distillation]] — 模型蒸馏通用概念与分类
- [[exposure-bias]] — 暴露偏差：训练-推理分布不一致问题
- [[entropy-aware-on-policy-distillation]] — 熵感知 OPD：动态 divergence 自适应
- [[reopold]] — ReOPOLD：高效推理扩展的 relaxed on-policy 蒸馏
- [[cascade-rl]] — Cascade RL：级联强化学习用于多域 post-training
- [[token-level-entropy-analysis]] — Token 级别熵分析：理解蒸馏中的信息流动
- [[sample-routed-policy-optimization]] — SRPO：统一 GRPO 强化 + SDPO 蒸馏的样本路由框架，熵感知动态加权
- [[rl-aware-distillation]] — RLAD：强化学习感知蒸馏，仅当 RL 有益时模仿 teacher（TRRD 目标）
- [[hybrid-distillation-policy-optimization]] — HDPO：特权自蒸馏针对"悬崖 prompt"，共享权重 teacher/student
- [[on-policy-self-distillation-reasoning-compression]] — OPSDC：推理压缩的自蒸馏，"be concise" 条件化 teacher
- [[chain-of-thought]] — Chain-of-Thought (CoT)：逐步推理 prompting 技术，现代推理模型基础
- [[deepseek-r1-distillation]] — DeepSeek R1 蒸馏：将推理能力蒸馏到小模型的方法
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
- [[dp-opd]] — DP-OPD：差分隐私 + OPD，正式隐私保证 + 高效模型适配
- [[rethinking-opd]] — "Rethinking OPD"：OPD 动力学系统研究，成功条件、token 级机制、失败恢复策略
- [[lightning-opd]] — Lightning OPD：离线预计算 teacher log-probs，4x speedup，Teacher Consistency 理论
- [[opd-calibration]] — CaOPD：OPD 中的校准退化问题，信息不对称根因，Pareto-optimal 校准
- [[tip-opd]] — TIP：Token 级别重要性分析，非均匀 token 蒸馏
- [[opsdl]] — OPSDL：On-Policy Self-Distillation 扩展到 long-context 场景
- [[self-distilled-rlvr]] — Self-Distilled RLVR：OPD + RLVR 融合，dense fine-grained signals
- [[self-distillation-zero]] — Self-Distillation Zero：自修订将 binary rewards 转化为 dense supervision
- [[hybrid-policy-distillation]] — Hybrid Policy Distillation：混合策略蒸馏框架（融合前/反向 KL，on/off-policy）

### LongCat 核心技术 (LongCat Core Techniques)

- [[zero-computation-experts]] — Zero-Computation Experts：MoE 动态计算预算分配，PID 控制器调节
- [[shortcut-connected-moe]] — Shortcut-Connected MoE (ScMoE)：跨层 shortcut 扩大计算-通信重叠窗口

### RL 后训练缩放定律 (RL Scaling Laws)

- [[rl-post-training-scaling-laws]] — RL Post-Training Scaling Laws for LLMs：Qwen2.5 数学推理研究，log-linear 趋势，饱和效应

### 强化学习基础 (RL Foundations)

- [[ppo]] — PPO：Proximal Policy Optimization，策略梯度核心算法
- [[stable-baselines3]] — Stable Baselines3：RL 算法开源工具库
- [[atari-2600]] — Atari 2600：经典 RL 基准环境（ALE），DQN/Policy Distillation 标准测试
- [[deep-q-network]] — DQN (Deep Q-Network)：深度 RL 值方法，DeepMind 2015
- [[grpo]] — GRPO (Group Relative Policy Optimization)：组内相对奖励策略优化，现代 LLM 后训练核心
- [[grpo-rl-training]] — GRPO RL Training：基于 GRPO 的强化学习训练方法论
- [[imitation-learning]] — Imitation Learning：从专家示范中学习，SFT 的 RL 视角
- [[faithful-grpo]] — Faithful GRPO：约束策略优化，解决 RLVR accuracy-faithfulness 矛盾

### Agent 训练与多轮 RL (Agent Training & Multi-Turn RL)

- [[ml-agent-autonomous-ml]] — ML-Agent：自主机器学习的 RL 框架，7B 胜过 671B，三阶段训练（探索 SFT + 步骤级 RL + 统一奖励）
- [[ragegen-multi-turn-rl-agents]] — RAGEN：多轮 RL for LLM Agents，StarPO 框架，Echo Trap 现象，轨迹级优化
- [[agent-r1-end-to-end-rl]] — Agent-R1：端到端 RL for LLM Agents，MDP 扩展，3-phase 训练（PT→Offline RL→Online RL）
- [[agent2-rl-bench]] — Agent² RL-Bench：LLM Agent 自主设计 RL pipeline 的评测基准
- [[policy-split]] — Policy Split：LLM RL 中的双模式探索策略 — TTVS
- [[supernova]] — SUPERNOVA：自然指令 RL 激发 LLM 通用推理能力
- [[omnijigsaw]] — OmniJigsaw：Qwen3-Omni RL 后训练，时间重排自监督
- [[omni-r1]] — Omni-R1：统一生成式多模态推理（推理中生成中间图像）
- [[relax-async-rl-omni]] — Relax：异步 RL 引擎，三平面架构，Omni 后训练 1.76-2x 加速
- [[visual-depth-scaling]] — Visual Depth Scaling：多模态潜在推理的视觉增强深度缩放

### Agent 记忆与安全 (Agent Memory & Safety)

- [[agent-memory-system]] — Agent Memory System 总览：LLM Agent 长期记忆方案分类与对比
- [[lightmem-agent-memory]] — LightMem：轻量级 Agent 记忆高效存储
- [[a-mem]] — A-MEM：Zettelkasten 启发的 Agentic Memory，LLM 属性标注+自主链接
- [[memeovobench-memory-safety]] — MemEvoBench：记忆误演化基准，36 风险类型，长期记忆安全评估
- [[pask-proactive-agent]] — PASK：意图感知主动 Agent，DD-MM-PAS 流式框架
- [[saver-faithful-reasoning]] — SAVeR：Agent 自审计验证推理，行动前验证内部信念状态
- [[agent-poison]] — AgentPoison：通过记忆或知识库投毒的后门攻击，82% 攻击成功率
- [[agent-supply-chain-attack]] — LLM Agent 供应链攻击：第三方 Agent 依赖的风险
- [[clawguard]] — ClawGuard：Tool-Augmented Agent 运行时安全框架
- [[agent-align]] — AgentAlign：Agentic LLM 安全对齐，抽象行为链合成数据，安全性 +43.7%
- [[agent-safety-via-rl]] — Agent Safety via RL：统一安全对齐框架，三模态分类，沙箱环境
- [[safe-belal]] — Safe-BeAl：具身 Agent 安全规划与对齐框架，8.55-15.22% 安全提升
- [[thought-aligner]] — Thought-Aligner：实时思维纠正模块，安全性从 ~50% → 90%
- [[alignment-waltz]] — WaltzRL：多 Agent 安全协作框架，Unsafe 从 39.0% → 4.6%
- [[verificagent]] — VerificAgent：专家种子记忆 + 迭代增长 + 人工验证的监督框架

### Agentic Coding (Agent 编程)

- [[agentic-coding]] — Agentic Coding：AI Agent 自主完成软件工程任务的模式与训练方法
- [[oracle-swe]] — ORACLE-SWE：量化 oracle 信息对 SWE Agent 解决率的贡献分解
- [[swe-hero]] — SWE-ZERO→SWE-HERO：从 execution-free 到 execution-based SWE Agent
- [[less-is-more-agentic]] — Even Less Is Even Better：Agentic/Reasoning/Coding L
- [[rethinking-se-for-agentic-ai]] — Rethinking SE for Agentic AI
- [[swe-agile]] — SWE-AGILE：SWE Agent 动态推理上下文管理
- [[swe-shepherd]] — SWE-Shepherd：Code Agents 的 Process Reward Models
- [[epistemological-self-learning]] — 认识论驱动的 LLM 自学习对话

### 模型行为与安全 (Behavior & Safety)

- [[safe-world]] — SafeWorld：地理多样性安全对齐，50 国 493 地区多维度评估
- [[think-twice-before-act]] — Think Twice Before You Act：思维纠正提升行为安全
- [[alignment-waltz]] — WaltzRL：多 Agent 安全协作（也列在记忆与安全）

### 自动驾驶与 RL (Autonomous Driving & RL)

- [[perlad]] — PerlAD：伪仿真 RL 闭环端到端自动驾驶，Bench2Drive SoTA
- [[opd-autonomous-driving]] — On-Policy Distillation 自动驾驶运动规划（GPT-Driver + GKD）

## 近期原始资料 (Recent Raw Papers)

### OPD 与蒸馏 (2026-04)
- `raw/papers/2026/04/2604.13016.md` — Rethinking OPD：现象学、机制与配方
- `raw/papers/2026/04/2604.00626.md` — OPD 综述：统一 f-divergence 框架
- `raw/papers/2026/04/2604.20244.md` — Hybrid Policy Distillation：混合策略蒸馏
- `raw/papers/2026/04/2604.15774.md` — MemEvoBench：记忆误演化基准
- `raw/papers/2026/04/2604.04461.md` — DP-OPD：差分隐私 OPD
- `raw/papers/2026/04/2604.02288.md` — Fast Prefix Distillation (OPPD)：前缀蒸馏 2-47x 加速
- `raw/papers/2026/04/2604.08000.md` — PASK Proactive Agent
- `raw/papers/2026/04/2604.08407.md` — Agent Supply Chain Attack
- `raw/papers/2026/04/2604.00715.md` — RAG-Considerate Pretraining Scaling Laws
- `raw/papers/2026/04/2604.07789.md` — ORACLE-SWE：SWE Agent 的 oracle 信息贡献
- `raw/papers/2026/04/2604.10599.md` — Rethinking SE for Agentic AI
- `raw/papers/2026/04/2604.08477.md` — SUPERNOVA：自然指令 RL
- `raw/papers/2026/04/2604.07884.md` — RL-Guided Synthetic Data
- `raw/papers/2026/04/2604.11790.md` — ClawGuard：Agent 运行时安全
- `raw/papers/2026/04/2604.10547.md` — Agent² RL-Bench
- `raw/papers/2026/04/2604.10493.md` — SWE-Shepherd：Code Agent PRMs
- `raw/papers/2026/04/2604.11790.md` — Visual Enhanced Depth Scaling
- `raw/papers/2026/04/2604.14004.md` — Memory Transfer Learning in Coding Agents

### RL Agent 与安全 (2025-05 ~ 2025-11)
- `raw/papers/2025/05/23723.md` — ML-Agent：自主 ML 的 RL 框架
- `raw/papers/2025/04/20073.md` — RAGEN：多轮 RL Agent，StarPO 框架
- `raw/papers/2025/11/14460.md` — Agent-R1：端到端 RL for LLM Agents
- `raw/papers/2025/05/23020.md` — AgentAlign：Agentic LLM 安全对齐
- `raw/papers/2025/07/08270.md` — Agent Safety via RL：统一安全框架
- `raw/papers/2025/04/14650.md` — Safe-BeAl：具身 Agent 安全
- `raw/papers/2025/05/11063.md` — Thought-Aligner：思维纠正安全
- `raw/papers/2025/09/25300.md` — RL Scaling Laws：Qwen2.5 数学推理缩放
- `raw/papers/2025/03/09516.md` — Search-R1：搜索增强 RL 推理

### 基础与早期 (2023-2024)
- `raw/papers/2023/06/13649.md` — Generalized Knowledge Distillation (GKD)
- `raw/papers/2024/12/20367.md` — SWE-RL：软件演化 RL
- `raw/papers/2024/07/12784.md` — AgentPoison：记忆/知识库投毒
- `raw/papers/2024/12/06483.md` — SafeWorld：地理多样性安全
- `raw/papers/2021/03/14659.md` — Alignment of Language Agents

## Queries

- [[qwen3-tech-overview]] — Qwen3 技术全景：思考/非思考模式、MoE、缩放、语音家族
- [[qwen3-opd-usage]] — Qwen3 如何应用 OPD：后训练管线与思考预算
- [[opd-tokenizer-requirement]] — OPD 的 tokenizer 要求与不匹配问题
- [[opd-vs-sft]] — OPD vs SFT：分布匹配与长期推理收益

## Comparisons

- [[distillation-methods-comparison]] — 蒸馏方法对比：SFT / DPO / PPO / OPD / GKD
- [[agent-frameworks-comparison]] — Agent 框架对比：RAGEN / Agent-R1 / ML-Agent / ReAct

---