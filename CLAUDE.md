# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A personal AI/ML research wiki built on [Karpathy's llm-wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) pattern. Raw papers are converted with `arxiv2md`, cleaned into `papers/YYYY/MM/*.md`, and connected to top-level `concepts/`, `entities/`, and `queries/` pages. The static site generator publishes the wiki as a browsable research desk covering LLMs, post-training, speech models, multimodal AI, and reasoning.

## Commands

```bash
# Clean raw paper markdown into papers/YYYY/MM/*.md
python3 scripts/clean-papers.py .

# Validate metadata, required fields, links, sources, and page-size warnings
python3 scripts/lint-wiki.py .
python3 scripts/lint-wiki.py . --max-findings 80

# Generate or inspect the static site
python3 scripts/generate-web.py
python3 scripts/generate-web.py --status
python3 scripts/generate-web.py --incremental
```

Legacy `llm-wiki` helper scripts are still present:

```bash
bash scripts/convert.sh 2603.25562 .
python3 scripts/bulk-ingest.py .
python3 scripts/rebuild-index.py .
bash setup-arxiv-wiki.sh [wiki_dir] [base_url] [model] [api_key]
```

`setup-arxiv-wiki.sh` installs `llm-wiki` globally, applies 4 patches to fix
ArXiv paper handling, and initializes another wiki workspace with `.wikirc.yaml`.

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
concepts/         # Concept/topic pages
entities/         # Entity pages: models, orgs, products
queries/          # Filed query results worth keeping
raw/              # Immutable source material
papers/           # Cleaned paper markdown organized by YYYY/MM
scripts/          # cleaning, lint, static generation, legacy helpers
web/output/       # Generated static site, ignored by git
web/app/          # Experimental multi-wiki FastAPI app
references/       # Reference docs and patch documentation
patches/          # Source patches for upstream llm-wiki
```

## Quality Gate

Run `python3 scripts/lint-wiki.py .` before publishing or large content edits.
The lint blocks structural errors that break downstream tools: invalid YAML
frontmatter, missing required fields, and malformed `tags`/`sources` fields.
It currently reports tag taxonomy drift, missing source files, broken wikilinks,
long pages, and sparse links as warnings so historical debt can be fixed in
batches.

GitHub Pages runs:

1. `python3 scripts/lint-wiki.py .`
2. `python3 scripts/generate-web.py`
3. `python3 -m json.tool web/output/search-index.json`

## Patches for Upstream llm-wiki

The `wiki` CLI (npm global) has bugs with large ArXiv papers. Four patches in `patches/` fix:

1. **chatJSON()** — forces `response_format: json_object` for reliable JSON output
2. **Use chatJSON in ingest** — replaces `chat()` with `chatJSON()` in the ingest flow
3. **No LaTeX rule** — prevents JSON escaping failures from LaTeX in agent prompt
4. **Path lookup fix** — recursive file search for `raw/ingested/YYYY/MM/` paths

Applied by `setup-arxiv-wiki.sh`. Manual fallback documented in `references/llm-wiki-patches.md`.

## Known Limitations

- Long papers are currently cleaned through a fixed input window in `clean-papers.py`; chunked section-level cleaning is a future improvement.
- `scripts/lint-wiki.py` currently reports historical warnings for tag taxonomy drift, missing sources, broken wikilinks, long pages, and sparse links.
- The legacy `wiki ingest` path can still hit upstream `llm-wiki` JSON/PTY issues; use `-y` and `--no-save` when running it non-interactively.
