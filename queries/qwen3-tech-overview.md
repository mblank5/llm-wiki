---
title: "Qwen3 技术要点总览"
created: 2026-04-06
updated: 2026-04-12
type: query
tags: [on-policy-distillation, distillation]
sources: [raw/papers/2025/05/2505.09388.md]
---

# Research - 关于qwen3的技术提到过吗

**Question:** 关于qwen3的技术提到过吗

## 关于 Qwen3 技术：已详细记录 ✅

是的，您的个人 Wiki 中**明确包含了 Qwen3 的技术文档**，来源为：

> **[src: raw/papers/2505.09388.md]** — Qwen3 Technical Report（Qwen Team, arXiv:2505.09388）

### 涵盖的核心技术要点：

| 模块 | 关键内容 |
|------|----------|
| **架构** | 6个Dense模型（0.6B~32B）+ 2个MoE模型（30B-A3B、235B-A22B）；GQA、SwiGLU、RoPE、RMSNorm、QK-Norm；MoE采用细粒度专家分割（128专家/8激活）|
| **预训练** | 36万亿token、119语言；三阶段策略（通用→推理→长上下文）；合成数据（Qwen2.5-Math/Coder/VL）|
| **后训练** | 四阶段：① Long-CoT冷启动 ② 推理RL（GRPO）③ 思维模式融合（Thinking/Non-thinking统一）④ 通用RL |
| **创新特性** | ✅ **思维预算（Thinking Budget）**：用户可控制推理token数；✅ **思维/非思维模式切换**：单模型内通过`/think`/`/no_think`标志切换；✅ **强到弱蒸馏（Strong-to-Weak Distillation）**：大模型蒸馏提升小模型性能，GPU耗时仅1/10 |
| **评测亮点** | Qwen3-235B-A22B：AIME'24=85.7、CodeForces=2056、BFCL=70.8，全面超越DeepSeek-V3-Base（参数量仅其1/3）|

### 与On-Policy Distillation知识库的关联
该文档在Wiki Index中被归类为 **Sources之一**，且文中明确提到：
> *"For smaller models, we use strong-to-weak distillation, leveraging both off-policy and on-policy knowledge transfer"*

这与您的OPD（On-Policy Distillation）主题直接相关 → 可进一步交叉参考 [src: 2604.00626]（OPD综述）和 [src: 2407.15134]（PPD）。

如需深入某个技术细节（如GRPO调参、蒸馏策略、思维预算实现），请指定方向，我可帮您精读原文段落。