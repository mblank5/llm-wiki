---
title: "Agent 供应链攻击"
created: 2026-04-15
updated: 2026-04-15
type: concept
tags: [agent, security, supply-chain, api, tool-use]
sources: [raw/papers/2026/04/2604.08407.md]
---

# LLM Agent 供应链攻击

## 威胁模型

第三方 API router 作为应用层代理，对每个 JSON payload 有完全明文访问权限。
没有任何 provider 强制 client 和上游模型间的密码学完整性校验。

## 四种攻击类型

1. **AC-1: Payload Injection** — 注入恶意工具调用
2. **AC-1.a: Dependency-targeted Injection** — 自适应定向注入
3. **AC-1.b: Conditional Delivery** — 条件触发投放
4. **AC-2: Secret Exfiltration** — 窃取密钥/凭证

## 实测发现

- 28 个付费 router 中 1 个注入恶意代码
- 400 个免费 router 中 8 个活跃注入
- 17 个触及 AWS canary 凭证
- 1 个从私钥盗取 ETH

## 防御

三种客户端防御：fail-closed policy gate、response-side anomaly screening、append-only transparency log。

## 意义

随着 Agent 系统越来越依赖第三方 API 和 tool calling，供应链安全成为关键问题。

## Related

- [[memreader]]
- [[saver-faithful-reasoning]]
