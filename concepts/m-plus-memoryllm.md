---
title: "M+: MemoryLLM 的可扩展长期记忆扩展"
created: 2026-04-17
updated: 2026-04-17
type: concept
tags: [model, architecture, memory, long-term, training]
sources: [raw/papers/2025/02/2502.00592.md]
---

# M+: Extending MemoryLLM with Scalable Long-Term Memory

## 核心问题

[[memoryllm]] 的记忆池固定大小（1B 参数），有效知识保持范围仅约 20k token。
超过此范围，被丢弃的 memory token 永久丢失，无法回溯。

M+ 在 MemoryLLM 基础上引入**可扩展长期记忆 (LTM)** 和**协同训练检索器**，
将知识保持范围从 <20k 扩展至 **160k+ token**，同时保持相近 GPU 内存开销。

## 方法

### 双层记忆架构

- **短期记忆 $\theta$**: 原 MemoryLLM 记忆池，GPU 常驻
- **长期记忆 $\Theta$**: 每层独立的灵活大小记忆池，最大 $M$=150k token，存储在 CPU

### 更新过程

1. MemoryLLM 原本随机丢弃的 $K$ 个 token **不再丢弃**，转存入长期记忆 $\Theta_l$
2. 每个 token 附带 `age` 属性用于时序排序
3. 长期记忆满时淘汰最旧 token（FIFO）

### 生成过程

1. 协同训练的检索器从 $\Theta_l$ 提取 $K_0$ 个相关 token
2. 按 age 排序后与短期记忆 $\theta_l$ 拼接
3. 通过 cross-attention 同时访问两层记忆

### 检索器设计

- 查询投影器 $f_q$ + 键投影器 $f_k$，两层 MLP
- 输出维度 $d_{proj} = d/20$（极度压缩）
- **与语言模型协同训练**，优化检索相关性
- 每层仅检索一次服务于所有注意力头，比 H2O/SnapKV 更高效

### Multi-LoRA 训练

- 更新过程用一组 LoRA 权重（"写入"模式）
- 生成过程用另一组 LoRA 权重（"读取"模式）

### 三阶段数据课程

1. **Stage 1**: MemoryLLM 持续训练（同原始）
2. **Stage 2**: 长文档长上下文建模
3. **Stage 3**: 长期记忆训练

## 结果

基于 LLaMA-3.1-8B 骨干网络：

| 任务 | MemoryLLM | M+ |
|------|-----------|-----|
| 知识保持 (SQuAD, 160k) | 严重退化 | **显著优于** |
| Long Book QA | — | 优于 RMT、ICAE 等基线 |
| 短文档 PPL | 1.9734 | 1.9828（可比） |
| GPU 内存 | 基准 | **相近**（LTM 在 CPU） |
| 128k 延迟 | 基准 | +3%（offload 模式） |

- 检索质量：30% ground-truth token 被成功召回（随机仅 3%）
- 20× 延续扩展：从 20k → 160k+，GPU 内存不增加

## 意义

- **长短双记忆**: 首次在 latent-space memory 中引入分级记忆，类比人类 STM/LTM
- **CPU-GPU 分离**: 长期记忆驻留 CPU，突破 GPU 内存瓶颈
- **协同训练检索**: 检索器与 LM 端到端优化，优于注意力检索基线
- **局限**: CPU-GPU 通信引入额外延迟；检索仍是粗粒度 token 级别

## Related

- [[memoryllm]] — 基础模型
- [[agent-memory-system]] — Agent 记忆系统总览
- [[memgpt]] — 外部层次化记忆
- [[memori-layer]] — 另一种 API 层持久记忆方案
