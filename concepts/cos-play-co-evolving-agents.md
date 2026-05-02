---
title: COS-PLAY — Co-Evolving LLM Decision and Skill Bank Agents
created: 2026-05-02
updated: 2026-05-02
type: concept
tags: [rl, training, fine-tuning]
sources: [raw/papers/2026/04/2604.20987.md]
---

# COS-PLAY — Co-Evolving LLM Decision and Skill Bank Agents

**arXiv:** [2604.20987](https://arxiv.org/abs/2604.20987)
**Authors:** Xiyang Wu, Zongxia Li, Guangyao Shi, et al. (UMD + USC + MBZUAI)
**Date:** April 2026

## Overview

COS-PLAY is a co-evolution framework for long-horizon interactive tasks where an LLM decision agent retrieves skills from a learnable skill bank, while an agent-managed skill pipeline discovers reusable skills from unlabeled rollouts. An 8B model with COS-PLAY achieves **25.1% average reward improvement** over frontier LLM baselines on single-player game benchmarks.

## Architecture

### Decision Agent

At each timestep, the decision agent performs three operations:

1. **Skill retrieval:** $\tilde{s}_t = \pi^{skill}_\theta(o_t, B)$ — retrieve candidate skills from the bank $B$
2. **Intention update:** $z_t = \pi^{int}_\theta(o_t, \tilde{s}_t)$ — update intention state conditioned on observation and retrieved skill
3. **Action execution:** $a_t \sim \pi^{act}_\theta(\cdot | o_t, z_t, \tilde{s}_t)$ — execute action

The agent maximizes expected cumulative reward:
$$\max_\theta J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta}\left[\sum_{t=1}^T r_t\right]$$

### Skill Bank Agent

The skill bank agent manages a pipeline for discovering and maintaining reusable skills:

1. **Infer segmentation:** Map high-value trajectory segments to existing skills, allowing new skills to appear
2. **Contract learning:** Learn compact state-transition summaries (contracts) that generalize across episodes
3. **Skill bank maintenance:** Update the bank through retention, exploration, and evidence-based merging/splitting/rejection

### Skill Protocol

Each skill has a structured contract:
- **Summary:** What is the purpose of this skill?
- **Pre-condition:** When is this skill applicable?
- **Plan:** How should this skill be carried out?
- **Success/Abort criteria:** When does it succeed or fail?
- **Contract:** What changes after execution?

## Co-Evolving Training

### Three-Stage Loop

1. Decision agent interacts with environment, collects rollouts
2. Skill bank agent segments trajectories, learns contracts, updates skill bank
3. GRPO updates both agents

### Multi-LoRA Design

Separate LoRA adapters for each trainable function:
- **Decision agent (2 adapters):**
  - Action-taking: rewards progress on active skill, discourages unnecessary retrieval
  - Skill-retrieval: evaluated at episode end, rewards skills that led to useful, contract-satisfying outcomes
- **Skill bank agent (3 adapters):**
  - Segmentation adapter
  - Contract adapter
  - Curator adapter

### Cold Start

- GPT-5.4 as teacher model generates 60 seed trajectories per game
- SFT on these trajectories trains Qwen3-8B as shared initialization for both agents

## Reward Design

- **Action-taking reward:** Progress on active skill + penalty for unnecessary skill retrieval
- **Skill-retrieval reward:** Evaluated at episode end based on whether retrieved skills led to contract-satisfying outcomes
- **Skill bank rewards:** Based on skill utility, contract generalization, and bank efficiency

## Experimental Results

### Environments
Six game environments: 2048, Candy Crush, Tetris, Super Mario Bros. (single-player), Avalon, Diplomacy (multi-player social reasoning)

### Key Results
- COS-PLAY with 8B model: **25.1% average reward improvement** over 4 frontier LLM baselines on single-player benchmarks
- Competitive on multi-player social reasoning games (Avalon, Diplomacy)
- Strong opponent (GPT-5-mini) used for social games provides strong supervision signals

## Self-Reinforcing Loop

Better skills → better decision making → better rollouts → better skill learning → repeat

The closed loop is self-reinforcing: the skill bank and decision agent co-evolve, each round's trajectories reflecting the current policy while the updated bank shapes subsequent skill retrieval and action execution.

## Related

- [[imitation-learning]] — Learning from demonstrations
- [[interactive-imitation-learning]] — Interactive IL paradigm
- [[deep-q-network]] — RL foundations
- [[grpo-rl-training]] — GRPO training algorithm
- [[on-policy-distillation]] — On-policy distillation concepts

## Significance for Our Work

COS-PLAY demonstrates co-evolution of two specialized agents (decision + skill management) with separate LoRA adapters, trained via GRPO. This connects to CoPD's parallel training paradigm — both show that co-evolving specialized components outperforms monolithic training. The skill bank concept is relevant for agent systems where the "world model" (agentic world modeling) includes knowledge of available skills and their applicability conditions. For OPD/GRPO training, the multi-LoRA decomposition approach could be applied to distill different expert capabilities into separate adapter modules.
