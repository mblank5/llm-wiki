---
title: "LongCat-Image"
created: 2026-05-01
updated: 2026-05-01
type: entity
tags: [model, architecture, training, open-source, multimodal]
sources: [raw/papers/2025/12/2512.07584.md]
---

# LongCat-Image

美团 LongCat 团队发布的开源双语图像生成基础模型（arXiv 2512.07584，2025-12）。**6B 参数**，专攻中英双语文字渲染、照片级真实感和高效部署，性能优于 20B+ 的 MoE 架构模型。

## 一、核心参数

| 参数 | 值 |
|------|-----|
| 总参数量 | 6B（核心扩散模型） |
| 语言 | 中英双语 |
| 架构 | MM-DiT + Single-DiT 混合（继承 Flux1.dev） |
| 文本编码器 | Qwen2.5VL-7B |
| 支持任务 | 文生图、图像编辑 |

## 二、架构设计

### 混合架构

- **MM-DiT + Single-DiT 混合结构**：继承 Flux1.dev 的设计哲学
- **Qwen2.5VL-7B 文本编码器**：为生成和编辑任务提供统一的强大条件空间
- 6B 参数规模，远小于常见的 20B+ MoE 架构

### 设计理念

LongCat 团队的设计哲学：**"构建高效且强大的模型"**。不盲目追求参数规模，而是在 SOTA 性能和效率之间取得最优平衡。

## 三、训练策略

### 数据管线系统优化

**AIGC 污染防控**：
- 预训练和中期训练阶段严格排除所有 AIGC 数据
- 少量 AIGC 数据会导致模型过早收敛到狭窄局部最优
- SFT 阶段引入的高质量合成数据经过人工精筛

### 多阶段训练

1. **预训练**：大规模图像-文本对
2. **中期训练**：高质量数据
3. **SFT**：监督微调
4. **RL**：使用精心策划的奖励模型

### AIGC 检测奖励模型

RL 阶段创新性地将 **AIGC 检测模型**作为奖励模型之一：
- 使用对抗信号引导模型生成具有真实物理世界纹理和保真度的图像
- 有效防止模型生成"AI 感"过强的图像

## 四、关键能力

### 1. 中文文字渲染（行业新标准）

- 支持复杂和生僻汉字
- 覆盖度超越主要开源和商业方案
- 渲染精度领先

### 2. 照片级真实感

- 严格的数据筛选 + AIGC 检测奖励模型
- 显著提升美学质量

### 3. 高效部署

- 紧凑的 6B 参数设计
- 最小化 VRAM 占用
- 快速推理，显著降低部署成本

### 4. 图像编辑

- 在标准 benchmark 上达到 SOTA
- 编辑一致性优于其他开源方案

## 五、评测表现

| Benchmark | 表现 |
|-----------|------|
| **GenEval** | 量化评估领先 |
| **DPG** | 密集复杂提示语义对齐优异 |
| 照片级真实感 | 显著提升 |
| 编辑一致性 | 开源 SOTA |

## 六、开源生态

最全面的开源生态：
- 多个模型版本（文生图、图像编辑）
- 中期训练和训练后检查点
- 完整训练工具链开源

- **HuggingFace**：https://huggingface.co/meituan-longcat/LongCat-Image
- **GitHub**：https://github.com/meituan-longcat/LongCat-Image

## 七、相关页面

- [[longcat-flash]] — LongCat-Flash：同系列语言模型
- [[longcat-video]] — LongCat-Video：同系列视频生成模型
- [[longcat-next]] — LongCat-Next：同系列多模态模型
