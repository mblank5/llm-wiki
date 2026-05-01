---
title: "LongCat-Next"
created: 2026-05-01
updated: 2026-05-01
type: entity
tags: [model, architecture, training, open-source, multimodal, reasoning]
sources: [raw/papers/2026/03/2603.27538.md]
---

# LongCat-Next

美团 LongCat 团队发布的原生多模态自回归模型（arXiv 2603.27538，2026-03）。核心创新是 **DiNA（Discrete Native Autoregression）框架**——将所有模态统一离散化为 token，在单一共享离散空间中实现真正的原生多模态建模。

## 一、核心理念

### 问题：语言中心主义的多模态

当前多模态系统仍以语言为中心，将非语言模态视为外部附件，导致架构碎片化、集成次优。

### 方案：DiNA 框架

将所有模态表示为**可互操作的 token 序列**，由单一共享自回归目标统一管理。

**类比**：就像语言 tokenizer 将文字转为 token，DiNA 将视觉、音频也转为同一类 token。

## 二、架构创新

### 2.1 dNaViT：离散原生任意分辨率视觉 Transformer

核心组件：**dNaViT（Discrete Native Any-resolution Visual Transformer）**

- **任意分辨率**：支持任意分辨率的 tokenization 和 de-tokenization
- **分层离散 token**：将连续视觉信号转为分层离散 token
- **双向映射**：图像 ↔ 离散 ID 的双向映射
- **压缩比**：最高 28× 压缩
- **语义完整性**：理解任务的语义完整性 + 生成任务的高保真重建

**关键技术**：
1. **Semantic-and-Aligned Encoders (SAE)**：语义对齐编码器作为基础
2. **残差架构**：编码器的残差结构天然保留低级信号传播路径
3. **Residual Vector Quantization (RVQ)**：对残差的残差进行分层向量量化，保留理解和生成所需的信息

**自回归建模**：
- 多层 token 的加法编码
- DepthTransformer 高效解码
- 多层 token 形成指数级表示空间，同时保持单步自回归的计算效率

### 2.2 音频 Tokenizer

- 基于 Whisper 编码器捕获语义和副语言特征
- RVQ 架构，压缩波形为 12.5 Hz 的离散 token
- 音频 detokenizer：配对 decoder + flow matching 精化网络，高保真重建

### 2.3 文本-音频对齐

统一训练范式：
- segment 级文本和 token 与随机延迟对齐
- 支持**并行和串行**的文本引导语音生成
- 提升语音生成的语言质量

## 三、模型架构

- **骨干**：Mixture-of-Experts (MoE)
- **统一框架**：语言 + 视觉 + 音频，最小化模态特定设计
- **能力**：看、画、说，单一框架内完成

## 四、关键贡献

1. **DiNA 框架**：统一的多模态离散表示空间
2. **dNaViT**：任意分辨率的视觉 tokenizer，解决离散视觉建模的性能瓶颈
3. **理解-生成统一**：有效调和理解与生成之间的矛盾
4. **工业级训练配方**：大规模原生多模态模型的完整训练方案

## 五、评测表现

在多模态 benchmark 上达到强竞争力：
- 视觉理解：突破离散视觉建模的性能天花板
- 视觉生成：高质量图像生成
- 音频理解与生成：全面的音频能力
- 跨模态任务：统一的跨模态理解与生成

## 六、开源信息

- **GitHub**：https://github.com/meituan-longcat/LongCat-Next
- **HuggingFace**：https://huggingface.co/meituan-longcat/LongCat-Next
- 开源模型和 tokenizer

## 七、相关页面

- [[longcat-flash]] — LongCat-Flash：同系列语言模型
- [[longcat-flash-omni]] — LongCat-Flash-Omni：全模态版本
- [[longcat-video]] — LongCat-Video：视频生成版本
- [[longcat-image]] — LongCat-Image：图像生成版本
