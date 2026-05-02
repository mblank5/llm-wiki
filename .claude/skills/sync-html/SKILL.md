---
name: sync-html
description: Incrementally sync the llm-wiki static HTML site when markdown source files change. Detects new, modified, and deleted pages, then regenerates only the affected HTML files (detail pages, listings, search index). Also supports full rebuild. Use this skill whenever the user mentions updating the wiki site, regenerating HTML, syncing the web output, or says something like "update the site", "rebuild wiki HTML", "sync pages", "the site is out of date". Also trigger when the user runs wiki ingest commands or mentions that new papers were ingested.
---

# Wiki HTML Sync

This skill keeps the static HTML site (`web/output/`) in sync with the wiki's markdown sources (`entities/`, `concepts/`, `queries/`). It runs incrementally by default, only regenerating changed pages.

## How It Works

The generator script at `scripts/generate-web.py` contains everything: CSS, JS, HTML templates, and page generation logic. This skill wraps it with incremental change detection.

### Modes

1. **Incremental** (default, fast): Detect which `.md` files changed since last generation, regenerate only those HTML pages plus affected listing/index pages.
2. **Full rebuild**: Regenerate all 230+ HTML pages. Use when templates, CSS, or structural changes occur.

## Execution

### Step 1: Detect changes

Run this to see what changed:

```bash
cd /home/mblank/codes/llm-wiki-repo
python3 scripts/generate-web.py --status
```

This compares source `.md` files against existing HTML pages and reports:
- New pages (MD exists, no HTML)
- Modified pages (MD newer than HTML)
- Deleted pages (HTML exists, no MD)
- Structural changes (index.md, SCHEMA.md, or templates changed)

### Step 2: Run incremental update

```bash
python3 scripts/generate-web.py --incremental
```

This only regenerates affected pages. Typically completes in under 5 seconds.

If the user asks for a full rebuild, or if CSS/JS/templates changed:

```bash
python3 scripts/generate-web.py
```

### Step 3: Verify and serve

Check output:
```bash
python3 scripts/generate-web.py --status
```

Start preview server if needed:
```bash
cd web/output && python3 -m http.server 8080
```

## When to use each mode

| Situation | Mode |
|-----------|------|
| After `wiki ingest` or `bulk-ingest.py` | Incremental |
| New papers converted via `convert.sh` | Incremental |
| Modified existing wiki pages | Incremental |
| Changed CSS/JS in `generate-web.py` | Full rebuild |
| Changed HTML templates in generator | Full rebuild |
| New concept category added to `index.md` | Full rebuild |
| Uncertain what changed | `--status` first, then decide |

## Important paths

- Generator: `scripts/generate-web.py`
- Output: `web/output/` (gitignored)
- Source symlinks: `web/output/source/` → repo root dirs
- Search index: `web/output/search-index.json`
- Static assets: `web/output/static/wiki.css`, `wiki.js`

## Notes

- The generator auto-creates `web/output/source/` symlinks on first run
- Source `.md` links in HTML go through `../source/{type}/xxx.md`
- If `--status` or `--incremental` flags are not yet implemented, run full rebuild instead and tell the user the flags need to be added
- After syncing, remind the user they can preview at `http://localhost:8080`
