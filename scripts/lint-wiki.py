#!/usr/bin/env python3
"""Validate the top-level LLM wiki content.

The lint is intentionally split into blocking errors and migration warnings.
Errors are structural issues that make downstream tooling unreliable. Warnings
are existing knowledge-base hygiene issues that should be fixed in batches.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml


PAGE_DIRS = ("concepts", "entities", "queries")
REQUIRED_FIELDS = ("title", "created", "updated", "type", "tags", "sources")
MAX_PAGE_LINES = 200


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    path: str
    message: str


def extract_allowed_tags(schema_path: Path) -> set[str]:
    allowed: set[str] = set()
    if not schema_path.exists():
        return allowed
    for line in schema_path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("- **") or ":" not in line:
            continue
        _, values = line.split(":", 1)
        allowed.update(tag.strip() for tag in values.split(",") if tag.strip())
    return allowed


def iter_pages(root: Path) -> Iterable[Path]:
    for page_dir in PAGE_DIRS:
        base = root / page_dir
        if base.exists():
            yield from sorted(base.glob("*.md"))


def split_frontmatter(text: str) -> tuple[str | None, str]:
    if not text.startswith("---"):
        return None, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, text
    return parts[1], parts[2]


def wiki_links(body: str) -> set[str]:
    return {
        match.strip()
        for match in re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", body)
    }


def likely_page_link(link: str) -> bool:
    return "/" not in link and not link.endswith(".md")


def lint(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    allowed_tags = extract_allowed_tags(root / "SCHEMA.md")
    pages = {page.stem: page for page in iter_pages(root)}

    for page in iter_pages(root):
        rel = page.relative_to(root).as_posix()
        text = page.read_text(encoding="utf-8", errors="ignore")
        frontmatter, body = split_frontmatter(text)

        meta: dict = {}
        if frontmatter is None:
            findings.append(Finding("error", "missing-frontmatter", rel, "missing YAML frontmatter"))
        else:
            try:
                loaded = yaml.safe_load(frontmatter)
                if isinstance(loaded, dict):
                    meta = loaded
                else:
                    findings.append(Finding("error", "invalid-frontmatter", rel, "frontmatter must be a mapping"))
            except yaml.YAMLError as exc:
                first_line = str(exc).splitlines()[0]
                findings.append(Finding("error", "yaml-parse", rel, first_line))

        if meta:
            missing = [field for field in REQUIRED_FIELDS if field not in meta]
            if missing:
                findings.append(
                    Finding("error", "missing-required-field", rel, f"missing fields: {', '.join(missing)}")
                )

            page_type = meta.get("type")
            expected_type = {
                "concepts": "concept",
                "entities": "entity",
                "queries": "query",
            }.get(page.parent.name, page.parent.name)
            if page_type and page_type != expected_type:
                findings.append(
                    Finding("warning", "type-mismatch", rel, f"type is {page_type!r}, expected {expected_type!r}")
                )

            tags = meta.get("tags", [])
            if not isinstance(tags, list):
                findings.append(Finding("error", "invalid-tags", rel, "tags must be a YAML list"))
            elif allowed_tags:
                unknown = sorted(tag for tag in tags if tag not in allowed_tags)
                if unknown:
                    findings.append(
                        Finding("warning", "unknown-tags", rel, f"not in SCHEMA.md taxonomy: {', '.join(unknown)}")
                    )

            sources = meta.get("sources", [])
            if not isinstance(sources, list):
                findings.append(Finding("error", "invalid-sources", rel, "sources must be a YAML list"))
            else:
                missing_sources = [str(source) for source in sources if not (root / str(source)).exists()]
                if missing_sources:
                    findings.append(
                        Finding("warning", "missing-sources", rel, f"missing: {', '.join(missing_sources[:5])}")
                    )

        links = {link for link in wiki_links(body) if likely_page_link(link)}
        broken = sorted(link for link in links if link != page.stem and link not in pages and link not in allowed_tags)
        if broken:
            findings.append(
                Finding("warning", "broken-wikilinks", rel, f"broken: {', '.join(broken[:8])}")
            )
        if len(links) < 2:
            findings.append(
                Finding("warning", "few-wikilinks", rel, f"has {len(links)} wiki links, expected at least 2")
            )

        line_count = len(text.splitlines())
        if line_count > MAX_PAGE_LINES:
            findings.append(
                Finding("warning", "page-too-long", rel, f"{line_count} lines, split threshold is {MAX_PAGE_LINES}")
            )

    return findings


def print_findings(findings: list[Finding], max_findings: int = 0) -> None:
    counts = {"error": 0, "warning": 0}
    for finding in findings:
        counts[finding.severity] = counts.get(finding.severity, 0) + 1

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

    print(f"\nSummary: {counts.get('error', 0)} errors, {counts.get('warning', 0)} warnings")


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint LLM wiki markdown content")
    parser.add_argument("wiki_root", nargs="?", default=".", help="Repository/wiki root")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="fail on warnings as well as errors",
    )
    parser.add_argument(
        "--max-findings",
        type=int,
        default=0,
        help="maximum findings to print per severity; 0 prints all",
    )
    args = parser.parse_args()

    root = Path(args.wiki_root).resolve()
    findings = lint(root)
    print_findings(findings, args.max_findings)

    has_errors = any(f.severity == "error" for f in findings)
    has_warnings = any(f.severity == "warning" for f in findings)
    if has_errors or (args.strict and has_warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
