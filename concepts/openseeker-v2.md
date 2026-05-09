---
title: "OpenSeeker-v2: Pushing the Limits of Search Agents with Informative and High-Difficulty Trajectories"
created: 2026-05-09
updated: 2026-05-09
type: concept
tags: [rl, training, benchmark, dataset, open-source, reasoning, tool-use]
sources: [raw/papers/2026/05/2605.04036.md]
---

# OpenSeeker-v2: Pushing the Limits of Search Agents with Informative and High-Difficulty Trajectories

**arXiv**: 2605.04036v1 [cs.AI] | **Date**: 2026-05-05  
**Authors**: Yuwen Du*, Rui Ye*#,†, Shuo Tang, Keduan Huang, Xinyu Zhu, Yuzhu Cai, Siheng Chen† (Shanghai Jiao Tong University)  
**Code**: https://github.com/PolarSeeker/OpenSeeker  
**Model**: https://huggingface.co/PolarSeeker/OpenSeeker-v2-30B-SFT

## 1. Core Problem Definition

前沿 LLM 搜索 Agent（Deep Search）的开发长期被工业巨头垄断，典型方案依赖极其资源密集的多阶段训练管线：**持续预训练（CPT）→ 监督微调（SFT）→ 强化学习（RL）**。这种对庞大算力和私有数据管道的重度依赖，在学术界和开源社区与工业界之间制造了巨大的鸿沟。

OpenSeeker-v2 的核心假设是：**如果训练数据本身足够困难和信息丰富，仅凭简单的 SFT 目标就足以诱导强大的长程搜索与推理能力**。研究聚焦于回答一个关键问题：能否通过纯 SFT 方法，仅靠高质量数据，推动搜索 Agent 的性能极限，匹敌重型工业管线？

## 2. Method

### 2.1 知识图谱扩展（Scaling Graph Size for Richer Exploration）

设 $\mathcal{G} = (\mathcal{V}, \mathcal{E})$ 为用于任务合成的源知识图谱。对于每个种子节点 $v_{\mathrm{seed}} \in \mathcal{V}$，原始管线围绕 $v_{\mathrm{seed}}$ 构建局部子图 $\mathcal{G}_{\mathrm{sub}}$。OpenSeeker-v2 将扩展预算从 $k$ 增加到 $K$（$K > k$），获得更大的证据子图：

$$\mathcal{G}_{\mathrm{sub}}^{(K)} = \operatorname{Expand}(\mathcal{G}, v_{\mathrm{seed}}, K)$$

扩充后的子图包含更丰富的拓扑相关源信息，增加了可行推理路径的数量和多样性。合成查询基于此扩展上下文生成：

$$q \sim P_{\mathrm{gen}}\left(q \mid \mathcal{G}_{\mathrm{sub}}^{(K)}\right)$$

通过增大 $K$，生成的问题更可能需要跨多节点聚合证据，而非依赖少量源。

### 2.2 工具集扩展（Expanding the Tool Set for Broader Functionality）

给定生成的问题 $q$，为搜索 Agent 配备扩展的工具集 $\mathcal{A}$（相比 OpenSeeker-v1 更大），使其生成多步 ReAct 风格轨迹：

$$\tau = \left(r_1, a_1, o_1, r_2, a_2, o_2, \ldots, r_T, a_T, o_T, r_{T+1}, y\right)$$

其中每个动作 $a_t \in \mathcal{A}$ 对应从扩展工具集中选择的工具调用，$o_t$ 表示工具返回的观测，$r_t$ 表示每次行动前的推理轨迹。轨迹包含 $T$ 个工具调用步骤，随后是最终推理步 $r_{T+1}$ 和答案 $y$。

通过扩展 $\mathcal{A}$，Agent 被鼓励学习更多样化的交互模式并利用互补工具，产生更灵活和功能丰富的问题解决行为。

### 2.3 严格低步过滤（Strict Low-Step Filtering）

为移除过于简单的样本，应用严格的低步过滤规则：

$$\mathcal{D}_{\mathrm{v2}} = \left\{(q, \tau) \in \mathcal{D}_{\mathrm{raw}} \;\middle|\; T(\tau) \geq T_{\min}\right\}$$

其中 $T_{\min}$ 是预定义的最小工具调用阈值。$T(\tau) < T_{\min}$ 的轨迹被丢弃，因为它们通常可通过直接查找或浅层关键词匹配解决。

### 2.4 训练目标

在过滤后的数据集上使用标准 SFT 目标训练搜索 Agent。扩展的图谱增加了上下文丰富度和多跳依赖性，而低步过滤强制执行最低难度基线。这两个修改共同产生高质量的 SFT 数据，促使 Agent 学习持续的推理、鲁棒的信息提取和长程搜索行为。

### 2.5 数据合成管线总览

| 修改项 | OpenSeeker-v1 | OpenSeeker-v2 | 效果 |
|--------|---------------|---------------|------|
| 图谱扩展预算 | $k$ | $K$ ($K > k$) | 更丰富的拓扑上下文、更多可行推理路径 |
| 工具集大小 | 较小 | 更大 | 更多样化的交互模式、更灵活的求解行为 |
| 低步过滤 | 无/宽松 | 严格 ($T \geq T_{\min}$) | 强制最低难度基线，确保长程推理 |
| 平均轨迹步数 | 46.97 | 64.67 | 更复杂的多步推理需求 |

## 3. 完整实验结果

### 3.1 主结果表：ReAct-based Search Agent 对比

| Model | # Samples | Training | Academic | BrowseComp | BC-ZH | HLE | xbench |
|-------|-----------|----------|----------|------------|-------|-----|--------|
| **Closed-Source Proprietary** | | | | | | | |
| Claude-4-Opus | ? | ? | × | 18.8 | 37.4 | - | - |
| Claude-4.5-Sonnet | ? | ? | × | 24.1 | 42.4 | 32.0 | - |
| Gemini-3-pro | ? | ? | × | 37.8 | 66.8 | 45.8 | - |
| OpenAI-o3 | ? | ? | × | 49.1 | 68.7 | 20.2 | 65.0 |
| OpenAI Deep Research | ? | ? | × | 51.5 | 42.9 | 26.6 | - |
| GPT-5-High | ? | ? | × | 54.9 | 63.0 | 41.7 | - |
| **Open-Source Models > 30B** | | | | | | | |
| DeepSeek-V3.1-671B | ? | ? | × | 30.0 | 49.2 | 29.8 | 71.2 |
| DeepSeek-V3.2-671B | ? | ? | × | 51.4 | 65.0 | 40.8 | - |
| GLM-4.6-357B | ? | ? | × | 45.1 | 49.5 | 30.4 | - |
| GLM-4.7-357B | ? | ? | × | 52.0 | 66.6 | 42.8 | - |
| Minimax-M2-230B | ? | ? | × | 44.0 | 48.5 | - | - |
| **~30B Models** | | | | | | | |
| WebSailor-V2-30B-SFT | ? | SFT | × | 24.4 | 28.3 | 23.9 | 61.7 |
| WebSailor-V2-30B-RL | ? | SFT+RL | × | 35.3 | 44.1 | 30.6 | 73.7 |
| WebLeaper-30B-SFT | 15k | SFT | × | 27.7 | - | - | 66.0 |
| WebLeaper-30B-RL | ? | RL | × | 38.8 | - | - | 72.0 |
| Tongyi DeepResearch | ? | CPT+SFT+RL | × | 43.4 | 46.7 | 32.9 | 75.0 |
| RedSearcher-30B | ? | CPT+SFT+RL | × | 42.1 | 49.8 | 34.3 | - |
| OpenSeeker-v1-30B-SFT | 11.7k | SFT | ✓ | 29.5 | 48.4 | - | 74.0 |
| **OpenSeeker-v2-30B-SFT** | **10.6k** | **SFT** | **✓** | **46.0** | **58.1** | **34.6** | **78.0** |

**核心发现**：
- OpenSeeker-v2 以 **仅 10.6k 样本 + 纯 SFT** 超越了 Tongyi DeepResearch（CPT+SFT+RL 重型管线）和 RedSearcher（CPT+SFT+RL）
- BrowseComp: +2.6pp vs Tongyi DeepResearch
- BrowseComp-ZH: **+11.4pp** vs Tongyi DeepResearch（最大差距）
- HLE: +0.3pp vs RedSearcher
- xbench: **+3.0pp** vs Tongyi DeepResearch
- 也超越了 DeepSeek-V3.1-671B、GLM-4.6-357B、Minimax-M2-230B、Claude-4.5-Sonnet 等更大模型

### 3.2 数据难度对比：平均工具调用次数

| Agent | Avg Tool Calls / Trajectory |
|-------|----------------------------|
| RedSearcher | 36.01 |
| OpenSeeker-v1 | 46.97 |
| **OpenSeeker-v2** | **64.67** |

OpenSeeker-v2 的轨迹显著更长，表明训练数据需要更复杂的多步推理和更长程的信息搜索。

### 3.3 v1 → v2 改进幅度

| 指标 | OpenSeeker-v1 | OpenSeeker-v2 | 提升 |
|------|---------------|---------------|------|
| BrowseComp | 29.5 | 46.0 | **+16.5** |
| BrowseComp-ZH | 48.4 | 58.1 | **+9.7** |
| xbench | 74.0 | 78.0 | **+4.0** |
| Avg Trajectory Length | 46.97 | 64.67 | **+37.7%** |

## 4. Training Configuration

| 参数 | 值 |
|------|------|
| 基座模型 | Qwen3-30B-A3B-Thinking-2507 |
| 总参数量 | 30B |
| 推理激活参数 | 3B (MoE sparse) |
| 上下文窗口 | 256k tokens |
| 最大工具调用次数 | 200 / trajectory |
| 训练数据量 | 10.6k 样本 |
| 训练方法 | 纯 SFT（无 RL，无超参调优） |
| 范式 | ReAct |
| 团队 | 纯学术团队（上海交大） |
| 开源 | ✓（模型权重 + 代码） |

## 5. 与现有方法对比

| 维度 | OpenSeeker-v2 | Tongyi DeepResearch | RedSearcher | WebSailor-V2-RL |
|------|---------------|---------------------|-------------|-----------------|
| 训练管线 | 仅 SFT | CPT + SFT + RL | CPT + SFT + RL | SFT + RL |
| 数据量 | 10.6k | 未公开 | 未公开 | 未公开 |
| 平均轨迹长度 | 64.67 | 未公开 | 36.01 | 未公开 |
| BrowseComp | **46.0** | 43.4 | 42.1 | 35.3 |
| BC-ZH | **58.1** | 46.7 | 49.8 | 44.1 |
| HLE | **34.6** | 32.9 | 34.3 | 30.6 |
| xbench | **78.0** | 75.0 | - | 73.7 |
| 学术团队 | ✓ | × | × | × |
| 开源 | ✓ | 部分 | × | × |

## 6. Critical Analysis

### 6.1 优势

- **数据质量胜于训练复杂度**：核心贡献在于证明精心设计的合成数据可以替代 CPT+RL 的重型管线，为学术社区提供了一条可复现的路径
- **极高的数据效率**：仅 10.6k 样本即达到 SOTA，相比工业方案动辄数十万甚至百万级数据量，效率极高
- **完全开源**：模型权重和代码全部开放，是目前 ~30B ReAct 搜索 Agent 中唯一的学术开源 SOTA
- **v1→v2 改进幅度惊人**：BrowseComp 从 29.5→46.0（+16.5pp），证明 OpenSeeker 框架的 scaling 潜力远未饱和
- **跨越规模壁垒**：在 BrowseComp 和 HLE 上超越了 DeepSeek-V3.1-671B（671B 参数）等更大模型

### 6.2 不足与疑问

- **报告过于简短**：全文缺乏消融实验（ablation study），无法量化三个修改项各自的贡献度（图谱扩展 vs 工具扩展 vs 低步过滤分别贡献多少）
- **$T_{\min}$ 阈值未公开**：严格低步过滤的具体阈值未给出，复现困难
- **图谱扩展的具体数值**：$k \to K$ 的具体数值未说明，无法评估扩展的幅度
- **工具集的具体组成**：扩展的工具集包含哪些工具？与 v1 相比增加了什么？未详细说明
- **未报告 RL 上限**：纯 SFT 可能只是上限较低的策略，缺少 SFT+RL 的对比来验证"RL 是否还能进一步 gains"
- **单一基座模型**：仅在 Qwen3-30B-A3B 上实验，缺少跨模型泛化验证（如 LLaMA、Mistral 等）
- **推理成本未讨论**：200 工具调用上限意味着单次 query 可能极长，实际部署的延迟和 API 成本未被分析
- **BrowseComp-ZH 的异常高表现**：BC-ZH 上 OpenSeeker-v2 (58.1) 远超 GPT-5-High (63.0 接近，但 Tongyi 仅 46.7)，需确认评测协议一致性
- **无过程级评估**：仅报告了最终答案正确率，缺少对中间搜索步骤质量的分析

### 6.3 对我们工作的启发

- **数据质量是搜索 Agent 的核心瓶颈**：与其追求更复杂的训练管线，不如在数据合成和过滤上投入
- **严格难度过滤是关键策略**：移除简单样本、强制长轨迹可能比增加数据量更有效
- **学术团队可以做出 SOTA**：纯 SFT + 高质量数据足以匹敌工业级 CPT+SFT+RL，降低了研究门槛
- **SFT 作为 RL 的前置基线**：OpenSeeker-v2 证明了强大的 SFT 基线可以为后续 RL 训练提供更好的起点
- **与 [[agenticqwen-dual-flywheel]] 的互补性**：该工作的数据飞轮可以借鉴 OpenSeeker-v2 的难度过滤策略来合成更难的搜索任务
- **与 [[ragegen-multi-turn-rl-agents]] 的对比**：后者强调 RL 在多轮 Agent 训练中的作用，而 OpenSeeker-v2 证明在某些场景下纯 SFT 已足够——两者的结合点在于何时需要 RL

## Related

- [[agenticqwen-dual-flywheel]] — 双数据飞轮训练小型 agentic 模型，行为树扩展
- [[ragegen-multi-turn-rl-agents]] — 多轮 RL Agent 训练中的 reward engineering 和数据合成
- [[grpo-rl-training]] — GRPO 强化学习训练方法，常用于 Agent 后训练
- [[rl-conductor]] — RL 训练 LM 动态编排 worker LLM 搜索
- [[on-policy-distillation]] — 后训练中的策略蒸馏方法，可作为 SFT 的替代/补充
