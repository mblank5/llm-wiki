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
