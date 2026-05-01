---
title: "LongCat-Flash"
created: 2026-05-01
updated: 2026-05-01
type: entity
tags: [model, architecture, training, inference, alignment, open-source, reasoning]
sources: [raw/papers/2025/09/2509.01322.md]
---

# LongCat-Flash

美团 LongCat 团队发布的旗舰级开源 MoE 大语言模型（arXiv 2509.01322，2025-09）。**560B 总参数，18.6B~31.3B 动态激活（平均 27B）**，专为计算效率和 Agentic 能力设计。

## 一、核心参数

| 参数 | 值 |
|------|-----|
| 总参数量 | 560B |
| 激活参数量 | 18.6B~31.3B（平均 ~27B），动态分配 |
| 层数 | 28 层（不含 MTP 层） |
| 隐藏维度 | 6144 |
| 注意力头数 | 64，每头维度 128 |
| KV 压缩维度 | 512 |
| Query 压缩维度 | 1536 |
| FFN 中间维度（dense） | 12288 |
| FFN 专家中间维度 | 2048 |
| FFN 专家数 | 512 |
| 零计算专家数 | 256 |
| 每 token 激活专家数 | 12（含零计算专家） |
| 上下文窗口 | 128K tokens |
| 词表大小 | 131,072 |
| 预训练数据量 | 20+ trillion tokens |
| 训练时间 | 30 天 |
| 训练算力 | 5万~6万张国产计算卡 |

## 二、架构创新

LongCat-Flash 的核心设计理念：**不是所有 token 都值得同等计算**。通过两项架构创新实现动态计算分配。

### 2.1 Zero-Computation Experts（零计算专家）

**核心思想**：在 MoE 专家池中混入"零计算专家"——被选中的零计算专家直接将输入原样返回，不消耗任何 FLOPs。

**数学表达**：

```
MoE(x_t) = Σ(i=1 to N+Z) g_i · E_i(x_t)
```

其中 N 个标准 FFN 专家 + Z 个零计算专家。零计算专家 E_i(x_t) = x_t。

**动态计算预算控制**：

路由器为每个 token 选择 K 个专家，其中真实 FFN 专家的数量根据 token 重要性动态调整。通过 PID 控制器调节专家偏置：

```
Δb_i = μ · (K_e/K · 1/N - T_i / (K · T_all))
```

- μ：偏置自适应率
- K_e：期望激活的 FFN 专家数（< K）
- T_i：路由到第 i 个专家的 token 数
- T_all：全局 batch 中的总 token 数

PID 控制器确保专家分配收敛到目标比例。实验表明，约 20B tokens 调整后，所有层的平均激活专家数收敛到期望值，波动 <1%。

**负载均衡控制**：

在语料级均衡基础上，引入设备级负载均衡损失，防止 EP 组间的极端不均衡。将零计算专家视为一个额外组：

```
L_LB = α · Σ(j=1 to D+1) f_j · P_j
```

其中 D+1 组包含所有零计算专家，确保 FFN 专家与零计算专家的比例趋近 K_e/(K-K_e)。

### 2.2 Shortcut-Connected MoE (ScMoE)

**问题**：MoE 模型的大规模训练/推理受限于通信开销——all-to-all 通信必须在计算前完成。

**方案**：ScMoE 引入跨层 shortcut，重排执行流水线：前一层的 dense FFN 与当前 MoE 层的 dispatch/combine 通信**并行执行**。

**优势**：
- 相比 shared-expert 仅重叠一个专家的计算，ScMoE 重叠整个前一层的计算，窗口更大
- 训练：前一块的计算与 MoE 的 dispatch/combine 通信完全并行
- 推理：Single Batch 重叠流水线，TPOT（每输出 token 时间）降低约 50%
- 节点内 NVLink 通信（dense FFN 的 TP）与节点间 RDMA 通信（MoE 的 EP）同时执行

**无损质量**：训练损失曲线与无 ScMoE 的基线几乎完全一致，在多种配置下（2.4B-16B MoE + MLA、3B-20B + MHA、15B-193B + GQA）均验证。

### 2.3 方差对齐设计（Variance Alignment）

#### 2.3.1 MLA 尺度修正

LongCat-Flash 使用修正的 MLA（Multi-head Latent Attention），引入尺度修正因子 α_q 和 α_kv：

```
α_q = √(d_model / d_q)
α_kv = √(d_model / d_kv)
```

**原因**：查询/键向量的各组件方差与源维度成正比。RoPE 键组件 k_t^R 的方差 ∝ d_model，而低秩路径组件的方差 ∝ d_q 或 d_kv。当 d_q、d_kv、d_model 变化时，这种维度差异导致注意力分数在初始化时不稳定。

#### 2.3.2 专家初始化方差补偿

LongCat-Flash 采用 DeepSeek-MoE 的细粒度专家策略（每个专家分割为 m 个更细粒度的专家）。分割导致：
1. **Gating Dilution**：softmax 门控分布在更多专家上，单个 gating 值幅度降低 → 输出方差降低 m 倍
2. **维度缩减**：每个细粒度专家的中间隐藏维度降低 m 倍 → 单个专家输出方差降低 m 倍

补偿因子 γ = m（两个 m 倍效应的叠加）。

### 2.4 模型配置细节

**Tokenizer**：BPE，131,072 词表。继承 GPT-4 预分词框架，改进：(1) 增强 CJK 字符分割，(2) 独立数字 tokenization 提升数学能力。

**Multi-Token Prediction (MTP)**：辅助训练目标，使用单个 dense 层（非 MoE）作为 MTP 头。MTP 损失收敛快，在训练中期引入以平衡性能与预测准确率。MTP 头在评估中达到 >90% 接受率。

## 三、预训练

### 三阶段课程

1. **通用预训练**：~20T tokens，序列长度 8192，建立基础模型
2. **推理与代码增强**：万亿级推理/代码数据，增强数学和编程能力
3. **长上下文扩展**：训练上下文长度至 128K

### 训练策略

#### 超参数迁移（Hyperparameter Transfer）

基于宽度缩放理论，从小模型（proxy）迁移最优超参数到大模型：

1. 宽度缩放因子 s = n_target / n_proxy = 8（proxy 宽度 768）
2. 在 proxy 上搜索最优初始化方差 σ²_proxy 和学习率 η_proxy
3. 按"Adam LR Full Align"规则迁移：
   - Embedding：σ² 和 η 不变
   - Hidden/Unembedding：σ²_target = σ²_proxy / s，η_target = η_proxy / s

#### 模型增长初始化（Model Growth）

采用 layer stacking 技术：先训练 14 层模型，然后堆叠为 28 层。

```
L_small = l₁ ∘ l₂ ∘ ... ∘ l_n
L_target = L_small ∘ L_small （r=2 次堆叠）
```

模型增长的特征损失轨迹：初始上升 → 加速收敛 → 超越随机初始化基线。原因：(1) 小模型更快收敛提供更高质量的参数初始化，(2) 增长操作作为隐式正则化防止参数坍缩。

#### 训练稳定性套件

**路由器稳定性**：监控两个指标：
- **路由器权重相似度**：专家权重向量的平均成对余弦相似度
- **梯度范数比 R_g**：R_g = ‖α∇L_LB‖₂ / ‖∇L_LM‖₂

推荐 R_g < 0.1，确保负载均衡项作为正则器而不压倒 LM 损失。

**激活稳定性（Hidden z-loss）**：

```
L_Z = (λ/T) Σ_t (log Σ_i exp(|z_t^i|))²
```

极小的 λ 即可显著抑制大规模激活现象，降低 BF16 训练中的数值错误风险。

**优化器稳定性**：精细调整 Adam epsilon 参数。

**确定性计算**：保证实验完全可复现，支持 SDC（静默数据损坏）检测。

### 训练基础设施

- 数值精度控制与故障检测
- Kernel 优化（确定性与性能）
- 大规模分布式训练策略
- 可靠性与可观测性
- **98.48% 时间可用率**，无需人工干预故障恢复

## 四、后训练

### 4.1 推理与代码

- **数学**：多阶段数学推理训练
- **代码**：代码生成与理解
- **逻辑推理**：形式化与常识推理

### 4.2 Agentic 工具使用

多智能体合成框架生成高质量 Agentic 训练数据，任务难度沿三个轴定义：
1. **信息处理**复杂度
2. **工具集复杂度**
3. **用户交互**复杂度

使用专用控制器生成需要迭代推理和环境交互的复杂任务。

### 4.3 通用能力

- 指令跟随
- 长上下文
- 安全性

## 五、推理与部署

### 模型特定优化

- **计算与通信编排**：ScMoE 架构天然支持计算-通信重叠
- **投机解码**：MTP 头作为 draft model，>90% 接受率
- **KV Cache 压缩**：MLA 的 KV 压缩维度 512

### 系统级优化

- 最小化调度开销
- 自定义 Kernel
- 量化（FP8/BF16）

### 实测性能

| 指标 | 值 |
|------|-----|
| 推理吞吐 | >100 tokens/秒（H800） |
| 推理成本 | $0.70 / 百万 output tokens |
| FP8 部署 | 单节点 8xH20-141G |
| BF16 部署 | 双节点 16xH800-80G |

## 六、评测表现

### 基础模型评测

与 DeepSeek-V3.1、Kimi-K2 等非推理前沿模型相当，使用更少参数且推理更快。

### 指令微调模型评测

| Benchmark | 分数 |
|-----------|------|
| ArenaHard-V2 | 86.5 |
| TerminalBench | 39.5 |
| τ²-Bench | 67.7 |
| Meeseeks | 与前沿 LLM 相当 |
| VitaBench | 优于其他 LLM |

**Meeseeks**：美团自研 benchmark，通过迭代反馈框架模拟真实人机交互，评估多轮指令跟随能力。

**VitaBench**：美团自研 benchmark，利用真实业务场景评估复杂现实任务处理能力。

## 七、开源信息

- **在线体验**：https://longcat.ai
- **HuggingFace**：https://huggingface.co/meituan-longcat
- **GitHub**：https://github.com/meituan-longcat
- **协议**：MIT

## 八、相关页面

- [[longcat-flash-omni]] — LongCat-Flash-Omni：全模态版本
- [[longcat-flash-thinking]] — LongCat-Flash-Thinking：推理版本
- [[longcat-flash-thinking-2601]] — LongCat-Flash-Thinking-2601：升级版推理
- [[longcat-video]] — LongCat-Video：视频生成版本
- [[longcat-image]] — LongCat-Image：图像生成版本
- [[longcat-next]] — LongCat-Next：原生多模态自回归版本
- [[mixture-of-experts]] — MoE 架构概念
- [[speculative-decoding]] — 投机解码概念
