#!/usr/bin/env python3
"""Sync DeepXiv weekly trending papers into the wiki.

The DeepXiv CLI exposes rolling 7/14/30 day windows. This script uses the
7-day window as the weekly hot-paper feed, fetches missing paper bodies, builds
Chinese paper briefs for newly fetched papers, and writes a durable hot list
for the static site.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


def paper_relpath(arxiv_id: str) -> Path:
    year = f"20{arxiv_id[:2]}"
    month = arxiv_id[2:4]
    return Path(year) / month / f"{arxiv_id}.md"


def parse_json_output(output: str) -> dict[str, Any]:
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        start = output.find("{")
        end = output.rfind("}")
        if start >= 0 and end > start:
            return json.loads(output[start : end + 1])
        raise


def run_json(cmd: list[str]) -> dict[str, Any]:
    result = subprocess.run(cmd, check=True, text=True, capture_output=True)
    return parse_json_output(result.stdout)


def existing_raw_paths(root: Path) -> dict[str, Path]:
    papers_dir = root / "raw" / "papers"
    if not papers_dir.exists():
        return {}
    return {path.stem: path for path in papers_dir.rglob("*.md")}


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    try:
        meta = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        meta = {}
    return meta if isinstance(meta, dict) else {}, parts[2].strip()


def first_paragraph(markdown: str) -> str:
    lines: list[str] = []
    in_target = False
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("## 一句话定位") or stripped.startswith("## 小学生也能听懂"):
            in_target = True
            lines = []
            continue
        if in_target and stripped.startswith("## "):
            break
        if in_target and stripped and not stripped.startswith("#"):
            lines.append(stripped.lstrip("- ").strip())
            if len(" ".join(lines)) > 180:
                break
    return " ".join(lines).strip()


def read_brief_summary(root: Path, raw_path: Path | None, arxiv_id: str) -> dict[str, str]:
    if raw_path:
        rel = raw_path.relative_to(root / "raw" / "papers")
        brief_path = root / "paper-briefs" / rel
    else:
        brief_path = root / "paper-briefs" / paper_relpath(arxiv_id)
    if not brief_path.exists():
        return {}

    text = brief_path.read_text(encoding="utf-8", errors="ignore")
    meta, body = split_frontmatter(text)
    return {
        "title": str(meta.get("title") or ""),
        "title_zh": str(meta.get("title_zh") or ""),
        "quality": str(meta.get("quality") or ""),
        "paper_type": str(meta.get("paper_type") or ""),
        "preview": first_paragraph(body),
    }


def fetch_raw(root: Path, arxiv_id: str) -> Path:
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


def build_briefs(root: Path, ids: list[str], workers: int) -> None:
    if not ids:
        return
    subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "build-paper-briefs.py"),
            str(root),
            "--ids",
            *ids,
            "--workers",
            str(workers),
        ],
        check=True,
    )


def mentioned_by_count(paper: dict[str, Any]) -> int:
    mentioned_by = paper.get("mentioned_by")
    if isinstance(mentioned_by, list):
        return len(mentioned_by)
    stats = paper.get("stats")
    if isinstance(stats, dict):
        for key in ("mentions", "mention_count", "count"):
            if isinstance(stats.get(key), int):
                return int(stats[key])
    return 0


def comparable_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if key not in {"generated_at", "deepxiv_generated_at"}}


def write_hot_payload(path: Path, payload: dict[str, Any], dry_run: bool) -> None:
    if dry_run:
        return
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
            if comparable_payload(existing) == comparable_payload(payload):
                print(f"No material hot list changes: {path.relative_to(path.parent.parent)}")
                return
        except json.JSONDecodeError:
            pass
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sync(root: Path, days: int, limit: int, workers: int, dry_run: bool, strict: bool) -> int:
    feed = run_json(["deepxiv", "trending", "--days", str(days), "--limit", str(limit), "--json"])
    feed_papers = feed.get("papers") or []
    if not isinstance(feed_papers, list):
        raise RuntimeError("DeepXiv trending response did not include a papers list")

    raw_paths = existing_raw_paths(root)
    new_ids: list[str] = []
    failed: list[str] = []

    for item in feed_papers:
        if not isinstance(item, dict):
            continue
        arxiv_id = str(item.get("arxiv_id") or "").strip()
        if not arxiv_id or arxiv_id in raw_paths:
            continue
        new_ids.append(arxiv_id)
        if dry_run:
            continue
        try:
            raw_paths[arxiv_id] = fetch_raw(root, arxiv_id)
            print(f"Fetched {arxiv_id}: {raw_paths[arxiv_id].relative_to(root)}")
        except Exception as exc:
            failed.append(arxiv_id)
            print(f"{arxiv_id}: ERROR fetching raw paper: {exc}", file=sys.stderr)

    fetched_ids = [paper_id for paper_id in new_ids if paper_id in raw_paths]
    if fetched_ids and not dry_run:
        build_briefs(root, fetched_ids, workers)
        raw_paths = existing_raw_paths(root)

    output_papers: list[dict[str, Any]] = []
    for item in feed_papers:
        if not isinstance(item, dict):
            continue
        arxiv_id = str(item.get("arxiv_id") or "").strip()
        if not arxiv_id:
            continue
        raw_path = raw_paths.get(arxiv_id)
        brief = read_brief_summary(root, raw_path, arxiv_id)
        output_papers.append(
            {
                "rank": item.get("rank"),
                "arxiv_id": arxiv_id,
                "arxiv_url": item.get("arxiv_url") or f"https://arxiv.org/abs/{arxiv_id}",
                "mentioned_by_count": mentioned_by_count(item),
                "mentioned_by": item.get("mentioned_by") or [],
                "stats": item.get("stats") or {},
                "timeline": item.get("timeline") or [],
                "in_library": bool(raw_path),
                "is_new": arxiv_id in fetched_ids,
                "href": f"papers/{arxiv_id}.html" if raw_path else "",
                "raw_path": raw_path.relative_to(root).as_posix() if raw_path else "",
                "title": brief.get("title") or str(item.get("title") or ""),
                "title_zh": brief.get("title_zh") or "",
                "paper_type": brief.get("paper_type") or "",
                "quality": brief.get("quality") or "",
                "preview": brief.get("preview") or "",
            }
        )

    hot_dir = root / "hot"
    hot_dir.mkdir(exist_ok=True)
    payload = {
        "source": "deepxiv",
        "window": "weekly",
        "days": days,
        "limit": limit,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "deepxiv_generated_at": feed.get("generated_at"),
        "new_ids": fetched_ids,
        "failed_ids": failed,
        "papers": output_papers,
    }
    write_hot_payload(hot_dir / "trending-weekly.json", payload, dry_run)

    print(f"Trending papers: {len(output_papers)}")
    print(f"New in feed: {len(new_ids)}")
    print(f"Fetched: {len(fetched_ids)}")
    if failed:
        print(f"Failed: {', '.join(failed)}", file=sys.stderr)
    return 1 if failed and strict else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync DeepXiv trending papers into this wiki")
    parser.add_argument("wiki_root", nargs="?", default=".", help="Repository/wiki root")
    parser.add_argument("--days", type=int, choices=[7, 14, 30], default=7, help="DeepXiv rolling window")
    parser.add_argument("--limit", type=int, default=30, help="Maximum trending papers to sync")
    parser.add_argument("--workers", type=int, default=2, help="Concurrent paper brief workers")
    parser.add_argument("--dry-run", action="store_true", help="Fetch feed and print plan without writing")
    parser.add_argument("--strict", action="store_true", help="Return non-zero when a feed item cannot be fetched")
    args = parser.parse_args()

    return sync(Path(args.wiki_root).resolve(), args.days, args.limit, args.workers, args.dry_run, args.strict)


if __name__ == "__main__":
    raise SystemExit(main())
