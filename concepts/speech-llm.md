---
title: Speech Llm
created: 2026-04-06
updated: 2026-04-10
type: concept
tags: ['speech-model', 'multimodal']
sources: []
---

     1|# Speech LLM
     2|
     3|Speech Large Language Models (Speech LLMs) are end-to-end (E2E) multimodal models that process continuous speech signals directly, replacing traditional cascaded architectures (ASR + LLM + TTS).
     4|
     5|## Key Properties
     6|- **Direct speech modeling**: Operates in continuous speech signal space rather than discrete text tokens
     7|- **Reduced latency**: Eliminates intermediate ASR/TTS conversion steps
     8|- **Paralinguistic capture**: Models intonation, emotion, and environmental context
     9|- **Performance gap**: Exhibit significant degradation in complex instruction following, logical reasoning, and knowledge-intensive queries compared to text-based counterparts
    10|
    11|## Current Challenges
    12|- Scarcity of high-quality paired speech-reasoning data
    13|- Misalignment between continuous acoustic representations and discrete logical space of text LLMs
    14|- Inability to transfer high-quality SFT and RL data from text LLM training
    15|- Exposure bias in offline distillation methods
    16|
    17|## Notable Systems
    18|- GPT-4o, Gemini 2.5, Qwen3-Omni, Voxtral
    19|
    20|## Training Paradigms
    21|- Standard SFT + RL (insufficient for gap closure)
    22|- Offline distillation (exposure bias issues)
    23|- [[x-opd|X-OPD]]: Cross-Modal On-Policy Distillation for capability alignment
    24|
    25|[src: raw/ingested/2026/03/2603.24596.md]

## Related

- [[seeduplex]]
- [[moshi]]
- [[minmo]]
- [[llama-omni]]
- [[freeze-omni]]
- [[full-duplex-speech-model]]
- [[stream-omni]] — streaming speech model for real-time interaction