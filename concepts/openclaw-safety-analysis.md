---
title: "Your Agent, Their Asset: A Real-World Safety Analysis of OpenClaw"
created: 2026-05-01
updated: 2026-05-01
type: concept
tags: [safety, agent, analysis, behavioral-awareness]
sources: [raw/papers/2026/04/2604.04759.md]
---

# OpenClaw 真实世界安全分析

*对开放平台 AI Agent 进行系统性状态投毒攻击与防御评估 (2026-04)*

## 概要

本文对 OpenClaw（一个开放生态的 AI Agent 平台）进行了系统性安全分析，提出 CIK（Capability-Identity-Knowledge）三维攻击模型，在四种主流 LLM 上评估状态投毒攻击，并提出 GuardianClaw 防御机制。研究发现可执行载荷攻击在所有模型上均达 77%+ 成功率，而上下文媒介攻击对更强模型的效果大幅下降。

## Overview

**攻击模型 CIK**：将 Agent 持久化状态分为三个维度：

1. **Knowledge（知识投毒）**：在 MEMORY.md 中伪造事实或习惯，如伪造退款习惯导致未经授权的批量退款
2. **Identity（身份投毒）**：在 AGENTS.md 中植入信任锚点，如植入虚假 owner 偏好实现凭证窃取
3. **Capability（能力投毒）**：在 skill 脚本中嵌入可执行恶意载荷，如 `rm -rf` 静默删除工作区

**测试模型**：Sonnet 4.5、Gemini 3 Pro、GPT-5.4、Opus 4.5

**防御机制 GuardianClaw**：一个安全检查 skill，在操作执行前触发安全检查清单

## Key Contribution

- **CIK 攻击分类法**：首次系统性定义 Agent 持久化状态的三个攻击面及其对应机制
- **不对称性发现**：上下文媒介攻击（Knowledge/Identity）对强模型效果递减（Opus 仅 3.3%），但可执行载荷攻击跨模型一致高效（77%+）
- **部署鸿沟发现**：被动安装防御 skill 效果有限（ASR 仅降 10%），必须主动加载才能有效防御（ASR 降 70%）
- **案例分析**：提供退款欺诈（R-F2）、凭证窃取（P-F1）、工作区破坏（R-D1）三个真实攻击路径

## Experimental Results

**攻击成功率 (ASR)**（Phase 2，各模型）：

| 攻击向量 | Sonnet 4.5 | Gemini 3 Pro | GPT-5.4 | Opus 4.5 |
|----------|-----------|-------------|---------|----------|
| Knowledge | 85.4% | 93.1% | 89.2% | 76.2% |
| Identity | 80.0% | 91.5% | 85.4% | 60.8% |
| skill-md | 75.0% | 40.0% | 35.0% | 3.3% |
| skill-bash/py | **100%** | **98.6%** | **77.1%** | **100%** |

**GuardianClaw 防御效果**（Sonnet 4.5）：

| 条件 | Baseline | Knowledge | Identity | Capability |
|------|----------|-----------|----------|------------|
| 无防御 | 26.7% | 89.2% | 85.4% | 88.5% |
| 被动安装 | 16.7% | 71.7% | 76.2% | 83.1% |
| 主动加载 | **1.7%** | **17.5%** | **9.2%** | **63.8%** |

关键发现：
- skill-bash/py 是最可靠的攻击向量，在所有模型上 ≥77%
- 主动加载 GuardianClaw 将上下文媒介攻击 ASR 降至 <18%，但可执行载荷攻击仍为 63.8%
- 更强的模型更能抵抗上下文媒介攻击，但无法防御代码执行攻击

## Related

- [[agent-align]] — Agent 安全性对齐是防御状态投毒的根本方法
- [[clawguard]] — GuardianClaw 作为 OpenClaw 平台的安全检查机制
- [[agent-safety-via-rl]] — RL 方法训练 Agent 拒绝危险操作
