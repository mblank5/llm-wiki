---
title: AriadneMem: 线团式终身记忆导航
created: 2026-04-17
updated: 2026-04-17
type: concept
tags: [memory, agent, architecture, long-term, graph, optimization]
sources: [raw/papers/2026/02/2603.03290.md]
---

# AriadneMem: Threading the Maze of Lifelong Memory

## 核心问题

长期对话中 agent 记忆面临两大失败模式：
1. **断裂证据 (Disconnected Evidence)**: 多跳推理需要链接跨越时间的分散事实
2. **状态更新 (State Updates)**: 信息演化（如日程变更）与旧记录冲突

现有方案要么存储扁平原子但缺乏拓扑连接（[[simplemem]]），
要么用迭代 LLM 推理连接事实但高延迟高成本。

## 方法

AriadneMem（以希腊神话中赠予线团导航迷宫的 Ariadne 命名）采用**解耦双阶段管线**。

### Phase I: 异步记忆构建（离线）

将原始对话流转化为**稀疏、冲突消解的演化图**。

1. **Entropy-Aware Gating**: 基于嵌入相似度的冗余检测
   - 高相似度 + 短时间窗口内 → 丢弃（过滤 chit-chat 和短期重复）
   - 长期重复仍保留

2. **Atomic Entry Extraction**: 通过 LLM 从滑动窗口提取原子条目
   $$\{m_k\} = \mathcal{F}_\theta(W_t)$$

3. **Conflict-Aware Graph Coarsening**: 区分冗余与状态更新
   - $\text{sim} > \lambda_{\text{coal}} \wedge \text{ovlp} > \lambda_{\text{ovlp}}$ → **Merge**（去重）
   - $\text{sim} > \lambda_{\text{coal}} \wedge \text{ovlp} \leq \lambda_{\text{ovlp}}$ → **Link**（状态更新，保留有向时序边）
   - 否则 → **Add**（新节点）

### Phase II: 实时结构化推理（在线）

将检索重构为**确定性图遍历**而非概率式猜测。

1. **Fast Paths**: 缓存命中 + 正则属性查找（零 LLM 调用）
2. **Hybrid Retrieval**: dense + lexical 混合检索获取终端节点
3. **Algorithmic Bridge Discovery (Steiner Tree)**:
   - 对断开的节点对，搜索时间窗口内的桥接节点
   - $b^* = \arg\max_{m} \cos(E(\mathbf{q}_{ij}), \mathbf{v}_m)$，时间约束
4. **Multi-Hop Path Mining**: DFS 提取有向路径（最大 L=3 跳）
5. **Topology-Aware Reasoning**: 序列化图结构为 $\mathcal{C}_{\text{graph}}$，单次 LLM 调用生成答案

$$a = \text{LLM}(q, \mathcal{C}_{\text{graph}})$$

## 结果

[[locomo-benchmark]] (GPT-4o)：

| 方法 | Multi-Hop F1 | Average F1 | Token Cost | Runtime |
|------|-------------|-----------|------------|---------|
| [[simplemem]] | 35.89 | 39.06 | 550 | 基准 |
| [[a-mem]] | 25.06 | 32.58 | 2,520 | — |
| **AriadneMem** | **41.34** | **42.57** | **497** | **−77.8%** |

- Multi-Hop F1 比 SimpleMem **+15.2%**，Average F1 **+9.0%**
- 运行时间减少 **77.8%**（推理从迭代规划变为图遍历）
- 在 Qwen3-Plus 上优势更大：Average F1 46.03 vs SimpleMem 37.49

## 意义

- **从迭代规划到结构遍历**: 将多跳推理从"LLM 反复猜测中间节点"转为"确定性图路径发现"
- **冲突感知图**: 显式编码状态转移为有向边，解决时间矛盾
- **Steiner Tree 近似**: 首次在 agent memory 中用算法桥接断裂证据
- **极致效率**: 单次 LLM 调用 + 497 token 完成复杂多跳推理
- **对 [[simplemem]] 的定位**: SimpleMem 存储高效但拓扑扁平，多跳推理时被迫回退到昂贵规划循环

## Related

- [[agent-memory-system]] — 记忆系统总览
- [[simplemem]] — 语义压缩记忆（AriadneMem 的直接前驱和对比对象）
- [[a-mem]] — Zettelkasten 式自组织记忆
- [[memgpt]] — 层次化记忆先驱
- [[locomo-benchmark]] — 主要评测基准
- [[nemori]] — 自适应记忆蒸馏（互补的蒸馏层）
