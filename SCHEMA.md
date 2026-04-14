# Wiki Schema

## Domain
AI/ML 研究与技术，聚焦：大语言模型（LLM）、后训练技术（On-Policy Distillation、RLHF/GRPO、知识蒸馏）、语音交互模型（全双工/半双工）、多模态 AI、推理优化、AI Agent、模型行为与安全。

## Conventions
- File names: lowercase, hyphens, no spaces (e.g., `seeduplex.md`)
- Every wiki page starts with YAML frontmatter (see below)
- Use `[[wikilinks]]` to link between pages (minimum 2 outbound links per page)
- When updating a page, always bump the `updated` date
- Every new page must be added to `index.md` under the correct section
- Every action must be appended to `log.md`

## Frontmatter
```yaml
---
title: Page Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: entity | concept | comparison | query | summary
tags: [from taxonomy below]
sources: [raw/papers/source-name.md]
---
```

## Tag Taxonomy
- **Models**: model, architecture, benchmark, training, inference, alignment, speech-model, multimodal, open-source
- **People/Orgs**: person, company, lab, open-source
- **Techniques**: optimization, fine-tuning, rlhf, grpo, distillation, on-policy, quantization, codec, rl, ppo
- **Reasoning**: reasoning, chain-of-thought, self-play
- **Applications**: voice-assistant, chatbot, robotics, tool-use
- **Data**: dataset, benchmark, evaluation, mos
- **Paradigms**: full-duplex, half-duplex, end-to-end, streaming, cascaded
- **Safety**: behavioral-awareness, safety, alignment, backdoor
- **Meta**: comparison, timeline, controversy, prediction, survey

Rule: every tag on a page must appear in this taxonomy. If a new tag is needed, add it here first, then use it.

## Page Thresholds
- **Create a page** when an entity/concept appears in 2+ sources OR is central to one source
- **Add to existing page** when a source mentions something already covered
- **DON'T create a page** for passing mentions, minor details, or things outside the domain
- **Split a page** when it exceeds ~200 lines — break into sub-topics with cross-links
- **Archive a page** when its content is fully superseded — move to `_archive/`, remove from index

## Entity Pages
One page per notable entity. Include:
- Overview / what it is
- Key facts and dates
- Relationships to other entities ([[wikilinks]])
- Source references

## Concept Pages
One page per concept or topic. Include:
- Definition / explanation
- Current state of knowledge
- Open questions or debates
- Related concepts ([[wikilinks]])

## Comparison Pages
Side-by-side analyses. Include:
- What is being compared and why
- Dimensions of comparison (table format preferred)
- Verdict or synthesis
- Sources

## Update Policy
When new information conflicts with existing content:
1. Check the dates — newer sources generally supersede older ones
2. If genuinely contradictory, note both positions with dates and sources
3. Mark the contradiction in frontmatter: `contradictions: [page-name]`
4. Flag for user review in the lint report

## Directory Structure
```
wiki/
├── SCHEMA.md           # This file
├── index.md            # Content catalog with one-line summaries
├── log.md              # Chronological action log (append-only)
├── raw/                # Immutable source material
│   ├── articles/       # Web articles, clippings
│   ├── papers/         # PDFs, arxiv papers (date-organized)
│   ├── transcripts/    # Meeting notes, interviews
│   └── assets/         # Images, diagrams
├── entities/           # Entity pages (people, orgs, products, models)
├── concepts/           # Concept/topic pages
├── comparisons/        # Side-by-side analyses
└── queries/            # Filed query results worth keeping
```
