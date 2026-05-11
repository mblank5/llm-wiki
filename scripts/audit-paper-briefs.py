#!/usr/bin/env python3
"""Audit Chinese paper brief coverage and quality state."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    path: str
    message: str


def frontmatter_value(text: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}:\s*[\"']?([^\"'\n]+)", text[:1200], re.MULTILINE)
    return match.group(1).strip() if match else ""


def audit(root: Path) -> tuple[Counter[str], list[Finding]]:
    findings: list[Finding] = []
    counts: Counter[str] = Counter()
    raw_dir = root / "raw" / "papers"
    brief_dir = root / "paper-briefs"

    raw_paths = sorted(raw_dir.rglob("*.md")) if raw_dir.exists() else []
    counts["raw_papers"] = len(raw_paths)

    for raw_path in raw_paths:
        rel = raw_path.relative_to(raw_dir)
        brief_path = brief_dir / rel
        rel_brief = brief_path.relative_to(root).as_posix()
        if not brief_path.exists():
            findings.append(Finding("error", "missing-brief", rel_brief, "missing Chinese paper brief"))
            continue

        text = brief_path.read_text(encoding="utf-8", errors="ignore")
        quality = frontmatter_value(text, "quality")
        if not quality:
            findings.append(Finding("error", "missing-quality", rel_brief, "missing quality frontmatter"))
            continue

        counts[f"quality:{quality}"] += 1
        if quality == "pending_brief":
            findings.append(Finding("error", "pending-brief", rel_brief, "temporary pending brief must be completed"))
        elif quality == "source_limited":
            findings.append(Finding("warning", "source-limited", rel_brief, "source material is too limited for a full brief"))
        elif quality != "ok":
            findings.append(Finding("warning", "unknown-quality", rel_brief, f"unknown quality value: {quality}"))

        title_zh = frontmatter_value(text, "title_zh")
        if not title_zh:
            findings.append(Finding("error", "missing-title-zh", rel_brief, "missing title_zh frontmatter"))

    for brief_path in sorted(brief_dir.rglob("*.md")) if brief_dir.exists() else []:
        rel = brief_path.relative_to(brief_dir)
        raw_path = raw_dir / rel
        if not raw_path.exists():
            findings.append(
                Finding("warning", "orphan-brief", brief_path.relative_to(root).as_posix(), "brief has no raw paper source")
            )

    return counts, findings


def print_report(counts: Counter[str], findings: list[Finding], max_findings: int) -> None:
    print("Paper brief audit")
    print("=" * 50)
    print(f"raw papers: {counts.get('raw_papers', 0)}")
    for key in sorted(k for k in counts if k.startswith("quality:")):
        print(f"{key}: {counts[key]}")

    for severity in ("error", "warning"):
        scoped = [f for f in findings if f.severity == severity]
        if not scoped:
            continue
        print(f"\n{severity.upper()} ({len(scoped)})")
        shown = scoped if max_findings <= 0 else scoped[:max_findings]
        for finding in shown:
            print(f"  {finding.path}: [{finding.code}] {finding.message}")
        if len(shown) < len(scoped):
            print(f"  ... {len(scoped) - len(shown)} more {severity}s omitted")

        by_code = Counter(f.code for f in scoped)
        summary = ", ".join(f"{code}={count}" for code, count in sorted(by_code.items()))
        print(f"  by code: {summary}")

    errors = sum(1 for f in findings if f.severity == "error")
    warnings = sum(1 for f in findings if f.severity == "warning")
    print(f"\nSummary: {errors} errors, {warnings} warnings")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Chinese paper brief coverage")
    parser.add_argument("wiki_root", nargs="?", default=".", help="Repository/wiki root")
    parser.add_argument("--strict", action="store_true", help="fail on warnings as well as errors")
    parser.add_argument("--max-findings", type=int, default=80, help="maximum findings to print per severity")
    args = parser.parse_args()

    counts, findings = audit(Path(args.wiki_root).resolve())
    print_report(counts, findings, args.max_findings)

    has_errors = any(f.severity == "error" for f in findings)
    has_warnings = any(f.severity == "warning" for f in findings)
    if has_errors or (args.strict and has_warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
