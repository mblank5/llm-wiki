---
title: "OPD 技术中 Student/Teacher 是否需要同一 Tokenizer"
created: 2026-04-06
updated: 2026-04-12
type: query
tags: [on-policy-distillation, distillation]
sources: [raw/papers/2026/04/2604.00626.md, raw/papers/2026/03/2603.24596.md, raw/papers/2026/02/2602.15260.md]
---

# Research - 所有的on policy distill

**Question:** 所有的on policy distillation技术里面student和teacher都需要是一套tokenizer吗

根据现有Wiki中关于On-Policy Distillation（OPD）技术的文档，**并非所有OPD技术都要求student和teacher使用同一套tokenizer**。

具体来说：

- **标准OPD（如Policy Distillation、PPD、G-OPD等）**：通常假设student和teacher共享相同的tokenizer和词汇表，因为蒸馏过程依赖token-level的KL散度计算（$D_{\text{KL}}(\pi_{\text{teacher}} \parallel \pi_{\text{student}})$），这要求两者的输出空间一致。[src: raw/papers/2604.00626.md]

- **X-OPD（Cross-Modal OPD）**：这是一个明确的**反例**。在X-OPD中，student是Speech LLM（处理音频token），teacher是纯文本LLM（处理文本token），两者**使用完全不同的tokenizer**。X-OPD通过转录文本作为对齐桥梁，在文本空间计算advantage function，从而绕过tokenizer不一致的问题。其核心公式为：
  $$
  A_{cm}(y_t) = \log\pi_{\phi}(y_t|T,y_{<t}) - \log\pi_{\theta}(y_t|S,y_{<t})
  $$
  其中$T$是文本prompt，$S$是语音输入，$\pi_\phi$是文本teacher，$\pi_\theta$是语音student。[src: raw/papers/2603.24596.md]

- **On-Policy Prefix Distillation (OPPD)**：通过prefix共享来缓解tokenizer差异，但通常仍建议tokenizer兼容。[src: raw/papers/2602.15260.md]

**结论**：是否共用tokenizer取决于具体OPD变体。**跨模态OPD（如X-OPD）明确支持不同tokenizer**，而单模态OPD通常要求一致。