---
title: 'Relax: Async RL Engine for Omni-Modal Post-Training'
created: 2026-04-27
updated: 2026-04-27
type: concept
tags:
- rl
- training
- architecture
- multimodal
sources:
- raw/papers/2026/04/2604.11554.md
---

# Relax: Async RL Engine for Omni-Modal Post-Training

## Core Problem

Reinforcement learning (RL) post-training has become essential for unlocking reasoning, self-reflection, and tool-use in large language models. However, as models extend to **omni-modal** inputs (image, video, audio, text) and **agentic multi-turn** workflows, existing RL training systems face three interdependent challenges:

1. **Heterogeneous modality pipelines**: A single training batch may contain image patches of varying resolutions, variable-length video frame sequences, and audio waveforms at different sampling rates. These modalities differ in representation, preprocessing latency, memory footprint, and parallelization strategy. Text-first frameworks that bolt on multimodal support via ad hoc wrappers produce fragile pipelines.

2. **Operational robustness at scale**: Omni-modal workloads exhibit severe long-tail latency (a 30-second video clip may take 10x longer than text-only). At hundreds to thousands of GPUs running for days, the system must tolerate hardware failures, NCCL timeouts, and individual service crashes without full-job restart.

3. **Staleness-throughput tradeoff**: In synchronous training, the trainer GPU sits idle waiting for the slowest rollout. Async execution recovers idle time but introduces data staleness (training on rollouts from older policies). Existing systems require separate code paths for on-policy vs. off-policy modes.

## Technical Solution

Relax (Reinforcement Engine Leveraging Agentic X-modality) addresses these through three co-designed architectural layers:

### 1. Three-Plane System Decomposition

Relax separates the RL training system into three orthogonal planes:

- **Control Plane**: A Controller orchestrates the training loop by issuing high-level directives ("generate rollouts", "compute advantages", "run gradient step") without embedding computation logic.
- **Computation Plane**: Each RL role runs in an independent backend. Training roles use Megatron-LM for distributed model parallelism; inference roles use SGLang for high-throughput generation.
- **Data Plane**: A TransferQueue (TQ) data bus mediates all inter-role data movement. No role holds a direct reference to another.

This separation enables independent upgrades — replacing Megatron with FSDP requires no changes to the data bus or orchestration.

### 2. Role-Isolated Service Architecture (Ray Serve)

Each RL role (Actor, Critic, Rollout, Reward, Reference) runs as an independent **Ray Serve Deployment** with its own:
- Failure domain (a crash in the reward model doesn't propagate)
- Resource quota (scale rollout replicas independently)
- Lifecycle management (per-service checkpoint and restart)

**Distributed Checkpoint Service (DCS)**: Weight synchronization from trainer to inference engines is extracted into a dedicated service:
- **Coordinator** (Ray Serve app): topology discovery, synchronization barriers, Prometheus metrics
- **CheckpointEngineClient**: unified save/load interface abstracting transport details
- **NCCL backend**: intra-cluster GPU-to-GPU transfer (lowest latency, data stays on GPU)
- **TCP backend**: cross-cluster scenarios where NCCL is unavailable

**Two-tier fault recovery**:
- Stateless/recomputable roles (Critic, Advantages): in-place restart
- Stateful roles with model weights (Actor, Rollout): global restart from last checkpoint

### 3. Staleness-Unified Asynchronous Training

Relax integrates **TransferQueue** as the asynchronous data bus and introduces a single integer parameter `max_staleness` that unifies the entire on-policy to off-policy spectrum:

Let `v_t` = current training weight version, `v_r` = weight version used by rollout worker. Staleness `s = v_t - v_r`.

- `max_staleness = 0`: Pure on-policy (PPO/GRPO)
- `max_staleness = k`: Near-on-policy (bounded staleness)
- `max_staleness = ∞`: Fully asynchronous off-policy

TQ's **field-based storage** allows different fields of the same sample (responses, log probs, rewards) to be independently written and read, matching the multi-stage RL computation pattern.

A **streaming micro-batch pipeline** eliminates long-tail blocking by allowing downstream stages to consume data as it arrives.

### 4. Omni-Modal Agentic RL Pipeline

- Unified multimodal data preprocessing natively handles images, text, audio, video
- Modality-aware parallelism: ViT replication across tensor-parallel ranks, encoder-aware pipeline placement
- Extension points for agentic RL: multi-turn rollout, custom reward services, tool/sandbox integration
- **R3 (Rollout Routing Replay)** for MoE models with only 1.9% overhead (vs. 32% degradation in veRL)

### Key Formulas

**Staleness definition**: `s = v_t - v_r` where `v_t` is current policy version and `v_r` is rollout generation version

**TransferQueue field independence**: Each sample field `f_i` can be written/read independently:
```
write(sample_id, field_name, data)
read(sample_id, field_name) → data
```

## Experimental Results

**Speedup** (16×H800 cluster):
- On-policy mode: **1.20×** over veRL on Qwen3-4B
- Fully async off-policy: **1.76×** over colocate on Qwen3-4B
- Fully async on Qwen3-Omni-30B: **2.00×** speedup
- All modes converge to the **same reward level**

**MoE support**: R3 routing replay adds only 1.9% overhead vs. 32% degradation in veRL

**Omni-modal convergence**: Stable RL training on Qwen3-Omni across image, text, audio, and video, sustaining over **2,000 steps** on video without degradation

## Comparison with Existing Methods

| System | Async Training | Omni-Modal Native | Staleness Control | Fault Isolation |
|--------|---------------|-------------------|-------------------|-----------------|
| veRL | Partial | No (text-first) | No | No |
| OpenRLHF | Yes | No | No | Partial |
| AReaL | Yes | No | Yes (PPO-specific) | No |
| Relax | **Yes** | **Yes** | **Yes (unified knob)** | **Yes (service-level)** |

## Open Questions

1. **Staleness bounds for convergence**: What is the theoretical maximum staleness that still guarantees convergence for different RL algorithms (GRPO, DAPO, PPO)?

2. **MoE expert routing consistency**: How does R3 handle cases where the MoE routing pattern changes significantly between policy versions?

3. **Multi-modal reward design**: How to design reward functions that properly balance quality across modalities (e.g., audio quality vs. visual alignment)?

4. **Elastic scaling dynamics**: What is the optimal strategy for dynamically provisioning rollout vs. training resources based on workload characteristics?

## See Also

- [[omni-modal-llm]] — Omni-modal LLM architectures that Relax trains
- [[qwen3-omni]] — Qwen3-Omni model family used in Relax experiments
- [[rl]] — Reinforcement learning fundamentals for LLM post-training
