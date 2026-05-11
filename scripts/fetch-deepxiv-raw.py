#!/usr/bin/env python3
"""Fetch raw paper Markdown from the deepxiv CLI into raw/papers.

Use this when arxiv2md produces an empty/short arXiv HTML conversion but
DeepXiv has the parsed paper body.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def paper_relpath(arxiv_id: str) -> Path:
    year = f"20{arxiv_id[:2]}"
    month = arxiv_id[2:4]
    return Path(year) / month / f"{arxiv_id}.md"


def fetch_one(root: Path, arxiv_id: str) -> Path:
    result = subprocess.run(
        ["deepxiv", "paper", arxiv_id, "--raw"],
        check=True,
        text=True,
        capture_output=True,
    )
    content = result.stdout.strip()
    if len(content) < 1000:
        raise RuntimeError(f"{arxiv_id}: DeepXiv returned only {len(content)} chars")
    out_path = root / "raw" / "papers" / paper_relpath(arxiv_id)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content + "\n", encoding="utf-8")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch raw Markdown from DeepXiv")
    parser.add_argument("wiki_root", help="Repository/wiki root")
    parser.add_argument("arxiv_ids", nargs="+", help="arXiv IDs to fetch")
    args = parser.parse_args()

    root = Path(args.wiki_root).resolve()
    ok = 0
    for arxiv_id in args.arxiv_ids:
        try:
            out_path = fetch_one(root, arxiv_id)
            print(f"{arxiv_id}: {out_path.relative_to(root)} ({out_path.stat().st_size:,} bytes)")
            ok += 1
        except Exception as exc:
            print(f"{arxiv_id}: ERROR: {exc}", file=sys.stderr)
    return 0 if ok == len(args.arxiv_ids) else 1


if __name__ == "__main__":
    raise SystemExit(main())
