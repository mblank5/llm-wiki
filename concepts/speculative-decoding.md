---
title: "Speculative Decoding"
created: 2026-04-21
updated: 2026-04-21
type: concept
tags: [inference-optimization, acceleration, decoding]
sources: []
---

# Speculative Decoding

Speculative Decoding 是一种 LLM 推理加速技术，通过轻量级 **draft model** 提前生成候选 token，由 **target model** 并行验证，实现无损加速。

## 核心原理

```
传统推理: Target 逐 token 生成 (序列化)
         t1 → t2 → t3 → t4 → ...  (每步 1 token)

Speculative Decoding:
Draft: 快速生成多个候选 [t1', t2', t3', t4']
Verify: Target 单次 forward 并行验证
Accept: 匹配的 token + 继续生成
```

**无损保证**：rejected token 由 target model 从正确分布采样，输出与 target model standalone 完全一致。

## 关键组件

### Draft Model

- 轻量级、快速生成
- 传统方法：小 AR model（如 0.5B → 7B target）
- 新方法：Diffusion model（DFlash）、Tree-based（DDTree）

### Verification

- Target model 单次 forward pass
- 比较 draft token 与 target logits
- 接受匹配 token，拒绝不匹配

### Acceptance Rate

关键指标：平均接受的 token 数量
- 高 acceptance → 高 speedup
- 取决于 draft quality 和 target alignment

## 方法演进

| Era | Method | Draft Model | 特点 |
|---|---|---|---|
| Early | Small AR | 小 autoregressive model | 序列化 drafting |
| 2024 | EAGLE-2/3 | AR + target features | 特征注入提升 alignment |
| 2026 | DFlash | Block Diffusion | 并行 drafting，6x+ 加速 |
| 2026 | DDTree | Block Diffusion + Tree | 多路径验证，acceptance 3-4x |

## 局限与挑战

1. **Draft-Target Alignment**：draft model 分布与 target 越接近越好
2. **Drafting Latency**：draft model 不能太慢，否则抵消加速收益
3. **Memory Footprint**：大 draft model 内存开销高
4. **Long Context**：长序列时 KV cache 增长

## Related

- [[dflash]] — DFlash: Block Diffusion Speculative Decoding
- [[ddtree]] — DDTree: Draft Tree 扩展
- [[eagle-3]] — EAGLE-3: AR-based 高效 drafter
- [[llm-inference-optimization]] — LLM 推理优化总览