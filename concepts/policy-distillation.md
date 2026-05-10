---
title: "Policy Distillation"
created: 2026-04-06
updated: 2026-04-10
type: concept
tags: ['distillation', 'rl']
sources: []
---

     1|# Policy Distillation
     2|
     3|Policy distillation is a method for transferring knowledge from a trained reinforcement learning agent (teacher) to a new network (student), enabling model compression, multi-task policy consolidation, and online learning stabilization. Introduced by Rusu et al. (2015), it adapts supervised distillation techniques (originally for classification) to the reinforcement learning domain, where the teacher's Q-values are used as training targets.
     4|
     5|## Key Properties
     6|
     7|- **Model Compression**: Student networks can be up to 15 times smaller than the teacher DQN with minimal performance loss.
     8|
     9|- **Multi-Task Learning**: Multiple single-task expert policies can be combined into a single multi-task policy that outperforms individual teachers.
    10|
    11|- **Online Distillation**: The student can track and stabilize a continuously improving DQN teacher during training.
    12|
    13|- **Loss Function Sensitivity**: The Kullback-Leibler (KL) divergence with a low temperature (tau=0.01) outperforms mean squared error (MSE) and negative log likelihood (NLL) for policy distillation. MSE fails because small Q-value differences can determine optimal actions, while NLL amplifies teacher noise.
    14|
    15|## Technical Approach
    16|
    17|The teacher generates a dataset of state observations and Q-value vectors. The student is trained via supervised regression. Three loss functions were evaluated:
    18|
    19|1.  **MSE**: Minimizes squared error between teacher and student Q-values.
    20|2.  **NLL**: Trains student to predict only the teacher's highest-valued action.
    21|3.  **KL Divergence**: Uses a sharpened softmax of teacher Q-values as targets, balancing information transfer and noise reduction.
    22|
    23|For multi-task distillation, separate replay memories and output layers (controllers) per task are used, with shared convolutional features.
    24|
    25|## Context and Related Concepts
    26|
    27|- Originates from supervised [[model-distillation]] (Bucila et al., 2006; Hinton et al., 2014).
    28|
    29|- Applied to [[deep-q-network|Deep Q-Networks (DQN)]] teachers in the [[atari-2600]] domain.
    30|
    31|- Contrasts with [[imitation-learning]] methods like DAGGER, as the student does not generate training trajectories.
    32|
    33|- Addresses challenges of [[multi-task-learning]] in RL, where tasks (games) have diverse inputs and reward scales.
    34|
    35|[src: raw/ingested/2015/11/1511.06295.md]