# llm-wiki

Karpathy LLM Wiki for ArXiv papers — powered by `arxiv2md` + `llm-wiki`.

A pattern for building personal knowledge bases using LLMs, specifically tailored for ArXiv papers. Instead of just retrieving from raw documents at query time, the LLM incrementally builds and maintains a persistent, interlinked wiki where knowledge is compiled once, kept current, and grows smarter over time.

See Karpathy's original idea: [karpathy/llm-wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)

## Current Workflow

```bash
# Clean raw paper markdown into papers/YYYY/MM/*.md
python3 scripts/clean-papers.py . --limit 3

# Validate wiki structure and metadata
python3 scripts/lint-wiki.py .
# Limit CI-style warning output while keeping full counts
python3 scripts/lint-wiki.py . --max-findings 80

# Audit Chinese paper brief coverage and quality state
python3 scripts/audit-paper-briefs.py .

# Generate the static web site into web/output/
python3 scripts/generate-web.py

# Build Chinese paper reading cards into paper-briefs/YYYY/MM/*.md
python3 scripts/build-paper-briefs.py .

# Repair weak arXiv conversions using DeepXiv raw Markdown
python3 scripts/fetch-deepxiv-raw.py . 2601.04720 2604.15774

# Check whether web/output is stale
python3 scripts/generate-web.py --status
```

The repository itself is the active wiki root. GitHub Pages rebuilds the static
site on pushes to `main`.

The static site renders both wiki pages and raw paper pages. `concepts/`,
`entities/`, and `queries/` become interlinked detail pages; every
`raw/papers/YYYY/MM/*.md` file also gets a readable HTML page under
`web/output/papers/<arxiv-id>.html`. Paper pages prefer the Chinese research
cards in `paper-briefs/YYYY/MM/*.md`, then link back to the cleaned Markdown and
raw source. The papers listing links to both the HTML reader and the original
Markdown source, and source chips on wiki pages point to the rendered paper page
when one exists.

## Legacy Setup Helper

`setup-arxiv-wiki.sh` remains as a one-shot helper for creating another
`llm-wiki` workspace and applying the local upstream patches:

```bash
bash setup-arxiv-wiki.sh ~/my-wiki <base_url> <model> <api_key>
```

## Repo Structure

```
├── concepts/                 # Concept/topic pages
├── entities/                 # Entity pages: models, orgs, products
├── queries/                  # Saved research query answers
├── raw/                      # Immutable source material
│   ├── articles/
│   └── papers/
├── papers/                   # Cleaned paper markdown, organized by YYYY/MM
├── paper-briefs/             # Chinese research cards for paper HTML pages
├── scripts/
│   ├── clean-papers.py       # LLM paper cleaning pipeline
│   ├── build-paper-briefs.py # Chinese paper brief generation pipeline
│   ├── audit-paper-briefs.py # Paper brief coverage/quality audit
│   ├── fetch-deepxiv-raw.py  # DeepXiv fallback for weak arxiv2md sources
│   ├── lint-wiki.py          # Wiki metadata/link/source lint
│   ├── generate-web.py       # Static site generator
│   ├── convert.sh            # Legacy arxiv2md helper
│   ├── bulk-ingest.py        # Legacy llm-wiki ingest helper
│   └── rebuild-index.py      # Legacy llm-wiki index helper
├── web/
│   ├── app/main.py           # Experimental multi-wiki FastAPI app
│   └── output/               # Generated static site, ignored by git
├── patches/                  # Source patches for upstream llm-wiki
├── references/               # Patch documentation
├── SCHEMA.md                 # Wiki content schema and tag taxonomy
├── index.md                  # Human-maintained knowledge index
└── log.md / log-2026.md      # Append-only work logs
```

## Quality Gates

`scripts/lint-wiki.py` blocks structural errors:

- missing or invalid YAML frontmatter
- missing required frontmatter fields
- invalid `tags` / `sources` field shapes

It reports current migration debt as warnings:

- tags outside `SCHEMA.md`
- missing source paths
- broken wikilinks
- pages over the split threshold
- pages with too few outbound wikilinks

Wikilinks that point to valid tags, such as `[[grpo]]`, are rendered as links
to the generated tags page instead of broken page links.

The generated search index includes wiki pages plus rendered paper pages, so
search can jump directly to a paper HTML reader instead of only exposing the raw
Markdown file.

If model quota is unavailable, `scripts/build-paper-briefs.py --fallback-missing`
creates Chinese "pending brief" cards so the site does not fall back to raw
English paper dumps. Re-run with `--force --ids <paper-id>` or normal batch mode
when quota is restored to replace pending cards with full Chinese briefs.

`scripts/audit-paper-briefs.py` is the coverage guard for paper pages. It fails
on missing briefs or `pending_brief` placeholders, and reports `source_limited`
cards as warnings so incomplete upstream source material remains visible.

`deepxiv` is available as a local CLI and is the preferred fallback when
`arxiv2md` produces empty arXiv HTML captures. Use `scripts/fetch-deepxiv-raw.py`
to replace weak raw sources, then rerun `scripts/build-paper-briefs.py --force
--ids <paper-id>` for the affected papers.

## Patches Applied

The upstream `llm-wiki` (npm) has bugs with large ArXiv papers. We apply 4 patches:

| Patch | What it fixes |
|-------|--------------|
| 01 | `chatJSON()` — Forces `response_format: json_object` for reliable JSON output |
| 02 | Ingest flow — Use `chatJSON()` instead of `chat()` for ingest |
| 03 | Agent prompt — No LaTeX rule to prevent JSON escaping failures |
| 04 | Path lookup — Recursive search for files stored in `raw/ingested/YYYY/MM/` |

## Known Limitations

- Long papers are currently cleaned through a fixed input window in `clean-papers.py`; chunked section-level cleaning is a future improvement.
- `scripts/lint-wiki.py` still reports historical warnings for tag taxonomy drift, missing sources, broken wikilinks, and long pages.
- The legacy `wiki ingest` path can still hit upstream `llm-wiki` JSON/PTY issues; use `-y` and `--no-save` when running it non-interactively.

## Prerequisites

- Node.js 18+
- `arxiv2md` CLI
- OpenAI-compatible API endpoint (LongCat, OpenAI, vLLM, Ollama, etc.)
