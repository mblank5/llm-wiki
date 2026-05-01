---
title: "LongCat-Flash-Thinking-2601"
created: 2026-05-01
updated: 2026-05-01
type: entity
tags: [model, architecture, training, reasoning, tool-use, open-source, rl]
sources: [raw/papers/2026/01/2601.16725.md]
---

# LongCat-Flash-Thinking-2601

美团 LongCat 团队发布的升级版开源 MoE 推理模型（arXiv 2601.16725，2026-01）。在 [[longcat-flash-thinking]] 基础上，通过**环境扩展、噪声感知训练和 Heavy Thinking 模式**，大幅提升 Agentic 推理能力。

## 一、核心参数

| 参数 | 值 |
|------|-----|
| 总参数量 | 560B（MoE） |
| 激活参数量 | ~27B（平均） |

## 二、训练框架

### 预训练

继承 [[longcat-flash]] 的预训练配方，保留原始数据分布以维持通用推理能力。

### 中期训练（Mid-training）

**问题**：Agentic 行为（长轨迹 + 主动工具调用）在真实语料中极为稀缺，原始模型不熟悉 Agentic 交互动态，导致 RL 阶段探索效率低。

**方案**：在中期训练中引入**中等规模的合成结构化 Agentic 轨迹**，为 Agentic 行为提供强初始化。

### 后训练 RL：三大核心创新

#### 1. 环境扩展与多领域环境训练

**自动化环境扩展管道**：构建覆盖 **20+ 领域**、**10,000+ 环境**的复杂多样环境，严格保证可执行性和可验证性。

**DORA 扩展**：将异步 RL 框架 DORA 扩展到大规模多环境训练，支持最多 **32,000 个环境并发执行**。

#### 2. 噪声感知训练（Noise-Aware Training）

**问题**：真实世界环境天然不完美，理想化训练环境到真实部署存在 gap。

**方案**：
- 系统分析真实世界噪声模式
- 设计自动化管道，将**多类型、多层次的环境缺陷**逐步融入多领域环境训练
- 提升模型在真实应用中的鲁棒性

#### 3. Heavy Thinking 模式

**核心思想**：通过**联合扩展推理宽度和深度**，实现有效的测试时扩展（Test-Time Scaling）。

**机制**：
- 将复杂问题分解为互补阶段
- 同时探索多条推理路径（宽度）并逐步深化（深度）
- 额外的 RL 阶段强化模型聚合和精炼中间推理结果的能力

## 三、评测表现

在 Agentic benchmark 上全面达到开源 SOTA：

| Benchmark | 分数 | 说明 |
|-----------|------|------|
| **BrowseComp** | 73.1% | Agentic 搜索 |
| **RWSearch** | 77.7% | 真实世界搜索 |
| **τ²-Bench** | 88.2% | Agentic 工具使用 |
| **VitaBench** | 29.3% | 真实业务场景 |

在通用推理 benchmark 上保持强竞争力。

## 四、核心贡献总结

1. **环境扩展与多领域 RL**：10,000+ 环境、20+ 领域、32,000 并发
2. **噪声感知训练**：弥合理想训练环境与真实部署的 gap
3. **Heavy Thinking 模式**：测试时推理宽度和深度的联合扩展
4. **端到端协同设计**：数据构建、环境、算法、基础设施全链路优化

## 五、开源信息

- **HuggingFace**：https://huggingface.co/meituan-longcat/LongCat-Flash-Thinking-2601
- **GitHub**：https://github.com/meituan-longcat/LongCat-Flash-Thinking-2601

## 六、相关页面

- [[longcat-flash]] — LongCat-Flash：基础模型
- [[longcat-flash-thinking]] — LongCat-Flash-Thinking：前代推理模型
- [[longcat-flash-omni]] — LongCat-Flash-Omni：全模态版本
