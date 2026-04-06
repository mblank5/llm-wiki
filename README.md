# llm-wiki

Karpathy LLM Wiki for ArXiv papers — powered by `arxiv2md` + `llm-wiki`.

A pattern for building personal knowledge bases using LLMs, specifically tailored for ArXiv papers. Instead of just retrieving from raw documents at query time, the LLM incrementally builds and maintains a persistent, interlinked wiki where knowledge is compiled once, kept current, and grows smarter over time.

See Karpathy's original idea: [karpathy/llm-wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)

## Quick Start

```bash
git clone git@github.com:mblank5/llm-wiki.git
cd llm-wiki
bash setup-arxiv-wiki.sh ~/my-wiki <base_url> <model> <api_key>
```

Then convert your first paper:

```bash
cd ~/my-wiki
bash <llm-wiki-repo>/scripts/convert.sh 2501.11120v1 .
wiki ingest "2025/01/2501.11120v1.md" -y
wiki query "What are the key findings?"
```

## Repo Structure

```
├── setup-arxiv-wiki.sh      # One-shot setup: install llm-wiki, patch, init wiki
├── SKILL.md                  # AI Agent skill definition
├── README.md                 # This file
├── patches/                  # 4 source patches for llm-wiki
│   ├── 01-chatjson.patch     # Add chatJSON() method to LLMClient
│   ├── 02-use-chatjson.patch # Use chatJSON in ingest flow
│   ├── 03-no-latex-agent     # No LaTeX rule in agent.md
│   └── 04-path-lookup.patch  # Fix recursive path lookup for nested files
├── scripts/                  # Helper utilities
│   ├── convert.sh            # arxiv2md + auto-place in raw/untracked
│   ├── bulk-ingest.py        # Ingest all pending papers sequentially
│   └── rebuild-index.py      # Rebuild wiki/index.md from actual content
└── references/               # Detailed reference docs
    └── llm-wiki-patches.md   # Full patch documentation for manual apply
```

## Patches Applied

The upstream `llm-wiki` (npm) has bugs with large ArXiv papers. We apply 4 patches:

| Patch | What it fixes |
|-------|--------------|
| 01 | `chatJSON()` — Forces `response_format: json_object` for reliable JSON output |
| 02 | Ingest flow — Use `chatJSON()` instead of `chat()` for ingest |
| 03 | Agent prompt — No LaTeX rule to prevent JSON escaping failures |
| 04 | Path lookup — Recursive search for files stored in `raw/ingested/YYYY/MM/` |

## Known Limitations

- Papers >150KB with dense LaTeX formulas may still fail ingest despite patches. Manual fallback is documented in SKILL.md.
- The LLM often truncates operations after the first page. Run `scripts/rebuild-index.py` after batch ingest.
- Interactive prompts (`wiki ingest`, `wiki query --save`) crash in non-PTY mode. Use `-y` flags and `--no-save`.

## Prerequisites

- Node.js 18+
- `arxiv2md` CLI
- OpenAI-compatible API endpoint (LongCat, OpenAI, vLLM, Ollama, etc.)
