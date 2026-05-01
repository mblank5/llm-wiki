---
title: "An Imperfect Verifier is Good Enough: Learning with Noisy Rewards"
created: 2026-05-01
updated: 2026-05-01
type: concept
tags: [rl, reward-model, rlvr, noise]
sources: [raw/papers/2026/04/2604.07666.md]
---

# An Imperfect Verifier is Good Enough

**不完美验证器也足够好** —— 系统性研究 RLVR 中奖励噪声的影响，发现 15% 噪声率下训练效果无损，精度比召回率更重要。

## Overview

RLVR 的理想是完美验证器，但实际中验证器几乎总有误差——即使确定性检查也可能出错（如数学等价判断），模型 judge 更加剧了这一问题。本文首次系统性研究：

1. RLVR 对验证器噪声的鲁棒性阈值是多少？
2. 不同噪声类型的影响是否不同？
3. 验证器应优化精度 (precision) 还是召回率 (recall)?

在代码生成 (MBPP) 和科学推理 (GPQA) 两个领域，横跨 GLM4、Qwen3、Llama 3.1 三个模型家族 (4B-9B) 进行实验。

## Key Contribution / 核心创新

### 1. 四种受控噪声模式

将噪声建模为对 G×T 二进制奖励矩阵 M 的翻转：

| 模式 | 粒度 | 描述 |
|------|------|------|
| Sample × Unit Test | 最细 | 每个单元格独立翻转 |
| Sample × Rollout | 行级 | 整行翻转（整体误判） |
| Group × Unit Test | 列级 | 整列翻转（缺陷测试用例） |
| Group × Rollout | 最粗 | 整个矩阵翻转 |

### 2. 核心发现

**15% 噪声阈值**：所有噪声模式下，p ≤ 0.15 时峰值验证准确率与干净基线差距 <2 个百分点。

**噪声可能有益**：基于 Ackley 函数的 toy experiment 证明，适度噪声可帮助 GRPO 逃离局部最优。

**精度 > 召回率**：模型验证器的假阳性（误标错误代码为正确）比假阴性危害更大。

### 3. GPQA 上的惊人结果

Qwen3 8B + GSPO 在 GPQA Diamond 上：
- 无噪声：0.600 → p=0.05 噪声：**0.604** → p=0.30 噪声：**0.603**
- 噪声训练反而略微超越干净基线

## Experimental Results

### MBPP 代码生成 (Best Validation Reward)

| 配置 | GLM4 9B | Qwen3 8B | Llama 3.1 8B |
|------|---------|----------|--------------|
| Baseline (无噪声) | 0.905±0.002 | 0.901±0.009 | 0.658±0.001 |
| p=0.10 Group rollout | 0.900±0.005 | 0.886±0.003 | 0.651 |
| p=0.10 Group unit test | 0.891 | 0.893±0.003 | - |
| p=0.10 Sample rollout | 0.866 | 0.864±0.011 | - |
| p=0.10 Unit test | 0.875 | 0.854±0.013 | - |
| Model verifier 30B | - | 0.871 | - |
| Model verifier 4B | - | 0.704 | - |

### GPQA 科学推理 (Best Validation Reward)

| 配置 | Qwen3 8B |
|------|----------|
| Base model | 0.540 |
| No noise | 0.600 |
| p=0.05 noise | **0.604** |
| p=0.30 noise | **0.603** |

### 关键数字
- ≈85% 准确率/精度的模型验证器可恢复大部分 ground-truth 训练信号
- 4B 验证器：高召回 (>90%) 但低精度 → 训练停滞 (0.704 vs 0.901)
- 30B 验证器：高精度 → 性能接近无噪声基线 (0.871 vs 0.901)
- 超参敏感：top-p 从 1.00 降到 0.95 严重影响 GLM4 (0.905→0.817)

## Relation to Existing Work

- 与 [[free-process-rewards]] 互补：process reward 提供更强信号，但本文证明 outcome reward 对噪声容忍度高
- 对 [[self-distilled-rlvr]] 的验证器选择有指导意义：不追求完美，精度优先
- 对 [[rl-post-training-scaling-laws]] 的补充：scaling laws 假设干净奖励，本文量化了实际场景的容忍度
- 对比 Rad et al. (2026) 的理论分析：本文通过更广泛的实验挑战其部分结论
- 与 Shao et al. (2025) 的 spurious rewards 研究互补：关注低到中等噪声而非完全错误标签

## Related

- [[free-process-rewards]]
- [[self-distilled-rlvr]]
- [[rl-post-training-scaling-laws]]
