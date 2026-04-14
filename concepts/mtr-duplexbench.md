---
title: MTR-DuplexBench
created: 2026-04-10
updated: 2026-04-10
type: concept
tags: [concept, benchmark, evaluation, full-duplex, speech-model, dataset]
sources: [raw/papers/2025/11/2511.10262.md]
---

# MTR-DuplexBench — 多轮全双工语音模型评测基准

## 定义

MTR-DuplexBench 是首个面向全双工语音语言模型（FD-SLM）的**多轮综合评测基准**。它不仅将连续全双工对话分割为离散轮次进行逐轮评估，还涵盖了对话质量、对话特征、指令跟随和安全性四个评价维度，弥补了现有基准仅评估单轮交互、仅关注对话特征的不足。

- **论文**: "MTR-DuplexBench: Towards a Comprehensive Evaluation of Multi-Round Conversations for Full-Duplex Speech Language Models" (arXiv: 2511.10262, 2025)
- **作者**: He Zhang, Wenqian Cui, Haoning Xu, Xiaohui Li, Lei Zhu, Haoli Bai, Shaohua Ma, Irwin King

## 背景与动机

### 现有基准的局限

| 基准 | 多轮对话 | 逐轮评测 | 对话特征 | 对话质量 | 指令跟随 | 安全性 |
|------|---------|---------|---------|---------|---------|-------|
| Full-Duplex-Bench | ✗ | ✗ | ✓ | ✓ | ✗ | ✗ |
| Full-Duplex-Bench v1.5 | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ |
| Full-Duplex-Bench v2 | ✓ | ✗ | ✓ | ✗ | ✓ | ✓ |
| FD-Bench | ✓ | ✗ | ✓ | ✓ | ✗ | ✗ |
| Talking Turns | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ |
| **MTR-DuplexBench** | **✓** | **✓** | **✓** | **✓** | **✓** | **✓** |

### 多轮全双工评测的两大挑战

1. **轮次边界模糊（Blurred Turn Boundary）**：全双工对话无严格轮次结构，没有明确的起止标志
2. **上下文不一致（Context Inconsistency）**：评估时模型历史回复可能与 ground truth 不同，造成上下文失配

## 核心方法

### 全双工轮次分割方法

1. **信息提取**：使用 Whisper-timestamped + Silero VAD 提取双通道转录与时间戳
2. **GPT 轮次分割**：GPT-4o 根据内容和时间戳判断用户轮次边界
3. **多数投票聚类过滤**：重复 GPT 分割 6 次，聚合候选轮次（≥30% 时间重叠），取中位数时间戳
4. **助手响应期分配**：助手对当前轮次的响应窗口为 `[当前用户轮次开始, 下一用户轮次结束]`，之前轮次用 ground truth 语音填充以保持上下文一致

### 四个评测维度

#### 1. 对话特征（Conversational Features）

- **涵盖**：平滑轮次切换、打断、暂停处理、背景语音、附和
- **数据**：200 条 10 轮合成对话（GPT-4o 生成文本 + CosyVoice 2 合成语音）
- **指标**：成功率（success rate）、延迟（latency）、附和频率
- **RQ**：FD-SLM 能否在多轮单一特征和混合特征下保持性能？

#### 2. 对话质量（Dialogue Quality）

- **数据**：200 条 120s Candor 自然对话（真实人类语音）
- **指标**：GPT-score（0-5 分，GPT-4o 评估有意义性和连贯性）
- **RQ**：FD-SLM 能否产生有意义且连贯的自然对话？

#### 3. 指令跟随（Instruction Following）

- **数据**：Llama Question 300 条语音查询
- **指标**：成功率（GPT-4o 判定）
- **RQ**：多轮正常交互和频繁打断下能否保持指令跟随能力？

#### 4. 安全性（Safety）

- **数据**：AdvBench 520 条语音查询
- **指标**：拒绝率（GPT-4o 判定）
- **RQ**：多轮交互（含打断）下能否维持安全行为？

## 关键发现

### 对话特征

1. **性能随轮次增加而持续下降**：所有 FD-SLM 在 10 轮交互中成功率逐轮递减
2. **延迟随轮次增长**：多轮延迟评估比首次包延迟更有意义
3. **HD-SLM 和级联方法在背景语音下完全失效**：任何用户输入检测都会触发停止说话

### 对话质量

- 端到端 FD-SLM（Moshi, 3.13）语义质量低于级联 FD-SLM（Freeze-Omni, 3.48），低于 HD-SLM（VocalNet, 3.96）
- 级联方法因极高延迟导致对话质量最低

### 指令跟随与安全

- Moshi 是唯一在多轮中指令跟随显著退化的模型
- 所有模型安全性表现稳健（拒绝率 > 90%），且打断不影响安全性
- **安全性对齐比指令跟随更容易实现**

## 评测模型

- **Moshi**：端到端 FD-SLM
- **Freeze-Omni**：级联 FD-SLM
- **VocalNet**：半双工 SLM
- **Cascaded**（SenseVoice + GPT-4o + ChatTTS）：级联基线

## 局限性

- 依赖自然+合成混合数据集，可能未完全捕捉真实对话多样性
- 仅评估英语
- 轮次分割依赖 GPT-4o，引入成本和可变性

## 相关页面

- [[full-duplex-speech-model]] — 全双工语音模型总览
- [[moshi]] — Moshi 全双工语音对话模型
- [[freeze-omni]] — Freeze-Omni 冻结 LLM 方案
- [[speech-llm]] — 语音大语言模型
- [[turnguide]] — TurnGuide 文本引导方法（同团队相关工作）
- [[duplex-cascade]] — DuplexCascade VAD-free 级联方案
