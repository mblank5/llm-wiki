#!/usr/bin/env python3
"""
Clean raw arXiv paper MDs into well-structured, detailed markdown pages.
Uses LLM to extract metadata, remove HTML noise, and restructure content.

Usage:
    # Process all unprocessed papers
    python3 scripts/clean-papers.py .

    # Process first 3 papers (test run)
    python3 scripts/clean-papers.py . --limit 3

    # Force reprocess specific papers
    python3 scripts/clean-papers.py . --force 2603.09023 2604.01496

    # Dry run (show what would be processed)
    python3 scripts/clean-papers.py . --dry-run
"""

import os
import sys
import re
import json
import time
import argparse
from pathlib import Path
from datetime import date
from dotenv import dotenv_values
from openai import OpenAI


WIKI_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = WIKI_ROOT / "raw" / "papers"
OUTPUT_DIR = WIKI_ROOT / "papers"
DONE_FILE = WIKI_ROOT / "papers" / ".processed.json"

MAX_INPUT_CHARS = 48000
DELAY = 1.5


def load_config():
    env_path = WIKI_ROOT / ".env"
    cfg = {}
    if env_path.exists():
        cfg = dotenv_values(env_path)
    return {
        "api_base": os.environ.get("PAPER_API_BASE", cfg.get("PAPER_API_BASE", "")),
        "api_key": os.environ.get("PAPER_API_KEY", cfg.get("PAPER_API_KEY", "")),
        "model": os.environ.get("PAPER_MODEL", cfg.get("PAPER_MODEL", "gpt-4o")),
    }


def find_papers():
    return sorted(RAW_DIR.rglob("*.md"), reverse=True)


def load_processed():
    if DONE_FILE.exists():
        return set(json.loads(DONE_FILE.read_text()))
    return set()


def save_processed(done):
    DONE_FILE.parent.mkdir(parents=True, exist_ok=True)
    DONE_FILE.write_text(json.dumps(sorted(done)))


def read_paper(path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    if len(text) > MAX_INPUT_CHARS:
        # Keep beginning and end
        head = text[:MAX_INPUT_CHARS // 2]
        tail = text[-(MAX_INPUT_CHARS // 4):]
        text = head + "\n\n[... content truncated for length ...]\n\n" + tail
    return text


SYSTEM_PROMPT = """You are a research paper processing assistant. Your job is to convert noisy, poorly-formatted arXiv paper text into clean, detailed, well-structured Markdown.

Rules:
1. Extract metadata into YAML frontmatter: title, arxiv ID, authors, date, tags, affiliation
2. Remove ALL HTML/web artifacts: "Report GitHub Issue", "Back to arXiv", "Why HTML?", "Download PDF", "Submit", "Content selection saved", navigation links, form elements
3. Use proper Markdown formatting: ## for main sections, ### for subsections
4. Preserve ALL technical content: formulas (use LaTeX $...$ and $$...$$), algorithms, tables
5. Do NOT summarize or shorten the paper. Preserve full detail.
6. Keep the paper in English (original language).
7. Clean up author names, affiliations, emails into structured format
8. Convert figure/table references into proper Markdown
9. Ensure the abstract is complete and verbatim from the original
10. Add a ## Key Contributions section listing 3-5 main contributions as bullet points
11. If the paper has experimental results, ensure key numbers are preserved in tables or structured text

Output ONLY the markdown content starting with the --- frontmatter. No explanations before or after."""


def process_paper(client, model, paper_path):
    content = read_paper(paper_path)
    paper_id = paper_path.stem

    user_msg = f"Paper ID: {paper_id}\n\nRaw paper text:\n\n{content}"

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.1,
        max_tokens=16000,
    )

    result = resp.choices[0].message.content.strip()

    # Strip code block markers if the LLM wrapped output
    if result.startswith("```"):
        result = re.sub(r"^```\w*\n?", "", result)
        result = re.sub(r"\n?```$", "", result)

    return result.strip()


def main():
    parser = argparse.ArgumentParser(description="Clean raw paper MDs into structured pages")
    parser.add_argument("wiki_root", help="Wiki root directory (usually .)")
    parser.add_argument("--limit", type=int, help="Max papers to process")
    parser.add_argument("--force", nargs="+", help="Paper IDs to force reprocess")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be processed")
    args = parser.parse_args()

    global WIKI_ROOT, RAW_DIR, OUTPUT_DIR, DONE_FILE
    WIKI_ROOT = Path(args.wiki_root).resolve()
    RAW_DIR = WIKI_ROOT / "raw" / "papers"
    OUTPUT_DIR = WIKI_ROOT / "papers"
    DONE_FILE = OUTPUT_DIR / ".processed.json"

    cfg = load_config()
    if not cfg["api_key"]:
        print("Error: Set PAPER_API_KEY in .env or environment")
        sys.exit(1)

    client = OpenAI(base_url=cfg["api_base"], api_key=cfg["api_key"])

    papers = find_papers()
    print(f"Found {len(papers)} papers in raw/papers/")
    print(f"Model: {cfg['model']}")
    print(f"API: {cfg['api_base']}")
    print()

    done = load_processed()
    force_ids = set(args.force or [])

    todo = []
    for p in papers:
        pid = p.stem
        if pid in force_ids:
            todo.append(p)
        elif pid not in done:
            todo.append(p)

    if args.limit:
        todo = todo[:args.limit]

    print(f"Already processed: {len(done)}")
    print(f"To process: {len(todo)}")

    if args.dry_run:
        for p in todo:
            rel = p.relative_to(RAW_DIR)
            size = p.stat().st_size
            print(f"  {rel} ({size:,} bytes)")
        return

    if not todo:
        print("Nothing to do.")
        return

    print()

    ok = 0
    err = 0
    for i, paper in enumerate(todo):
        pid = paper.stem
        rel = paper.relative_to(RAW_DIR)
        print(f"[{i+1}/{len(todo)}] {pid} ({paper.stat().st_size:,} bytes) ...", flush=True)

        t0 = time.time()
        try:
            result = process_paper(client, cfg["model"], paper)

            out_path = OUTPUT_DIR / rel
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(result, encoding="utf-8")

            done.add(pid)
            save_processed(done)
            ok += 1
            dt = time.time() - t0
            print(f"  OK ({len(result):,} chars, {dt:.1f}s) -> papers/{rel}")

        except Exception as e:
            err += 1
            print(f"  ERROR: {e}")

        if i < len(todo) - 1:
            time.sleep(DELAY)

    print(f"\nDone! OK: {ok}, Errors: {err}")


if __name__ == "__main__":
    main()
