---
title: DDTree
created: 2026-04-21
updated: 2026-04-21
type: entity
tags: [inference-optimization, speculative-decoding, diffusion, tree-based]
sources: [raw/papers/2026/04/2604.12989.md]
---

# DDTree: Accelerating Speculative Decoding with Block Diffusion Draft Trees

DDTree 是 DFlash 的扩展方法，通过构建 **Draft Tree** 从 block diffusion 的 per-position distributions 中选择多条候选路径，进一步提升 acceptance length。

## 背景：DFlash 的局限

Vanilla DFlash 只验证**单条 drafted trajectory**：
- 每轮只尝试一条 token 序列
- Acceptance length 可能受限（~3.1 tokens）
- Draft model 生成的完整分布信息未被充分利用

## DDTree 的创新

### Draft Tree from Block Diffusion Distributions

Block diffusion drafter 在单次 forward pass 中生成 **per-position marginal distributions**：
```
Position 1: {token_a: 0.3, token_b: 0.2, token_c: 0.15, ...}
Position 2: {token_x: 0.25, token_y: 0.2, ...}
Position 3: {...}
```

DDTree 利用这些分布构建 **draft tree**：
- 节点 = token candidates
- 边 = prefix continuations
- 树覆盖多条 plausible paths

### Best-First Heap Algorithm

给定节点预算 B：
1. 从 root 开始，按 probability 排序候选
2. 用 heap 选择 top-B prefixes（最大化 surrogate acceptance length）
3. 构建前缀闭包树（prefix-closed tree）

**Surrogate objective**：用 draft model 分布近似 target model alignment

### Ancestor-Only Attention Mask

验证阶段：
- 单次 target model forward pass
- 使用 ancestor-only attention mask
- 每个节点只 attend to 其祖先路径
- 并行验证多条候选 → 取最长匹配

## 性能表现

| Metric | Vanilla DFlash | DDTree |
|---|---|---|
| Mean acceptance length τ | ~3.1 tokens | ~10.7 tokens |
| Speedup (DFlash baseline) | 1x | 3.95x - 8.22x |
| End-to-end speedup | 6x+ | 进一步提升 |

**关键收益**：
- Acceptance length 提升 **3-4 倍**
- 无额外 verifier cost（仍是单次 forward）
- 充分利用 draft model 的分布信息

## 与其他 Tree-Based 方法的对比

| Method | Tree Construction | Verification |
|---|---|
| DDTree | Block diffusion distributions (one pass) | Ancestor-only attention |
| 传统 Tree-based | External continuity scoring | 多次 forward 或复杂 mask |

DDTree 的优势：
- **One-pass construction**：无需额外 scoring model
- **理论最优**：在 factorized surrogate 下最优树结构有解
- **简单高效**：heap + prefix-closed 保证

## Related

- [[dflash]] — DFlash: Block Diffusion 基础方法
- [[speculative-decoding]] — Speculative Decoding 基础概念
- [[eagle-3]] — EAGLE-3: AR drafter baseline