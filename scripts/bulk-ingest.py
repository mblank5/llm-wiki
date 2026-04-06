#!/usr/bin/env python3
"""bulk-ingest.py — Ingest all papers in raw/untracked sequentially.
Usage: python3 bulk-ingest.py [wiki_dir]
"""
import os, sys, subprocess, glob

wiki_dir = sys.argv[1] if len(sys.argv) > 1 else "."
untracked = sorted(glob.glob(f"{wiki_dir}/raw/untracked/**/*.md", recursive=True))

if not untracked:
    print("No papers found in raw/untracked/")
    sys.exit(0)

print(f"Found {len(untracked)} papers to ingest\n")
success, failed = [], []

for i, paper in enumerate(untracked):
    rel = os.path.relpath(paper, f"{wiki_dir}/raw/untracked")
    aid = os.path.basename(paper).replace('.md', '')
    print(f"[{i+1}/{len(untracked)}] {aid}...", flush=True)

    result = subprocess.run(
        ["wiki", "ingest", rel, "-y"],
        capture_output=True, text=True, timeout=300, cwd=wiki_dir
    )

    if result.returncode == 0 and ("Ingested successfully" in result.stdout or "Proposed Operations" in result.stdout):
        success.append(aid)
        print(f"  OK")
    else:
        failed.append((aid, result.stderr[:200] if result.stderr else result.stdout[-200:]))
        print(f"  FAILED: {result.stderr[:150] if result.stderr else 'unknown'}")

print(f"\n{'='*50}")
print(f"Done: {len(success)}/{len(untracked)} succeeded")
if failed:
    print(f"\nFailed:")
    for aid, err in failed:
        print(f"  {aid}: {err[:120]}")
