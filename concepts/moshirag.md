---
title: "MoshiRAG: Asynchronous Knowledge Retrieval for Full-Duplex Speech Language Models"
created: 2026-06-07
updated: 2026-06-07
type: concept
tags: [full-duplex, speech-model, rag, retrieval, kyutai, moshi, voice-assistant]
sources: [raw/papers/2026/04/2604.12928.md]
---

# MoshiRAG: Asynchronous Knowledge Retrieval for Full-Duplex Speech Language Models

**arXiv**: [2604.12928](https://arxiv.org/abs/2604.12928) | **Date**: 2026-04-14 | **Authors**: Chung-Ming Chien, Manu Orsini, Eugene Kharitonov, Neil Zeghidour, Karen Livescu, Alexandre Défossez | **Affiliation**: Kyutai Labs | **Code**: [kyutai-labs/moshi-rag](https://github.com/kyutai-labs/moshi-rag)

## TL;DR

首个将 **RAG** 集成到**全双工语音语言模型**的系统。核心思想：利用全双工对话中"回复开头"到"关键信息出现"之间的**天然时间差**（keyword delay），在此期间**异步**触发外部知识检索，检索结果在关键信息到达前注入模型，从而在不破坏实时交互的前提下大幅提升事实性。基于 [[moshi]] 7B 模型，检索后端可插拔（Gemma 3 27B / GPT-4.1 / Tavily 搜索），无需重新训练即可切换。

## 1. 问题定义

全双工语音模型（如 [[moshi]]、[[seeduplex]]、[[minicpm-o-4-5]]）能同时"听"和"说"，实时交互性强，但**事实性**显著弱于文本 LLM 和非双工语音模型。原因在于语音训练数据（按词计）远少于文本数据。直接放大模型参数会使实时推理成本不可接受。

**关键洞察：Keyword Delay**

人类-机器语音对话中，从模型开始说话到说出**关键信息**（直接回答用户问题的关键词）之间存在天然时间间隔。论文定义：

- **TTFAT** (Time-To-First-Audio-Token)：用户话语结束到模型生成第一个音频 token 的延迟
- **Keyword Delay (KD)**：模型回复开始到关键信息首次出现的时间间隔
- **E2EKD** (End-to-End Keyword Delay) = TTFAT + KD：从用户问题结束到关键信息出现的总时间
- **Retrieval Delay**：从触发检索到检索完成的时间

**核心约束**：Retrieval Delay < E2EKD，则检索信息可以在关键信息到达前注入回复。

现有语音 LLM 的 E2EKD 通常 > 3 秒，因此 2 秒内的检索完全可行。

## 2. 系统架构

MoshiRAG 采用**前后端分离**的异步架构：

```
用户语音 ──→ [前端: Moshi 7B (全双工)] ──→ 用户音频输出
              ↕                           ↕
         [ASR 1B (流式)]              ⟨ret⟩ 触发
              ↓                           ↓
         对话文本 ──→ [后端: 检索系统] ──→ 参考文档
                           ↓
              ARC-Encoder 压缩 ──→ 注入 Moshi
```

### 2.1 前端 (Front End)

- **Moshi 7B**：原始 Moshi 模型 + 新增 `<ret>` 特殊 token + reference text encoder
- 基于 RQ-Transformer 架构：temporal Transformer (12.5 Hz) + depth Transformer (每步 8 个音频 token)
- 同时接收用户音频 token 并自回归生成文本 + 音频输出

**原始 Moshi 输入**（时间步 $i$）：

$$h_i = \text{emb}_{\text{text},i}^{\text{model}} + \text{emb}_{\text{speech},i}^{\text{model}} + \text{emb}_{\text{speech},i}^{\text{user}}$$

其中：
- $\text{emb}_{\text{text},i}^{\text{model}} = \text{Emb}_{\text{text}}(t_i^{\text{model}})$
- $\text{emb}_{\text{speech},i}^{r} = \text{Emb}_{\text{speech},1}^{r}(s_{i,1}^{r}) + \sum_{j=2}^{8} \text{Emb}_{\text{speech},j}^{r}(s_{i-1,j}^{r})$

### 2.2 检索触发与注入机制

当 `<ret>` 在时间步 $i_{\text{ret}}$ 被预测时：

1. **收集对话文本**：从 ASR（用户端）和 Moshi（助手端）获取转录文本
2. **发送到检索后端**（异步，不阻塞前端）
3. **前端继续全双工运行**，生成 "pre-RAG content"（引导性回复，如 "让我查一下..."）
4. **检索完成后**，参考文档经 ARC-Encoder 压缩（4x 缩短）+ 单层线性投影
5. **流式注入**到 temporal Transformer 输入：

$$h'_i = \begin{cases} h_i + h^{\text{ref}}_{i - (i_{\text{ret}} + \frac{d}{f_r})} & \text{if } i_{\text{ret}} + \frac{d}{f_r} < i \leq i_{\text{ret}} + \frac{d}{f_r} + l \\ h_i & \text{otherwise} \end{cases}$$

其中 $d$ 是检索延迟（秒），$f_r$ 是 Moshi 帧率 (12.5 Hz)，$l$ 是压缩后的参考序列长度，$h^{\text{ref}}_i = \text{proj}(\text{emb}^{\text{ref}}_i)$。

**关键设计**：参考文档的 embedding 是**逐时间步相加**到 Transformer 输入的，而非拼接。这样长文档不会打乱时间线。

### 2.3 后端 (Back End)

两种检索后端：
- **LLM-based**：用 Gemma 3 27B 阅读对话上下文，生成简洁事实性参考文档
- **Search-based**：用 Tavily 搜索引擎获取实时网络信息

**即插即用**：无需重新训练即可切换后端。

### 2.4 流式 ASR

- 1B 参数的流式 ASR 模型（0.5 秒延迟），用于将用户语音转文本供检索使用
- 独立于 Moshi，计算开销极小

## 3. 数据与训练

### 3.1 数据生成（~1.9M 对话实例）

**Topic 来源**：
- Natural Questions: ~307k topics
- HotpotQA: ~90k topics
- TriviaQA: ~76k topics
- LLM 生成的专家领域 topics: 5.5k（111 个专家领域 × 50 topics）

**对话脚本生成**：
- 用 3 个 Gemma 3 27B LLM 角色扮演（user / Moshi / reference）
- User LLM 看不到参考文档，防止信息泄露
- Moshi 和 reference LLM 能看到参考但看不到 topic
- 3 种 prompt 变体：基本对话 / 用户挑战式 / 闲聊式
- RAG 回复分为三段：**lead**（不需要外部知识）+ **body**（基于参考的内容）+ **tail**（可选结尾）

**语音合成**：多通道 TTS 模型，Moshi 用固定 speaker，user 随机采样。

### 3.2 训练策略

**`<ret>` token 放置**：利用 TTS 提供的 forced alignment，将 lead 部分第一个 text token 替换为 `<ret>`。

**检索延迟采样**（训练时模拟）：

$$d' = \begin{cases} \mathcal{U}(0, d_{\text{lead}}) & \text{if } d_{\text{lead}} < 2 \text{ or } p < 0.2 \\ \mathcal{U}(1.0, d_{\text{lead}} - 1.0) & \text{otherwise} \end{cases}$$

其中 $p \sim \mathcal{U}(0, 1)$，$d_{\text{lead}}$ 是 lead 部分时长。

这个设计保证：
- 大多数情况下检索延迟在 $(1.0, d_{\text{lead}}-1.0)$ 内，确保 body 内容前至少有 1 秒缓冲
- 20% 概率 fallback 到宽分布，覆盖边界情况（检索极快或极慢）

**训练配置**：
- 初始化：原始 Moshi 权重
- 可训练参数：除 reference text encoder 外的全部参数
- Reference document dropout: 0.2（丢弃时用可学习向量 $h_{\text{dropout}}$ 替代）
- 学习率: $2 \times 10^{-6}$
- Batch size: 32
- 更新步数: 100k
- 音频预处理：80ms window-based filtering，RMS < -65 dBFS 的片段归零

## 4. 实验结果

### 4.1 事实性评估

| Model | LlamaQ | WebQ | TriviaQA | HaluEval | TTFAT | KD | E2EKD | FLOPs/s |
|-------|--------|------|----------|----------|-------|-----|-------|---------|
| GPT-4o Audio | 88.4 | 81.0 | 90.6 | 68.7 | - | 5.5 | - | - |
| Qwen3-Omni-A3B (30B) | 84.7 | 68.8 | 73.6 | 38.9 | 3.7 | 2.0 | 5.7 | 0.57 |
| Kimi-Audio (7B) | 79.3 | 70.2 | 62.1 | 43.2 | 0.2 | 3.3 | 3.5 | 6.93 |
| SALMONN-omni (8B) | 80.0 | 50.5 | 66.0 | - | - | - | - | - |
| **MoshiRAG** (Gemma 27B) | **83.0** \| 80.3 | **71.5** \| 67.2 | **73.7** \| 69.6 | **42.0** \| 36.3 | 0.0 | 3.1 | 3.1 | 0.37 |
| **MoshiRAG** (GPT-4.1) | **87.8** \| 80.6 | **77.7** \| 68.9 | **86.8** \| 78.2 | **61.2** \| 51.3 | - | - | - | - |
| **MoshiRAG** (Tavily) | **84.6** \| 78.2 | **73.5** \| 66.1 | **84.9** \| 77.5 | **54.3** \| 47.0 | - | - | - | - |
| Vanilla Moshi (7B) | 62.3 | 26.6 | 22.8 | 10.5 | 0.0 | 2.1 | 2.1 | 0.22 |
| Moshi fine-tuned on RAG | 61.2 | 37.0 | 29.7 | 18.7 | 0.0 | 3.1 | 3.1 | 0.22 |

> 表中 `ref. | resp.` 分别表示检索参考文档的准确率和 Moshi 最终回复的准确率。

**关键发现**：
- MoshiRAG vs Vanilla Moshi：TriviaQA 从 22.8% → 69.6%（**+46.8pp**），HaluEval 从 10.5% → 36.3%
- MoshiRAG vs RAG fine-tuned Moshi：证明 RAG 机制本身（而非仅 RAG 数据微调）是关键
- 换用 GPT-4.1 后端：TriviaQA 从 69.6% → 78.2%，HaluEval 从 36.3% → 51.3%
- ref. 和 resp. 之间约 5% 差距，反映 RAG 信息注入过程中的信息损失

### 4.2 全双工交互性评估 (Full-Duplex-Bench)

| Model | Pause TOR↓ | Backchannel Freq | Turn-taking TOR↑ | Interruption GPT↑ | Latency↓ |
|-------|-----------|-----------------|-----------------|-------------------|----------|
| Vanilla Moshi | 0.99 | 0.001 | 0.96 | 0.77 | 0.26 |
| **MoshiRAG** | **0.32** | 0.010 | **0.94** | **0.85** | 1.02 |
| Gemini | 0.26 | 0.012 | 0.90 | 0.89 | 1.18 |
| Freeze-Omni | 0.64 | 0.001 | 0.96 | 0.95 | 0.87 |

- TOR（Takeover Rate）越低越好在 pause 场景
- MoshiRAG 的 TOR 显著降低（0.99→0.32），因为知识密集型回复更长，turn-taking 更保守
- 中断响应能力从 0.77 → 0.85（得益于 v2/v3 训练数据中的对抗性对话场景）
- 延迟略增但仍低于 Gemini 和 Freeze-Omni

### 4.3 域外泛化：数学推理

| Model | AddSub | MultiArith | SingleEq | SVAMP | GSM8K |
|-------|--------|-----------|----------|-------|-------|
| STITCH-S (专用) | 81.7 | 87.9 | 91.7 | 72.2 | 56.7 |
| **MoshiRAG** | 76.6 \| **61.7** | 87.1 \| **69.0** | 83.2 \| **68.2** | 74.1 \| **55.0** | 66.2 \| **33.9** |
| **MoshiRAG** (summ.) | - | - | - | - | **51.2** |
| **MoshiRAG** (GPT-4.1) | 87.9 \| **64.8** | 87.1 \| **76.0** | 89.6 \| **72.9** | 80.5 \| **61.1** | 70.8 \| **43.2** |
| Vanilla Moshi | 8.3 | 9.8 | 18.4 | 9.7 | 2.1 |

- 未经数学推理训练的 MoshiRAG 远超 vanilla Moshi（GSM8K: 2.1% → 33.9%）
- **Reference summary** 后注入比直接用原始参考更好（GSM8K: 33.9% → 51.2%），因为原始参考包含过多数值/符号/推理过程，不利于知识注入
- 换用 GPT-4.1 后端后 GSM8K 达到 43.2%

## 5. 批判性分析

### 优势
1. **开创性工作**：首个全双工 + RAG 系统，解决了实时交互与事实性的根本矛盾
2. **优雅的异步设计**：利用 keyword delay 天然时间窗，不需要等待检索再开始回复
3. **即插即用的后端**：无需重训练即可升级检索能力，未来可扩展到更多工具
4. **域外泛化能力**：证明检索可以作为外部工具使用，不仅是 QA
5. **计算效率**：FLOPs/s 仅 0.37，远低于 Kimi-Audio (6.93) 和 Step-Audio-Chat (5.03)

### 不足与疑问
1. **ref-resp gap**：检索准确率与最终回复准确率之间始终存在 ~5% 差距，说明 reference embedding 注入机制还有优化空间
2. **数学推理上限**：即使是 GPT-4.1 后端，GSM8K 也只有 43.2%，远低于专用模型 STITCH-S (56.7%)
3. **trigger 训练依赖**：`<ret>` token 的触发完全由训练数据决定，未来需要基于查询难度的自适应触发或 RL 优化
4. **未开源模型权重**：GitHub 有代码但模型未 release，限制了复现和二次开发
5. **多轮对话评估缺失**：现有 benchmark 主要是单轮，未充分评估多轮场景下的 RAG 表现
6. **参考文档长度限制**：虽然用了 ARC-Encoder 4x 压缩，但极长文档仍然可能在时间线上注入过多 embedding

### 与相关工作对比

| 维度 | MoshiRAG | Stream RAG | 传统 RAG (文本 LLM) |
|------|----------|-----------|-------------------|
| 双工能力 | ✅ 全双工 | ❌ 非全双工 | ❌ 不适用 |
| 检索时机 | 异步 + keyword delay | 利用时间差 | 同步（先检索再生成） |
| 后端灵活性 | 即插即用 | 固定 | 固定 |
| 实时约束 | < 2s retrieval | 较宽松 | 无实时约束 |
| 训练方式 | 合成数据微调 | 合成数据 | 通常不需微调 |

## 6. 对我们的启发

1. **全双工 + Tool Use 范式**：MoshiRAG 展示了全双工模型可以通过异步机制调用外部工具（RAG、计算器、搜索等），这是 [[duplex-agent-integration]] 方向的重要探索
2. **Keyword Delay 作为设计原语**：任何需要外部计算的全双工系统都可以利用 keyword delay 的时间窗
3. **Reference injection 机制**：逐时间步相加 embedding 的方式值得在其他流式场景（如 [[silent-thought]] 中的潜在推理注入）中借鉴
4. **合成数据管线**：三角色扮演 + TTS 合成的数据生成流程可扩展到其他全双工训练任务
5. **Trigger token 训练**：`<ret>` token 的放置策略（基于 lead/body 分割 + forced alignment）是可控训练的好范式

## Related

- [[moshi]] — Kyutai 原始全双工语音模型，MoshiRAG 的基础
- [[full-duplex-speech-model]] — 全双工语音模型概念页
- [[duplex-agent-integration]] — 全双工 + Agent 能力融合的架构设计
- [[duplex-cascade]] — 无 VAD 的级联流式全双工流水线
