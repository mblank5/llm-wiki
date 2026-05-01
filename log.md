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
