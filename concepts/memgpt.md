---
title: MemGPT: LLM 即操作系统
created: 2026-04-17
updated: 2026-04-17
type: concept
tags: [memory, agent, architecture, long-term]
sources: [raw/papers/2023/10/2310.08560.md]
---

# MemGPT: LLM 作为操作系统的层次化记忆

## 核心问题

LLM 受限于固定上下文窗口，无法在多轮交互中管理超出上下文容量的信息。
MemGPT 将 LLM 类比为操作系统，引入 **虚拟上下文管理**（virtual context management），
通过分页机制在有限上下文窗口内操作超出容量的记忆。

## 方法

### 操作系统隐喻

- **Main Context** = RAM：LLM 当前可见的上下文窗口
- **External Context** = Disk：外部存储（对话历史、文档等），不在当前窗口内

LLM 通过 **自指导的工具调用**（self-directed memory operations）在两层间移动信息。

### 记忆操作

MemGPT 定义了一组类 OS 的 memory functions：

| 操作 | 类比 | 描述 |
|------|------|------|
| `memory.insert` | 写入文件 | 将信息写入 external context |
| `memory.search` | 搜索文件 | 从 external context 检索相关片段 |
| `memory.replace` | 修改文件 | 更新已有记忆内容 |
| `send_message` | I/O | 向用户或其他 agent 发送消息 |

### 关键设计

1. **Self-directed**: LLM 自主决定何时读写记忆，无需外部调度
2. **Hierarchical paging**: 类似 OS 的分页机制，main context 作为 cache 优先缓存最近信息
3. **Function calling**: 通过 LLM 的 tool-use 能力实现记忆操作

## 结果

- 在多文档 QA 和长期对话任务上显著优于固定上下文基线
- 证明了 LLM 能自主管理超出上下文窗口的信息
- 为后续 agent memory 系统奠定基础架构思路

## 意义

- **开创性工作**: 首次提出 LLM-as-OS 隐喻，启发后续所有 agent memory 设计
- **自指导记忆**: LLM 自主决定记忆操作的方向，而非依赖预设规则
- **层次化设计**: main/external context 的分层思想被 [[mem0]]、[[lightmem-agent-memory]] 等继承
- **局限性**: 依赖 LLM 的 tool-calling 能力，记忆操作的质量受 LLM 推理能力限制；在
  [[locomo-benchmark]] 上性能不如后继方案 [[a-mem]]、[[simplemem]]

## Related

- [[agent-memory-system]] — Agent 记忆系统总览
- [[mem0]] — 增量记忆管线方案
- [[lightmem-agent-memory]] — 三层记忆架构
- [[a-mem]] — Zettelkasten 式自组织记忆
- [[simplemem]] — 高效语义压缩记忆
