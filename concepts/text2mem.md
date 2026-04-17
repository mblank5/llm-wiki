---
title: Text2Mem: 统一记忆操作语言
created: 2026-04-17
updated: 2026-04-17
type: concept
tags: [memory, agent, architecture, tool-use]
sources: [raw/papers/2025/09/2509.11145.md]
---

# Text2Mem: A Unified Memory Operation Language for Memory OS

## 核心问题

现有 agent 记忆框架暴露的操作原语不完整且不一致：
- 大多仅支持 encode/retrieve/delete 等基本操作
- merge、promote/demote、split、lock、expire 等高阶控制缺失或各系统实现不同
- 自然语言指令（"暂时不要提午饭的事"）歧义严重，不同系统行为不一致
- 缺乏**形式化可执行规范**

## 方法

### 设计哲学

借鉴 text-to-SQL 的经验：自然语言模糊 → 需要约束 schema → 才能标准化执行和评估。

### 三原则

1. **互斥性 (Mutual Exclusivity)**: 每个操作代表唯一原子行为，无语义重叠
2. **完备性 (Completeness)**: 覆盖编码、存储、检索全生命周期
3. **极小性 (Minimality)**: 消除冗余动词，每个操作贡献独特表达力

### 12 个操作动词

| 阶段 | 操作 | 描述 |
|------|------|------|
| 编码 | **Encode** | 语义理解后创建结构化记忆条目 |
| 存储 | **Update** | 字段修改，含验证和血缘追踪 |
| | **Label** | 标签/分面增删，含去重约束 |
| | **Promote** | 提升优先级，可附定期提醒 |
| | **Demote** | 降低优先级，不删除数据 |
| | **Merge** | 合并记录，保留血缘链接 |
| | **Delete** | 软/硬删除，含策略和锁检查 |
| | **Split** | 拆分复合条目为链接子单元 |
| | **Lock** | 只读/追加策略限制编辑 |
| | **Expire** | TTL 过期触发降级或匿名化 |
| 检索 | **Retrieve** | 过滤排序查询，权限感知 |
| | **Summarize** | 聚焦摘要，token 预算控制 |

### Schema 规范

每个操作实例化为 **JSON-based schema**，包含：
- 必填字段、类型约束、语义不变量
- 时间范围、优先级、标签等参数标准化

### Validator–Parser–Adapter 管线

1. **Validator**: 检查结构+语义合法性（锁定的条目不可硬删除等）
2. **Parser**: 转为强类型操作对象，参数标准化
3. **Adapter**: 映射到 SQL 原型后端 **或** 真实框架（MemGPT/mem0/Letta）

**跨后端可移植**: 同一 typed object 在不同系统上行为等价。

### Text2Mem Bench

规划中的评测基准，分离 schema 生成和后端执行：
- **Plan-level**: schema 准确性、执行成功率
- **Execution-level**: 期望匹配率、检索质量

## 意义

- **首个统一记忆操作语言**: 填补了 agent memory 领域缺乏形式化操作规范的空白
- **与 text-to-SQL 类比**: 将记忆操作从 ad-hoc API 提升为可审计的语言层
- **高阶操作标准化**: Promote/Demote/Merge/Lock/Expire 为首次被标准化定义
- **实际覆盖**: 12 个操作中仅 Encode/Delete/Retrieve 在现有框架中普遍支持，
  其余 9 个为 Text2Mem 首次系统化
- **局限**: Text2Mem Bench 尚为规划阶段；实际后端适配仍需逐框架实现

## Related

- [[memgpt]] — LLM-as-OS 记忆框架（可适配后端）
- [[mem0]] — 增量记忆管线（可适配后端）
- [[agent-memory-system]] — 记忆系统总览
- [[ariadne-mem]] — 图结构终身记忆系统
- [[nemori]] — 自适应记忆蒸馏（互补的蒸馏层）
