---
title: "DFlash"
created: 2026-04-21
updated: 2026-04-21
type: entity
tags: [inference-optimization, speculative-decoding, diffusion, acceleration]
sources: [raw/papers/2026/02/2602.06036.md]
---

# DFlash: Block Diffusion for Flash Speculative Decoding

DFlash 是一种基于 **Block Diffusion** 的 Speculative Decoding 框架，用轻量级 diffusion model 替代传统 autoregressive drafting，实现并行 token 生成，达到 **6x+ 无损加速**。

## 核心问题

Autoregressive LLM 推理天生序列化：
- Token-by-token 生成，每步依赖完整上下文
- GPU 利用率低（memory-bound）
- 长 CoT reasoning 进一步加剧瓶颈

传统 Speculative Decoding 的局限：
- Draft model 仍是 autoregressive → 仍然序列化
- 大 draft model（如 DiffuSpec 用 7B）内存开销高、latency 大
- 小 draft model（如 PARD）容量不足，acceptance length 低，speedup 上限 ~3x

## DFlash 的创新

### 核心思想：The Target Knows Best

大型 AR LLM 的 hidden features **隐含未来 token 信息**（Samragh et al. 2025）。DFlash 利用这一发现：
- 将 target model 的 hidden states 作为 draft model 的 context
- Draft model 变成 diffusion adapter，高效利用 target 的"未来知识"

### Block Diffusion Drafting

```
传统 AR Drafting:  t1 → t2 → t3 → t4 (序列化, 4 steps)
DFlash Block Diff: [t1, t2, t3, t4] (并行, 1 forward pass)
```

- **单次 forward pass** 生成整个 draft block
- 无需 autoregressive 序列化
- 足够轻量（~0.1B 参数），drafting latency 极低

### KV Injection (Context-Aware Drafting)

Draft model condition on target model 的 hidden features：
- 提取 target LLM 的 KV cache / hidden states
- 注入到 diffusion model 作为 conditioning
- Draft quality 与 target alignment 更高 → acceptance rate 提升

## 技术细节

### Block Diffusion Model

基于 discrete diffusion for text generation：
- Mask denoising paradigm
- **Loss decay**：训练时逐步衰减 loss weight，改善收敛
- **Random masked block sampling**：增强鲁棒性和 acceptance length

### 训练策略

- 监督信号：target model 的真实 token distribution
- 数据：来自 target model 的生成样本
- 灵活：可适配任意 AR LLM（Qwen、LLaMA、Kimi 等）

## 性能表现

| Model | Speedup vs Baseline | vs EAGLE-3 |
|---|---|---|
| Qwen3-8B | 6x+ | 2.5x faster |
| Qwen3.5-27B | 4.9x | - |
| Reasoning tasks | 特别显著 | - |

**关键指标**：
- Acceptance length 更高（target-informed drafting）
- Verification overhead 低（单次 forward 验证）
- Lossless：输出与 target model 完全一致

## 支持模型

已发布 DFlash draft model：
- Qwen3.5 系列（4B/9B/27B/35B-A3B）
- Qwen3 系列（4B/8B）
- Kimi-K2.5
- LLaMA-3.1-8B
- Qwen3-Coder 系列
- 更多模型持续扩展

GitHub: https://github.com/z-lab/dflash (1953 stars)

## 部署方式

### vLLM

```bash
vllm serve Qwen/Qwen3.5-27B \
  --speculative-config '{"method": "dflash", "model": "z-lab/Qwen3.5-27B-DFlash", "num_speculative_tokens": 15}' \
  --attention-backend flash_attn
```

### SGLang

```bash
python -m sglang.launch_server \
  --model-path Qwen/Qwen3.5-35B-A3B \
  --speculative-algorithm DFLASH \
  --speculative-draft-model-path z-lab/Qwen3.5-35B-A3B-DFlash \
  --speculative-num-draft-tokens 16
```

### MLX (Apple Silicon)

```python
from dflash.model_mlx import load, load_draft, stream_generate
model, tokenizer = load("Qwen/Qwen3.5-4B")
draft = load_draft("z-lab/Qwen3.5-4B-DFlash")
for r in stream_generate(model, draft, tokenizer, prompt, block_size=16):
    print(r.text)
```

## Related

- [[speculative-decoding]] — Speculative Decoding 基础概念
- [[ddtree]] — DDTree: DFlash 的 draft tree 扩展
- [[eagle-3]] — EAGLE-3: DFlash 的主要竞品（AR drafter）
- [[diffusion-lm]] — Diffusion Language Models
- [[llm-inference-optimization]] — LLM 推理优化总览