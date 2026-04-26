# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A personal AI/ML research wiki built on [Karpathy's llm-wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) pattern. Papers are converted from ArXiv via `arxiv2md`, ingested by the `wiki` CLI (LLM-powered), and the wiki grows as an interlinked knowledge base covering LLMs, post-training, speech models, multimodal AI, and reasoning.

## Commands

```bash
# Convert a paper from ArXiv to markdown and place it
bash scripts/convert.sh 2603.25562 .
# → creates raw/papers/2026/03/2603.25562.md

# Ingest a converted paper (LLM reads it and proposes wiki updates)
wiki ingest "2026/03/2603.25562.md" -y

# Bulk ingest all papers in raw/untracked/
python3 scripts/bulk-ingest.py .

# Rebuild index.md from actual wiki content
python3 scripts/rebuild-index.py .

# Query the wiki
wiki query "your question"
```

## Setup (One-shot)

```bash
bash setup-arxiv-wiki.sh [wiki_dir] [base_url] [model] [api_key]
```

This installs `llm-wiki` globally, applies 4 patches to fix ArXiv paper handling, and initializes the wiki with `.wikirc.yaml`.

## Schema and Conventions

All rules are in **SCHEMA.md** — read it before editing wiki content. Key points:

- **Page naming**: lowercase, hyphens, no spaces
- **YAML frontmatter** on every page (`title`, `created`, `updated`, `type`, `tags`, `sources`)
- **`[[wikilinks]]`** for cross-references (minimum 2 outbound links per page)
- **Tags** must come from the taxonomy in SCHEMA.md — add new tags there first
- **`index.md`** is the content catalog — every new page must be added under the correct section
- **`log.md`** is append-only — every action gets logged with date, sources, and changes
- **Update policy**: newer sources supersede older; flag contradictions in frontmatter

## Directory Structure

```
raw/papers/       # Immutable source material (organized by YYYY/MM/)
entities/         # Entity pages (models, orgs, people, products)
concepts/         # Concept/topic pages (techniques, paradigms, methods)
comparisons/      # Side-by-side analyses
queries/          # Filed query results worth keeping
references/       # Reference docs (patch documentation)
patches/          # 4 source patches for the upstream llm-wiki npm package
scripts/          # convert.sh, bulk-ingest.py, rebuild-index.py
_archive/         # Superseded pages (removed from index)
```

## Patches for Upstream llm-wiki

The `wiki` CLI (npm global) has bugs with large ArXiv papers. Four patches in `patches/` fix:

1. **chatJSON()** — forces `response_format: json_object` for reliable JSON output
2. **Use chatJSON in ingest** — replaces `chat()` with `chatJSON()` in the ingest flow
3. **No LaTeX rule** — prevents JSON escaping failures from LaTeX in agent prompt
4. **Path lookup fix** — recursive file search for `raw/ingested/YYYY/MM/` paths

Applied by `setup-arxiv-wiki.sh`. Manual fallback documented in `references/llm-wiki-patches.md`.

## Known Limitations

- Papers >150KB with dense LaTeX may still fail ingest
- LLM truncates operations after first page — run `scripts/rebuild-index.py` after batch ingest
- Interactive prompts (`wiki ingest`, `wiki query --save`) crash in non-PTY mode — use `-y` and `--no-save` flags
