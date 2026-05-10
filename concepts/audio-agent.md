---
title: "Audio-Agent"
created: 2026-05-01
updated: 2026-05-01
type: concept
tags: [concept, speech-model, agent, tool-use, training, architecture]
sources: []
---

# Audio-Agent

## 定义

Audio-Agent 是指能够直接以音频为输入、通过 ReAct（Reasoning + Acting）循环执行 Function Call 和 Tool 调用的智能体系统。区别于"ASR + Text Agent"的级联方案，Audio-Agent 从音频到动作端到端完成，保留语气、情感、停顿等非语言信息。

## 核心架构

```
音频输入 → [Encoder] → [Adaptor] → [LLM Agent] → Function Call → Tool → Tool Response → LLM → 语音输出
```

### 组件说明

| 组件 | 作用 | 是否训练 |
|------|------|---------|
| Encoder | 音频特征提取（如 FireRedASR Encoder） | 阶段1后冻结 |
| Adaptor | 音频特征 → LLM token embedding 映射 | 阶段1-2训练 |
| LLM Agent | 推理 + Function Call + 回复生成 | 阶段2-4训练 |
| Audio Decoder | 文本 → 语音合成 | 可选，可用 TTS 替代 |

## 训练管线（四阶段）

### 阶段1：Adaptor 预训练

目标：建立音频到文本的对齐能力。

```
Encoder: FireRedASR / Qwen3-ASR (冻结)
LLM: Qwen3 / Qwen3.5 (冻结)
Adaptor: Causal Downsample (训练)
数据: 100-500h ASR 数据
目标: WER < 5%（中文）
```

### 阶段2：Agent SFT

目标：恢复 LLM 的 Agent 能力，初步对齐音频输入和 Agent 输出。

```
数据构成:
├── 40% 纯文本 Agent 数据（恢复 Function Call 能力）
├── 30% 音频-文本对（保持 ASR 能力）
└── 30% 音频-Agent 数据（合成，初步对齐）
目标: Function Call 准确率 > 80%
```

### 阶段3：OPD 对齐

目标：用 Teacher（文本 Agent）的信号对齐音频输入下的 Agent 能力。

```
Teacher: Qwen3.5-xxx（文本 Agent）
Student: Audio-Agent
损失: JSD / Reverse KL（轨迹级对齐，非单轮）
数据: 音频输入 + Teacher 生成的 Function Call 序列
目标: 音频输入下 Agent 能力接近文本输入
```

### 阶段4：RL 优化

目标：端到端优化任务完成率。

```
算法: GRPO（不需要 Critic，训练稳定）
奖励设计:
├── 0.4 Function Call 正确性
├── 0.2 Tool Response 匹配度
├── 0.3 推理逻辑连贯性（LLM judge）
└── 0.1 任务完成率
目标: 端到端任务完成率 > 70%
```

## 级联 vs 端到端对比

| 维度 | 方案A：级联（ASR+LLM） | 方案B：端到端 Audio-Agent |
|------|----------------------|-------------------------|
| ASR 准确率 | 高（独立优化） | 中（联合优化） |
| Agent 能力 | 强（Teacher 直接能力） | 中（OPD 对齐后） |
| 延迟 | 高（ASR + LLM） | 低（一次推理） |
| 非语言信息 | 丢失 | 保留 |
| 训练成本 | 零 | 高 |
| 部署复杂度 | 中（2个模型） | 低（1个模型） |

## OPD 在 Audio-Agent 中的关键作用

OPD（On-Policy Distillation）是 Audio-Agent 训练的核心，因为：

1. **跨模态对齐**：Teacher 处理文本，Student 处理音频，OPD 对齐两者的输出分布
2. **轨迹级监督**：不是单轮 Function Call 对齐，而是整个 ReAct 循环的对齐
3. **数据效率**：Teacher 自动生成标注，无需大量人工标注的音频-Agent 数据

### OPD 损失函数

```
L_OPD = E_{x_audio ~ D} [ KL(π_teacher(·|ASR(x_audio)) || π_student(·|x_audio)) ]
```

其中 π 是生成 Function Call 的策略，ASR(x_audio) 作为 Teacher 的输入。

## 流式改造路线

```
非流式（阶段1-4）→ 流式（阶段5）

非流式: [===== 8s audio =====] → full attention → output
流式:   [== 2s chunk ==] → attention + sliding window → output

关键参数:
- Chunk 大小: 2s（250 token @ 12.5Hz）
- Sliding window: 4s
- 首包延迟: < 2s
```

## 垂直领域 vs 通用领域

| 能力维度 | 通用 Audio-Agent | 垂直领域（如车载） |
|---------|-----------------|-------------------|
| Function Call 准确率 | 85-90% | 93-96% |
| 单轮指令理解 | 88-92% | 90-94% |
| 多轮对话 | 75-85% | 80-88% |
| 隐含意图推理 | 60-70% | 65-75% |
| 数据量需求 | 千万级 | 万级 |

**建议**：先做垂直领域（车载/智能家居）验证管线，再扩展到通用领域。

## 相关页面

- [[on-policy-distillation]] — OPD 方法
- [[speech-llm]] — 语音大语言模型
- [[full-duplex-speech-model]] — 全双工语音模型
- [[duplex-agent-integration]] — 全双工 + Agent 融合架构
- [[nim4-asr]] — NIM4-ASR 模型
- [[qwen3-asr]] — Qwen3-ASR 模型
