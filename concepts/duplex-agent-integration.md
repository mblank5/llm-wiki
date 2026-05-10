---
title: "全双工 Agent 融合架构（Duplex-Agent Integration）"
created: 2026-05-01
updated: 2026-05-01
type: concept
tags: [concept, full-duplex, agent, tool-use, architecture, streaming]
sources: []
---

# 全双工 Agent 融合架构

## 定义

全双工 Agent 融合架构是指将全双工对话能力（同时听和说、打断、判停）与 Agent 能力（Function Call、Tool 使用）结合的系统架构。核心挑战在于：**轮次管理和 Function Call 执行可能冲突**。

## 两种融合路线

### 路线 A：外挂式（DuplexCascade 方案）

全双工控制层独立于 Audio-Agent，通过特殊 token 控制 Agent 的输入时机。

```
用户音频 → [流式ASR] → 微轮次文本 → [全双工控制层] → [Audio-Agent] → Function Call → Tool
                ↑                              ↑
           每 0.6s 聚合                    控制 token 决策
```

**特殊 Token 设计**：

```
用户侧:
├── <uvoice>: 当前有用户语音
├── <uvend>: 用户说完了（判停）
├── <uinterrupt>: 用户打断
├── <ubackchannel>: 用户附和（"嗯"、"好的"）
├── <novoice>: 当前无用户语音
└── <uthinking>: 用户思考中

Agent 侧:
├── <astart>: Agent 开始回复
├── <aend>: Agent 结束回复
├── <astop>: Agent 停止回复（被打断）
├── <await>: Agent 等待用户输入
├── <afcall>: Agent 执行 Function Call
├── <atwait>: Agent 等待 Tool 响应
├── <abackchannel>: Agent 发出附和
├── <abusy>: Agent 正在处理（不可被打断）
└── <aidle>: Agent 空闲
```

**关键设计**：`<afcall>` 和 `<atwait>` 是 Agent 场景特有的 token。当 Agent 执行 Function Call 时，全双工控制层知道 Agent 正在忙，即使用户说话也不打断。

**训练方法**：LoRA 微调（参考 DuplexCascade）
- 数据：50k 文本对话 + 合成双通道对话
- 步数：5k 步
- 成本：8 卡 5 小时

### 路线 B：原生式（双流 Token 方案）

全双工能力和 Agent 能力融合在一个模型中，同时建模用户音频流和 Agent 音频流。

```
用户音频流: u1, u2, u3, ...
Agent 音频流: a1, a2, a3, ...

交织 Token 序列:
[u1, u2, a1, u3, u4, a2, a3, u5, ...]
```

**打断判断逻辑**：
```
正常对话: [u1, u2, u3, <uvend>, a1, a2, <aend>, u4, u5, <uvend>, ...]
                                         ↑ 正常轮次切换

打断:     [u1, u2, u3, <uvend>, a1, u4, u5, ...]
                                  ↑ Agent 刚开始回复，用户又说话 → 打断
```

**参考工作**：
- [[moshi]] — 双流 Token 建模
- [[turnguide]] — 文本-语音交织生成
- [[silent-thought]] — FLAIR 潜在推理

## 状态机设计

全双工控制层的核心是一个状态机：

```
IDLE ──用户开始说话──→ LISTENING ──用户说完──→ PROCESSING
  ↑                        │                        │
  │                        │ 用户打断               │ Agent 开始回复
  │                        ↓                        ↓
  └──Agent 完成────────← RESPONDING ←──执行中──── PROCESSING
                            │
                            │ 用户打断
                            ↓
                       INTERRUPTED ──处理新输入──→ PROCESSING
```

**Function Call 状态感知**：

```python
class DuplexStateMachine:
    def on_user_speech(self, text):
        if self.state == "IDLE":
            self.state = "LISTENING"
        elif self.state == "LISTENING":
            self.user_buffer.append(text)
        elif self.state == "RESPONDING":
            if self.agent_is_busy:  # Function Call 执行中
                self.queue_interrupt(text)  # 排队，等 Function Call 完成
            else:
                self.stop_agent()
                self.state = "INTERRUPTED"
```

## Function Call 与轮次管理的冲突解决

### 场景 1：Function Call 执行期间用户打断

```
用户: "帮我查明天天气"
Agent: FunctionCall(get_weather) → 执行中（500ms）
用户: "算了不查了"

处理:
1. Function Call 执行期间，全双工控制层保持 <abusy> 状态
2. 如果用户打断，立即取消 Function Call
3. 回复 "好的，不查了"
```

### 场景 2：Tool Response 等待期间用户打断

```
Agent: FunctionCall(search_parking) → Tool 执行中
用户: "换个地方找"

处理:
1. Tool 执行期间，全双工控制层保持 <atwait> 状态
2. 如果用户打断，取消 Tool 执行
3. 用新的用户输入重新执行 Function Call
```

### 场景 3：多轮对话中的打断

```
用户: "播放周杰伦的歌"
Agent: FunctionCall(play_music, {artist: "周杰伦"}) → 播放中
用户: "下一首"

处理:
1. 这不是打断，是新的指令
2. Function Call 已完成（正在播放）
3. 作为新的用户输入处理: FunctionCall(play_music, {action: "next"})
```

## 路线对比

| 维度 | 路线 A（外挂式） | 路线 B（原生式） |
|------|-----------------|-----------------|
| 延迟 | 1-2s | 0.5-1s |
| 训练难度 | 中 | 极高 |
| 部署复杂度 | 中（2个模型） | 低（1个模型） |
| Agent 能力 | 不变 | 可能降级 |
| 全双工能力 | 中 | 高 |
| Function Call 感知 | 通过 token 感知 | 原生感知 |

## 推荐路线

| 阶段 | 方案 | 时间 |
|------|------|------|
| MVP | 路线 A 外挂式 | 3-6 月 |
| V2 | 路线 A 优化（联合训练） | 6-12 月 |
| V3 | 路线 B 原生式 | 12-24 月 |

## 相关页面

- [[full-duplex-speech-model]] — 全双工语音模型总览
- [[audio-agent]] — Audio-Agent 训练管线
- [[duplex-cascade]] — DuplexCascade VAD-free 级联方案
- [[moshi]] — Moshi 双流全双工模型
- [[turnguide]] — TurnGuide 文本-语音交织方法
- [[silent-thought]] — FLAIR 潜在推理全双工方法
