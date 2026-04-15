# Wiki Log

> Chronological record of all wiki actions. Append-only.
> Format: `## [YYYY-MM-DD] action | subject`

## [2026-04-06] ingest | Seeduplex 论文 + 全双工语音模型专题
- Sources: ByteDance Seeduplex (2026-04) + 相关语音模型论文
- Created entities:
  - entities/seeduplex.md
  - entities/moshi.md
  - entities/llama-omni.md
  - entities/freeze-omni.md
  - entities/minmo.md
  - entities/seed-realtime-voice.md
  - entities/byte-seed.md
  - entities/seed-tts.md
- Created concepts:
  - concepts/full-duplex-speech-model.md（含 2024-2026 论文索引、架构方案、竞品格局）
- Total pages created: 10

## [2026-04-15] ingest | Qwen3 语音家族 + Omni-Modal LLM 深度调研 (13 篇论文)
- Sources:
  - Qwen3-Omni (2509.17765), Qwen3-ASR (2601.21337), Qwen3-TTS (2601.15621)
  - Qwen3-VL-Embedding (2601.04720), Qwen-Audio (2311.07919)
  - EMOVA (2409.18042), SALMONN-omni (2411.18138)
  - Stream-Omni (2506.13642), MGM-Omni (2509.25131)
  - ROMA (2601.10323), Speech-Omni-Lite (2603.09627)
  - Omni-R1 (2601.09536), U-SAM (2505.13880)
- Created entities:
  - entities/qwen3-omni.md (Thinker-Talker MoE 架构详解)
  - entities/qwen3-asr.md (52 语言 ASR，4 阶段训练含 RL)
  - entities/qwen3-tts.md (双轨 TTS，97ms 首包延迟)
  - entities/emova.md (CVPR 2025，语义-声学分离)
  - entities/salmonn-omni.md (Codec-free 全双工)
  - entities/stream-omni.md (CTC layer-dimension 对齐)
  - entities/mgm-omni.md (Brain-Mouth 双轨)
- Created concepts:
  - concepts/omni-modal-llm.md (统一概念页：4 种架构方案对比、性能矩阵、6 大趋势)
- Created queries:
  - queries/qwen3-voice-family-deep-dive.md (家族技术传承链、竞品定位)
- Updated:
  - index.md (51 → 61 pages)
- Total pages created: 8 new | 1 updated

## [2026-04-06] ingest | OPD 专题 15 篇论文批量导入
- Sources: Policy Distillation (2015) → OPD Survey (2026-04)
- Created concepts:
  - concepts/on-policy-distillation.md
  - concepts/on-policy-prefix-distillation.md
  - concepts/generalized-on-policy-distillation.md
  - concepts/policy-distillation.md
  - concepts/model-distillation.md
  - concepts/dual-policy-distillation.md
  - concepts/stop-gradient-distillation.md
  - concepts/per-token-kl-clipping.md
  - concepts/proximal-policy-distillation.md
  - concepts/ppo.md
  - concepts/cascade-rl.md
  - concepts/entropy-aware-on-policy-distillation.md
  - concepts/exposure_bias.md
  - concepts/video-opd.md
  - concepts/vold.md
  - concepts/x-opd.md
  - concepts/speech-llm.md

## [2026-04-15] ingest | Cursor Composer 2 Technical Report
- Source: Cursor Research Team, Composer 2 Technical Report (2026-03-24)
- PDF: raw/papers/cursor-composer2-technical-report-2026.pdf
- Text: raw/papers/cursor-composer2-technical-report-2026.txt
- Created entities:
  - entities/composer2.md
- Created concepts:
  - concepts/cursorbench.md
  - concepts/agentic-coding.md
- Updated: index.md (3 new pages, total 47)
  - concepts/reopold.md
  - concepts/stable-baselines3.md
  - concepts/token-level-entropy-analysis.md
  - concepts/on-policy-distillation-survey.md
- Created entities:
  - entities/qwen3.md
- Total: 15 raw papers + 22 concept pages + 1 entity page

## [2026-04-06] ingest | LLM Behavioral Self-Awareness 论文
- Source: 2501.11120v1 (2025-01)
- Created concepts:
  - concepts/behavioral-self-awareness.md

## [2026-04-10] merge | 三库合并
- Merged ~/wiki (语音模型专题) + ~/wikis/opd (OPD 专题) + ~/arxiv-wiki (行为自意识) → ~/wiki
- Raw papers: 16 篇 → raw/papers/ (按年份组织)
- Concept pages: 23 个
- Entity pages: 9 个
- Updated SCHEMA.md: 扩展标签体系覆盖蒸馏、RL、安全、多模态
- Rebuilt index.md: 完整内容目录
- Backup: ~/wiki-backup-20260410.tar.gz

## [2026-04-10] ingest | 补充 8 篇新论文（语音模型 × 5 + 行为自意识 × 3）
- Sources:
  - 2508.07375 — TurnGuide: Text-Guided Full-Duplex Spoken Interactions
  - 2511.10262 — MTR-DuplexBench: Multi-Round Full-Duplex Evaluation
  - 2603.17837 — Silent Thought / FLAIR: Latent Reasoning in Full-Duplex Dialogue
  - 2603.09180 — DuplexCascade: VAD-Free Cascaded ASR-LLM-TTS
  - 2603.08179 — Privacy-Preserving End-to-End Full-Duplex Speech Dialogue
  - 2602.14777 — Emergently Misaligned LMs Show Behavioral Self-Awareness
  - 2603.26089 — Selective Deficits in LLM Mental Self-Modeling
  - 2511.00926 — AI Self-Awareness Measured Through Game Theory
- New concept pages (8):
  - concepts/turnguide.md
  - concepts/silent-thought.md
  - concepts/mtr-duplexbench.md
  - concepts/duplex-cascade.md
  - concepts/privacy-preserving-speech.md
  - concepts/emergent-misalignment.md
  - concepts/mental-self-modeling.md
  - concepts/ai-self-awareness-game-theory.md
- Updated pages:
  - concepts/full-duplex-speech-model.md (新增 5 篇论文引用)
  - concepts/behavioral-self-awareness.md (新增 Recent Developments 节)
- Raw papers: 16 → 24 | Concept pages: 23 → 31 | Total wiki pages: 33 → 40

## [2026-04-12] merge | 三 wiki 合并到 ~/wiki
- 迁入 ~/wikis/opd/wiki/answers/ 的 4 个查询记录到 queries/
  - queries/qwen3-opd-usage.md
  - queries/qwen3-tech-overview.md
  - queries/opd-tokenizer-requirement.md
  - queries/opd-vs-sft.md
- 修复 frontmatter、source 路径（raw/ingested/ → raw/papers/）
- ~/arxiv-wiki 和 ~/wikis/opd 的其余内容（raw papers、concept pages）均为 ~/wiki 的子集，无需迁入
- Total wiki pages: 40 → 44

## [2026-04-15] ingest | SRPO + 3 篇 GRPO/OPD 论文批量导入
- Sources:
  - 2604.02288 — Sample-Routed Policy Optimization (SRPO)
  - 2602.22495 — Reinforcement-Aware Knowledge Distillation (RLAD)
  - 2603.23871 — Hybrid Distillation Policy Optimization (HDPO)
  - 2603.05433 — On-Policy Self-Distillation for Reasoning Compression (OPSDC)
- New concept pages (4):
  - concepts/sample_routed_policy_optimization.md
  - concepts/rl_aware_distillation.md
  - concepts/hybrid_distillation_policy_optimization.md
  - concepts/on_policy_self_distillation_reasoning_compression.md
- Updated pages:
  - concepts/on_policy_distillation.md (added SRPO, RLAD to Related Methods)
  - index.md (4 new entries, total pages 47 → 51)
- Downloaded raw papers (HTML extraction):
  - raw/papers/2026/04/2604.02288.md (68KB)
  - raw/papers/2026/02/2602.22495.md (65KB)
  - raw/papers/2026/03/2603.23871.md (70KB)
  - raw/papers/2026/03/2603.05433.md (80KB)
- Updated index.md raw sources: 24 → 28 papers (蒸馏 16 → 20)
- Total wiki pages: 47 → 51 | Raw papers: 24 → 28

## [2026-04-15] ingest | 16 new papers: post-training, RL, agent memory, omni-modal, pretraining

### Papers downloaded (16)
- raw/papers/2026/04/2604.07941.md — LLM Post-Training Unified View (134KB)
- raw/papers/2026/04/2604.08539.md — G²RPO / OpenVLThinkerV2 (71KB)
- raw/papers/2026/04/2604.08476.md — Faithful GRPO (75KB)
- raw/papers/2026/04/2604.08468.md — TTVS: Test-Time Variational Synthesis (58KB)
- raw/papers/2026/04/2604.07506.md — ReflectRM (54KB)
- raw/papers/2026/04/2604.07944.md — OPD for AV Motion Planning (40KB)
- raw/papers/2026/04/2604.08256.md — HyperMem (61KB)
- raw/papers/2026/04/2604.07877.md — MemReader (69KB)
- raw/papers/2026/04/2604.07798.md — LightMem (58KB)
- raw/papers/2026/04/2604.08000.md — PASK Proactive Agent (86KB)
- raw/papers/2026/04/2604.06829.md — WRAP++ (58KB)
- raw/papers/2026/04/2604.08348.md — Learning is Forgetting (64KB)
- raw/papers/2026/04/2604.08209.md — OmniJigsaw (92KB)
- raw/papers/2026/04/2604.06694.md — AudioKV (52KB)
- raw/papers/2026/04/2604.08401.md — SAVeR (57KB)
- raw/papers/2026/04/2604.08407.md — Agent Supply Chain Attack (97KB)

### Wiki pages created (16 concepts)
- concepts/llm-post-training-unified-view.md — Off-policy/on-policy 统一框架
- concepts/g2rpo.md — Gaussian GRPO
- concepts/faithful-grpo.md — 约束策略优化
- concepts/ttvs.md — Test-time RL
- concepts/reflectrm.md — 自反思 RM
- concepts/opd-autonomous-driving.md — OPD 自动驾驶应用
- concepts/hypermem.md — 超图记忆
- concepts/memreader.md — 主动记忆提取
- concepts/lightmem-agent-memory.md — 轻量记忆
- concepts/pask-proactive-agent.md — 主动 Agent
- concepts/saver-faithful-reasoning.md — 自审计推理
- concepts/agent-supply-chain-attack.md — 供应链攻击
- concepts/wrap-plus-plus.md — 跨文档预训练
- concepts/llm-training-as-lossy-compression.md — 有损压缩视角
- concepts/omnijigsaw.md — 全模态 RL 后训练
- concepts/audiokv.md — KV Cache 驱逐

### Index updated
- Total wiki pages: 91 → 107 | Raw papers: 55 → 71
- New section: Agent 记忆与安全 (6 pages)
- New entries in 蒸馏与后训练 (6 pages), 强化学习基础 (0 new), 语音与多模态 (4 pages)

## [2026-04-15] ingest | 15 papers: pretraining, agentic coding, multimodal reasoning, data engineering

### Gap areas filled (4 new topics)
1. **LLM 预训练/底座** (2 papers, 2 concepts)
2. **Agentic Coding** (4 papers, 4 concepts)
3. **多模态推理** (5 papers, 5 concepts)
4. **数据工程** (4 papers, 4 concepts)

### Papers downloaded (15)
- 2604.00715 — RAG-Considerate Pretraining (70KB)
- 2604.00785 — Scalable MoE Pretraining (39KB)
- 2604.07789 — ORACLE-SWE (96KB)
- 2604.10599 — Rethinking SE for Agentic AI (57KB)
- 2604.01496 — SWE-ZERO to SWE-HERO (75KB)
- 2604.00824 — Even Less Is Even Better (63KB)
- 2604.08477 — SUPERNOVA (74KB)
- 2604.01840 — Perception-Grounded PO (93KB)
- 2604.09349 — Visually-Guided PO (85KB)
- 2604.10228 — SVSR (62KB)
- 2604.08065 — Multimodal Latent Reasoning (68KB)
- 2604.09022 — BlendFusion (47KB)
- 2604.01904 — Data Laundering (91KB)
- 2604.07884 — RL-Guided Synthetic Data (57KB)
- 2604.00536 — Optimsyn (92KB)

### Wiki pages created (15 concepts)
- concepts/rag-considerate-pretraining.md
- concepts/scalable-moe-pretraining.md
- concepts/oracle-swe.md
- concepts/swe-hero.md
- concepts/less-is-more-agentic.md
- concepts/rethinking-se-for-agentic-ai.md
- concepts/supernova.md
- concepts/perception-grounded-po.md
- concepts/visually-guided-po.md
- concepts/svsr.md
- concepts/multimodal-latent-reasoning.md
- concepts/blendfusion.md
- concepts/data-laundering-llm.md
- concepts/rl-guided-synthetic-data.md
- concepts/optimsyn.md

### Index updated
- Total wiki pages: 107 → 122 | Raw papers: 71 → 86
- New sections: 数据工程 (4), expanded Agentic Coding (6), 预训练 (2), 多模态推理 (5)

## [2026-04-15] ingest | 16 papers (latest Apr 12-15): SCOPE, Audio-Omni, Agent² RL-Bench, SWE-Shepherd

### Papers downloaded (16/18, 3 not yet available on arxiv)
- 2604.10688 — SCOPE: Signal-Calibrated OPD (54KB)
- 2604.10674 — Skill-SD (85KB)
- 2604.10547 — Agent² RL-Bench (108KB)
- 2604.11510 — Policy Split (36KB)
- 2604.11610 — Self-Evolving Memory (88KB)
- 2604.10708 — Audio-Omni (69KB)
- 2604.10438 — Whisper-AuT (13KB)
- 2604.11716 — SWE-AGILE (54KB)
- 2604.10493 — SWE-Shepherd (13KB)
- 2604.10545 — Epistemological Self-Learning (132KB)
- 2604.10500 — Visual Depth Scaling (58KB)
- 2604.10949 — Pseudo-Unification Entropy (55KB)
- 2604.11290 — Polyglot Teachers (124KB)
- 2604.10390 — LLM-PRISM (60KB)
- 2604.11790 — ClawGuard (70KB)

### Wiki pages created (15 concepts)
- OPD: scope-opd, skill-sd
- RL: agent2-rl-bench, policy-split
- Memory: self-evolving-memory
- Omni: audio-omni, whisper-aut
- Coding: swe-agile, swe-shepherd, epistemological-self-learning
- MR: visual-depth-scaling, pseudo-unification-entropy
- Data: polyglot-teachers, llm-prism
- Safety: clawguard

### Index updated
- Total wiki pages: 122 → 137 | Raw papers: 86 → 102

## [2026-04-16] deep-read | 3 Omni papers: Audio-Omni, Pseudo-Unification, Omni-R1

### Papers deep-read
- 2604.10708 — Audio-Omni: Frozen Qwen2.5-Omni-3B + DiT Rectified Flow, 7.9B, AudioEdit 1M+ pairs
- 2604.10949 — Pseudo-Unification: Matrix-based Rényi entropy probing reveals dual divergence in UMMs
- 2601.09536 — Omni-R1: Generative multimodal reasoning with intermediate image generation

### Wiki pages updated/created (4)
- concepts/audio-omni.md — FULL REWRITE: architecture diagram, dual-stream conditioning, Rectified Flow, experiments table
- concepts/pseudo-unification-entropy.md — FULL REWRITE: entropy probing method, dual divergence findings, impact on Qwen3-Omni
- concepts/omni-r1.md — NEW: PeSFT+PeRPO training, Uni-Skills, Omni-R1-Zero bootstrap
- concepts/omni-modal-llm.md — MAJOR UPDATE: added Route B (Frozen MLLM+DiT), Pseudo-Unification section, RL post-training table, generative reasoning section

### Key insights integrated
- Two audio synthesis routes now clearly differentiated (AR+ConvNet vs DiT+RF)
- Pseudo-unification challenges "no degradation" claims across all UMMs
- Omni-R1's PeRPO introduces perception-calibrated reward for multimodal RL
- omni-modal-llm.md updated from 128 lines to ~200 lines

### Index updated
- Total wiki pages: 137 → 138 | Raw papers: 102
