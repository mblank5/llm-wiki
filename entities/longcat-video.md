---
title: "LongCat-Video"
created: 2026-05-01
updated: 2026-05-01
type: entity
tags: [model, architecture, training, open-source, multimodal]
sources: [raw/papers/2025/10/2510.22200.md]
---

# LongCat-Video

美团 LongCat 团队发布的开源视频生成基础模型（arXiv 2510.22200，2025-10）。**13.6B 参数**，基于 DiT 框架，支持文生视频、图生视频、视频续写，通过多奖励 RLHF 达到 SOTA 水平。

## 一、核心参数

| 参数 | 值 |
|------|-----|
| 总参数量 | 13.6B |
| 架构 | Diffusion Transformer (DiT) + Block Sparse Attention |
| 支持任务 | Text-to-Video、Image-to-Video、Video-Continuation |
| 长视频 | 支持分钟级长视频生成，保持时间连贯性 |
| 推理速度 | 720p、30fps 视频在分钟内生成 |

## 二、架构设计

### 统一架构

单个模型统一支持三种任务，通过**条件帧数量**区分：
- **Text-to-Video**：0 帧条件
- **Image-to-Video**：1 帧条件
- **Video-Continuation**：多帧条件

### Block Sparse Attention

核心效率创新：
- **3D 块重排**：将时空注意力组织为 3D 块
- **块选择掩码**：基于内容的块级稀疏注意力
- **Ring Block Sparse Attention**：支持上下文并行的环形稀疏注意力
- 在高分辨率下显著提升效率

### 粗到细生成策略

沿时间和空间轴的**粗到细（Coarse-to-Fine）**生成：
- 先生成低分辨率/低帧率草稿
- 逐步细化到目标分辨率
- 平衡生成质量与推理速度

## 三、训练策略

### 多阶段训练

1. **预训练**：大规模视频-文本对
2. **微调**：高质量数据微调
3. **SFT**：监督微调
4. **RLHF**：多奖励强化学习

### 多奖励 RLHF

使用多个奖励模型联合优化：
- **视频质量奖励**：视觉质量评估
- **文本对齐奖励**：生成内容与提示词的对齐度
- **运动流畅度奖励**：时间连贯性和运动自然度

**效果**：多奖励 RLHF 使模型达到与最新闭源和领先开源模型相当的性能。

## 四、评测表现

- **VBench 2.0**：在广泛使用的公开 benchmark 上表现优异
- 视频生成质量、文本对齐、运动流畅度等指标均达到领先水平

## 五、开源信息

- **GitHub**：https://github.com/meituan-longcat/LongCat-Video
- 代码和模型权重全开源

## 六、相关页面

- [[longcat-flash]] — LongCat-Flash：同系列语言模型
- [[longcat-image]] — LongCat-Image：同系列图像生成模型
- [[longcat-next]] — LongCat-Next：同系列多模态模型
