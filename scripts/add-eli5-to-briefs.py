#!/usr/bin/env python3
"""Add child-friendly explanations to existing Chinese paper briefs."""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from dotenv import dotenv_values
from openai import OpenAI


SECTION_TITLE = "## 小学生也能听懂"


def load_config(root: Path) -> dict[str, str]:
    env_path = root / ".env"
    cfg = dotenv_values(env_path) if env_path.exists() else {}
    return {
        "api_base": os.environ.get("PAPER_API_BASE", cfg.get("PAPER_API_BASE", "")),
        "api_key": os.environ.get("PAPER_API_KEY", cfg.get("PAPER_API_KEY", "")),
        "model": os.environ.get("PAPER_MODEL", cfg.get("PAPER_MODEL", "gpt-4o")),
    }


def extract_section(text: str, heading: str) -> str:
    pattern = re.compile(rf"^{re.escape(heading)}\s*\n(.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL)
    match = pattern.search(text)
    if not match:
        return ""
    return re.sub(r"\s+", " ", match.group(1)).strip()


def extract_title(text: str, fallback: str) -> str:
    if match := re.search(r"^title_zh:\s*[\"']?([^\"'\n]+)", text[:1200], re.MULTILINE):
        return match.group(1).strip()
    if match := re.search(r"^#\s+(.+)$", text, re.MULTILINE):
        return match.group(1).strip()
    return fallback


def deterministic_explanation(title: str, one_liner: str) -> str:
    basis = one_liner or title
    basis = basis.rstrip("。")
    if len(basis) > 92:
        basis = basis[:92].rstrip("，,；; ") + "..."
    return f"可以把这篇论文想成一次给电脑上的小实验：研究者想解决“{basis}”这个问题，并看看这个办法是不是真的更有用。"


def call_model(client: OpenAI, model: str, title: str, one_liner: str, notes: str) -> str:
    prompt = f"""请用小学生能听懂的中文解释这篇论文做了什么。

要求：
- 只输出一段话，不要标题，不要列表。
- 不超过 120 个中文字。
- 可以打比方，但必须保留论文真实问题和核心方法，不能编造。

论文标题：{title}
一句话定位：{one_liner}
已有摘要片段：{notes[:1600]}
"""
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=220,
            )
            content = (resp.choices[0].message.content or "").strip()
            content = re.sub(r"^#+\s*", "", content).strip()
            return content.strip("` \n")
        except Exception as exc:
            last_error = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(str(last_error))


def insert_section(text: str, explanation: str) -> str:
    pattern = re.compile(r"(^## 一句话定位\s*\n.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL)
    match = pattern.search(text)
    if not match:
        return text.rstrip() + f"\n\n{SECTION_TITLE}\n\n{explanation}\n"
    block = match.group(1).rstrip()
    replacement = f"{block}\n\n{SECTION_TITLE}\n\n{explanation}\n\n"
    return text[: match.start()] + replacement + text[match.end() :]


def process_one(path: Path, client: OpenAI | None, model: str, force: bool) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if SECTION_TITLE in text and not force:
        return path.as_posix(), "skip"
    title = extract_title(text, path.stem)
    one_liner = extract_section(text, "## 一句话定位")
    notes = "\n\n".join(
        value for value in [
            extract_section(text, "## 为什么值得记录"),
            extract_section(text, "## 核心方法"),
            extract_section(text, "## 关键结果"),
        ]
        if value
    )
    if client:
        explanation = call_model(client, model, title, one_liner, notes)
    else:
        explanation = deterministic_explanation(title, one_liner)
    if not explanation:
        explanation = deterministic_explanation(title, one_liner)
    path.write_text(insert_section(text, explanation), encoding="utf-8")
    return path.as_posix(), "updated"


def main() -> int:
    parser = argparse.ArgumentParser(description="Ensure paper briefs include an ELI5 section")
    parser.add_argument("wiki_root", nargs="?", default=".", help="Repository/wiki root")
    parser.add_argument("--workers", type=int, default=4, help="Concurrent API workers")
    parser.add_argument("--limit", type=int, help="Maximum briefs to update")
    parser.add_argument("--force", action="store_true", help="Regenerate existing ELI5 sections")
    parser.add_argument("--fallback", action="store_true", help="Use deterministic fallback instead of the model")
    parser.add_argument("--dry-run", action="store_true", help="Only print missing files")
    args = parser.parse_args()

    root = Path(args.wiki_root).resolve()
    paths = sorted((root / "paper-briefs").rglob("*.md"))
    if not args.force:
        paths = [p for p in paths if SECTION_TITLE not in p.read_text(encoding="utf-8", errors="ignore")]
    if args.limit:
        paths = paths[: args.limit]

    print(f"To update: {len(paths)}")
    if args.dry_run:
        for path in paths:
            print(path.relative_to(root))
        return 0
    if not paths:
        return 0

    cfg = load_config(root)
    client = None
    if not args.fallback:
        if not cfg["api_key"]:
            print("Error: Set PAPER_API_KEY or pass --fallback", file=sys.stderr)
            return 1
        client = OpenAI(base_url=cfg["api_base"], api_key=cfg["api_key"])

    updated = 0
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = {pool.submit(process_one, path, client, cfg["model"], args.force): path for path in paths}
        for future in as_completed(futures):
            path = futures[future]
            try:
                _, status = future.result()
                if status == "updated":
                    updated += 1
                print(f"{path.relative_to(root)}: {status}")
            except Exception as exc:
                print(f"{path.relative_to(root)}: ERROR: {exc}", file=sys.stderr)
                return 1
    print(f"Updated: {updated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
